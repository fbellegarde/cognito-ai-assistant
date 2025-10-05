# D:\cognito_ai_assistant\ai_core\agent_executor.py (Modification)

# Assume ALL_TOOLS is a dictionary mapping tool names to tool objects
# ALL_TOOLS = {"get_stock_price": fn_obj, "send_email": fn_obj, ...}

def agent_executor_node(state: AgentState) -> AgentState:
    """
    Executes the LLM with a dynamically bound subset of tools.
    """
    # 1. Retrieve the list of tool names selected in the state
    selected_tool_names = state["current_tool_names"]
    
    # 2. Map names to actual tool objects
    active_tools = [ALL_TOOLS[name] for name in selected_tool_names if name in ALL_TOOLS]
    
    # 3. Instantiate the LLM with ONLY the active tools
    # LLM_MODEL is your main, powerful model (e.g., gpt-4-turbo)
    llm_with_dynamic_tools = LLM_MODEL.bind_tools(active_tools)
    
    # ... (rest of the ReAct/planning logic remains the same) ...
    
    # Use llm_with_dynamic_tools to invoke the model
    response = llm_with_dynamic_tools.invoke(state["messages"])
    
    # ... (rest of the state update) ...
    
    return state