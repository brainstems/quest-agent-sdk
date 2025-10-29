# Getting Started with Quest Agent SDK

**Complete beginner's guide to integrating your LangChain agents or hard-coded algorithms with Quest Agent Forge.**

## Prerequisites

- Python 3.11+
- Redis (for event-driven integration)
- Quest Agent Forge running (http://localhost:3000)
- OpenAI API key (if using LangChain)

## Installation

### 1. Clone or Download SDK

```bash
# If you have the full repository
cd quest-agent-forge/external-agent-sdk

# Or download just the SDK
# (extract to your working directory)
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables

```bash
cp docker/.env.example .env

# Edit .env file
export OPENAI_API_KEY="your-key-here"
export API_URL="http://localhost:3000"
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
```

## Your First Agent (5 Minutes)

### Step 1: Create Your Agent File

Create `my_first_agent.py`:

```python
from python.quest_agent_sdk import (
    QuestAgentConfig,
    QuestLangChainAgent,
    EvidenceBuilder
)

# Configure your agent
config = QuestAgentConfig(
    agent_name="My First Agent",
    agent_version="1.0.0",
    redis_host="localhost",
    redis_port=6379,
    api_url="http://localhost:3000"
)

# Create agent instance
agent = QuestLangChainAgent(config)

# Define your algorithm/logic
def my_handler(action):
    """
    This function processes incoming actions.
    Replace this with your actual business logic!
    """
    action_id = action.get("id")
    inputs = action.get("inputs", {})
    
    print(f"Processing action: {action_id}")
    print(f"Inputs: {inputs}")
    
    # YOUR LOGIC HERE - Example: simple calculation
    result = {
        "answer": "Hello from my first agent!",
        "processed": True,
        "input_count": len(inputs)
    }
    
    # Return evidence object
    return EvidenceBuilder.create_evidence(
        answer="Successfully processed action",
        structured_data=result,
        agent_id=config.agent_id,
        confidence=0.95,
        workflow="my-first-agent"
    )

# Register agent capabilities
agent.register(
    capabilities=["test_capability"],
    description="My first Quest agent"
)

print("\n🚀 Agent registered and ready!")
print("Listening for actions on Redis Streams...")

# Start event-driven worker
agent.start_worker(handler=my_handler)
```

### Step 2: Run Your Agent

```bash
python my_first_agent.py
```

You should see:
```
🚀 Agent registered and ready!
Listening for actions on Redis Streams...
```

### Step 3: Test Your Agent

#### Option A: Via REST API

```bash
curl -X POST http://localhost:3000/api/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agentName": "My First Agent",
    "capability": "test_capability",
    "parameters": {
      "test": "hello"
    }
  }'
```

#### Option B: Via Redis Streams (Advanced)

```bash
# Publish test command
redis-cli XADD mesh:commands "*" json '{"command_type":"action.execution.requested","payload":{"action":{"id":"test_123","type":"test","inputs":{"test":"hello"}}}}'
```

### Step 4: Verify Results

Check your agent's console output. You should see:
```
Processing action: test_123
Inputs: {'test': 'hello'}
✅ Published evidence for action: test_123
```

## Next Steps

### Learn by Example

Run the provided examples to see different patterns:

```bash
# 1. Hard-coded algorithm agent
python examples/algorithm_executor_agent.py

# 2. LangChain SQL agent
python examples/simple_sql_agent.py

# 3. RAG document Q&A agent
python examples/rag_analysis_agent.py

# 4. Schema validation
python examples/schema_registration_example.py

# 5. Advanced features (ontology, discovery)
python examples/advanced_integration_example.py
```

### Add Schema Validation

Improve your agent with input validation:

```python
# Define input schema
INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "message": {"type": "string", "minLength": 1}
    },
    "required": ["message"]
}

# Register with schema
agent.register(
    capabilities=["test_capability"],
    input_schema=INPUT_SCHEMA  # ← Automatic validation
)

# Now all requests are validated before reaching your handler!
```

See [SCHEMA_GUIDE.md](SCHEMA_GUIDE.md) for details.

### Use Advanced Features

Level up with ontology and agent discovery:

```python
from python.ontology_integration import OntologyClient, AgentDiscoveryClient

ontology = OntologyClient()
discovery = AgentDiscoveryClient()

def advanced_handler(action):
    # 1. Enrich with ontology
    concept_uri = ontology.resolve("pricing")
    
    # 2. Get business constraints
    constraints = ontology.get_constraints("cat:Beverages")
    
    # 3. Discover and call other agents
    helpers = discovery.discover_by_capability("inventory_management")
    if helpers:
        inventory_data = agent.call_agent(helpers[0]["name"], ...)
    
    # Your logic with enriched context
    result = my_algorithm(action["inputs"], constraints, inventory_data)
    
    # 4. Validate output
    validation = ontology.validate_shacl(result, "shape:PriceEvent")
    
    return create_evidence(result)
```

See [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md) for details.

## Common Patterns

### Pattern 1: Wrapping Existing Algorithms

```python
# You have existing code
def calculate_reorder_point(daily_demand, lead_time):
    return daily_demand * lead_time * 1.5

# Wrap it with Quest SDK
def handler(action):
    inputs = action["inputs"]
    result = calculate_reorder_point(
        inputs["daily_demand"],
        inputs["lead_time"]
    )
    
    return EvidenceBuilder.create_evidence(
        answer=f"Reorder point: {result}",
        structured_data={"reorder_point": result},
        agent_id=config.agent_id,
        confidence=0.98
    )
```

### Pattern 2: LangChain Integration

```python
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

llm = ChatOpenAI(model="gpt-4")

def handler(action):
    query = action["inputs"]["query"]
    
    # Use LangChain
    result = llm.invoke(query)
    
    return create_llm_evidence(
        answer=result.content,
        prompt=query,
        agent_id=config.agent_id
    )
```

### Pattern 3: Coordinating Multiple Agents

```python
def handler(action):
    discovery = AgentDiscoveryClient()
    
    # Find helpers
    inv_agents = discovery.discover_by_capability("inventory")
    forecast_agents = discovery.discover_by_capability("forecasting")
    
    # Call them
    inventory = agent.call_agent(inv_agents[0]["name"], ...)
    forecast = agent.call_agent(forecast_agents[0]["name"], ...)
    
    # Use both results
    result = optimize(inventory, forecast)
    return create_evidence(result)
```

## Troubleshooting

### Agent Not Receiving Actions

**Check Redis connection:**
```bash
redis-cli ping  # Should return PONG
```

**Check agent registration:**
```bash
curl http://localhost:3000/api/agents
# Should include your agent
```

**Check Redis consumer group:**
```bash
redis-cli XINFO GROUPS mesh:commands
# Should show langchain-agents group
```

### Actions Failing

**Check logs in your agent console**

**Enable debug mode:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Validate your handler always returns evidence:**
```python
def handler(action):
    try:
        result = my_logic(action)
        return create_evidence(result)
    except Exception as e:
        # Always return evidence, even on error
        return create_evidence(
            answer=f"Error: {e}",
            confidence=0.0
        )
```

## Getting Help

- **Documentation:** See [docs/](../) directory
- **Examples:** Check [examples/](../examples/) directory
- **API Reference:** See [API_REFERENCE.md](API_REFERENCE.md)
- **Issues:** GitHub Issues

## What's Next?

1. ✅ You have a working agent
2. → Add [schema validation](SCHEMA_GUIDE.md)
3. → Explore [advanced features](ADVANCED_FEATURES.md)
4. → Deploy with [Docker](../docker/)
5. → Read [API reference](API_REFERENCE.md)

---

**Congratulations! You've built your first Quest agent.** 🎉

Continue to [Schema Validation Guide](SCHEMA_GUIDE.md) →
