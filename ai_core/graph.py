# D:\cognito_ai_assistant\ai_core\graph.py

from typing import TypedDict, Dict, Any, List, Literal, Annotated
from typing_extensions import NotRequired
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
import os

# --- 1. CONFIGURATION AND TYPES ---

# Define all possible expert nodes
EXPERT_OPTIONS = Literal[
    "finance_expert", 
    "legal_expert", 
    "fitness_expert", 
    "business_expert", 
    "health_expert",  
    "general_qa"
]

# --- 2. STATE DEFINITION (TypedDict for LangGraph State) ---

class AgentState(TypedDict):
    """The shared state for the multi-agent graph, ensuring type-safe data flow."""
    
    # Core Communication (History of messages)
    messages: Annotated[List[BaseMessage], add_messages] 

    # Multi-Lingual / Multi-Modal Context
    raw_user_input: str      # The original, unprocessed input
    original_language: str
    cultural_context: str
    original_modality: str   # e.g., 'text', 'image', 'audio'
    modality_metadata: Dict[str, Any] 

    # Routing and Expert Selection
    target_expert: NotRequired[EXPERT_OPTIONS]
    current_model: str 
    
    # Safety and Risk Assessment
    risk_score: float        # Numeric score (0.0 to 1.0)
    risk_assessment_report: str
    
    # Self-Improvement and Reflection
    critique_report: str
    fusion_block: str 
    agent_reputation: Dict[str, float] 
    
    # Audit and Trust
    audit_hash: str
    digital_signature: str
    
# --- 3. HELPER FUNCTIONS (Conditional Edges Logic) ---

def route_to_expert(state: AgentState) -> str:
    """Routes based on the Supervisor/Router's selection."""
    expert = state.get("target_expert", "general_qa")
    # Ensure a valid route, default to general_qa for safety
    if expert not in EXPERT_OPTIONS.__args__:
        return "general_qa"
    return expert

def route_critique_final(state: AgentState) -> str:
    """Routes to Knowledge Fusion on success, or back to revision on failure."""
    critique = state.get("critique_report", "").upper()
    
    if "PERFECT" in critique:
        return "knowledge_fusion" # Success path
    else:
        # Revision path: return to the expert for another attempt
        return state.get("target_expert", "general_qa") 

# --- 4. GRAPH CONSTRUCTION ---

def create_cognito_omega_graph(nodes_map: Dict[str, Any]):
    """Creates and compiles the final Cognito Omega StateGraph."""
    
    workflow = StateGraph(AgentState)

    # Add all nodes 
    for name, func in nodes_map.items():
        workflow.add_node(name, func)
        
    # --- Define Flow ---

    # 1. Entry Point: Multi-Modal Decoder
    workflow.set_entry_point("multi_modal_decoder")
    
    # 2. Initial Flow
    workflow.add_edge("multi_modal_decoder", "mlcc_nlu_agent")
    workflow.add_edge("mlcc_nlu_agent", "emotion_intent_detector")
    workflow.add_edge("emotion_intent_detector", "supervisor")
    workflow.add_edge("supervisor", "universal_model_selector")
    
    # 3. Prioritization Path
    workflow.add_edge("universal_model_selector", "q_value_prioritizer")
    workflow.add_edge("q_value_prioritizer", "cognitive_latency_check")
    
    # 4. Expert Routing (Conditional)
    workflow.add_conditional_edges(
        "cognitive_latency_check",
        route_to_expert,
        {expert: expert for expert in EXPERT_OPTIONS.__args__} 
    )
    
    # 5. Execution Path (Expert -> Tool Manager -> Risk Assessor -> Critique)
    for expert in EXPERT_OPTIONS.__args__:
        workflow.add_edge(expert, "dynamic_tool_manager")

    workflow.add_edge("dynamic_tool_manager", "causal_risk_assessor")
    workflow.add_edge("causal_risk_assessor", "critique_revise")

    # 6. Self-Improvement Loop (Conditional)
    workflow.add_conditional_edges(
        "critique_revise",
        route_critique_final,
        {
            "knowledge_fusion": "knowledge_fusion_node", # Success path
            # All other options route back to the expert for revision
            **{expert: expert for expert in EXPERT_OPTIONS.__args__}
        } 
    )

    # 7. Trust and Final Audit Path
    workflow.add_edge("knowledge_fusion_node", "meta_cognition_node")
    workflow.add_edge("meta_cognition_node", "verifiable_identity_node")
    workflow.add_edge("verifiable_identity_node", "verifiable_audit_node")
    workflow.add_edge("verifiable_audit_node", END)
    
    # Compile the final graph
    app = workflow.compile()
    return app