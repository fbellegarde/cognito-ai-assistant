from ai_core.graph import create_cognito_omega_graph
from ai_core.experts import (
    multi_modal_decoder, mlcc_nlu_agent, emotion_intent_detector, supervisor,
    universal_model_selector, q_value_prioritizer, cognitive_latency_check,
    finance_expert, legal_expert, fitness_expert, business_expert, health_expert, general_qa,
    dynamic_tool_manager, causal_risk_assessor, critique_revise,
    knowledge_fusion_node, meta_cognition_node, verifiable_identity_node, verifiable_audit_node
)
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- 1. Map all nodes for the graph builder ---
NODE_MAP = {
    "multi_modal_decoder": multi_modal_decoder,
    "mlcc_nlu_agent": mlcc_nlu_agent,
    "emotion_intent_detector": emotion_intent_detector,
    "supervisor": supervisor,
    "universal_model_selector": universal_model_selector,
    "q_value_prioritizer": q_value_prioritizer,
    "cognitive_latency_check": cognitive_latency_check,
    "finance_expert": finance_expert,
    "legal_expert": legal_expert,
    "fitness_expert": fitness_expert,
    "business_expert": business_expert,
    "health_expert": health_expert,
    "general_qa": general_qa,
    "dynamic_tool_manager": dynamic_tool_manager,
    "causal_risk_assessor": causal_risk_assessor,
    "critique_revise": critique_revise,
    "knowledge_fusion_node": knowledge_fusion_node,
    "meta_cognition_node": meta_cognition_node,
    "verifiable_identity_node": verifiable_identity_node,
    "verifiable_audit_node": verifiable_audit_node,
}

# --- 2. Initialize and Compile the Graph ---
app = create_cognito_omega_graph(NODE_MAP)

# --- 3. Define Initial State and Input (High-Risk Test Case) ---
# Testing the Multi-Modal, Risk Assessor, and Finance flow
initial_state: Dict[str, Any] = {
    "messages": [], 
    # Using an input that triggers Multi-Modal Decoder and the high-risk Finance expert
    "raw_user_input": "audio: I need the latest data on capital gains tax and investment data.",
    "agent_reputation": { 
        "finance_expert": 0.8, 
        "legal_expert": 0.5, 
        "health_expert": 0.9,
        "general_qa": 0.7 
    } 
}

# --- 4. Run the Graph with Error Handling ---
print("--- COGNITO OMEGA SYSTEM INITIATED ---")
final_state: Dict[str, Any] = {} # Initialize a container for the final state

try:
    # Use stream to show the flow step-by-step
    result_generator = app.stream(initial_state)
    
    # Iterate through the stream, capturing execution log and the final state data
    for step in result_generator:
        # Print the node that just executed and accumulate the state updates
        for key, value in step.items():
            if key != "__end__":
                print(f"|--- Node Executed: {key}")
                # LangGraph stream yields the diffs (changes). Merging them builds the final state.
                final_state.update(value) 

    print("\n--- FINAL EXECUTION COMPLETE ---")
    
    # The final_state dictionary now holds the complete state.
    # We have removed the problematic app.get_state() call.
    
    print("\n--- FINAL OUTPUT MESSAGE ---")
    
    messages = final_state.get("messages", [])
    
    # Check if a message exists, and print its content
    if messages and len(messages) > 0:
        # Safely access the content of the last message
        print(messages[-1].content)
    else:
        print("No final message content found.")
        
    print(f"\nFinal Audit Hash: {final_state.get('audit_hash', 'N/A')}")
    print(f"Expert Used: {final_state.get('target_expert', 'N/A')}")
    print(f"Risk Score: {final_state.get('risk_score', 'N/A')}")

except Exception as e:
    print(f"\n--- CRITICAL SYSTEM FAILURE ---")
    print(f"An unexpected error occurred during graph execution: {e}")
