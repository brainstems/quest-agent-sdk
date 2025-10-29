# API Reference

Complete reference for Quest Agent SDK.

## Python SDK

### Core Classes

#### `QuestAgentConfig`

Configuration object for the SDK.

```python
from python.quest_agent_sdk import QuestAgentConfig

config = QuestAgentConfig(
    agent_id="optional-custom-id",      # Auto-generated if not provided
    agent_name="My Agent",              # Required
    agent_version="1.0.0",              # Recommended
    redis_host="localhost",             # Default: localhost
    redis_port=6379,                    # Default: 6379
    redis_password=None,                # Optional
    api_url="http://localhost:3000",   # Quest API URL
    api_key=None,                       # Optional
    command_stream="mesh:commands",     # Redis stream for commands
    event_stream="mesh:events",         # Redis stream for events
    consumer_group="langchain-agents"   # Redis consumer group
)
```

---

#### `QuestLangChainAgent`

Main SDK class for integrating agents.

##### Constructor

```python
from python.quest_agent_sdk import QuestLangChainAgent

agent = QuestLangChainAgent(config: QuestAgentConfig)
```

##### Methods

**`register()`**

Register agent with Quest system.

```python
agent.register(
    capabilities: List[str],            # Required: agent capabilities
    intents: List[str] = None,         # Optional: user intents
    description: str = None,            # Optional: description
    tools: List[str] = None,           # Optional: tool names
    input_schema: Dict = None,          # Optional: JSON Schema for inputs
    output_schema: Dict = None          # Optional: JSON Schema for outputs
) -> Dict
```

Returns: Registration result with agent ID

**`start_worker()`**

Start event-driven worker loop.

```python
agent.start_worker(
    handler: Callable[[Dict], Dict]     # Required: action handler function
) -> None
```

Handler signature: `def handler(action: Dict) -> Dict (evidence object)`

**`stop_worker()`**

Stop the worker loop.

```python
agent.stop_worker() -> None
```

**`call_agent()`**

Call another agent via REST API.

```python
agent.call_agent(
    agent_name: str,                    # Required: agent name
    capability: str,                    # Required: capability to invoke
    parameters: Dict,                   # Required: parameters
    context: Dict = None                # Optional: execution context
) -> Dict
```

Returns: Agent execution result

**`discover_agents()`**

Discover available agents.

```python
agent.discover_agents(
    intent: str = None,                 # Optional: filter by intent
    capability: str = None              # Optional: filter by capability
) -> List[Dict]
```

Returns: List of agent manifests

**`validate_input()`**

Validate action inputs against registered schema.

```python
agent.validate_input(action: Dict) -> bool
```

**`validate_output()`**

Validate evidence against registered output schema.

```python
agent.validate_output(evidence: Dict) -> bool
```

**`register_input_schema()`**

Register input schema for this agent.

```python
agent.register_input_schema(schema: Dict) -> str
```

Returns: Schema URI

**`register_output_schema()`**

Register output schema for this agent.

```python
agent.register_output_schema(schema: Dict) -> str
```

Returns: Schema URI

---

#### `EvidenceBuilder`

Helper class to create verifiable evidence objects.

```python
from python.quest_agent_sdk import EvidenceBuilder

evidence = EvidenceBuilder.create_evidence(
    answer: str,                        # Required: human-readable answer
    structured_data: Dict = None,       # Optional: structured result
    support: List[Dict] = None,         # Optional: supporting evidence
    workflow: str = "langchain-agent",  # Workflow identifier
    tools_used: List[str] = None,       # Tools used
    agent_id: str = "unknown",          # Agent identifier
    agent_version: str = "1.0.0",       # Agent version
    confidence: float = 0.85,           # Confidence score (0-1)
    latency_ms: int = 0,                # Execution time
    tokens_in: int = 0,                 # LLM input tokens
    tokens_out: int = 0,                # LLM output tokens
    cost_usd: float = 0.0               # Execution cost
) -> Dict
```

Returns: Evidence object

**Helper Functions:**

```python
# SQL evidence
create_sql_evidence(
    query: str,
    result_data: Any,
    row_count: int,
    execution_time_ms: int,
    agent_id: str,
    confidence: float = 0.95
) -> Dict

# LLM evidence
create_llm_evidence(
    answer: str,
    prompt: str,
    sources: List[str],
    agent_id: str,
    tokens_in: int = 0,
    tokens_out: int = 0,
    cost_usd: float = 0.0,
    confidence: float = 0.85
) -> Dict
```

---

### Advanced Features

#### `OntologyClient`

Access Quest's semantic ontology.

```python
from python.ontology_integration import OntologyClient

ontology = OntologyClient(api_url: str = "http://localhost:3000")
```

**Methods:**

```python
# Resolve term to canonical URI
ontology.resolve(term: str) -> Optional[str]

# Expand concepts using SKOS relations
ontology.expand(
    concepts: List[str],
    relations: List[str] = None,       # ['broader', 'narrower', 'related']
    depth: int = 1
) -> List[str]

# Get external ID for entity
ontology.same_as(entity_uri: str, system: str) -> Optional[str]

# Get business constraints
ontology.get_constraints(concept_uri: str) -> List[Dict]

# Get SHACL shape
ontology.get_shape(shape_uri: str) -> Optional[Dict]

# Validate against SHACL shape
ontology.validate_shacl(
    data: Dict,
    shape_uri: str,
    category_uri: Optional[str] = None
) -> Dict
```

---

#### `AgentDiscoveryClient`

Discover and coordinate with other agents.

```python
from python.ontology_integration import AgentDiscoveryClient

discovery = AgentDiscoveryClient(api_url: str = "http://localhost:3000")
```

**Methods:**

```python
# Discover by capability
discovery.discover_by_capability(capability: str) -> List[Dict]

# Discover by ontology concepts
discovery.discover_by_concepts(
    concepts: List[str],
    ontology: OntologyClient = None
) -> List[Dict]

# Semantic search
discovery.discover_by_semantic_search(
    query: str,
    limit: int = 10
) -> List[Dict]

# Bid for task
discovery.bid_for_task(
    task: Dict,
    my_capabilities: List[str],
    my_confidence: float
) -> Dict
```

---

#### `TemplateIntegration`

Integrate with ACT-R templates.

```python
from python.ontology_integration import TemplateIntegration

templates = TemplateIntegration(api_url: str = "http://localhost:3000")
```

**Methods:**

```python
# Get templates for intent
templates.get_templates_for_intent(intent: str) -> List[Dict]

# Execute template
templates.execute_template(
    template_id: str,
    context: Dict,
    user_id: str
) -> Dict

# Register for templates
templates.register_agent_for_template(
    agent_name: str,
    template_ids: List[str],
    capabilities: List[str]
) -> Dict
```

---

## TypeScript/JavaScript Client

### QuestAgentClient

```typescript
import { QuestAgentClient } from './quest-agent-client';

const client = new QuestAgentClient({
    apiUrl?: string;
    apiKey?: string;
    redisUrl?: string;
    timeout?: number;
});
```

**Methods:**

```typescript
// List agents
listAgents(filters?: {
    intent?: string;
    capability?: string;
    limit?: number;
}): Promise<AgentManifest[]>

// Semantic search
searchAgents(query: string, limit?: number): Promise<AgentManifest[]>

// Execute agent
executeAgent(params: {
    agentName: string;
    capability: string;
    parameters: Record<string, any>;
    context?: Record<string, any>;
}): Promise<AgentExecuteResult>

// Register agent
registerAgent(manifest: AgentManifest): Promise<AgentManifest>

// Publish command (Redis Streams)
publishCommand(
    commandType: string,
    payload: Record<string, any>,
    options?: {
        stream?: string;
        traceId?: string;
        correlationId?: string;
    }
): Promise<string>

// Subscribe to events
subscribeToEvents(
    callback: (event: MeshEnvelope) => void | Promise<void>,
    options?: {
        stream?: string;
        group?: string;
        consumer?: string;
    }
): Promise<() => void>

// Close connections
close(): Promise<void>
```

**Convenience Functions:**

```typescript
// Quick execute
import { executeAgent } from './quest-agent-client';

const result = await executeAgent(agentName, capability, parameters);

// Quick discover
import { discoverAgents } from './quest-agent-client';

const agents = await discoverAgents(capability);
```

---

## Data Structures

### Action Object

Structure of action your handler receives:

```python
{
    "id": "action_123",                 # Unique action ID
    "type": "pricing_optimization",     # Action type
    "inputs": {                          # Input parameters
        "product_id": "prod_456",
        "current_price": 99.99
    },
    "priority": "high",                  # Optional: low/medium/high
    "metadata": {...}                    # Optional: additional context
}
```

### Evidence Object

Structure of evidence your handler returns:

```python
{
    "claim": {
        "answer": "Price optimized to $89.99",
        "structured": {
            "recommended_price": 89.99,
            "margin": 0.25
        }
    },
    "support": [                         # Supporting evidence
        {
            "type": "calculation",
            "text": "Elasticity model v2.0"
        }
    ],
    "method": {
        "workflow": "pricing-optimizer",
        "tools_used": ["elasticity_model"]
    },
    "uncertainty": {
        "self": 0.05                     # 1 - confidence
    },
    "metrics": {
        "latency_ms": 250,
        "tokens_in": 0,
        "tokens_out": 0,
        "cost_usd": 0.0
    },
    "rights": {
        "redistribute": True
    },
    "signature": {
        "agent_id": "my-agent-123",
        "version": "1.0.0"
    },
    "timestamp": "2025-10-29T12:00:00Z"
}
```

### MeshEnvelope (CloudEvents)

Structure of messages on Redis Streams:

```python
{
    "envelope_version": "1.0",
    "event_type": "agent.evidence.produced",    # or command_type
    "trace_id": "uuid",                         # Distributed tracing
    "span_id": "uuid",
    "correlation_id": "uuid",
    "timestamp": "2025-10-29T12:00:00Z",
    "producer": {
        "service": "langchain",
        "agent_id": "my-agent-123",
        "agent_version": "1.0.0"
    },
    "subject": {
        "type": "action",
        "id": "action_123"
    },
    "rights": {
        "classification": "internal",
        "pii": False,
        "retention_days": 14,
        "shareable": True
    },
    "idempotency_key": "sha256_hash",
    "tags": ["agent:my-agent", "status:succeeded"],
    "payload": {                                # Actual data
        "action_id": "action_123",
        "status": "succeeded",
        "evidence": {...}
    }
}
```

---

## Error Handling

### Python

```python
try:
    agent.register(capabilities=["test"])
    agent.start_worker(handler)
except Exception as e:
    print(f"Error: {e}")
```

### Handler Errors

```python
def handler(action):
    try:
        result = my_logic(action)
        return create_evidence(result)
    except Exception as e:
        # Always return evidence, even on error
        return EvidenceBuilder.create_evidence(
            answer=f"Error: {str(e)}",
            structured_data={"error": str(e)},
            agent_id=config.agent_id,
            confidence=0.0
        )
```

---

## Environment Variables

```bash
# Required
OPENAI_API_KEY=your-key              # If using LangChain

# Optional
API_URL=http://localhost:3000        # Quest API URL
REDIS_HOST=localhost                 # Redis host
REDIS_PORT=6379                      # Redis port
REDIS_PASSWORD=                      # Redis password
API_KEY=                             # Quest API key
AGENT_NAME=My Agent                  # Agent name
AGENT_VERSION=1.0.0                  # Agent version
```

---

## HTTP API Endpoints

### Quest Agent Forge REST API

```bash
# List agents
GET /api/agents?capability=pricing

# Semantic search
GET /api/agents?q=optimize+pricing&limit=10

# Execute agent
POST /api/agents/execute
{
  "agentName": "My Agent",
  "capability": "pricing",
  "parameters": {...}
}

# Register agent
POST /api/agents
{
  "name": "My Agent",
  "capabilities": ["pricing"],
  ...
}

# Ontology operations
GET /api/ontology/resolve/:term
POST /api/ontology/expand
GET /api/ontology/constraints/:conceptUri
POST /api/ontology/validate-shacl

# Schema operations
POST /api/schemas/register
POST /api/schemas/validate
GET /api/schemas/by-uri?uri=...
```

---

## Redis Streams

### Stream Names

- `mesh:commands` - Commands for agents
- `mesh:events` - Events from agents
- `mesh:telemetry` - Metrics and monitoring
- `mesh:dlq` - Dead letter queue

### Consumer Groups

- `langchain-agents` - External agents
- `crew-agents:analytics` - Internal analytics agents

---

## Examples

See [../examples/](../examples/) directory for complete working examples.

---

**Need help? Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)**
