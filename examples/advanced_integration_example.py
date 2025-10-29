"""
Example: Advanced Integration with Ontology, KG, and Agent Discovery
======================================================================

This example shows how to build a sophisticated agent that:
1. Uses ontology for semantic understanding
2. Validates against SHACL constraints
3. Discovers and coordinates with other agents
4. Integrates with templates
5. Uses knowledge graph for context

Use Case: Intelligent Pricing Agent that coordinates with inventory and marketing agents
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from python.quest_agent_sdk import (
    QuestAgentConfig,
    QuestLangChainAgent,
    EvidenceBuilder
)
from python.ontology_integration import (
    OntologyClient,
    AgentDiscoveryClient,
    TemplateIntegration,
    enrich_action_with_ontology,
    validate_output_with_ontology
)


# ============================================================================
# Sophisticated Pricing Agent with Semantic Understanding
# ============================================================================

class IntelligentPricingAgent:
    """
    Pricing agent that uses ontology and coordinates with other agents
    """
    
    def __init__(self, config: QuestAgentConfig):
        self.config = config
        self.quest_agent = QuestLangChainAgent(config)
        self.ontology = OntologyClient(config.api_url)
        self.discovery = AgentDiscoveryClient(config.api_url)
        self.templates = TemplateIntegration(config.api_url)
    
    def optimize_price(self, action: Dict) -> Dict:
        """
        Optimize price using ontology-aware approach
        """
        print("\n" + "="*60)
        print("🧠 Intelligent Pricing Optimization")
        print("="*60 + "\n")
        
        inputs = action.get("inputs", {})
        
        # Step 1: Enrich action with ontology
        print("1️⃣ Enriching action with ontology...")
        enriched = enrich_action_with_ontology(action, self.ontology)
        
        concepts = enriched.get("@context", [])
        print(f"   Related concepts: {concepts}")
        
        # Step 2: Get business constraints
        category_uri = enriched.get("inputs", {}).get("@category")
        constraints = []
        
        if category_uri:
            print(f"\n2️⃣ Getting constraints for category: {category_uri}")
            constraints = self.ontology.get_constraints(category_uri)
            print(f"   Found {len(constraints)} constraints")
            
            for c in constraints:
                if c["constraint_type"] == "minMarginPct":
                    print(f"   - Minimum margin: {c['constraint_value']*100}%")
                elif c["constraint_type"] == "floorPrice":
                    print(f"   - Floor price: ${c['constraint_value']}")
        
        # Step 3: Discover related agents
        print("\n3️⃣ Discovering related agents...")
        
        # Find inventory agents (might affect pricing)
        inventory_agents = self.discovery.discover_by_capability("inventory_management")
        print(f"   Inventory agents: {len(inventory_agents)}")
        
        # Find demand forecasting agents
        forecast_agents = self.discovery.discover_by_capability("forecasting")
        print(f"   Forecasting agents: {len(forecast_agents)}")
        
        # Step 4: Execute pricing algorithm with constraints
        print("\n4️⃣ Executing pricing algorithm...")
        
        current_price = inputs.get("current_price", 100.0)
        cost = inputs.get("cost", 60.0)
        elasticity = inputs.get("demand_elasticity", -1.5)
        
        # Apply minimum margin constraint
        min_margin = 0.0
        for c in constraints:
            if c["constraint_type"] == "minMarginPct":
                min_margin = c["constraint_value"]
        
        min_price = cost * (1 + min_margin)
        optimal_markup = 1 / (1 + abs(elasticity))
        optimal_price = cost * (1 + optimal_markup)
        recommended_price = max(min_price, optimal_price)
        
        # Check against floor price constraint
        for c in constraints:
            if c["constraint_type"] == "floorPrice":
                recommended_price = max(recommended_price, c["constraint_value"])
        
        result = {
            "recommended_price": round(recommended_price, 2),
            "current_price": current_price,
            "margin_pct": round(((recommended_price - cost) / recommended_price) * 100, 2),
            "meets_constraints": True,
            "applied_constraints": [c["constraint_type"] for c in constraints]
        }
        
        print(f"   Recommended price: ${result['recommended_price']}")
        print(f"   Margin: {result['margin_pct']}%")
        print(f"   Applied {len(constraints)} constraints")
        
        # Step 5: Validate against SHACL shape
        print("\n5️⃣ Validating against SHACL shape...")
        
        output_data = {
            "price": recommended_price,
            "marginPct": result["margin_pct"] / 100,
            "category": category_uri
        }
        
        validation = self.ontology.validate_shacl(
            data=output_data,
            shape_uri="shape:PriceEvent",
            category_uri=category_uri
        )
        
        if validation.get("conforms"):
            print("   ✅ SHACL validation passed")
        else:
            print("   ⚠️ SHACL validation warnings:")
            for warning in validation.get("warnings", []):
                print(f"      - {warning}")
        
        # Step 6: Coordinate with inventory agent if needed
        if inputs.get("check_inventory", False):
            print("\n6️⃣ Coordinating with inventory agent...")
            
            if inventory_agents:
                inv_agent = inventory_agents[0]
                print(f"   Calling {inv_agent['name']}...")
                
                # Call inventory agent via Quest
                try:
                    inv_result = self.quest_agent.call_agent(
                        agent_name=inv_agent["name"],
                        capability="inventory_check",
                        parameters={"product_id": inputs.get("product_id")}
                    )
                    print(f"   Inventory level: {inv_result.get('result', {}).get('level', 'unknown')}")
                except Exception as e:
                    print(f"   ⚠️ Could not reach inventory agent: {e}")
        
        return result
    
    def handle_action(self, action: Dict) -> Dict:
        """Handle incoming actions"""
        action_id = action.get("id")
        action_type = action.get("type")
        
        print(f"\n🔵 Received action: {action_id} ({action_type})")
        
        try:
            if action_type in ["pricing_optimization", "optimization.pricing"]:
                result = self.optimize_price(action)
                
                # Create evidence
                evidence = EvidenceBuilder.create_evidence(
                    answer=f"Optimized price to ${result['recommended_price']} with {result['margin_pct']}% margin",
                    structured_data=result,
                    support=[{
                        "type": "calculation",
                        "text": "Ontology-aware pricing optimization with SHACL validation"
                    }],
                    workflow="intelligent-pricing-agent",
                    tools_used=["ontology", "shacl_validator", "elasticity_model"],
                    agent_id=self.config.agent_id,
                    confidence=0.95
                )
                
                return evidence
            
            else:
                raise ValueError(f"Unsupported action type: {action_type}")
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return EvidenceBuilder.create_evidence(
                answer=f"Error: {str(e)}",
                structured_data={"error": str(e)},
                agent_id=self.config.agent_id,
                confidence=0.0
            )


# ============================================================================
# Bidding and Discovery Demo
# ============================================================================

def demo_agent_bidding(config: QuestAgentConfig):
    """Demonstrate agent bidding and discovery"""
    
    print("\n" + "="*60)
    print("🏷️ Agent Bidding and Discovery Demo")
    print("="*60 + "\n")
    
    discovery = AgentDiscoveryClient(config.api_url)
    ontology = OntologyClient(config.api_url)
    
    # Scenario: A task needs pricing optimization
    task = {
        "id": "task_123",
        "required_capabilities": ["pricing_optimization", "elasticity_modeling"],
        "priority": "high"
    }
    
    print("📋 Task requirements:")
    print(f"   Capabilities: {task['required_capabilities']}")
    print(f"   Priority: {task['priority']}")
    
    # Discover agents by capability
    print("\n1️⃣ Discovering agents by capability...")
    agents = discovery.discover_by_capability("pricing_optimization")
    print(f"   Found {len(agents)} agents with pricing_optimization")
    
    # Discover agents by ontology concepts
    print("\n2️⃣ Discovering agents by ontology concepts...")
    pricing_uri = ontology.resolve("pricing")
    if pricing_uri:
        semantic_agents = discovery.discover_by_concepts([pricing_uri], ontology)
        print(f"   Found {len(semantic_agents)} agents via semantic discovery")
    
    # Semantic search
    print("\n3️⃣ Semantic search...")
    nlp_agents = discovery.discover_by_semantic_search(
        "agents that can optimize prices considering demand elasticity",
        limit=5
    )
    print(f"   Found {len(nlp_agents)} agents via NLP search")
    
    # Submit a bid for the task
    print("\n4️⃣ Submitting bid...")
    my_capabilities = ["pricing_optimization", "elasticity_modeling", "constraint_checking"]
    my_confidence = 0.92
    
    bid_result = discovery.bid_for_task(
        task=task,
        my_capabilities=my_capabilities,
        my_confidence=my_confidence
    )
    
    print(f"   Bid result: {bid_result}")


# ============================================================================
# Template Integration Demo
# ============================================================================

def demo_template_integration(config: QuestAgentConfig):
    """Demonstrate template integration"""
    
    print("\n" + "="*60)
    print("📝 Template Integration Demo")
    print("="*60 + "\n")
    
    templates = TemplateIntegration(config.api_url)
    
    # Register agent for templates
    print("1️⃣ Registering agent for templates...")
    result = templates.register_agent_for_template(
        agent_name="Intelligent Pricing Agent",
        template_ids=["pricing-optimization", "markdown-planning"],
        capabilities=["pricing_optimization", "elasticity_modeling", "constraint_checking"]
    )
    print(f"   Registration: {result}")
    
    # Get templates for an intent
    print("\n2️⃣ Finding templates for 'optimize_pricing' intent...")
    matching_templates = templates.get_templates_for_intent("optimize_pricing")
    print(f"   Found {len(matching_templates)} templates")
    
    # Execute a template (if available)
    if matching_templates:
        template_id = matching_templates[0].get("id")
        print(f"\n3️⃣ Executing template: {template_id}")
        
        exec_result = templates.execute_template(
            template_id=template_id,
            context={"product_id": "prod_123", "current_price": 99.99},
            user_id="user_456"
        )
        print(f"   Execution result: {exec_result}")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    
    # Configure agent
    config = QuestAgentConfig(
        agent_name="Intelligent Pricing Agent",
        agent_version="2.0.0",
        redis_host="localhost",
        redis_port=6379,
        api_url="http://localhost:3000"
    )
    
    print("="*60)
    print("🚀 Advanced Integration Example")
    print("="*60)
    
    # Create intelligent agent
    intelligent_agent = IntelligentPricingAgent(config)
    
    # Register agent with extended capabilities
    print("\n📝 Registering agent...")
    intelligent_agent.quest_agent.register(
        capabilities=[
            "pricing_optimization",
            "elasticity_modeling",
            "constraint_checking",
            "ontology_aware",
            "shacl_validation"
        ],
        intents=[
            "optimize_price",
            "check_constraints",
            "validate_pricing"
        ],
        description="Intelligent pricing agent with ontology, SHACL validation, and agent coordination"
    )
    
    print("✅ Agent registered with semantic capabilities")
    
    # Run demos
    demo_agent_bidding(config)
    demo_template_integration(config)
    
    # Start worker
    print("\n" + "="*60)
    print("Starting worker with advanced features...")
    print("="*60 + "\n")
    
    intelligent_agent.quest_agent.start_worker(
        handler=lambda action: intelligent_agent.handle_action(action)
    )


if __name__ == "__main__":
    main()
