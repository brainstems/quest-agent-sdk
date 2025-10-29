"""
Ontology and Knowledge Graph Integration
==========================================

Provides external agents with access to Quest's semantic layer:
1. Ontology (SKOS) - Concept resolution and expansion
2. Knowledge Graph - Entity navigation and relationships
3. SHACL Validation - Semantic constraints
4. Agent Discovery - Find capable agents by concepts
5. Template Integration - Work with ACT-R templates

This enables semantic interoperability between external and internal agents.
"""

import requests
from typing import List, Dict, Optional, Any


class OntologyClient:
    """Client for Quest Ontology Service"""
    
    def __init__(self, api_url: str = "http://localhost:3000"):
        self.api_url = api_url
        self.base = f"{api_url}/api/ontology"
    
    def resolve(self, term: str) -> Optional[str]:
        """
        Resolve a term/label to its canonical URI
        
        Example:
            uri = ontology.resolve("pricing")
            # Returns: "ex:Pricing"
        """
        response = requests.get(f"{self.base}/resolve/{requests.utils.quote(term)}")
        if response.status_code == 200:
            return response.json().get("uri")
        return None
    
    def expand(
        self,
        concepts: List[str],
        relations: List[str] = None,
        depth: int = 1
    ) -> List[str]:
        """
        Expand concepts using SKOS relations
        
        Args:
            concepts: List of concept URIs
            relations: Types of relations ['broader', 'narrower', 'related', 'synonym']
            depth: How many hops to traverse
        
        Returns:
            Expanded list of concept URIs
        
        Example:
            expanded = ontology.expand(
                ["ex:Pricing"],
                relations=["broader", "related"],
                depth=1
            )
            # Returns: ["ex:Pricing", "ex:Revenue", "ex:Markdown", ...]
        """
        if relations is None:
            relations = ["broader", "narrower", "related"]
        
        response = requests.post(f"{self.base}/expand", json={
            "concepts": concepts,
            "relations": relations,
            "depth": depth
        })
        
        if response.status_code == 200:
            return response.json().get("expanded", [])
        return []
    
    def same_as(self, entity_uri: str, system: str) -> Optional[str]:
        """
        Get external ID for an entity in a different system
        
        Example:
            external_id = ontology.same_as("ent:product_123", "shopify")
            # Returns: "shopify:prod_xyz"
        """
        response = requests.get(
            f"{self.base}/same-as/{requests.utils.quote(entity_uri)}/{system}"
        )
        if response.status_code == 200:
            return response.json().get("externalId")
        return None
    
    def get_constraints(self, concept_uri: str) -> List[Dict]:
        """
        Get business constraints for a concept/category
        
        Example:
            constraints = ontology.get_constraints("cat:Beverages")
            # Returns: [{"constraint_type": "minMarginPct", "constraint_value": 0.15, ...}]
        """
        response = requests.get(
            f"{self.base}/constraints/{requests.utils.quote(concept_uri)}"
        )
        if response.status_code == 200:
            return response.json()
        return []
    
    def get_shape(self, shape_uri: str) -> Optional[Dict]:
        """
        Get SHACL shape definition
        
        Example:
            shape = ontology.get_shape("shape:PriceEvent")
            # Returns: SHACL shape definition
        """
        response = requests.get(f"{self.base}/shape/{requests.utils.quote(shape_uri)}")
        if response.status_code == 200:
            return response.json()
        return None
    
    def validate_shacl(
        self,
        data: Dict,
        shape_uri: str,
        category_uri: Optional[str] = None
    ) -> Dict:
        """
        Validate data against SHACL shape
        
        Args:
            data: Data to validate
            shape_uri: SHACL shape URI
            category_uri: Optional category for additional constraints
        
        Returns:
            {
                "conforms": bool,
                "violations": [...],
                "warnings": [...]
            }
        
        Example:
            result = ontology.validate_shacl(
                data={"price": 9.99, "marginPct": 0.10},
                shape_uri="shape:PriceEvent",
                category_uri="cat:Beverages"
            )
            if not result["conforms"]:
                print("Violations:", result["violations"])
        """
        payload = {
            "data": data,
            "shape_uri": shape_uri
        }
        if category_uri:
            payload["category_uri"] = category_uri
        
        response = requests.post(f"{self.base}/validate-shacl", json=payload)
        if response.status_code == 200:
            return response.json()
        return {"conforms": False, "violations": ["Validation request failed"]}


class KnowledgeGraphClient:
    """Client for Quest Knowledge Graph"""
    
    def __init__(self, api_url: str = "http://localhost:3000"):
        self.api_url = api_url
        # Knowledge graph typically accessed via GraphQL or custom API
        # For now, using REST endpoints
    
    def get_entity(self, entity_id: str) -> Optional[Dict]:
        """Get entity by ID"""
        # Implementation depends on your KG API
        # This is a placeholder
        response = requests.get(f"{self.api_url}/api/kg/entity/{entity_id}")
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_related(self, entity_id: str, relationship_type: Optional[str] = None) -> List[Dict]:
        """Get related entities"""
        params = {}
        if relationship_type:
            params["type"] = relationship_type
        
        response = requests.get(
            f"{self.api_url}/api/kg/entity/{entity_id}/related",
            params=params
        )
        if response.status_code == 200:
            return response.json()
        return []
    
    def find_path(self, source_id: str, target_id: str, max_depth: int = 3) -> Optional[List[Dict]]:
        """Find shortest path between entities"""
        response = requests.get(
            f"{self.api_url}/api/kg/path",
            params={"source": source_id, "target": target_id, "max_depth": max_depth}
        )
        if response.status_code == 200:
            return response.json().get("path")
        return None


class AgentDiscoveryClient:
    """Client for semantic agent discovery"""
    
    def __init__(self, api_url: str = "http://localhost:3000"):
        self.api_url = api_url
    
    def discover_by_capability(self, capability: str) -> List[Dict]:
        """
        Discover agents by capability
        
        Example:
            agents = discovery.discover_by_capability("pricing_optimization")
        """
        response = requests.get(
            f"{self.api_url}/api/agents",
            params={"capability": capability}
        )
        if response.status_code == 200:
            return response.json().get("agents", [])
        return []
    
    def discover_by_concepts(self, concepts: List[str], ontology: Optional[OntologyClient] = None) -> List[Dict]:
        """
        Discover agents by ontology concepts (with expansion)
        
        This is semantic discovery - finds agents that match:
        1. Exact concept matches
        2. Broader/narrower concepts
        3. Related concepts
        
        Example:
            # Find all agents that can handle pricing (including markdowns, discounts, etc.)
            agents = discovery.discover_by_concepts(["ex:Pricing"])
        """
        # Expand concepts using ontology
        expanded_concepts = concepts
        if ontology:
            expanded_concepts = ontology.expand(concepts, depth=1)
        
        # Find agents interested in these concepts
        all_agents = []
        for concept in expanded_concepts:
            # This would query agent_ontology_profiles table
            # For now, using capability search as fallback
            response = requests.get(
                f"{self.api_url}/api/agents/by-concept/{requests.utils.quote(concept)}"
            )
            if response.status_code == 200:
                all_agents.extend(response.json().get("agents", []))
        
        # Deduplicate
        seen = set()
        unique_agents = []
        for agent in all_agents:
            if agent["name"] not in seen:
                seen.add(agent["name"])
                unique_agents.append(agent)
        
        return unique_agents
    
    def discover_by_semantic_search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Discover agents by natural language query
        
        Example:
            agents = discovery.discover_by_semantic_search(
                "agents that can optimize pricing and inventory together",
                limit=5
            )
        """
        response = requests.get(
            f"{self.api_url}/api/agents",
            params={"q": query, "limit": limit}
        )
        if response.status_code == 200:
            return response.json().get("agents", [])
        return []
    
    def bid_for_task(
        self,
        task: Dict,
        my_capabilities: List[str],
        my_confidence: float
    ) -> Dict:
        """
        Submit a bid for a task (agent marketplace pattern)
        
        Args:
            task: Task specification with required capabilities
            my_capabilities: Your agent's capabilities
            my_confidence: Your confidence level (0-1)
        
        Returns:
            Bid acceptance/rejection
        
        Example:
            bid = discovery.bid_for_task(
                task={"required_capabilities": ["pricing_optimization"]},
                my_capabilities=["pricing_optimization", "elasticity_modeling"],
                my_confidence=0.92
            )
        """
        # Calculate capability match
        required = set(task.get("required_capabilities", []))
        provided = set(my_capabilities)
        match_score = len(required & provided) / len(required) if required else 0
        
        # Submit bid
        response = requests.post(f"{self.api_url}/api/agents/bid", json={
            "task_id": task.get("id"),
            "agent_capabilities": my_capabilities,
            "confidence": my_confidence,
            "match_score": match_score,
            "bid_amount": 0.0  # Could be cost-based bidding
        })
        
        if response.status_code == 200:
            return response.json()
        return {"accepted": False, "reason": "Bid submission failed"}


class TemplateIntegration:
    """Integration with ACT-R templates for agent orchestration"""
    
    def __init__(self, api_url: str = "http://localhost:3000"):
        self.api_url = api_url
    
    def get_templates_for_intent(self, intent: str) -> List[Dict]:
        """
        Get ACT-R templates matching an intent
        
        Example:
            templates = template.get_templates_for_intent("optimize_pricing")
        """
        response = requests.get(
            f"{self.api_url}/api/templates",
            params={"intent": intent}
        )
        if response.status_code == 200:
            return response.json().get("templates", [])
        return []
    
    def execute_template(
        self,
        template_id: str,
        context: Dict,
        user_id: str
    ) -> Dict:
        """
        Execute a template (triggers agent orchestration)
        
        Example:
            result = template.execute_template(
                template_id="pricing-optimization",
                context={"product_id": "123", "current_price": 99.99},
                user_id="user_456"
            )
        """
        response = requests.post(f"{self.api_url}/api/templates/execute", json={
            "template_id": template_id,
            "context": context,
            "user_id": user_id
        })
        if response.status_code == 200:
            return response.json()
        return {"success": False, "error": "Template execution failed"}
    
    def register_agent_for_template(
        self,
        agent_name: str,
        template_ids: List[str],
        capabilities: List[str]
    ) -> Dict:
        """
        Register your agent to be discovered by templates
        
        Example:
            template.register_agent_for_template(
                agent_name="My Pricing Agent",
                template_ids=["pricing-optimization", "markdown-planning"],
                capabilities=["pricing_optimization", "elasticity_modeling"]
            )
        """
        response = requests.post(f"{self.api_url}/api/agents/template-registration", json={
            "agent_name": agent_name,
            "template_ids": template_ids,
            "capabilities": capabilities
        })
        if response.status_code == 200:
            return response.json()
        return {"success": False}


# ============================================================================
# Helper Functions
# ============================================================================

def enrich_action_with_ontology(action: Dict, ontology: OntologyClient) -> Dict:
    """
    Enrich an action with ontology concepts
    
    Example:
        action = {
            "type": "pricing",
            "inputs": {"product": "beverage_cola"}
        }
        enriched = enrich_action_with_ontology(action, ontology)
        # Adds: enriched["@context"] = ["ex:Pricing", "cat:Beverages", ...]
    """
    enriched = action.copy()
    
    # Resolve action type to concept
    action_type = action.get("type", "")
    concept_uri = ontology.resolve(action_type)
    
    if concept_uri:
        # Expand to get related concepts
        expanded = ontology.expand([concept_uri], depth=1)
        enriched["@context"] = expanded
    
    # Resolve product category if present
    product = action.get("inputs", {}).get("product", "")
    if product:
        category_uri = ontology.resolve(product)
        if category_uri:
            enriched["inputs"]["@category"] = category_uri
            # Get business constraints for this category
            constraints = ontology.get_constraints(category_uri)
            enriched["inputs"]["@constraints"] = constraints
    
    return enriched


def validate_output_with_ontology(
    output: Dict,
    expected_shape: str,
    ontology: OntologyClient
) -> Dict:
    """
    Validate output against SHACL shape
    
    Example:
        result = validate_output_with_ontology(
            output={"price": 9.99, "marginPct": 0.10},
            expected_shape="shape:PriceEvent",
            ontology=ontology
        )
    """
    return ontology.validate_shacl(
        data=output,
        shape_uri=expected_shape,
        category_uri=output.get("@category")
    )
