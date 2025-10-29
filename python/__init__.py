"""
Quest Agent SDK - Python Module

External agent integration SDK for Quest Agent Forge.

Basic usage:
    from python.quest_agent_sdk import QuestAgentConfig, QuestLangChainAgent
    
    config = QuestAgentConfig(agent_name="My Agent")
    agent = QuestLangChainAgent(config)
    agent.register(capabilities=["test"])
    agent.start_worker(handler=my_handler)

Advanced usage:
    from python.ontology_integration import OntologyClient, AgentDiscoveryClient
    
    ontology = OntologyClient()
    discovery = AgentDiscoveryClient()
"""

__version__ = "1.0.0"
__all__ = ["quest_agent_sdk", "ontology_integration"]
