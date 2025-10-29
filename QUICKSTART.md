# 5-Minute Quick Start

**Get your first agent running in 5 minutes.**

## Step 1: Install (1 min)

```bash
cd external-agent-sdk
pip install -r requirements.txt
```

## Step 2: Configure (1 min)

```bash
# Set environment variables
export OPENAI_API_KEY="your-key-here"  # Optional, only for LangChain examples
export API_URL="http://localhost:3000"
export REDIS_HOST="localhost"
```

## Step 3: Create Agent (2 min)

Create `my_agent.py`:

```python
from python.quest_agent_sdk import QuestAgentConfig, QuestLangChainAgent, EvidenceBuilder

# Configure
config = QuestAgentConfig(agent_name="My First Agent")
agent = QuestLangChainAgent(config)

# Your algorithm
def handler(action):
    inputs = action.get("inputs", {})
    result = {"message": "Hello from my agent!", "input_count": len(inputs)}
    
    return EvidenceBuilder.create_evidence(
        answer="Processed successfully",
        structured_data=result,
        agent_id=config.agent_id,
        confidence=0.95
    )

# Register and start
agent.register(capabilities=["test"])
print("🚀 Agent ready!")
agent.start_worker(handler=handler)
```

## Step 4: Run (1 min)

```bash
python my_agent.py
```

You should see:
```
🚀 Agent ready!
Listening for actions...
```

## Test It

In another terminal:

```bash
curl -X POST http://localhost:3000/api/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agentName": "My First Agent",
    "capability": "test",
    "parameters": {"test": "hello"}
  }'
```

## What's Next?

1. **Add your algorithm** - Replace `handler` function with your logic
2. **Add validation** - See [docs/SCHEMA_GUIDE.md](docs/SCHEMA_GUIDE.md)
3. **Use ontology** - See [docs/ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md)
4. **Deploy with Docker** - See [docker/README.md](docker/README.md)

## Examples

Run complete examples:

```bash
# Hard-coded algorithms
python examples/algorithm_executor_agent.py

# LangChain SQL
python examples/simple_sql_agent.py

# With schema validation
python examples/schema_registration_example.py
```

## Need Help?

- **Docs:** [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)
- **API Reference:** [docs/API_REFERENCE.md](docs/API_REFERENCE.md)
- **Troubleshooting:** [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

**That's it! You have a working Quest agent.** 🎉
