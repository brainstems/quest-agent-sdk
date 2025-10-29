# Python SDK

Core Python modules for integrating with Quest Agent Forge.

## Files

### `quest_agent_sdk.py`

**Core SDK module** - Everything you need for basic integration.

**Includes:**
- `QuestAgentConfig` - Configuration class
- `QuestLangChainAgent` - Main agent wrapper
- `MeshEnvelopeBuilder` - CloudEvents envelope builder
- `EvidenceBuilder` - Evidence object builder
- `RedisStreamClient` - Redis Streams integration
- `RestAPIClient` - REST API client

**Basic Usage:**

```python
from python.quest_agent_sdk import QuestAgentConfig, QuestLangChainAgent, EvidenceBuilder

config = QuestAgentConfig(agent_name="My Agent")
agent = QuestLangChainAgent(config)

def handler(action):
    result = my_algorithm(action["inputs"])
    return EvidenceBuilder.create_evidence(
        answer="Done",
        structured_data=result,
        agent_id=config.agent_id,
        confidence=0.95
    )

agent.register(capabilities=["my_capability"])
agent.start_worker(handler=handler)
```

---

### `ontology_integration.py`

**Advanced features module** - Ontology, discovery, templates.

**Includes:**
- `OntologyClient` - SKOS ontology operations
- `KnowledgeGraphClient` - Entity navigation
- `AgentDiscoveryClient` - Agent discovery and bidding
- `TemplateIntegration` - ACT-R template integration

**Advanced Usage:**

```python
from python.ontology_integration import OntologyClient, AgentDiscoveryClient

ontology = OntologyClient()
discovery = AgentDiscoveryClient()

def handler(action):
    # Semantic enrichment
    concept_uri = ontology.resolve("pricing")
    expanded = ontology.expand([concept_uri])
    
    # Get business constraints
    constraints = ontology.get_constraints("cat:Beverages")
    
    # Discover helper agents
    helpers = discovery.discover_by_capability("inventory")
    
    # Your logic with enriched context
    result = my_algorithm(action, constraints, helpers)
    
    # Validate output
    validation = ontology.validate_shacl(result, "shape:PriceEvent")
    
    return create_evidence(result)
```

---

## Installation

```bash
# Install from external-agent-sdk directory
cd ..
pip install -r requirements.txt
```

---

## Quick Reference

### Import Patterns

```python
# Basic integration
from python.quest_agent_sdk import (
    QuestAgentConfig,
    QuestLangChainAgent,
    EvidenceBuilder
)

# Advanced features
from python.ontology_integration import (
    OntologyClient,
    AgentDiscoveryClient,
    TemplateIntegration
)

# Helper functions
from python.quest_agent_sdk import (
    create_sql_evidence,
    create_llm_evidence
)
```

---

## Documentation

- **Getting Started:** See [../docs/GETTING_STARTED.md](../docs/GETTING_STARTED.md)
- **API Reference:** See [../docs/API_REFERENCE.md](../docs/API_REFERENCE.md)
- **Advanced Features:** See [../docs/ADVANCED_FEATURES.md](../docs/ADVANCED_FEATURES.md)

---

## Examples

See [../examples/](../examples/) for complete working examples:
- `simple_sql_agent.py` - LangChain SQL agent
- `rag_analysis_agent.py` - RAG Q&A agent
- `algorithm_executor_agent.py` - Hard-coded algorithms
- `advanced_integration_example.py` - Ontology + discovery

---

**These modules provide everything you need to integrate your agents with Quest Agent Forge!**
