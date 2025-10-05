# D:\cognito_ai_assistant\ai_core\runtime_safety.py

from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Literal

# Schema for the Safety Agent's structured decision
class SafetyDecision(BaseModel):
    """Router decision: whether the LLM output is safe to proceed."""
    action: Literal["APPROVE", "FLAG_AND_REJECT", "REWRITE_SAFE"] = Field(
        description="The prescribed action based on safety policy."
    )
    justification: str = Field(
        description="Justification for the decision, especially if flagged."
    )
    
def runtime_safety_check(state: AgentState) -> str:
    """
    LLM checks the latest message (thought/tool-call/answer) for compliance violations 
    (e.g., self-harm, illegal activity, excessive data exposure).
    """
    latest_message = state["messages"][-1].content # Check the last thought/tool call LLM output
    
    # 1. LLM Policy Check (e.g., using a smaller, highly tuned model like Llama 3)
    # The LLM's prompt includes strict rules (e.g., "Do not authorize 'delete' commands without HITL approval," 
    # "Do not output PII").
    
    # Mock Safety Decision for illustration:
    if "delete database" in latest_message.lower() and "HITL approved" not in latest_message:
        decision = "FLAG_AND_REJECT"
        justification = "Attempted unauthorized critical action (Database Deletion) without explicit HITL approval status."
    elif len(latest_message.split()) > 500:
        decision = "REWRITE_SAFE"
        justification = "Output is excessively verbose; requires summarization to maintain clarity."
    else:
        decision = "APPROVE"
        justification = "Output is compliant and safe."
        
    print(f"**Runtime Safety Agent:** Decision: {decision}. Justification: {justification}")
    
    # Update state with the safety log entry
    state["safety_log"].append(f"CHECK: {latest_message[:50]}... | DECISION: {decision}")
    
    # The return value routes the graph
    return decision

# --- Update AgentState ---
# Add a key for the running safety log
class AgentState(TypedDict):
    # ... (existing keys) ...
    safety_log: Annotated[list[str], operator.add] = Field(default=list)