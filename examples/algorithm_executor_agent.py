"""
Example: Algorithm Executor Agent
==================================

This example shows how an agent builder with hard-coded algorithms can:
1. Wrap their algorithms in the Quest Agent SDK
2. Execute algorithms based on action requests
3. Return structured evidence

This pattern works for:
- Optimization algorithms (pricing, inventory, budgets)
- Forecasting algorithms (demand, revenue)
- Statistical models
- Custom business logic

Integration Pattern: Redis Streams (Event-Driven)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from python.quest_agent_sdk import (
    QuestAgentConfig,
    QuestLangChainAgent,
    EvidenceBuilder
)
import time
import numpy as np
from typing import Dict, List


# ============================================================================
# Example Algorithms (Replace with your actual algorithms)
# ============================================================================

class PricingOptimizer:
    """Example pricing optimization algorithm"""
    
    def optimize_price(
        self,
        current_price: float,
        cost: float,
        demand_elasticity: float,
        target_margin: float
    ) -> Dict:
        """
        Optimize price based on elasticity and margin targets
        
        This is a simplified example - replace with your actual algorithm
        """
        # Ensure minimum margin
        min_price = cost * (1 + target_margin)
        
        # Calculate optimal price using elasticity
        # Price elasticity of demand: % change in quantity / % change in price
        # Optimal markup = 1 / (1 + elasticity)
        optimal_markup = 1 / (1 + abs(demand_elasticity))
        optimal_price = cost * (1 + optimal_markup)
        
        # Apply constraints
        recommended_price = max(min_price, optimal_price)
        
        # Calculate expected impact
        price_change_pct = ((recommended_price - current_price) / current_price) * 100
        demand_change_pct = price_change_pct * demand_elasticity
        
        return {
            "recommended_price": round(recommended_price, 2),
            "current_price": current_price,
            "price_change_pct": round(price_change_pct, 2),
            "expected_demand_change_pct": round(demand_change_pct, 2),
            "margin": round(((recommended_price - cost) / recommended_price) * 100, 2),
            "reasoning": f"Optimal price balances margin ({target_margin*100}% target) and demand elasticity ({demand_elasticity})"
        }


class InventoryOptimizer:
    """Example inventory optimization algorithm"""
    
    def optimize_inventory(
        self,
        current_stock: int,
        daily_demand: float,
        lead_time_days: int,
        service_level: float = 0.95
    ) -> Dict:
        """
        Calculate optimal reorder point and quantity
        
        This is a simplified example - replace with your actual algorithm
        """
        # Safety stock calculation (assuming normal distribution)
        # Z-score for service level
        z_scores = {0.90: 1.28, 0.95: 1.65, 0.99: 2.33}
        z = z_scores.get(service_level, 1.65)
        
        # Assume demand variance is 20% of mean
        demand_std = daily_demand * 0.2
        
        # Safety stock
        safety_stock = z * demand_std * np.sqrt(lead_time_days)
        
        # Reorder point
        reorder_point = (daily_demand * lead_time_days) + safety_stock
        
        # Economic order quantity (simplified)
        annual_demand = daily_demand * 365
        eoq = np.sqrt((2 * annual_demand * 100) / 1)  # Simplified EOQ
        
        # Current status
        days_of_stock = current_stock / daily_demand if daily_demand > 0 else 999
        needs_reorder = current_stock <= reorder_point
        
        return {
            "current_stock": current_stock,
            "reorder_point": round(reorder_point, 0),
            "safety_stock": round(safety_stock, 0),
            "recommended_order_quantity": round(eoq, 0),
            "days_of_stock_remaining": round(days_of_stock, 1),
            "needs_reorder": needs_reorder,
            "service_level": service_level,
            "reasoning": f"ROP ensures {service_level*100}% service level with {lead_time_days}-day lead time"
        }


# ============================================================================
# Action Handler
# ============================================================================

def handle_action(action: dict) -> dict:
    """
    Handle incoming action requests and execute algorithms
    
    Args:
        action: Action dictionary with type, id, and inputs
    
    Returns:
        Evidence object with algorithm results
    """
    action_id = action.get("id")
    action_type = action.get("type")
    inputs = action.get("inputs", {})
    
    print(f"\n🔵 Executing action: {action_id} ({action_type})")
    print(f"   Inputs: {inputs}")
    
    start_time = time.time()
    
    try:
        # Route to appropriate algorithm
        if action_type == "optimization.pricing":
            optimizer = PricingOptimizer()
            result = optimizer.optimize_price(
                current_price=inputs.get("current_price", 100.0),
                cost=inputs.get("cost", 60.0),
                demand_elasticity=inputs.get("demand_elasticity", -1.5),
                target_margin=inputs.get("target_margin", 0.25)
            )
            
            algorithm_name = "pricing_optimizer_v1"
            tools_used = ["elasticity_model", "margin_constraints"]
        
        elif action_type == "optimization.inventory":
            optimizer = InventoryOptimizer()
            result = optimizer.optimize_inventory(
                current_stock=inputs.get("current_stock", 100),
                daily_demand=inputs.get("daily_demand", 10.0),
                lead_time_days=inputs.get("lead_time_days", 7),
                service_level=inputs.get("service_level", 0.95)
            )
            
            algorithm_name = "inventory_optimizer_v1"
            tools_used = ["eoq_model", "safety_stock_calculator"]
        
        else:
            raise ValueError(f"Unsupported action type: {action_type}")
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Create evidence object
        evidence = EvidenceBuilder.create_evidence(
            answer=result.get("reasoning", "Algorithm executed successfully"),
            structured_data=result,
            support=[{
                "type": "calculation",
                "text": f"Algorithm: {algorithm_name}",
                "data_ref": f"action_{action_id}"
            }],
            workflow=f"algorithm-executor:{algorithm_name}",
            tools_used=tools_used,
            agent_id="algorithm-executor-agent",
            agent_version="1.0.0",
            confidence=0.92,  # High confidence for algorithmic results
            latency_ms=latency_ms
        )
        
        print(f"✅ Algorithm completed in {latency_ms}ms")
        return evidence
    
    except Exception as e:
        print(f"❌ Error executing algorithm: {e}")
        
        # Return error evidence
        return EvidenceBuilder.create_evidence(
            answer=f"Algorithm execution failed: {str(e)}",
            structured_data={"error": str(e), "action_id": action_id},
            support=[],
            workflow="algorithm-executor:error",
            tools_used=[],
            agent_id="algorithm-executor-agent",
            confidence=0.0
        )


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    
    # Configure agent
    config = QuestAgentConfig(
        agent_name="Algorithm Executor Agent",
        agent_version="1.0.0",
        redis_host="localhost",
        redis_port=6379,
        api_url="http://localhost:3000"
    )
    
    # Create Quest agent wrapper
    quest_agent = QuestLangChainAgent(config)
    
    # Register with the system
    quest_agent.register(
        capabilities=[
            "pricing_optimization",
            "inventory_optimization",
            "algorithm_execution"
        ],
        intents=[
            "optimize_price",
            "optimize_inventory",
            "calculate_reorder"
        ],
        description="Hard-coded algorithm executor for pricing and inventory optimization",
        tools=[
            "pricing_optimizer",
            "inventory_optimizer",
            "elasticity_model",
            "eoq_calculator"
        ]
    )
    
    print("\n" + "="*60)
    print("Algorithm Executor Agent Ready")
    print("="*60)
    print(f"Agent ID: {config.agent_id}")
    print(f"Agent Name: {config.agent_name}")
    print(f"Capabilities:")
    print("  - pricing_optimization")
    print("  - inventory_optimization")
    print("  - algorithm_execution")
    print("\nSupported Action Types:")
    print("  - optimization.pricing")
    print("  - optimization.inventory")
    print("="*60 + "\n")
    
    # Start worker loop (event-driven)
    quest_agent.start_worker(handler=handle_action)


if __name__ == "__main__":
    main()
