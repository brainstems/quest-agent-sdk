"""
Example: RAG (Retrieval-Augmented Generation) Analysis Agent
=============================================================

This example shows how to integrate a LangChain RAG agent that:
1. Loads documents into a vector store
2. Performs semantic search
3. Generates analysis with citations

Integration Pattern: Redis Streams (Event-Driven)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from python.quest_agent_sdk import (
    QuestAgentConfig,
    QuestLangChainAgent,
    create_llm_evidence
)

# LangChain imports
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.chains import RetrievalQA
import time


# ============================================================================
# RAG Agent Setup
# ============================================================================

class RAGAnalysisAgent:
    """LangChain RAG agent for document analysis"""
    
    def __init__(self, documents_path: str = "./documents"):
        """Initialize RAG agent with document path"""
        self.documents_path = documents_path
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.7)
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None
        self.qa_chain = None
        
        # Load documents
        self._load_documents()
    
    def _load_documents(self):
        """Load documents into vector store"""
        print(f"📂 Loading documents from {self.documents_path}...")
        
        try:
            # Load documents
            loader = DirectoryLoader(
                self.documents_path,
                glob="**/*.txt",
                loader_cls=TextLoader
            )
            documents = loader.load()
            
            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(documents)
            
            print(f"📄 Loaded {len(documents)} documents, split into {len(splits)} chunks")
            
            # Create vector store
            self.vector_store = FAISS.from_documents(splits, self.embeddings)
            
            # Create QA chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )
            
            print("✅ Vector store initialized")
        
        except Exception as e:
            print(f"⚠️ Error loading documents: {e}")
            print("   Agent will run but may have limited capabilities")
    
    def analyze(self, query: str) -> dict:
        """Perform RAG analysis on query"""
        if not self.qa_chain:
            raise ValueError("Vector store not initialized. No documents loaded.")
        
        start_time = time.time()
        
        # Run query
        result = self.qa_chain({"query": query})
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Extract sources
        sources = []
        if "source_documents" in result:
            for doc in result["source_documents"]:
                source = doc.metadata.get("source", "unknown")
                sources.append(source)
        
        return {
            "answer": result.get("result", ""),
            "sources": sources,
            "query": query,
            "latency_ms": latency_ms
        }


# ============================================================================
# Action Handler
# ============================================================================

# Global agent instance (initialized once)
rag_agent = None

def handle_action(action: dict) -> dict:
    """
    Handle incoming action requests
    
    Args:
        action: Action dictionary with type, id, and inputs
    
    Returns:
        Evidence object with results
    """
    global rag_agent
    
    # Initialize agent on first request
    if rag_agent is None:
        documents_path = os.environ.get("DOCUMENTS_PATH", "./documents")
        rag_agent = RAGAnalysisAgent(documents_path)
    
    action_id = action.get("id")
    action_type = action.get("type")
    inputs = action.get("inputs", {})
    
    print(f"\n🔵 Executing action: {action_id} ({action_type})")
    
    try:
        if action_type in ["analysis.rag.query", "analysis.document.search", "analysis.semantic.search"]:
            # Extract query from inputs
            query = inputs.get("query", inputs.get("question", ""))
            
            if not query:
                raise ValueError("No query provided in inputs")
            
            # Perform RAG analysis
            result = rag_agent.analyze(query)
            
            # Estimate tokens (rough approximation)
            tokens_in = len(query.split()) * 1.5
            tokens_out = len(result["answer"].split()) * 1.5
            cost_usd = (tokens_in * 0.00003 + tokens_out * 0.00006) / 1000  # GPT-4 pricing
            
            # Create evidence object
            evidence = create_llm_evidence(
                answer=result["answer"],
                prompt=query,
                sources=result["sources"],
                agent_id="langchain-rag-agent",
                tokens_in=int(tokens_in),
                tokens_out=int(tokens_out),
                cost_usd=cost_usd,
                confidence=0.85
            )
            
            # Add execution time
            evidence["metrics"]["latency_ms"] = result["latency_ms"]
            
            return evidence
        
        else:
            raise ValueError(f"Unsupported action type: {action_type}")
    
    except Exception as e:
        print(f"❌ Error executing action: {e}")
        # Return error evidence
        return create_llm_evidence(
            answer=f"Error: {str(e)}",
            prompt=inputs.get("query", ""),
            sources=[],
            agent_id="langchain-rag-agent",
            confidence=0.0
        )


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point"""
    
    # Configure agent
    config = QuestAgentConfig(
        agent_name="RAG Analysis Agent",
        agent_version="1.0.0",
        redis_host="localhost",
        redis_port=6379,
        api_url="http://localhost:3000"
    )
    
    # Create Quest agent wrapper
    quest_agent = QuestLangChainAgent(config)
    
    # Register with the system
    quest_agent.register(
        capabilities=["rag_analysis", "document_search", "semantic_search", "qa"],
        intents=["answer_question", "search_documents", "analyze_content"],
        description="LangChain RAG agent for document analysis and Q&A",
        tools=["vector_store", "langchain_rag", "openai_embeddings"]
    )
    
    print("\n" + "="*60)
    print("RAG Analysis Agent Ready")
    print("="*60)
    print(f"Agent ID: {config.agent_id}")
    print(f"Agent Name: {config.agent_name}")
    print(f"Capabilities: rag_analysis, document_search, semantic_search")
    print(f"Documents Path: {os.environ.get('DOCUMENTS_PATH', './documents')}")
    print("="*60 + "\n")
    
    # Start worker loop (event-driven)
    quest_agent.start_worker(handler=handle_action)


if __name__ == "__main__":
    main()
