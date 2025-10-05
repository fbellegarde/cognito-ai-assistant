# D:\cognito_ai_assistant\ai_core\tool_selector.py

from typing import List, Literal
from langchain_core.pydantic_v1 import BaseModel, Field

# Define the Tool Groups (must map to your code's tool collections)
class ToolGroups(BaseModel):
    selected_tool_group: Literal["FINANCE_ANALYSIS", "CODE_GENERATION", "EMAIL_COMMUNICATION", "GENERAL_RESEARCH"] = Field(
        description="The primary domain of the user's query."
    )
    
# Mapping of groups to actual tool functions (Simplified for example)
TOOL_MAPPING = {
    "FINANCE_ANALYSIS": ["get_stock_price", "calculate_portfolio_risk"],
    "CODE_GENERATION": ["python_interpreter", "read_local_file"],
    "EMAIL_COMMUNICATION": ["send_email"], # Note: send_email is critical and will still be flagged for HITL later
    "GENERAL_RESEARCH": ["web_search", "rag_retriever"]
}

# Assume a fast, small LLM for this classification task
SELECTOR_LLM = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0) 

def tool_selector_node(state: AgentState) -> AgentState:
    """
    Classifies the user query to select a domain-specific, minimal toolset.
    """
    user_query = state["user_query"]
    
    # LLM Prompt: "Analyze the user query and classify it into one of the following domains: [List Domains]. Use the Pydantic schema."
    
    # Mock ToolGroup classification for illustration:
    if "email" in user_query.lower() or "send message" in user_query.lower():
        selected_group = "EMAIL_COMMUNICATION"
    elif "stock" in user_query.lower() or "risk" in user_query.lower():
        selected_group = "FINANCE_ANALYSIS"
    else:
        selected_group = "GENERAL_RESEARCH" # Default to a safe set

    # Map the group to the list of tool names
    selected_tool_names = TOOL_MAPPING.get(selected_group, TOOL_MAPPING["GENERAL_RESEARCH"])
    
    print(f"**Tool Selector:** Task classified as {selected_group}. Tools loaded: {selected_tool_names}")
    
    return AgentState(
        current_tool_names=selected_tool_names,
        status="tools_selected"
    )

# --- Update AgentState ---
# Add a key to hold the currently selected tool names
class AgentState(TypedDict):
    # ... (existing keys) ...
    current_tool_names: List[str] = Field(default=list)