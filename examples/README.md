# Examples

Complete working examples showing different integration patterns.

## Quick Start

```bash
# Install dependencies
cd ..
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-key"
export API_URL="http://localhost:3000"

# Run an example
python examples/algorithm_executor_agent.py
```

---

## Examples

### 1. `algorithm_executor_agent.py` ⭐ **Start Here**

**Best for:** Wrapping hard-coded algorithms

**What it shows:**
- Wrapping existing business logic
- Pricing optimization algorithm
- Inventory optimization algorithm
- No LangChain required
- Structured evidence objects

**Run:**
```bash
python algorithm_executor_agent.py
```

**Use when:** You have existing algorithms (pricing, forecasting, inventory) and want to make them accessible via Quest.

---

### 2. `simple_sql_agent.py`

**Best for:** LangChain SQL analysis

**What it shows:**
- LangChain integration
- Natural language to SQL
- Database query execution
- SQL evidence with citations

**Run:**
```bash
python simple_sql_agent.py
```

**Use when:** You want to build a SQL agent that converts natural language to database queries.

---

### 3. `rag_analysis_agent.py`

**Best for:** Document Q&A with RAG

**What it shows:**
- LangChain RAG pattern
- Vector search over documents
- Document retrieval
- Answer generation with sources

**Setup:**
```bash
export DOCUMENTS_PATH="./your/documents"
python rag_analysis_agent.py
```

**Use when:** You want to build a Q&A agent over your documents.

---

### 4. `schema_registration_example.py`

**Best for:** Input/output validation

**What it shows:**
- JSON Schema definition
- Automatic input validation
- Automatic output validation
- Schema versioning
- Error handling

**Run:**
```bash
python schema_registration_example.py
```

**Use when:** You want to validate inputs/outputs and enforce data contracts.

---

### 5. `advanced_integration_example.py`

**Best for:** Production-grade integration

**What it shows:**
- Ontology enrichment
- Business constraint enforcement
- SHACL validation
- Agent discovery
- Agent coordination
- Bidding for tasks
- Template integration

**Run:**
```bash
python advanced_integration_example.py
```

**Use when:** You want full semantic interoperability with Quest's ontology and other agents.

---

### 6. `rest_api_example.py`

**Best for:** REST API patterns

**What it shows:**
- Synchronous agent calls
- Agent discovery via REST
- Agent-to-agent communication
- HTTP integration patterns

**Run:**
```bash
python rest_api_example.py
```

**Use when:** You prefer REST API over Redis Streams, or need to call Quest agents from your code.

---

## Comparison

| Example | Complexity | LangChain | Ontology | Best For |
|---------|-----------|-----------|----------|----------|
| algorithm_executor | Low | No | No | Hard-coded algorithms |
| simple_sql | Medium | Yes | No | SQL queries |
| rag_analysis | Medium | Yes | No | Document Q&A |
| schema_registration | Low | No | No | Validation |
| advanced_integration | High | No | Yes | Production systems |
| rest_api | Low | No | No | HTTP integration |

---

## Common Patterns

### Pattern: Basic Agent

```python
from python.quest_agent_sdk import QuestAgentConfig, QuestLangChainAgent, EvidenceBuilder

config = QuestAgentConfig(agent_name="My Agent")
agent = QuestLangChainAgent(config)

def handler(action):
    result = my_logic(action["inputs"])
    return EvidenceBuilder.create_evidence(
        answer="Done",
        structured_data=result,
        agent_id=config.agent_id,
        confidence=0.95
    )

agent.register(capabilities=["my_capability"])
agent.start_worker(handler)
```

### Pattern: With Schema Validation

```python
INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "price": {"type": "number", "minimum": 0}
    },
    "required": ["price"]
}

agent.register(
    capabilities=["pricing"],
    input_schema=INPUT_SCHEMA  # ← Automatic validation
)
```

### Pattern: With Ontology

```python
from python.ontology_integration import OntologyClient

ontology = OntologyClient()

def handler(action):
    # Enrich with ontology
    concept_uri = ontology.resolve("pricing")
    constraints = ontology.get_constraints("cat:Beverages")
    
    # Your logic with constraints
    result = optimize_price(action["inputs"], constraints)
    
    # Validate output
    validation = ontology.validate_shacl(result, "shape:PriceEvent")
    
    return create_evidence(result)
```

### Pattern: Multi-Agent Coordination

```python
from python.ontology_integration import AgentDiscoveryClient

discovery = AgentDiscoveryClient()

def handler(action):
    # Find helper agents
    inv_agents = discovery.discover_by_capability("inventory")
    forecast_agents = discovery.discover_by_capability("forecasting")
    
    # Call them
    inventory = agent.call_agent(inv_agents[0]["name"], ...)
    forecast = agent.call_agent(forecast_agents[0]["name"], ...)
    
    # Use results
    result = optimize(inventory, forecast)
    return create_evidence(result)
```

---

## Testing Examples

Each example can be tested independently:

```bash
# Test with curl (after agent is running)
curl -X POST http://localhost:3000/api/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agentName": "Algorithm Executor Agent",
    "capability": "pricing_optimization",
    "parameters": {
      "current_price": 100,
      "cost": 60,
      "demand_elasticity": -1.5,
      "target_margin": 0.25
    }
  }'
```

---

## Modifying Examples

All examples are designed to be copied and modified:

1. Copy an example file
2. Rename it to your use case
3. Modify the handler function
4. Update capabilities and schemas
5. Run your agent!

---

## Documentation

- **Getting Started:** [../docs/GETTING_STARTED.md](../docs/GETTING_STARTED.md)
- **API Reference:** [../docs/API_REFERENCE.md](../docs/API_REFERENCE.md)
- **Advanced Features:** [../docs/ADVANCED_FEATURES.md](../docs/ADVANCED_FEATURES.md)

---

**Start with `algorithm_executor_agent.py` to wrap your existing algorithms!** ⭐
