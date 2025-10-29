# Troubleshooting Guide

Common issues and solutions for Quest Agent SDK.

## Installation Issues

### Python Dependencies Won't Install

**Problem:** `pip install -r requirements.txt` fails

**Solutions:**

```bash
# Update pip
python -m pip install --upgrade pip

# Use virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install specific problematic package separately
pip install langchain==0.1.0
pip install -r requirements.txt
```

---

## Connection Issues

### Can't Connect to Quest Agent Forge

**Problem:** `Connection refused` or `Connection timeout`

**Check Quest is running:**
```bash
curl http://localhost:3000/api/agents
```

**Check network:**
```bash
# From your agent
ping localhost

# Test specific port
nc -zv localhost 3000
```

**Solutions:**
- Ensure Quest Agent Forge is running
- Check `API_URL` in your config
- Use `http://host.docker.internal:3000` in Docker
- Check firewall settings

---

### Can't Connect to Redis

**Problem:** `Connection to Redis failed`

**Check Redis is running:**
```bash
redis-cli ping  # Should return PONG
```

**Check Redis connection:**
```bash
redis-cli -h localhost -p 6379 ping
```

**Solutions:**
- Start Redis: `redis-server`
- Check `REDIS_HOST` and `REDIS_PORT`
- Use `redis` as host in Docker Compose
- Check Redis password if set

---

## Agent Registration Issues

### Agent Not Appearing in Quest

**Problem:** Agent registered but not visible

**Check registration:**
```bash
curl http://localhost:3000/api/agents
# Should include your agent
```

**Check agent output:**
```python
# Look for:
✅ Agent registered: {...}
```

**Solutions:**
- Verify `agent_name` is unique
- Check `capabilities` are specified
- Ensure Quest database is accessible
- Check Quest logs for errors

---

### Multiple Agents with Same Name

**Problem:** Agent name conflicts

**Solution:**
```python
# Use unique names
config = QuestAgentConfig(
    agent_name="My Pricing Agent v2",  # Make it unique
    agent_version="1.0.1"               # Or bump version
)
```

---

## Runtime Issues

### Agent Not Receiving Actions

**Problem:** Agent running but never processes actions

**Check consumer group:**
```bash
redis-cli XINFO GROUPS mesh:commands
# Should show your consumer group
```

**Check stream has messages:**
```bash
redis-cli XLEN mesh:commands
```

**Check agent is listening:**
```python
# Should see:
🚀 Starting worker: My Agent
Listening on: mesh:commands
```

**Solutions:**
- Verify Redis Streams connection
- Check consumer group name
- Ensure agent called `start_worker()`
- Check for exceptions in agent code

---

### Actions Failing Silently

**Problem:** Actions execute but no results

**Check handler returns evidence:**
```python
def handler(action):
    result = my_logic(action)
    # MUST return evidence object
    return EvidenceBuilder.create_evidence(...)
```

**Check for exceptions:**
```python
# Add error handling
def handler(action):
    try:
        result = my_logic(action)
        return create_evidence(result)
    except Exception as e:
        print(f"Error: {e}")  # This will show you the problem
        import traceback
        traceback.print_exc()
        return create_evidence(answer=f"Error: {e}", confidence=0.0)
```

**Enable debug logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

### Handler Exceptions

**Problem:** Handler crashes on certain inputs

**Always handle errors:**
```python
def handler(action):
    try:
        # Validate inputs first
        inputs = action.get("inputs", {})
        if "required_field" not in inputs:
            raise ValueError("Missing required_field")
        
        # Your logic
        result = my_logic(inputs)
        
        return create_evidence(result)
        
    except ValueError as e:
        return create_evidence(
            answer=f"Invalid input: {e}",
            confidence=0.0
        )
    except Exception as e:
        return create_evidence(
            answer=f"Error: {e}",
            confidence=0.0
        )
```

---

## Schema Validation Issues

### Input Validation Failing

**Problem:** All requests rejected as invalid

**Check schema:**
```python
# Test schema independently
from python.quest_agent_sdk import RestAPIClient

client = RestAPIClient(config)
result = client.validate_against_schema(schema_uri, test_data)
print(result["errors"])  # See what's wrong
```

**Common issues:**
- Missing required fields
- Wrong data types
- Extra fields when `additionalProperties: false`

**Debug:**
```python
# Temporarily disable validation
agent.register(
    capabilities=["test"],
    # input_schema=INPUT_SCHEMA  # Comment out
)
```

---

### Schema Not Found

**Problem:** `Schema not found: ...`

**Check schema was registered:**
```bash
curl http://localhost:3000/api/schemas/by-uri?uri=YOUR_SCHEMA_URI
```

**Re-register if needed:**
```python
agent.register_input_schema(INPUT_SCHEMA)
```

---

## Ontology Issues

### Concept Not Found

**Problem:** `ontology.resolve("term")` returns `None`

**Check available concepts:**
```bash
curl http://localhost:3000/api/ontology/resolve/pricing
```

**Use fallback:**
```python
concept_uri = ontology.resolve("pricing")
if not concept_uri:
    concept_uri = "ex:Unknown"  # Fallback
```

---

### SHACL Validation Failing

**Problem:** All SHACL validations fail

**Check warnings, not just errors:**
```python
result = ontology.validate_shacl(data, shape_uri)
if not result["conforms"]:
    print("Violations:", result["violations"])
    print("Warnings:", result.get("warnings", []))
```

**Warnings are often acceptable:**
```python
# You can continue even with warnings
if result.get("violations"):
    # Hard errors
    return error_evidence("Invalid data")
else:
    # Warnings OK, proceed
    return create_evidence(data)
```

---

## Docker Issues

### Container Won't Start

**Check logs:**
```bash
docker-compose logs agent-name
```

**Check environment:**
```bash
docker-compose exec agent-name env | grep API
```

**Common issues:**
- Missing environment variables
- Wrong API_URL (use `host.docker.internal`)
- Redis not ready (add `depends_on` with health check)

---

### Can't Access Quest from Container

**Problem:** Connection refused from Docker

**Use special Docker hostname:**
```yaml
environment:
  - API_URL=http://host.docker.internal:3000
```

**Or use host network:**
```yaml
network_mode: "host"
```

---

## Performance Issues

### Slow Response Times

**Check:**
- LLM latency (if using LangChain)
- Database query time
- Network latency

**Profile your code:**
```python
import time

def handler(action):
    start = time.time()
    
    # Your logic
    result = my_logic(action)
    
    elapsed = (time.time() - start) * 1000
    print(f"Processing took {elapsed}ms")
    
    return create_evidence(
        result,
        latency_ms=int(elapsed)
    )
```

---

### High Memory Usage

**Check:**
- Large data structures in memory
- Memory leaks in loops
- Vector store size (if using RAG)

**Solution:**
```python
# Process in batches
def handler(action):
    inputs = action["inputs"]
    
    # Don't load everything at once
    for batch in chunks(inputs["large_list"], 1000):
        process_batch(batch)
```

---

## Debugging Tips

### Enable Verbose Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Print Everything

```python
def handler(action):
    print(f"Action: {json.dumps(action, indent=2)}")
    
    result = my_logic(action["inputs"])
    print(f"Result: {json.dumps(result, indent=2)}")
    
    evidence = create_evidence(result)
    print(f"Evidence: {json.dumps(evidence, indent=2)}")
    
    return evidence
```

### Test Handler Independently

```python
# test_handler.py
from my_agent import handler

test_action = {
    "id": "test_123",
    "type": "test",
    "inputs": {"test": "data"}
}

result = handler(test_action)
print(result)
```

### Check Redis Streams Directly

```bash
# Check what's in the stream
redis-cli XREAD COUNT 10 STREAMS mesh:commands 0

# Check consumer group lag
redis-cli XPENDING mesh:commands langchain-agents

# Read as your consumer
redis-cli XREADGROUP GROUP langchain-agents consumer-1 COUNT 1 STREAMS mesh:commands >
```

---

## Still Need Help?

1. **Check examples** - [../examples/](../examples/)
2. **Review docs** - [../docs/](../docs/)
3. **Search issues** - GitHub Issues
4. **Ask questions** - GitHub Discussions
5. **Check Quest logs** - Quest Agent Forge console

---

## Quick Diagnostics

Run this diagnostic script:

```python
# diagnostic.py
import sys
from python.quest_agent_sdk import QuestAgentConfig, RestAPIClient
import redis

print("=== Quest Agent SDK Diagnostic ===\n")

# Test Python version
print(f"✓ Python version: {sys.version}")

# Test Redis connection
try:
    r = redis.Redis(host='localhost', port=6379)
    r.ping()
    print("✓ Redis connection: OK")
except Exception as e:
    print(f"✗ Redis connection: FAILED - {e}")

# Test Quest API
try:
    config = QuestAgentConfig()
    client = RestAPIClient(config)
    agents = client.list_agents()
    print(f"✓ Quest API connection: OK ({len(agents)} agents)")
except Exception as e:
    print(f"✗ Quest API connection: FAILED - {e}")

print("\nIf all checks pass, your environment is ready!")
```

Run with: `python diagnostic.py`

---

**Most issues are environment or configuration related. Double-check your setup!**
