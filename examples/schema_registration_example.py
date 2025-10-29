"""
Example: Schema Registration for External Agents
=================================================

This example shows how to register JSON schemas for your agent's
inputs and outputs, enabling automatic validation.

Benefits:
1. Input validation - Catch errors early
2. Output validation - Ensure consistent responses
3. Contract documentation - Auto-generated docs
4. Version management - Track schema evolution
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from python.quest_agent_sdk import (
    QuestAgentConfig,
    QuestLangChainAgent,
    EvidenceBuilder
)


# ============================================================================
# Define JSON Schemas
# ============================================================================

# Input Schema: What this agent expects to receive
PRICING_INPUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "Pricing Optimization Input",
    "description": "Input parameters for pricing optimization",
    "properties": {
        "current_price": {
            "type": "number",
            "description": "Current product price",
            "minimum": 0
        },
        "cost": {
            "type": "number",
            "description": "Product cost",
            "minimum": 0
        },
        "demand_elasticity": {
            "type": "number",
            "description": "Price elasticity of demand (negative number)",
            "maximum": 0
        },
        "target_margin": {
            "type": "number",
            "description": "Target profit margin (0-1)",
            "minimum": 0,
            "maximum": 1
        }
    },
    "required": ["current_price", "cost", "demand_elasticity", "target_margin"],
    "additionalProperties": false
}

# Output Schema: What this agent promises to return
PRICING_OUTPUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "Pricing Optimization Output",
    "description": "Evidence object from pricing optimization",
    "properties": {
        "claim": {
            "type": "object",
            "properties": {
                "answer": {"type": "string"},
                "structured": {
                    "type": "object",
                    "properties": {
                        "recommended_price": {"type": "number"},
                        "current_price": {"type": "number"},
                        "price_change_pct": {"type": "number"},
                        "expected_demand_change_pct": {"type": "number"},
                        "margin": {"type": "number"}
                    },
                    "required": ["recommended_price", "margin"]
                }
            },
            "required": ["answer", "structured"]
        },
        "support": {"type": "array"},
        "method": {"type": "object"},
        "uncertainty": {"type": "object"},
        "metrics": {"type": "object"},
        "rights": {"type": "object"},
        "signature": {"type": "object"}
    },
    "required": ["claim", "support", "method", "uncertainty", "metrics", "rights", "signature"]
}


# ============================================================================
# Algorithm Implementation
# ============================================================================

def optimize_price(current_price: float, cost: float, elasticity: float, target_margin: float) -> dict:
    """Pricing optimization algorithm"""
    min_price = cost * (1 + target_margin)
    optimal_markup = 1 / (1 + abs(elasticity))
    optimal_price = cost * (1 + optimal_markup)
    recommended_price = max(min_price, optimal_price)
    
    price_change_pct = ((recommended_price - current_price) / current_price) * 100
    demand_change_pct = price_change_pct * elasticity
    
    return {
        "recommended_price": round(recommended_price, 2),
        "current_price": current_price,
        "price_change_pct": round(price_change_pct, 2),
        "expected_demand_change_pct": round(demand_change_pct, 2),
        "margin": round(((recommended_price - cost) / recommended_price) * 100, 2),
        "reasoning": f"Optimal price balances {target_margin*100}% target margin and {elasticity} elasticity"
    }


# ============================================================================
# Action Handler with Validation
# ============================================================================

def handle_action(action: dict, agent: QuestLangChainAgent) -> dict:
    """
    Handle pricing optimization with input/output validation
    """
    action_id = action.get("id")
    inputs = action.get("inputs", {})
    
    print(f"\n🔵 Executing action: {action_id}")
    
    # Validate inputs against schema
    print("📋 Validating inputs...")
    if not agent.validate_input(action):
        print("❌ Input validation failed!")
        return EvidenceBuilder.create_evidence(
            answer="Input validation failed",
            structured_data={"error": "Invalid inputs"},
            agent_id=agent.config.agent_id,
            confidence=0.0
        )
    
    print("✅ Inputs valid")
    
    try:
        # Execute algorithm
        result = optimize_price(
            current_price=inputs["current_price"],
            cost=inputs["cost"],
            elasticity=inputs["demand_elasticity"],
            target_margin=inputs["target_margin"]
        )
        
        # Create evidence
        evidence = EvidenceBuilder.create_evidence(
            answer=result["reasoning"],
            structured_data=result,
            support=[{
                "type": "calculation",
                "text": "Pricing optimization algorithm v1.0"
            }],
            workflow="pricing-optimizer",
            tools_used=["elasticity_model"],
            agent_id=agent.config.agent_id,
            confidence=0.95
        )
        
        # Validate outputs against schema
        print("📋 Validating outputs...")
        if not agent.validate_output(evidence):
            print("⚠️ Output validation failed! (returning anyway)")
        else:
            print("✅ Outputs valid")
        
        return evidence
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return EvidenceBuilder.create_evidence(
            answer=f"Error: {str(e)}",
            structured_data={"error": str(e)},
            agent_id=agent.config.agent_id,
            confidence=0.0
        )


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    
    # Configure agent
    config = QuestAgentConfig(
        agent_name="Pricing Optimizer Agent",
        agent_version="1.0.0",
        redis_host="localhost",
        redis_port=6379,
        api_url="http://localhost:3000"
    )
    
    # Create agent
    quest_agent = QuestLangChainAgent(config)
    
    # Register agent WITH schemas
    print("\n" + "="*60)
    print("Registering Agent with Schemas")
    print("="*60 + "\n")
    
    quest_agent.register(
        capabilities=["pricing_optimization"],
        intents=["optimize_price"],
        description="Pricing optimization agent with schema validation",
        tools=["elasticity_model", "margin_calculator"],
        input_schema=PRICING_INPUT_SCHEMA,      # ← Input schema
        output_schema=PRICING_OUTPUT_SCHEMA     # ← Output schema
    )
    
    print("\n" + "="*60)
    print("Schema Registration Complete!")
    print("="*60)
    print("\n✅ Input schema: pricing-optimizer-agent-input/1.0.0")
    print("✅ Output schema: pricing-optimizer-agent-output/1.0.0")
    print("\nAll requests will be validated against these schemas.")
    print("="*60 + "\n")
    
    # Start worker with validation
    quest_agent.start_worker(handler=lambda action: handle_action(action, quest_agent))


if __name__ == "__main__":
    main()
