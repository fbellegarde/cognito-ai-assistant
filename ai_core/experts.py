# D:\cognito_ai_assistant\ai_core\experts.py

from typing import Dict, Any, List
import os
import random
import json
import time
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from .graph import AgentState, EXPERT_OPTIONS 
from .tools import (
    calculate_verifiable_hash, sign_data_with_did, PUBLIC_DID,
    save_fusion_block, log_training_script, 
    mock_external_search, mock_finance_api, mock_legal_database, mock_fitness_tracker
)

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the LLM instance
llm = ChatOpenAI(model="gpt-4o", temperature=0.0, api_key=OPENAI_API_KEY)

# --- Tool Call Schema (Structured Output for Experts) ---
class ToolCall(BaseModel):
    """Structured output for tool calls, used by Dynamic Tool Manager."""
    tool_name: str = Field(description="The name of the tool to be used: 'search', 'finance', 'legal', 'fitness'.")
    tool_query: str = Field(description="The precise query/arguments for the tool.")

# --- 1. ENTRY POINT: MULTI-MODAL DECODER (MMD) ---
def multi_modal_decoder(state: Dict[str, Any]) -> Dict[str, Any]:
    raw_input = state["raw_user_input"] 
    
    # Robust Modality Detection/Decoding Logic
    if raw_input.startswith("image:"):
        modality, decoded_text = "image", "OCR result: 'The graph shows a 5% increase in Q3.'"
    elif raw_input.startswith("audio:"):
        modality, decoded_text = "audio", "Transcription: 'I need a compliance check for HIPAA.'"
    else:
        modality, decoded_text = "text", raw_input
        
    standardized_message = HumanMessage(content=decoded_text)
    
    return {
        "messages": [standardized_message],
        "original_modality": modality,
        "modality_metadata": {"decoded_text": decoded_text},
    }

# --- 2. MULTI-LINGUAL & CULTURAL CONTEXT NLU (MLCC-NLU) ---
def mlcc_nlu_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    query = state["messages"][-1].content
    
    # Mock LLM result for context extraction (use actual LLM call in production)
    lang, context = "en", "general" 
    
    return {"original_language": lang, "cultural_context": context}

# --- 3. EMOTION/INTENT DETECTOR (EID) ---
def emotion_intent_detector(state: Dict[str, Any]) -> Dict[str, Any]:
    # Mock intent setting (for complexity, we just pass the state)
    return state 

# --- 4. SUPERVISOR/ROUTER ---
def supervisor(state: Dict[str, Any]) -> Dict[str, Any]:
    query = state["messages"][-1].content
    
    # Mock routing decision (force a high-risk route for testing)
    if "tax" in query.lower() or "investment" in query.lower():
        target_expert = "finance_expert"
    else:
        target_expert = "general_qa"
        
    return {"target_expert": target_expert}

# --- 5. UNIVERSAL MODEL SELECTOR (UMS) ---
def universal_model_selector(state: Dict[str, Any]) -> Dict[str, Any]:
    target_expert = state["target_expert"]
    # Dynamic selection logic
    current_model = "gpt-4o" if target_expert in ["legal_expert", "health_expert", "finance_expert"] else "gpt-3.5-turbo"
        
    return {"current_model": current_model}

# --- 6. Q-VALUE PRIORITIZER (RL-Informed Routing) ---
def q_value_prioritizer(state: Dict[str, Any]) -> Dict[str, Any]:
    # Logic is implemented in meta_cognition_node; here we check and log
    target_expert = state["target_expert"]
    reputation = state.get("agent_reputation", {})
    current_q_value = reputation.get(target_expert, 0.5)
    
    # If Q-Value is too low for a high-risk task, the Supervisor could reroute here.
    return state 

# --- 7. COGNITIVE LATENCY CHECK ---
def cognitive_latency_check(state: Dict[str, Any]) -> Dict[str, Any]:
    # Mock: check latency, but always proceed
    return state 

# --- 8. DOMAIN EXPERTS ---

def _run_expert_agent(state: Dict[str, Any], expert_role: str, disclaimer: str) -> Dict[str, Any]:
    """Template function for all specialized expert agents."""
    query = state["messages"][-1].content
    
    # Mock Logic: Determine if a tool is needed
    needs_tool = "data" in query.lower() or "latest" in query.lower()
    
    if needs_tool:
         # Return a structured JSON for the Tool Manager
         if expert_role == "finance_expert":
             tool_call_data = ToolCall(tool_name="finance", tool_query=query).json()
         elif expert_role == "legal_expert":
             tool_call_data = ToolCall(tool_name="legal", tool_query=query).json()
         elif expert_role == "fitness_expert":
             tool_call_data = ToolCall(tool_name="fitness", tool_query=query).json()
         else:
             tool_call_data = ToolCall(tool_name="search", tool_query=query).json()
             
         expert_response = tool_call_data
    else:
        # Provide a detailed, disclaimed answer without a tool
        expert_response = f"**{expert_role.upper()} RESPONSE:** {disclaimer} I have analyzed your query based on established principles."
        
    final_answer_message = AIMessage(content=expert_response)
    return {"messages": state["messages"] + [final_answer_message], "target_expert": expert_role}

# Expert definitions calling the template
def finance_expert(state: Dict[str, Any]) -> Dict[str, Any]:
    return _run_expert_agent(state, "finance_expert", "⚠️ FINANCIAL DISCLAIMER: AI, not a licensed advisor.")

def legal_expert(state: Dict[str, Any]) -> Dict[str, Any]:
    return _run_expert_agent(state, "legal_expert", "🛑 LEGAL DISCLAIMER: AI, not a lawyer.")

def fitness_expert(state: Dict[str, Any]) -> Dict[str, Any]:
    return _run_expert_agent(state, "fitness_expert", "💪 FITNESS DISCLAIMER: Consult your physician.")

def business_expert(state: Dict[str, Any]) -> Dict[str, Any]:
    return _run_expert_agent(state, "business_expert", "💼 BUSINESS DISCLAIMER: General strategy advice.")

def health_expert(state: Dict[str, Any]) -> Dict[str, Any]:
    return _run_expert_agent(state, "health_expert", "⚕️ HEALTH DISCLAIMER: Cannot diagnose or treat.")

def general_qa(state: Dict[str, Any]) -> Dict[str, Any]:
    return _run_expert_agent(state, "general_qa", "🌐 GENERAL QA: Based on general knowledge.")


# --- 9. DYNAMIC TOOL MANAGER (Security Enhancement: JSON Parsing) ---
def dynamic_tool_manager(state: Dict[str, Any]) -> Dict[str, Any]:
    """Manages the execution of external tools based on expert output."""
    last_message = state["messages"][-1].content
    
    tool_output = None
    try:
        # **CORRECTION:** Use json.loads() and Pydantic validation for security
        tool_call_dict = json.loads(last_message)
        ToolCall(**tool_call_dict) # Validate structure with Pydantic
        
        tool_name = tool_call_dict['tool_name']
        query = tool_call_dict['tool_query']
        
        if tool_name == "finance":
            tool_output = mock_finance_api(query)
        elif tool_name == "legal":
            tool_output = mock_legal_database(query)
        elif tool_name == "fitness":
            tool_output = mock_fitness_tracker(query)
        else: 
            tool_output = mock_external_search(query)
        
        # Expert response is now the tool result + original expert response
        tool_message = AIMessage(content=f"TOOL RESULT: {tool_output}")
        print(f"🛠️ [TOOL MGR] Executed {tool_name}.")
        return {"messages": state["messages"] + [tool_message]}
            
    except json.JSONDecodeError:
        # Not a tool call (just a plain answer), proceed
        pass 
    except Exception as e:
        # Handle unexpected errors gracefully, log, and proceed
        print(f"🛠️ [TOOL MGR] Tool execution failed: {e}. Proceeding without tool result.")
        pass

    return state 

# --- 10. CAUSAL RISK ASSESSOR (CRA) ---
def causal_risk_assessor(state: Dict[str, Any]) -> Dict[str, Any]:
    """Assesses the risk level of the final answer before delivery."""
    query = state["messages"][0].content
    last_message = state["messages"][-1].content
    
    target_expert = state["target_expert"]
    # Enforce risk logic
    if target_expert in ["legal_expert", "health_expert", "finance_expert"] or "investment" in query.lower():
        risk_score = 0.95
        report = "CRITICAL RISK: Content touches on regulated advice. Mandatory disclaimers confirmed."
        
        # **CORRECTION:** Ensure the final message contains all necessary info (Tool result + expert answer)
        new_answer = "🛑 **MANDATORY HIGH-RISK WARNING** 🛑 \n\n" + last_message
        state["messages"][-1] = AIMessage(content=new_answer)
    else:
        risk_score = 0.2
        report = "Low risk assessment."
        
    return {"risk_score": risk_score, "risk_assessment_report": report, "messages": state["messages"]}

# --- 11. CRITIQUE/REVISE (Self-Correction) ---
def critique_revise(state: Dict[str, Any]) -> Dict[str, Any]:
    last_message = state["messages"][-1].content
    
    # Mock LLM call for Critique
    if "MANDATORY HIGH-RISK WARNING" in last_message:
        critique = "PERFECT: Response is safe, accurate, and includes all mandatory warnings."
    elif random.random() < 0.2: 
        critique = "CRITICAL FAILURE: The answer is incomplete and needs to incorporate the TOOL RESULT."
        # The routing logic will send this back to the expert for revision
    else:
        critique = "PERFECT: Answer is accurate, relevant, and well-structured."
        
    return {"critique_report": critique}

# --- 12. KNOWLEDGE FUSION NODE ---
def knowledge_fusion_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # Mock LLM call for generalization
    fusion_block = f"GENERALIZATION: On {state['target_expert']} success, the CRA's risk warning was the key. | REASON: Safety compliance is the optimal path."
    save_fusion_block({"block": fusion_block, "expert": state["target_expert"], "timestamp": time.time()})
    
    return {"fusion_block": fusion_block}

# --- 13. META-COGNITION LOOP (Self-Improvement) ---
def meta_cognition_node(state: Dict[str, Any]) -> Dict[str, Any]:
    expert = state["target_expert"]
    is_successful = "PERFECT" in state.get("critique_report", "").upper()
    
    # Update Agent Reputation Score (Q-Learning)
    current_reputation = state.get("agent_reputation", {})
    current_score = current_reputation.get(expert, 0.5)
    
    new_score = min(1.0, current_score + 0.05) if is_successful else max(0.1, current_score - 0.05)
    current_reputation[expert] = new_score
    
    # Autonomous Training Script Generation 
    training_script = f"TRAINING PROMPT (Expert: {expert}): Example query related to {expert}. | IDEAL RESPONSE: A highly accurate and safe response."
    log_training_script(training_script)
    
    return {"agent_reputation": current_reputation}

# --- 14. DECENTRALIZED VERIFIABLE IDENTITY NODE (DVID) ---
def verifiable_identity_node(state: Dict[str, Any]) -> Dict[str, Any]:
    final_answer = state["messages"][-1].content
    audit_hash = state.get("audit_hash", "0xPENDING_HASH") 
    
    # Data to sign (must include the hash from the next node for true immutability, 
    # but we sign the data going *into* the hash for this flow)
    data_to_sign = f"ANSWER:{final_answer}|HASH:{audit_hash}|DID:{PUBLIC_DID}"
    digital_signature = sign_data_with_did(data_to_sign)
    
    # Embed verification details into the final message for the user
    final_answer_with_id = (
        f"{final_answer}\n\n---\n"
        f"✅ **Verifiable Trust Receipt:**\n"
        f"**Source DID:** {PUBLIC_DID}\n"
        f"**Digital Signature:** {digital_signature[:60]}..."
    )
    
    state["messages"][-1] = AIMessage(content=final_answer_with_id)
    
    return {"digital_signature": digital_signature, "messages": state["messages"]}


# --- 15. VERIFIABLE AUDIT NODE (Error Handling Refined) ---
def verifiable_audit_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a final, tamper-evident audit log of the entire transaction."""
    
    try:
        # Compile all critical state parts into a single string for hashing
        audit_data = {
            "user_query": state["messages"][0].content,
            "final_response_snippet": state["messages"][-1].content[:100] + "...",
            "expert_path": state.get("target_expert"),
            "risk_score": state.get("risk_score"),
            "signature": state.get("digital_signature")
        }
        
        # Calculate the hash
        audit_hash = calculate_verifiable_hash(json.dumps(audit_data))
        
        return {"audit_hash": audit_hash}
    except Exception as e:
        # Safe fallback in case of audit failure
        print(f"🔒 [AUDIT] CRITICAL ERROR: Audit failed. {e}")
        return {"audit_hash": "0xAUDIT_FAILED_SEC_ISSUE"}