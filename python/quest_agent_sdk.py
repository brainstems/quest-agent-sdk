"""
Quest Agent SDK for LangChain Integration
==========================================

Allows external LangChain agents to integrate with Quest Agent Forge system.

Integration Patterns:
1. Redis Streams (Event-Driven) - Recommended for production
2. REST API (Request-Response) - Simpler, good for synchronous calls
3. Hybrid (Both) - Maximum flexibility

Author: Quest Agent Forge Team
Version: 1.0.0
"""

import json
import hashlib
import uuid
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Callable
import redis
import requests
from dataclasses import dataclass, asdict


# ============================================================================
# Core Configuration
# ============================================================================

@dataclass
class QuestAgentConfig:
    """Configuration for Quest Agent SDK"""
    # Redis configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    
    # REST API configuration
    api_url: str = "http://localhost:3000"
    api_key: Optional[str] = None
    
    # Agent metadata
    agent_id: str = None
    agent_name: str = None
    agent_version: str = "1.0.0"
    
    # Stream configuration
    command_stream: str = "mesh:commands"
    event_stream: str = "mesh:events"
    consumer_group: str = "langchain-agents"
    
    def __post_init__(self):
        if not self.agent_id:
            self.agent_id = f"langchain-{uuid.uuid4().hex[:8]}"
        if not self.agent_name:
            self.agent_name = f"LangChain Agent ({self.agent_id})"


# ============================================================================
# CloudEvents Envelope Builder
# ============================================================================

class MeshEnvelopeBuilder:
    """Builds CloudEvents-compliant mesh envelopes"""
    
    @staticmethod
    def create_envelope(
        event_type: Optional[str] = None,
        command_type: Optional[str] = None,
        producer: Optional[Dict] = None,
        subject: Optional[Dict] = None,
        payload: Optional[Dict] = None,
        tags: Optional[List[str]] = None,
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> Dict:
        """Create a mesh envelope"""
        envelope = {
            "envelope_version": "1.0",
            "event_type": event_type,
            "command_type": command_type,
            "trace_id": trace_id or str(uuid.uuid4()),
            "span_id": str(uuid.uuid4()),
            "correlation_id": correlation_id or str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "producer": producer or {},
            "subject": subject or {"type": "agent", "id": "unknown"},
            "rights": {
                "classification": "internal",
                "pii": False,
                "retention_days": 14,
                "shareable": True
            },
            "tags": tags or [],
            "payload": payload or {}
        }
        
        # Compute idempotency key
        envelope["idempotency_key"] = MeshEnvelopeBuilder._compute_idempotency_key(envelope)
        
        return envelope
    
    @staticmethod
    def _compute_idempotency_key(envelope: Dict) -> str:
        """Compute SHA-256 hash for idempotency"""
        content = {
            "type": envelope.get("event_type") or envelope.get("command_type"),
            "producer": envelope.get("producer"),
            "subject": envelope.get("subject"),
            "payload": envelope.get("payload"),
            "timestamp": envelope.get("timestamp")
        }
        normalized = json.dumps(content, sort_keys=True)
        return hashlib.sha256(normalized.encode()).hexdigest()


# ============================================================================
# Evidence Object Builder
# ============================================================================

class EvidenceBuilder:
    """Builds verifiable evidence objects"""
    
    @staticmethod
    def create_evidence(
        answer: str,
        structured_data: Optional[Dict] = None,
        support: Optional[List[Dict]] = None,
        workflow: str = "langchain-agent",
        tools_used: Optional[List[str]] = None,
        agent_id: str = "unknown",
        agent_version: str = "1.0.0",
        confidence: float = 0.85,
        latency_ms: int = 0,
        tokens_in: int = 0,
        tokens_out: int = 0,
        cost_usd: float = 0.0
    ) -> Dict:
        """Create an evidence object"""
        return {
            "claim": {
                "answer": answer,
                "structured": structured_data
            },
            "support": support or [],
            "method": {
                "workflow": workflow,
                "tools_used": tools_used or []
            },
            "uncertainty": {
                "self": 1.0 - confidence
            },
            "metrics": {
                "latency_ms": latency_ms,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "cost_usd": cost_usd
            },
            "rights": {
                "redistribute": True
            },
            "signature": {
                "agent_id": agent_id,
                "version": agent_version
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# ============================================================================
# Redis Streams Integration
# ============================================================================

class RedisStreamClient:
    """Redis Streams client for event-driven integration"""
    
    def __init__(self, config: QuestAgentConfig):
        self.config = config
        self.redis = redis.Redis(
            host=config.redis_host,
            port=config.redis_port,
            password=config.redis_password,
            decode_responses=True
        )
        self.consumer_id = f"{config.agent_id}-{uuid.uuid4().hex[:6]}"
        
    def ensure_consumer_group(self):
        """Ensure consumer group exists"""
        try:
            self.redis.xgroup_create(
                self.config.command_stream,
                self.config.consumer_group,
                id="$",
                mkstream=True
            )
            print(f"✅ Created consumer group: {self.config.consumer_group}")
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise
    
    def publish_event(self, envelope: Dict) -> str:
        """Publish event to mesh:events stream"""
        message_id = self.redis.xadd(
            self.config.event_stream,
            {"json": json.dumps(envelope)},
            maxlen=100000,
            approximate=True
        )
        return message_id
    
    def publish_command(self, envelope: Dict, stream: Optional[str] = None) -> str:
        """Publish command to stream"""
        target_stream = stream or self.config.command_stream
        message_id = self.redis.xadd(
            target_stream,
            {"json": json.dumps(envelope)},
            maxlen=100000,
            approximate=True
        )
        return message_id
    
    def read_commands(self, count: int = 10, block_ms: int = 5000) -> List[tuple]:
        """Read commands from stream using consumer group"""
        self.ensure_consumer_group()
        
        response = self.redis.xreadgroup(
            self.config.consumer_group,
            self.consumer_id,
            {self.config.command_stream: ">"},
            count=count,
            block=block_ms
        )
        
        messages = []
        if response:
            for stream_name, entries in response:
                for entry_id, fields in entries:
                    envelope = json.loads(fields["json"])
                    messages.append((entry_id, envelope))
        
        return messages
    
    def ack_message(self, message_id: str):
        """Acknowledge message"""
        self.redis.xack(self.config.command_stream, self.config.consumer_group, message_id)


# ============================================================================
# REST API Client
# ============================================================================

class RestAPIClient:
    """REST API client for synchronous integration"""
    
    def __init__(self, config: QuestAgentConfig):
        self.config = config
        self.base_url = config.api_url
        self.headers = {
            "Content-Type": "application/json"
        }
        if config.api_key:
            self.headers["Authorization"] = f"Bearer {config.api_key}"
    
    def register_agent(self, manifest: Dict) -> Dict:
        """Register agent with the system"""
        response = requests.post(
            f"{self.base_url}/api/agents",
            json=manifest,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def list_agents(self, intent: Optional[str] = None, capability: Optional[str] = None) -> List[Dict]:
        """List available agents"""
        params = {}
        if intent:
            params["intent"] = intent
        if capability:
            params["capability"] = capability
        
        response = requests.get(
            f"{self.base_url}/api/agents",
            params=params,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json().get("agents", [])
    
    def execute_agent(self, agent_name: str, capability: str, parameters: Dict, context: Optional[Dict] = None) -> Dict:
        """Execute an agent capability"""
        payload = {
            "agentName": agent_name,
            "capability": capability,
            "parameters": parameters,
            "context": context or {}
        }
        
        response = requests.post(
            f"{self.base_url}/api/agents/execute",
            json=payload,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def register_schema(self, name: str, version: str, schema: Dict, compatibility: str = "backward") -> str:
        """Register a JSON schema for validation"""
        payload = {
            "name": name,
            "version": version,
            "schema": schema,
            "compatibility": compatibility
        }
        
        response = requests.post(
            f"{self.base_url}/api/schemas/register",
            json=payload,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json().get("schema_uri")
    
    def validate_against_schema(self, schema_uri: str, payload: Dict) -> Dict:
        """Validate a payload against a registered schema"""
        data = {
            "schema_uri": schema_uri,
            "payload": payload
        }
        
        response = requests.post(
            f"{self.base_url}/api/schemas/validate",
            json=data,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_schema(self, schema_uri: str) -> Optional[Dict]:
        """Get a schema by URI"""
        response = requests.get(
            f"{self.base_url}/api/schemas/by-uri",
            params={"uri": schema_uri},
            headers=self.headers
        )
        response.raise_for_status()
        result = response.json()
        return result.get("schema", {}).get("schema_definition") if result.get("success") else None


# ============================================================================
# LangChain Agent Wrapper
# ============================================================================

class QuestLangChainAgent:
    """
    Main SDK class for integrating LangChain agents with Quest Agent Forge
    
    Usage:
        config = QuestAgentConfig(
            agent_name="My LangChain Agent",
            agent_version="1.0.0"
        )
        
        agent = QuestLangChainAgent(config)
        agent.register(capabilities=["analysis", "sql_query"])
        
        # Event-driven (recommended)
        agent.start_worker(handler=my_action_handler)
        
        # Or REST API
        result = agent.execute_capability("other-agent", "forecast", {...})
    """
    
    def __init__(self, config: QuestAgentConfig):
        self.config = config
        self.redis_client = RedisStreamClient(config)
        self.rest_client = RestAPIClient(config)
        self._running = False
    
    def register(
        self,
        capabilities: List[str],
        intents: Optional[List[str]] = None,
        description: Optional[str] = None,
        tools: Optional[List[str]] = None,
        input_schema: Optional[Dict] = None,
        output_schema: Optional[Dict] = None
    ) -> Dict:
        """Register this agent with the system"""
        manifest = {
            "name": self.config.agent_name,
            "version": self.config.agent_version,
            "description": description or f"LangChain agent: {self.config.agent_name}",
            "capabilities": capabilities,
            "intents": intents or [],
            "enabled": True,
            "manifest": {
                "agent_type": "langchain",
                "framework": "langchain",
                "tools": tools or [],
                "allow_delegation": False,
                "integration_type": "redis_streams"
            }
        }
        
        print(f"📝 Registering agent: {self.config.agent_name}")
        result = self.rest_client.register_agent(manifest)
        print(f"✅ Agent registered: {result}")
        
        # Register input/output schemas if provided
        if input_schema:
            schema_uri = self.register_input_schema(input_schema)
            print(f"📋 Registered input schema: {schema_uri}")
        
        if output_schema:
            schema_uri = self.register_output_schema(output_schema)
            print(f"📋 Registered output schema: {schema_uri}")
        
        return result
    
    def register_input_schema(self, schema: Dict) -> str:
        """Register input schema for this agent"""
        name = f"{self.config.agent_name.lower().replace(' ', '-')}-input"
        return self.rest_client.register_schema(
            name=name,
            version=self.config.agent_version,
            schema=schema,
            compatibility="backward"
        )
    
    def register_output_schema(self, schema: Dict) -> str:
        """Register output schema for this agent"""
        name = f"{self.config.agent_name.lower().replace(' ', '-')}-output"
        return self.rest_client.register_schema(
            name=name,
            version=self.config.agent_version,
            schema=schema,
            compatibility="forward"
        )
    
    def validate_input(self, action: Dict) -> bool:
        """Validate action inputs against registered schema"""
        schema_uri = f"https://schemas.acme.com/{self.config.agent_name.lower().replace(' ', '-')}-input/{self.config.agent_version}"
        try:
            result = self.rest_client.validate_against_schema(schema_uri, action.get("inputs", {}))
            return result.get("valid", False)
        except:
            # Schema not registered, skip validation
            return True
    
    def validate_output(self, evidence: Dict) -> bool:
        """Validate evidence output against registered schema"""
        schema_uri = f"https://schemas.acme.com/{self.config.agent_name.lower().replace(' ', '-')}-output/{self.config.agent_version}"
        try:
            result = self.rest_client.validate_against_schema(schema_uri, evidence)
            return result.get("valid", False)
        except:
            # Schema not registered, skip validation
            return True
    
    def start_worker(self, handler: Callable[[Dict], Dict]):
        """
        Start event-driven worker loop
        
        Args:
            handler: Function that handles actions and returns evidence
                     handler(action: Dict) -> Dict (evidence object)
        """
        print(f"🚀 Starting worker: {self.config.agent_name}")
        print(f"   Consumer: {self.redis_client.consumer_id}")
        print(f"   Stream: {self.config.command_stream}")
        print(f"   Group: {self.config.consumer_group}\n")
        
        self._running = True
        
        try:
            while self._running:
                messages = self.redis_client.read_commands()
                
                for message_id, envelope in messages:
                    try:
                        command_type = envelope.get("command_type")
                        print(f"\n📨 Received: {command_type} ({message_id})")
                        
                        if command_type in ["action.execution.requested", "action.execution.dispatched"]:
                            action = envelope["payload"].get("action", envelope["payload"])
                            
                            # Execute handler
                            start_time = time.time()
                            evidence = handler(action)
                            latency_ms = int((time.time() - start_time) * 1000)
                            
                            # Update latency if not set
                            if "metrics" in evidence and evidence["metrics"].get("latency_ms", 0) == 0:
                                evidence["metrics"]["latency_ms"] = latency_ms
                            
                            # Publish evidence event
                            self.publish_evidence(
                                action_id=action.get("id"),
                                status="succeeded",
                                evidence=evidence,
                                trace_id=envelope.get("trace_id"),
                                correlation_id=envelope.get("correlation_id")
                            )
                            
                            print(f"✅ Published evidence for action: {action.get('id')}")
                        
                        # Acknowledge
                        self.redis_client.ack_message(message_id)
                        
                    except Exception as e:
                        print(f"❌ Error processing message {message_id}: {e}")
                        # Publish error event
                        self.publish_error(
                            action_id=envelope.get("payload", {}).get("action", {}).get("id", "unknown"),
                            error=str(e),
                            trace_id=envelope.get("trace_id")
                        )
                        # Still acknowledge to prevent reprocessing
                        self.redis_client.ack_message(message_id)
        
        except KeyboardInterrupt:
            print("\n🛑 Worker stopped by user")
            self._running = False
    
    def stop_worker(self):
        """Stop the worker loop"""
        self._running = False
    
    def publish_evidence(
        self,
        action_id: str,
        status: str,
        evidence: Dict,
        trace_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ):
        """Publish agent evidence to mesh:events"""
        envelope = MeshEnvelopeBuilder.create_envelope(
            event_type="agent.evidence.produced",
            producer={
                "service": "langchain",
                "agent_id": self.config.agent_id,
                "agent_version": self.config.agent_version
            },
            subject={
                "type": "action",
                "id": action_id
            },
            payload={
                "action_id": action_id,
                "status": status,
                "evidence": evidence
            },
            trace_id=trace_id,
            correlation_id=correlation_id,
            tags=[f"agent:{self.config.agent_id}", f"status:{status}"]
        )
        
        self.redis_client.publish_event(envelope)
    
    def publish_error(
        self,
        action_id: str,
        error: str,
        trace_id: Optional[str] = None
    ):
        """Publish error event"""
        envelope = MeshEnvelopeBuilder.create_envelope(
            event_type="agent.error",
            producer={
                "service": "langchain",
                "agent_id": self.config.agent_id,
                "agent_version": self.config.agent_version
            },
            subject={
                "type": "action",
                "id": action_id
            },
            payload={
                "action_id": action_id,
                "error": error,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            trace_id=trace_id,
            tags=["error"]
        )
        
        self.redis_client.publish_event(envelope)
    
    def call_agent(self, agent_name: str, capability: str, parameters: Dict, context: Optional[Dict] = None) -> Dict:
        """
        Call another agent via REST API
        
        Args:
            agent_name: Name of the agent to call
            capability: Capability to execute
            parameters: Parameters for the capability
            context: Optional context
        
        Returns:
            Result from the agent
        """
        return self.rest_client.execute_agent(agent_name, capability, parameters, context)
    
    def discover_agents(self, intent: Optional[str] = None, capability: Optional[str] = None) -> List[Dict]:
        """
        Discover available agents
        
        Args:
            intent: Filter by intent
            capability: Filter by capability
        
        Returns:
            List of agent manifests
        """
        return self.rest_client.list_agents(intent=intent, capability=capability)


# ============================================================================
# Helper Functions
# ============================================================================

def create_sql_evidence(
    query: str,
    result_data: Any,
    row_count: int,
    execution_time_ms: int,
    agent_id: str,
    confidence: float = 0.95
) -> Dict:
    """Helper to create evidence for SQL query execution"""
    return EvidenceBuilder.create_evidence(
        answer=f"Query executed successfully. {row_count} rows returned.",
        structured_data=result_data if isinstance(result_data, dict) else {"rows": row_count},
        support=[{
            "type": "sql",
            "text": query,
            "hash": hashlib.sha256(query.encode()).hexdigest()
        }],
        workflow="langchain-sql-agent",
        tools_used=["database.query"],
        agent_id=agent_id,
        confidence=confidence,
        latency_ms=execution_time_ms
    )


def create_llm_evidence(
    answer: str,
    prompt: str,
    sources: List[str],
    agent_id: str,
    tokens_in: int = 0,
    tokens_out: int = 0,
    cost_usd: float = 0.0,
    confidence: float = 0.85
) -> Dict:
    """Helper to create evidence for LLM-based analysis"""
    return EvidenceBuilder.create_evidence(
        answer=answer,
        support=[
            {
                "type": "llm",
                "snippet": prompt[:200] + "..." if len(prompt) > 200 else prompt,
                "hash": hashlib.sha256(prompt.encode()).hexdigest()
            }
        ] + [{"type": "doc", "uri": src} for src in sources],
        workflow="langchain-llm-agent",
        tools_used=["llm.chat", "retrieval.vector_search"],
        agent_id=agent_id,
        confidence=confidence,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cost_usd=cost_usd
    )
