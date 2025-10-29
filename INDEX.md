# Quest Agent SDK - File Index

**Quick navigation for all SDK files.**

## 📖 Start Here

| File | Purpose | Read Time |
|------|---------|-----------|
| [QUICKSTART.md](QUICKSTART.md) | Get running in 5 minutes | 3 min |
| [README.md](README.md) | Complete SDK overview | 10 min |

## 📚 Documentation

| File | Purpose | Audience |
|------|---------|----------|
| [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) | Beginner's tutorial | New users |
| [docs/SCHEMA_GUIDE.md](docs/SCHEMA_GUIDE.md) | Schema validation guide | All users |
| [docs/ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md) | Ontology, discovery, templates | Advanced users |
| [docs/API_REFERENCE.md](docs/API_REFERENCE.md) | Complete API documentation | All users |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Problem solving | All users |

## 💻 Code

### Python SDK

| File | Purpose | Lines |
|------|---------|-------|
| [python/quest_agent_sdk.py](python/quest_agent_sdk.py) | Core SDK module | 600 |
| [python/ontology_integration.py](python/ontology_integration.py) | Advanced features | 400 |
| [python/README.md](python/README.md) | Python SDK guide | - |

### TypeScript Client

| File | Purpose | Lines |
|------|---------|-------|
| [typescript/quest-agent-client.ts](typescript/quest-agent-client.ts) | Client library | 400 |
| [typescript/example-usage.ts](typescript/example-usage.ts) | Usage examples | 200 |
| [typescript/README.md](typescript/README.md) | TypeScript guide | - |

## 🎯 Examples

| File | Best For | Complexity |
|------|----------|------------|
| [examples/algorithm_executor_agent.py](examples/algorithm_executor_agent.py) ⭐ | Hard-coded algorithms | Low |
| [examples/simple_sql_agent.py](examples/simple_sql_agent.py) | LangChain SQL | Medium |
| [examples/rag_analysis_agent.py](examples/rag_analysis_agent.py) | RAG Q&A | Medium |
| [examples/schema_registration_example.py](examples/schema_registration_example.py) | Validation | Low |
| [examples/advanced_integration_example.py](examples/advanced_integration_example.py) | Production | High |
| [examples/rest_api_example.py](examples/rest_api_example.py) | HTTP calls | Low |
| [examples/README.md](examples/README.md) | Examples guide | - |

## 🐳 Docker

| File | Purpose |
|------|---------|
| [docker/docker-compose.yml](docker/docker-compose.yml) | Multi-agent deployment |
| [docker/Dockerfile.agent](docker/Dockerfile.agent) | Agent container |
| [docker/.env.example](docker/.env.example) | Environment template |
| [docker/README.md](docker/README.md) | Docker guide |

## 📋 Project Files

| File | Purpose |
|------|---------|
| [requirements.txt](requirements.txt) | Python dependencies |
| [LICENSE](LICENSE) | MIT License |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guide |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [.gitignore](.gitignore) | Git ignore patterns |

## 🗺️ Learning Paths

### Path 1: Quick Start (15 minutes)
1. [QUICKSTART.md](QUICKSTART.md) ← Run your first agent
2. [examples/algorithm_executor_agent.py](examples/algorithm_executor_agent.py) ← See a real example
3. [docs/API_REFERENCE.md](docs/API_REFERENCE.md) ← Look up functions

### Path 2: Complete Tutorial (2 hours)
1. [README.md](README.md) ← Overview
2. [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) ← Tutorial
3. Run all [examples/](examples/)
4. [docs/SCHEMA_GUIDE.md](docs/SCHEMA_GUIDE.md) ← Add validation
5. [docker/README.md](docker/README.md) ← Deploy

### Path 3: Production Integration (1 day)
1. [README.md](README.md) ← Overview
2. [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) ← Basics
3. [docs/SCHEMA_GUIDE.md](docs/SCHEMA_GUIDE.md) ← Validation
4. [docs/ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md) ← Ontology & discovery
5. [examples/advanced_integration_example.py](examples/advanced_integration_example.py) ← Full example
6. [docker/README.md](docker/README.md) ← Deploy
7. [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) ← Debug

## 🔍 Find by Topic

### Integration Patterns
- **Event-Driven:** [README.md](README.md#integration-patterns), [python/quest_agent_sdk.py](python/quest_agent_sdk.py)
- **REST API:** [examples/rest_api_example.py](examples/rest_api_example.py)
- **Hybrid:** [docs/ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md)

### Validation
- **JSON Schema:** [docs/SCHEMA_GUIDE.md](docs/SCHEMA_GUIDE.md), [examples/schema_registration_example.py](examples/schema_registration_example.py)
- **SHACL:** [docs/ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md#shacl-validation)

### Advanced Features
- **Ontology:** [python/ontology_integration.py](python/ontology_integration.py), [docs/ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md#ontology-integration)
- **Agent Discovery:** [docs/ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md#agent-discovery)
- **Templates:** [docs/ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md#template-integration)

### Deployment
- **Local:** [QUICKSTART.md](QUICKSTART.md)
- **Docker:** [docker/README.md](docker/README.md)
- **Production:** [docs/ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md)

### Troubleshooting
- **Connection Issues:** [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md#connection-issues)
- **Runtime Issues:** [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md#runtime-issues)
- **Schema Issues:** [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md#schema-validation-issues)

## 📊 File Statistics

- **Total Files:** 26
- **Documentation:** 12 files (README, guides, API ref)
- **Code:** 8 files (Python SDK, TypeScript client, examples)
- **Configuration:** 6 files (Docker, requirements, license)
- **Lines of Code:** ~2,000 (SDK + examples)
- **Lines of Docs:** ~8,000 (guides + references)

## 🎯 By Use Case

| I want to... | Start with... |
|-------------|---------------|
| Get started quickly | [QUICKSTART.md](QUICKSTART.md) |
| Wrap my algorithm | [examples/algorithm_executor_agent.py](examples/algorithm_executor_agent.py) |
| Build a SQL agent | [examples/simple_sql_agent.py](examples/simple_sql_agent.py) |
| Build a RAG agent | [examples/rag_analysis_agent.py](examples/rag_analysis_agent.py) |
| Add validation | [docs/SCHEMA_GUIDE.md](docs/SCHEMA_GUIDE.md) |
| Use ontology | [docs/ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md) |
| Deploy with Docker | [docker/README.md](docker/README.md) |
| Call Quest agents | [typescript/quest-agent-client.ts](typescript/quest-agent-client.ts) |
| Troubleshoot | [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) |
| Understand API | [docs/API_REFERENCE.md](docs/API_REFERENCE.md) |
| Contribute | [CONTRIBUTING.md](CONTRIBUTING.md) |

---

**Not sure where to start? → [QUICKSTART.md](QUICKSTART.md)** 🚀
