# Schema Registration Guide for External Agents

## Why Register Schemas?

Schema registration provides:
1. ✅ **Input Validation** - Catch invalid requests early
2. ✅ **Output Validation** - Ensure consistent responses
3. ✅ **Auto Documentation** - Schemas serve as contracts
4. ✅ **Version Management** - Track schema evolution
5. ✅ **Interoperability** - Other agents know your data format

## Quick Start

### 1. Define Your Schemas

```python
# Input Schema - What your agent expects
INPUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "SQL query to execute"
        },
        "database": {
            "type": "string",
            "description": "Target database name"
        }
    },
    "required": ["query"]
}

# Output Schema - What your agent returns
OUTPUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "claim": {
            "type": "object",
            "properties": {
                "answer": {"type": "string"},
                "structured": {"type": "object"}
            },
            "required": ["answer"]
        }
    },
    "required": ["claim", "support", "method"]
}
```

### 2. Register with Your Agent

```python
from quest_agent_sdk import QuestAgentConfig, QuestLangChainAgent

config = QuestAgentConfig(agent_name="My Agent")
agent = QuestLangChainAgent(config)

# Register with schemas
agent.register(
    capabilities=["sql_analysis"],
    input_schema=INPUT_SCHEMA,   # ← Add this
    output_schema=OUTPUT_SCHEMA  # ← Add this
)
```

### 3. Automatic Validation

```python
def handle_action(action, agent):
    # Validate inputs
    if not agent.validate_input(action):
        return error_evidence("Invalid inputs")
    
    # Your logic here
    result = process(action["inputs"])
    
    # Create evidence
    evidence = create_evidence(result)
    
    # Validate outputs
    if not agent.validate_output(evidence):
        print("Warning: Output doesn't match schema!")
    
    return evidence
```

## Schema Format

Quest Agent Forge uses **JSON Schema Draft 7**.

### Common Patterns

#### Basic Types
```json
{
  "type": "string"          // text
  "type": "number"          // 123.45
  "type": "integer"         // 123
  "type": "boolean"         // true/false
  "type": "array"           // []
  "type": "object"          // {}
}
```

#### Validation Rules
```json
{
  "type": "number",
  "minimum": 0,
  "maximum": 100,
  "multipleOf": 0.01
}
```

```json
{
  "type": "string",
  "minLength": 1,
  "maxLength": 100,
  "pattern": "^[A-Za-z0-9]+$"
}
```

```json
{
  "type": "array",
  "items": {"type": "string"},
  "minItems": 1,
  "maxItems": 10,
  "uniqueItems": true
}
```

#### Required Fields
```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "email": {"type": "string"}
  },
  "required": ["name"],      // email is optional
  "additionalProperties": false  // no extra fields
}
```

#### Enums
```json
{
  "type": "string",
  "enum": ["low", "medium", "high"]
}
```

## Schema Versioning

### Compatibility Modes

**Backward Compatible** (default for inputs):
```python
agent.register_input_schema(schema)
# New version can read old data
# Safe to add optional fields
# Cannot remove required fields
```

**Forward Compatible** (default for outputs):
```python
agent.register_output_schema(schema)
# Old version can read new data
# Cannot add required fields
# Safe to remove fields
```

**Full Compatible**:
```python
rest_client.register_schema(
    name="my-schema",
    version="2.0.0",
    schema=schema,
    compatibility="full"  # Both backward and forward
)
```

### Version Evolution

```python
# Version 1.0.0 - Initial
{
    "properties": {
        "price": {"type": "number"}
    },
    "required": ["price"]
}

# Version 1.1.0 - Add optional field (backward compatible)
{
    "properties": {
        "price": {"type": "number"},
        "currency": {"type": "string"}  # NEW, optional
    },
    "required": ["price"]
}

# Version 2.0.0 - Breaking change (new required field)
{
    "properties": {
        "price": {"type": "number"},
        "currency": {"type": "string"}  # NOW REQUIRED
    },
    "required": ["price", "currency"]  # BREAKING CHANGE
}
```

## Complete Example

See `examples/schema_registration_example.py` for a complete working example with:
- Input schema definition
- Output schema definition
- Schema registration
- Automatic validation
- Error handling

## API Reference

### Register Schema
```python
schema_uri = agent.register_input_schema(schema)
# Returns: "https://schemas.acme.com/my-agent-input/1.0.0"

schema_uri = agent.register_output_schema(schema)
# Returns: "https://schemas.acme.com/my-agent-output/1.0.0"
```

### Validate
```python
# Validate inputs
is_valid = agent.validate_input(action)

# Validate outputs
is_valid = agent.validate_output(evidence)
```

### Direct Schema API
```python
# Register custom schema
schema_uri = rest_client.register_schema(
    name="custom-schema",
    version="1.0.0",
    schema={...},
    compatibility="backward"
)

# Get schema
schema = rest_client.get_schema(schema_uri)

# Validate against schema
result = rest_client.validate_against_schema(schema_uri, data)
print(result["valid"])      # True/False
print(result["errors"])     # List of errors
```

## Testing Schemas

### Manual Test
```bash
# Register
curl -X POST http://localhost:3000/api/schemas/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-schema",
    "version": "1.0.0",
    "schema": {
      "type": "object",
      "properties": {"name": {"type": "string"}},
      "required": ["name"]
    }
  }'

# Validate
curl -X POST http://localhost:3000/api/schemas/validate \
  -H "Content-Type: application/json" \
  -d '{
    "schema_uri": "https://schemas.acme.com/test-schema/1.0.0",
    "payload": {"name": "John"}
  }'
```

### Python Test
```python
from quest_agent_sdk import RestAPIClient, QuestAgentConfig

config = QuestAgentConfig()
client = RestAPIClient(config)

# Register
uri = client.register_schema("test", "1.0.0", {
    "type": "object",
    "properties": {"name": {"type": "string"}},
    "required": ["name"]
})

# Validate valid data
result = client.validate_against_schema(uri, {"name": "John"})
assert result["valid"] == True

# Validate invalid data
result = client.validate_against_schema(uri, {"age": 30})
assert result["valid"] == False
print(result["errors"])  # ["name is required"]
```

## Best Practices

1. **Always version your schemas** - Use semantic versioning (1.0.0)
2. **Start strict, relax later** - Easier to add optional fields than remove required ones
3. **Document your schemas** - Use `description` fields
4. **Test schema changes** - Validate old data against new schemas
5. **Use compatibility modes** - Backward for inputs, forward for outputs
6. **Provide examples** - Include example values in descriptions
7. **Keep schemas simple** - Avoid deep nesting when possible

## Common Patterns

### Pricing Agent
```python
INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "current_price": {"type": "number", "minimum": 0},
        "cost": {"type": "number", "minimum": 0},
        "elasticity": {"type": "number", "maximum": 0}
    },
    "required": ["current_price", "cost", "elasticity"]
}
```

### SQL Agent
```python
INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "minLength": 1},
        "database": {"type": "string"},
        "timeout_ms": {"type": "integer", "minimum": 100, "default": 30000}
    },
    "required": ["query"]
}
```

### RAG Agent
```python
INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "minLength": 1},
        "max_results": {"type": "integer", "minimum": 1, "maximum": 10, "default": 5},
        "min_confidence": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.7}
    },
    "required": ["query"]
}
```

## Troubleshooting

### Schema Not Found
- Check schema URI format
- Verify registration succeeded
- Check schema name/version match

### Validation Failing
- Check error messages
- Validate your JSON manually
- Compare against schema definition
- Use online validators (jsonschemavalidator.net)

### Compatibility Errors
- Review breaking changes
- Increment major version for breaking changes
- Test with old and new data

## Resources

- JSON Schema Spec: https://json-schema.org/
- Online Validator: https://www.jsonschemavalidator.net/
- Schema Generator: https://www.liquid-technologies.com/online-json-to-schema-converter

---

**Schema registration is optional but highly recommended for production agents!**
