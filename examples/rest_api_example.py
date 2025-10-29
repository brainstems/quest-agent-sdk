"""
Example: REST API Integration (Synchronous)
============================================

This example shows how to integrate using REST API instead of Redis Streams.
Good for:
- Synchronous request-response patterns
- Simpler integration without Redis
- Calling other agents from your code

NOT recommended for:
- Production event-driven systems (use Redis Streams)
- High-throughput scenarios
- Async agent workflows
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from python.quest_agent_sdk import QuestAgentConfig, QuestLangChainAgent


# ============================================================================
# Example: Calling Other Agents via REST API
# ============================================================================

def example_call_other_agents():
    """Example of calling other agents in the system"""
    
    # Configure SDK
    config = QuestAgentConfig(
        agent_name="Orchestrator Agent",
        api_url="http://localhost:3000"
    )
    
    quest_agent = QuestLangChainAgent(config)
    
    print("="*60)
    print("Example: Calling Other Agents via REST API")
    print("="*60 + "\n")
    
    # 1. Discover available agents
    print("1️⃣ Discovering agents with 'sql_analysis' capability...")
    agents = quest_agent.discover_agents(capability="sql_analysis")
    print(f"   Found {len(agents)} agents:")
    for agent in agents:
        print(f"   - {agent.get('name')} (capabilities: {agent.get('capabilities', [])})")
    print()
    
    # 2. Call a specific agent
    if agents:
        agent_name = agents[0].get("name")
        print(f"2️⃣ Calling agent: {agent_name}")
        
        try:
            result = quest_agent.call_agent(
                agent_name=agent_name,
                capability="sql_analysis",
                parameters={
                    "query": "What were the top 5 products by revenue last month?",
                    "database": "analytics_db"
                },
                context={
                    "user_id": "user_123",
                    "conversation_id": "conv_456"
                }
            )
            
            print(f"   Result: {result}")
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n" + "="*60)


# ============================================================================
# Example: Register and Wait for HTTP Calls
# ============================================================================

def example_http_endpoint_style():
    """
    Example of registering an agent and handling calls via REST
    
    Note: This is NOT the recommended approach for production.
    Use Redis Streams for event-driven, scalable integration.
    """
    
    config = QuestAgentConfig(
        agent_name="HTTP Style Agent",
        api_url="http://localhost:3000"
    )
    
    quest_agent = QuestLangChainAgent(config)
    
    # Register agent
    quest_agent.register(
        capabilities=["custom_analysis"],
        description="Agent that handles REST API calls"
    )
    
    print("\n" + "="*60)
    print("Agent registered!")
    print("="*60)
    print("\nTo call this agent via REST API:")
    print(f"""
    curl -X POST http://localhost:3000/api/agents/execute \\
      -H "Content-Type: application/json" \\
      -d '{{
        "agentName": "{config.agent_name}",
        "capability": "custom_analysis",
        "parameters": {{
          "query": "your query here"
        }}
      }}'
    """)
    
    print("\nNote: For production, use Redis Streams integration instead!")
    print("="*60 + "\n")


# ============================================================================
# Example: Agent-to-Agent Communication
# ============================================================================

def example_agent_to_agent():
    """
    Example showing how one agent can call another
    (useful for agent orchestration and delegation)
    """
    
    config = QuestAgentConfig(
        agent_name="Orchestrator",
        api_url="http://localhost:3000"
    )
    
    quest_agent = QuestLangChainAgent(config)
    
    print("="*60)
    print("Example: Agent-to-Agent Communication")
    print("="*60 + "\n")
    
    # Scenario: Orchestrator agent delegates to specialists
    
    # Step 1: Call SQL agent to get data
    print("1️⃣ Orchestrator → SQL Agent: Get sales data")
    try:
        sql_result = quest_agent.call_agent(
            agent_name="SQL Analysis Agent",
            capability="sql_analysis",
            parameters={"query": "SELECT product_id, SUM(revenue) FROM sales GROUP BY product_id"}
        )
        print(f"   SQL Result: {sql_result.get('result', {}).get('data', 'No data')}")
    except Exception as e:
        print(f"   SQL Agent not available: {e}")
        sql_result = None
    
    # Step 2: Call RAG agent to get context
    print("\n2️⃣ Orchestrator → RAG Agent: Get product insights")
    try:
        rag_result = quest_agent.call_agent(
            agent_name="RAG Analysis Agent",
            capability="rag_analysis",
            parameters={"query": "What are the key features of our top products?"}
        )
        print(f"   RAG Result: {rag_result.get('result', {}).get('data', 'No data')}")
    except Exception as e:
        print(f"   RAG Agent not available: {e}")
        rag_result = None
    
    # Step 3: Combine results
    print("\n3️⃣ Orchestrator: Combining results...")
    combined_insight = {
        "sales_data": sql_result.get("result") if sql_result else None,
        "product_insights": rag_result.get("result") if rag_result else None,
        "recommendation": "Based on sales and product features, recommend focusing on top 3 products"
    }
    print(f"   Combined Insight: {combined_insight}")
    
    print("\n" + "="*60)


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Run REST API examples"""
    
    print("\n" + "🚀 "*20)
    print("Quest Agent SDK - REST API Examples")
    print("🚀 "*20 + "\n")
    
    # Example 1: Discover and call agents
    example_call_other_agents()
    
    print("\n" + "-"*60 + "\n")
    
    # Example 2: Agent-to-agent communication
    example_agent_to_agent()
    
    print("\n" + "-"*60 + "\n")
    
    # Example 3: HTTP endpoint style
    example_http_endpoint_style()


if __name__ == "__main__":
    main()
