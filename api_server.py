# D:\cognito_ai_assistant\api_server.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from ai_core.graph import create_cognito_omega_graph, AgentState, NODE_MAP
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

# --- 1. SETUP ---
load_dotenv()
# The global graph instance
try:
    COGNITO_GRAPH = create_cognito_omega_graph(NODE_MAP)
except Exception as e:
    print(f"FATAL ERROR: Could not initialize LangGraph: {e}")
    COGNITO_GRAPH = None
    
app = FastAPI(title="Cognito Omega AI Service", version="1.0")

# --- 2. INPUT SCHEMA ---
class QueryInput(BaseModel):
    """Schema for incoming user queries."""
    raw_user_input: str
    user_id: str = "guest_user" # Important for future user-specific state/memory

# --- 3. API ENDPOINT ---
@app.post("/query")
async def run_cognito_query(query_data: QueryInput) -> Dict[str, Any]:
    """Runs a user query through the Cognito Omega Graph."""
    
    if COGNITO_GRAPH is None:
        raise HTTPException(status_code=503, detail="AI Service is not initialized.")

    # Initialize the graph state with the required keys
    initial_state: Dict[str, Any] = {
        "messages": [], 
        "raw_user_input": query_data.raw_user_input,
        "agent_reputation": { 
            "finance_expert": 0.5, "legal_expert": 0.5, 
            "health_expert": 0.5, "general_qa": 0.5 
        }, 
        # Add other required initial keys from AgentState
        "original_language": "en", "cultural_context": "general",
        "original_modality": "text", "modality_metadata": {},
        "current_model": "gpt-3.5-turbo",
        "risk_score": 0.0, "risk_assessment_report": "",
        "critique_report": "", "fusion_block": "", 
        "audit_hash": "", "digital_signature": ""
    }

    try:
        # Run the entire graph
        final_state = COGNITO_GRAPH.invoke(initial_state)
        
        # Extract the final answer and audit data
        final_message = final_state.get("messages", [{}])[-1].content
        audit_hash = final_state.get("audit_hash", "N/A")
        
        return {
            "status": "success",
            "final_answer": final_message,
            "audit_hash": audit_hash,
            "expert_used": final_state.get("target_expert"),
            "risk_score": final_state.get("risk_score")
        }
        
    except Exception as e:
        print(f"Graph Execution Error: {e}")
        raise HTTPException(status_code=500, detail=f"AI execution error: {str(e)}")

# --- 4. START THE SERVER (Local Testing Command) ---
# To run locally: uvicorn api_server:app --host 0.0.0.0 --port 8000