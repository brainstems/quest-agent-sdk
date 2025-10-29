# Advanced Features Guide

Complete guide to advanced integration features for external agents.

## Table of Contents

1. [Ontology Integration](#ontology-integration)
2. [Knowledge Graph](#knowledge-graph)
3. [Agent Discovery](#agent-discovery)
4. [Agent Bidding](#agent-bidding)
5. [Template Integration](#template-integration)
6. [Semantic Interoperability](#semantic-interoperability)

---

## Ontology Integration

Quest Agent Forge uses a **SKOS ontology** for semantic understanding and interoperability.

### What is the Ontology?

The ontology defines:
- **Concepts** - Business concepts (Pricing, Inventory, Campaign, etc.)
- **Relations** - How concepts relate (broader, narrower, related, synonym)
- **Mappings** - Enum/unit translations between systems
- **Constraints** - Business rules (minimum margins, floor prices, etc.)
- **Shapes** - SHACL validation schemas

### Core Operations

```python
from ontology_integration import OntologyClient

ontology = OntologyClient("http://localhost:3000")

# 1. Resolve term to canonical URI
uri = ontology.resolve("pricing")
# Returns: "ex:Pricing"

# 2. Expand concepts (semantic expansion)
expanded = ontology.expand(
    ["ex:Pricing"],
    relations=["broader", "narrower", "related"],
    depth=1
)
# Returns: ["ex:Pricing", "ex:Revenue", "ex:Markdown", "ex:Promotion", ...]

# 3. Get business constraints
constraints = ontology.get_constraints("cat:Beverages")
# Returns: [
#   {"constraint_type": "minMarginPct", "constraint_value": 0.15},
#   {"constraint_type": "floorPrice", "constraint_value": 4.99}
# ]

# 4. SHACL validation
result = ontology.validate_shacl(
    data={"price": 9.99, "marginPct": 0.10},
    shape_uri="shape:PriceEvent",
    category_uri="cat:Beverages"
)
if not result["conforms"]:
    print("Violations:", result["violations"])
```

### Use Cases

**1. Semantic Understanding**
```python
# Enrich your action with ontology
enriched = enrich_action_with_ontology(action, ontology)
# Adds @context with related concepts
# Adds @constraints with business rules
```

**2. Business Constraint Validation**
```python
# Get category-specific constraints
product_category = ontology.resolve("beverage")
constraints = ontology.get_constraints(product_category)

# Apply to your algorithm
min_margin = next(c["constraint_value"] for c in constraints if c["constraint_type"] == "minMarginPct")
recommended_price = max(cost * (1 + min_margin), optimal_price)
```

**3. Cross-System Translation**
```python
# Translate between systems
shopify_id = ontology.same_as("ent:product_123", "shopify")
amazon_id = ontology.same_as("ent:product_123", "amazon")
```

### Available Concepts

Common ontology concepts:
- **ex:Pricing** - Pricing operations
- **ex:Inventory** - Inventory management
- **ex:Campaign** - Marketing campaigns
- **ex:Forecast** - Demand forecasting
- **ex:Optimization** - Optimization algorithms
- **ex:Revenue** - Revenue management
- **ex:Markdown** - Price reductions
- **ex:Elasticity** - Price elasticity

Categories:
- **cat:Beverages** - Beverage products (15% min margin)
- **cat:Electronics** - Electronics (20% min margin)
- **cat:Apparel** - Clothing (40% min margin)

---

## Knowledge Graph

The knowledge graph stores **entities, relationships, and properties**.

### Entities & Relationships

```python
from ontology_integration import KnowledgeGraphClient

kg = KnowledgeGraphClient("http://localhost:3000")

# Get entity
entity = kg.get_entity("product_123")

# Get related entities
related = kg.get_related("product_123", relationship_type="similar_to")

# Find path between entities
path = kg.find_path("product_123", "category_electronics", max_depth=3)
```

### Use Cases

**1. Product Context**
```python
# Get product and its relationships
product = kg.get_entity("product_123")
similar_products = kg.get_related("product_123", "similar_to")
category = kg.get_related("product_123", "belongs_to")
```

**2. Customer Context**
```python
# Get customer purchase history
customer = kg.get_entity("customer_456")
purchases = kg.get_related("customer_456", "purchased")
preferences = kg.get_related("customer_456", "prefers")
```

**3. Graph Navigation**
```python
# Find how two concepts are related
path = kg.find_path("product_pricing", "demand_forecast")
# Might return: product -> category -> demand_pattern -> forecast
```

---

## Agent Discovery

Discover agents by capability, ontology concepts, or semantic search.

### Discovery Methods

```python
from ontology_integration import AgentDiscoveryClient, OntologyClient

discovery = AgentDiscoveryClient("http://localhost:3000")
ontology = OntologyClient("http://localhost:3000")

# 1. By capability (exact match)
agents = discovery.discover_by_capability("pricing_optimization")

# 2. By ontology concepts (semantic match)
pricing_uri = ontology.resolve("pricing")
agents = discovery.discover_by_concepts([pricing_uri], ontology)
# Finds agents interested in pricing, revenue, markdown, etc.

# 3. By natural language
agents = discovery.discover_by_semantic_search(
    "agents that can optimize prices and inventory together"
)
```

### How It Works

**Agent Ontology Profiles:**
Every agent registers its interests as ontology concepts:

```python
# Your agent's profile (automatic)
{
    "agent_id": "my-pricing-agent",
    "interests_concepts_must": ["ex:Pricing", "ex:Optimization"],
    "interests_concepts_any": ["ex:Revenue", "ex:Elasticity"]
}
```

**Discovery Process:**
1. Query expands using ontology (Pricing → Revenue, Markdown, Promotion)
2. Finds agents interested in expanded concepts
3. Ranks by relevance and confidence
4. Returns sorted list

### Use in Your Agent

```python
def handle_action(action):
    # Discover agents that can help
    discovery = AgentDiscoveryClient()
    
    # Find inventory agents (for stock-aware pricing)
    inv_agents = discovery.discover_by_capability("inventory_management")
    
    # Find forecasting agents (for demand-aware pricing)
    forecast_agents = discovery.discover_by_capability("forecasting")
    
    # Call them if needed
    if inv_agents:
        inventory_data = quest_agent.call_agent(
            agent_name=inv_agents[0]["name"],
            capability="inventory_check",
            parameters={"product_id": "123"}
        )
```

---

## Agent Bidding

Agents can bid for tasks in a marketplace pattern.

### How Bidding Works

```python
from ontology_integration import AgentDiscoveryClient

discovery = AgentDiscoveryClient()

# Task is broadcast
task = {
    "id": "task_123",
    "required_capabilities": ["pricing_optimization", "elasticity_modeling"],
    "priority": "high",
    "deadline": "2025-10-30T12:00:00Z"
}

# Your agent bids
bid = discovery.bid_for_task(
    task=task,
    my_capabilities=["pricing_optimization", "elasticity_modeling", "constraint_checking"],
    my_confidence=0.92  # How confident you are
)

if bid["accepted"]:
    print("✅ Won the bid!")
    # Execute the task
else:
    print(f"❌ Bid rejected: {bid['reason']}")
```

### Bid Calculation

```python
# Automatic scoring
match_score = len(required ∩ provided) / len(required)
final_score = match_score * confidence

# Winning bid = highest final_score
```

### Use Cases

1. **Multi-Agent Systems** - Agents compete for tasks
2. **Load Balancing** - Distribute work to capable agents
3. **Quality Assurance** - High-confidence agents win critical tasks
4. **Specialization** - Domain experts bid higher for their specialty

---

## Template Integration

Templates orchestrate multi-agent workflows.

### What are Templates?

Templates are **ACT-R packlets** that:
- Define complex workflows
- Orchestrate multiple agents
- Handle user interactions
- Manage state transitions

### Working with Templates

```python
from ontology_integration import TemplateIntegration

templates = TemplateIntegration("http://localhost:3000")

# 1. Register your agent for templates
templates.register_agent_for_template(
    agent_name="My Pricing Agent",
    template_ids=["pricing-optimization", "markdown-planning"],
    capabilities=["pricing_optimization"]
)

# 2. Find templates for an intent
matching = templates.get_templates_for_intent("optimize_pricing")

# 3. Execute a template
result = templates.execute_template(
    template_id="pricing-optimization",
    context={"product_id": "123", "current_price": 99.99},
    user_id="user_456"
)
```

### How Templates Discover Your Agent

1. User triggers template (e.g., "optimize pricing")
2. Template identifies required capabilities
3. **Semantic router discovers capable agents** (including yours!)
4. Template invokes agent(s)
5. Orchestrates multi-step workflow

### Example Workflow

```
User: "Optimize pricing for holiday promotion"
  ↓
Template: "pricing-with-promotion"
  ↓
Discovers Agents:
  - Pricing Agent (pricing_optimization)
  - Demand Forecast Agent (forecasting)
  - Inventory Agent (inventory_check)
  - Promotion Agent (promotion_planning)
  ↓
Orchestrates:
  1. Get demand forecast
  2. Check inventory
  3. Calculate optimal price
  4. Apply promotion rules
  5. Validate constraints
  ↓
Present to user for approval
```

---

## Semantic Interoperability

Putting it all together for seamless integration.

### The Complete Flow

```python
from quest_agent_sdk import QuestLangChainAgent, QuestAgentConfig
from ontology_integration import (
    OntologyClient,
    AgentDiscoveryClient,
    enrich_action_with_ontology,
    validate_output_with_ontology
)

# Setup
config = QuestAgentConfig(agent_name="Smart Agent")
agent = QuestLangChainAgent(config)
ontology = OntologyClient()
discovery = AgentDiscoveryClient()

def handle_action(action):
    # 1. Enrich with ontology
    enriched = enrich_action_with_ontology(action, ontology)
    # Now has: @context, @constraints, @category
    
    # 2. Get constraints
    constraints = enriched["inputs"].get("@constraints", [])
    min_margin = next((c["constraint_value"] for c in constraints 
                      if c["constraint_type"] == "minMarginPct"), 0)
    
    # 3. Discover helper agents
    helpers = discovery.discover_by_concepts(enriched["@context"], ontology)
    
    # 4. Execute your algorithm
    result = my_algorithm(enriched["inputs"], min_margin)
    
    # 5. Validate output
    validation = validate_output_with_ontology(
        output=result,
        expected_shape="shape:PriceEvent",
        ontology=ontology
    )
    
    if not validation["conforms"]:
        print("⚠️ Output validation warnings:", validation["warnings"])
    
    # 6. Return evidence
    return create_evidence(result)
```

### Benefits

1. ✅ **Semantic Understanding** - Your agent understands business concepts
2. ✅ **Constraint Compliance** - Automatic business rule validation
3. ✅ **Agent Coordination** - Discover and call other agents
4. ✅ **Quality Assurance** - SHACL validation before returning
5. ✅ **Interoperability** - Works seamlessly with internal agents

---

## API Reference

### OntologyClient

```python
ontology = OntologyClient(api_url)

# Core methods
ontology.resolve(term: str) -> Optional[str]
ontology.expand(concepts: List[str], relations: List[str], depth: int) -> List[str]
ontology.same_as(entity_uri: str, system: str) -> Optional[str]
ontology.get_constraints(concept_uri: str) -> List[Dict]
ontology.get_shape(shape_uri: str) -> Optional[Dict]
ontology.validate_shacl(data: Dict, shape_uri: str, category_uri: str) -> Dict
```

### AgentDiscoveryClient

```python
discovery = AgentDiscoveryClient(api_url)

# Discovery methods
discovery.discover_by_capability(capability: str) -> List[Dict]
discovery.discover_by_concepts(concepts: List[str], ontology: OntologyClient) -> List[Dict]
discovery.discover_by_semantic_search(query: str, limit: int) -> List[Dict]
discovery.bid_for_task(task: Dict, my_capabilities: List[str], my_confidence: float) -> Dict
```

### TemplateIntegration

```python
templates = TemplateIntegration(api_url)

# Template methods
templates.get_templates_for_intent(intent: str) -> List[Dict]
templates.execute_template(template_id: str, context: Dict, user_id: str) -> Dict
templates.register_agent_for_template(agent_name: str, template_ids: List[str], capabilities: List[str]) -> Dict
```

---

## Complete Example

See `examples/advanced_integration_example.py` for a complete working example demonstrating:
- ✅ Ontology enrichment
- ✅ SHACL validation
- ✅ Agent discovery
- ✅ Agent coordination
- ✅ Template integration
- ✅ Constraint enforcement

Run it:
```bash
python examples/advanced_integration_example.py
```

---

## Best Practices

### 1. Always Use Ontology for Business Concepts

```python
# ❌ Bad: Hard-coded strings
if action_type == "pricing":
    ...

# ✅ Good: Ontology resolution
pricing_uri = ontology.resolve("pricing")
if ontology.resolve(action_type) == pricing_uri:
    ...
```

### 2. Validate Against Constraints

```python
# ✅ Always check business constraints
constraints = ontology.get_constraints(category_uri)
min_margin = get_constraint(constraints, "minMarginPct")
recommended_price = max(cost * (1 + min_margin), optimal_price)
```

### 3. Use Semantic Discovery

```python
# ❌ Bad: Hard-coded agent names
inventory_agent = call_agent("Inventory Agent")

# ✅ Good: Semantic discovery
agents = discovery.discover_by_capability("inventory_management")
if agents:
    inventory_agent = agents[0]
```

### 4. Coordinate with Other Agents

```python
# ✅ Don't work in isolation
helpers = discovery.discover_by_concepts(["ex:Inventory", "ex:Forecast"])
for helper in helpers:
    context_data = call_agent(helper["name"], ...)
    # Use in your algorithm
```

### 5. Register for Templates

```python
# ✅ Make your agent discoverable by templates
templates.register_agent_for_template(
    agent_name="My Agent",
    template_ids=["relevant-template"],
    capabilities=my_capabilities
)
```

---

## Troubleshooting

### Ontology Not Found

```python
uri = ontology.resolve("my-term")
if uri is None:
    # Term not in ontology - use fallback
    uri = "ex:Unknown"
```

### No Agents Discovered

```python
agents = discovery.discover_by_capability("rare_capability")
if not agents:
    # Fallback: do it yourself
    result = my_algorithm()
```

### SHACL Validation Fails

```python
result = ontology.validate_shacl(data, shape_uri)
if not result["conforms"]:
    # Log warnings but continue
    print("Warnings:", result["warnings"])
    # Or fix data and retry
```

---

**External agents now have full access to Quest's semantic layer!** 🎉
