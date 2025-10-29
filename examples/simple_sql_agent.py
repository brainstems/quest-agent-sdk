"""
Example: Simple SQL Analysis Agent
===================================

This example shows how to integrate a LangChain SQL agent that:
1. Connects to a database
2. Executes SQL queries from action requests
3. Returns verifiable evidence

Integration Pattern: Redis Streams (Event-Driven)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from python.quest_agent_sdk import (
    QuestAgentConfig,
    QuestLangChainAgent,
    create_sql_evidence
)

# LangChain imports (install: pip install langchain langchain-community sqlalchemy)
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
import time


# ============================================================================
# Database Setup (replace with your actual database)
# ============================================================================

def setup_database():
    """Setup database connection - replace with your actual DB"""
    # Example: SQLite
    db = SQLDatabase.from_uri("sqlite:///./example.db")
    
    # Example: PostgreSQL
    # db = SQLDatabase.from_uri(
    #     "postgresql://user:password@localhost:5432/dbname"
    # )
    
    return db


# ============================================================================
# LangChain SQL Agent
# ============================================================================

class SQLAnalysisAgent:
    """LangChain SQL agent for database queries"""
    
    def __init__(self):
        self.db = setup_database()
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.query_chain = create_sql_query_chain(self.llm, self.db)
    
    def execute_query(self, natural_language_query: str) -> dict:
        """Execute natural language query against database"""
        start_time = time.time()
        
        # Generate SQL from natural language
        sql_query = self.query_chain.invoke({"question": natural_language_query})
        
        # Execute query
        result = self.db.run(sql_query)
        
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        return {
            "query": sql_query,
            "result": result,
            "execution_time_ms": execution_time_ms
        }


# ============================================================================
# Action Handler
# ============================================================================

def handle_action(action: dict) -> dict:
    """
    Handle incoming action requests
    
    Args:
        action: Action dictionary with type, id, and inputs
    
    Returns:
        Evidence object with results
    """
    action_id = action.get("id")
    action_type = action.get("type")
    inputs = action.get("inputs", {})
    
    print(f"\n🔵 Executing action: {action_id} ({action_type})")
    
    # Initialize SQL agent
    sql_agent = SQLAnalysisAgent()
    
    try:
        if action_type == "analysis.sql.query":
            # Extract query from inputs
            query = inputs.get("query", inputs.get("question", ""))
            
            if not query:
                raise ValueError("No query provided in inputs")
            
            # Execute query
            result = sql_agent.execute_query(query)
            
            # Parse result (assume it's a list of rows)
            # Adjust based on your actual result format
            try:
                rows = eval(result["result"]) if isinstance(result["result"], str) else result["result"]
                row_count = len(rows) if isinstance(rows, list) else 1
                
                # Convert to structured format
                structured_data = {
                    "rows": rows[:10] if isinstance(rows, list) else rows,  # Limit to first 10
                    "total_count": row_count,
                    "sql_query": result["query"]
                }
            except:
                # Fallback if result parsing fails
                row_count = 1
                structured_data = {
                    "result": str(result["result"]),
                    "sql_query": result["query"]
                }
            
            # Create evidence object
            evidence = create_sql_evidence(
                query=result["query"],
                result_data=structured_data,
                row_count=row_count,
                execution_time_ms=result["execution_time_ms"],
                agent_id="langchain-sql-agent",
                confidence=0.95  # High confidence for SQL queries
            )
            
            return evidence
        
        else:
            raise ValueError(f"Unsupported action type: {action_type}")
    
    except Exception as e:
        print(f"❌ Error executing action: {e}")
        # Return error evidence
        return {
            "claim": {
                "answer": f"Error: {str(e)}",
                "structured": {"error": str(e), "action_id": action_id}
            },
            "support": [],
            "method": {
                "workflow": "langchain-sql-agent",
                "tools_used": ["database.query"]
            },
            "uncertainty": {
                "self": 1.0  # Complete uncertainty due to error
            },
            "metrics": {
                "latency_ms": 0
            },
            "rights": {
                "redistribute": True
            },
            "signature": {
                "agent_id": "langchain-sql-agent",
                "version": "1.0.0"
            }
        }


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    
    # Configure agent
    config = QuestAgentConfig(
        agent_name="SQL Analysis Agent",
        agent_version="1.0.0",
        redis_host="localhost",
        redis_port=6379,
        api_url="http://localhost:3000"
    )
    
    # Create Quest agent wrapper
    quest_agent = QuestLangChainAgent(config)
    
    # Register with the system
    quest_agent.register(
        capabilities=["sql_analysis", "database_query", "analytics"],
        intents=["analyze_data", "query_database"],
        description="LangChain SQL agent for natural language database queries",
        tools=["sql_database", "langchain_sql_chain"]
    )
    
    print("\n" + "="*60)
    print("SQL Analysis Agent Ready")
    print("="*60)
    print(f"Agent ID: {config.agent_id}")
    print(f"Agent Name: {config.agent_name}")
    print(f"Capabilities: sql_analysis, database_query, analytics")
    print("="*60 + "\n")
    
    # Start worker loop (event-driven)
    quest_agent.start_worker(handler=handle_action)


if __name__ == "__main__":
    main()
