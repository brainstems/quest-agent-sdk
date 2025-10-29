# Quest Agent SDK

**Production-ready SDK for integrating external LangChain agents and hard-coded algorithms with Quest Agent Forge.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)

## 🎯 What is This?

This SDK enables external developers to integrate their **LangChain agents** or **hard-coded algorithms** with Quest Agent Forge's intelligence mesh. Your agents can:

- ✅ Be discovered and invoked by Quest's semantic router
- ✅ Call other Quest agents for coordination
- ✅ Use Quest's ontology for semantic understanding
- ✅ Validate inputs/outputs with JSON Schema + SHACL
- ✅ Participate in ACT-R template workflows
- ✅ Bid for tasks in the agent marketplace

## 🚀 Quick Start (5 Minutes)

### 1. Install

```bash
cd external-agent-sdk
pip install -r requirements.txt
```

### 2. Create Your Agent

```python
from python.quest_agent_sdk import QuestAgentConfig, QuestLangChainAgent, EvidenceBuilder

# Configure
config = QuestAgentConfig(
    agent_name="My Pricing Agent",
    api_url="http://localhost:3000"
)

# Create agent
agent = QuestLangChainAgent(config)

# Register
agent.register(capabilities=["pricing_optimization"])

# Handle actions
def my_algorithm(action):
    # Your logic here
    result = {"recommended_price": 99.99}
    return EvidenceBuilder.create_evidence(
        answer="Price optimized",
        structured_data=result,
        agent_id=config.agent_id,
        confidence=0.95
    )

# Start worker
agent.start_worker(handler=my_algorithm)
```

### 3. Run

```bash
python examples/algorithm_executor_agent.py
```

## 📁 Directory Structure

```
external-agent-sdk/
├── README.md                    ← You are here
├── python/                      ← Python SDK
│   ├── quest_agent_sdk.py      ← Core SDK
│   └── ontology_integration.py ← Advanced features
├── typescript/                  ← TypeScript/JavaScript client
│   ├── quest-agent-client.ts   ← Client library
│   └── example-usage.ts        ← Usage examples
├── examples/                    ← Complete working examples
│   ├── simple_sql_agent.py     ← LangChain SQL agent
│   ├── rag_analysis_agent.py   ← RAG document Q&A
│   ├── algorithm_executor_agent.py ← Hard-coded algorithms ⭐
│   ├── schema_registration_example.py ← Schema validation
│   ├── advanced_integration_example.py ← Ontology + Discovery
│   └── rest_api_example.py     ← REST API patterns
├── docs/                        ← Documentation
│   ├── GETTING_STARTED.md      ← Start here
│   ├── SCHEMA_GUIDE.md         ← Schema registration
│   ├── ADVANCED_FEATURES.md    ← Ontology, discovery, templates
│   └── API_REFERENCE.md        ← Complete API docs
├── docker/                      ← Docker support
│   ├── docker-compose.yml      ← Multi-agent deployment
│   ├── Dockerfile.agent        ← Agent container
│   └── .env.example            ← Environment template
└── tests/                       ← Test suite
    └── test_sdk.py             ← SDK tests
```

## 📚 Documentation

### For Beginners
1. **[Getting Started Guide](docs/GETTING_STARTED.md)** - Step-by-step tutorial
2. **[Examples Directory](examples/)** - 6 complete working examples

### For Advanced Users
3. **[Schema Registration Guide](docs/SCHEMA_GUIDE.md)** - Input/output validation
4. **[Advanced Features Guide](docs/ADVANCED_FEATURES.md)** - Ontology, discovery, templates
5. **[API Reference](docs/API_REFERENCE.md)** - Complete API documentation

### For Operations
6. **[Docker Deployment](docker/)** - Containerized deployment
7. **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## 🎓 Integration Patterns

### Pattern 1: Redis Streams (Event-Driven) ⭐ Recommended

**Best for:** Production systems, high throughput, scalability

```python
agent = QuestLangChainAgent(config)
agent.register(capabilities=["pricing_optimization"])
agent.start_worker(handler=my_handler)  # Event loop
```

**How it works:**
- Your agent listens on `mesh:commands` Redis stream
- Quest publishes commands when your agent is needed
- Your agent processes and publishes results to `mesh:events`
- Fully async, scalable, production-ready

### Pattern 2: REST API (Request-Response)

**Best for:** Simple integrations, synchronous operations, prototypes

```python
agent = QuestLangChainAgent(config)
result = agent.call_agent("Other Agent", "capability", {...})
```

**How it works:**
- Your agent makes HTTP requests to Quest's API
- Synchronous request-response pattern
- Good for calling Quest agents from your code

### Pattern 3: Hybrid (Both)

**Best for:** Complex orchestration, enterprise deployments

Use Redis Streams for receiving work + REST API for calling other agents.

## 🎯 Use Cases

### Hard-Coded Algorithms
Perfect for wrapping existing business logic:
- **Pricing optimization** - Elasticity models, competitive pricing
- **Inventory management** - Reorder point calculation, safety stock
- **Forecasting** - Demand prediction, trend analysis
- **Budget allocation** - Portfolio optimization, constraint solving

**Example:** [algorithm_executor_agent.py](examples/algorithm_executor_agent.py)

### LangChain Agents
Integrate LangChain-based agents:
- **SQL analysis** - Natural language to SQL
- **RAG Q&A** - Document retrieval and answering
- **Data extraction** - Structured data from unstructured text
- **Report generation** - Automated insights

**Example:** [simple_sql_agent.py](examples/simple_sql_agent.py), [rag_analysis_agent.py](examples/rag_analysis_agent.py)

## 🔑 Key Features

### Core Features
- ✅ **Redis Streams Integration** - Event-driven, scalable
- ✅ **REST API Client** - Simple request-response
- ✅ **CloudEvents 1.0** - Industry-standard messaging
- ✅ **Evidence Objects** - Verifiable, traceable outputs
- ✅ **Distributed Tracing** - Full observability

### Advanced Features
- ✅ **JSON Schema Validation** - Input/output validation
- ✅ **SHACL Validation** - Semantic constraints
- ✅ **Ontology Integration** - Semantic understanding (31 concepts)
- ✅ **Agent Discovery** - Find and coordinate with other agents
- ✅ **Agent Bidding** - Marketplace pattern for task allocation
- ✅ **Template Integration** - ACT-R workflow orchestration
- ✅ **Knowledge Graph** - Entity and relationship navigation

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Your External Agent                         │
│  ┌────────────────────────────────────────────────┐     │
│  │  Hard-coded Algorithm or LangChain Agent       │     │
│  └─────────────────┬──────────────────────────────┘     │
│                    │                                     │
│         ┌──────────▼──────────┐                         │
│         │  Quest Agent SDK    │                         │
│         └──────────┬──────────┘                         │
└────────────────────┼──────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   Redis Streams  REST API   Ontology API
        │            │            │
        └────────────┼────────────┘
                     ▼
┌─────────────────────────────────────────────────────────┐
│            Quest Agent Forge System                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Semantic │  │   ACT-R  │  │ Internal │              │
│  │  Router  │  │Templates │  │  Agents  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
```

## 🚦 Getting Help

### Issues & Questions
- **GitHub Issues:** [Report bugs or request features](https://github.com/your-org/quest-agent-forge/issues)
- **Documentation:** Check [docs/](docs/) directory
- **Examples:** Run examples in [examples/](examples/) directory

### Common Questions

**Q: Can Quest agents call my agent?**  
A: Yes! Register with capabilities, Quest's semantic router will discover and invoke your agent.

**Q: Can my agent call Quest agents?**  
A: Yes! Use `agent.call_agent()` or the REST API to invoke other agents.

**Q: Do I need to use LangChain?**  
A: No! You can wrap any hard-coded algorithm. LangChain is optional.

**Q: Is this production-ready?**  
A: Yes! CloudEvents 1.0, distributed tracing, schema validation, and comprehensive error handling.

## 🧪 Testing

```bash
# Run all examples
cd examples
python simple_sql_agent.py
python rag_analysis_agent.py
python algorithm_executor_agent.py

# Run with Docker
cd docker
docker-compose up
```

## 📊 Comparison

| Feature | Basic SDK | + Schemas | + Advanced |
|---------|-----------|-----------|------------|
| Redis Streams | ✅ | ✅ | ✅ |
| REST API | ✅ | ✅ | ✅ |
| JSON Schema | ❌ | ✅ | ✅ |
| SHACL Validation | ❌ | ❌ | ✅ |
| Ontology | ❌ | ❌ | ✅ |
| Agent Discovery | ❌ | ❌ | ✅ |
| Templates | ❌ | ❌ | ✅ |

## 🎯 Roadmap

- [x] Core SDK (Redis Streams + REST)
- [x] Schema validation (JSON Schema)
- [x] Advanced features (Ontology, Discovery, Templates)
- [x] Docker support
- [ ] Go SDK
- [ ] Java SDK
- [ ] Kubernetes Helm charts
- [ ] Performance benchmarks
- [ ] Monitoring dashboard

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 🙏 Acknowledgments

Built with:
- [LangChain](https://langchain.com/) - LLM application framework
- [Redis](https://redis.io/) - Event streaming
- [CloudEvents](https://cloudevents.io/) - Event standards
- [SHACL](https://www.w3.org/TR/shacl/) - Semantic validation

---

**Ready to integrate? Start with [Getting Started Guide](docs/GETTING_STARTED.md)** 🚀
