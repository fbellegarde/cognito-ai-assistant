# D:\cognito_ai_assistant\ai_core\supervisor.py (Modified)

class AgentToCall(BaseModel):
    """Specifies the next agent to route the task to."""
    next_agent: Literal["ResearchAgent", "CodeExpert", "FinalSynthesizer", "Reflector"] = Field(
        description="The name of the next specialized agent or step to call."
    )

def supervisor_router(state: AgentState) -> str:
    """
    The main routing function. The Supervisor LLM decides which agent to delegate to.
    """
    user_query = state["user_query"]
    
    # Logic for Supervisor LLM (Prompted to output the AgentToCall Pydantic schema)
    # Prompt: "Analyze the user's request. Is it primarily research/data gathering, or does it require code execution/math/logic? Delegate to the appropriate agent."
    
    # Mock routing logic for illustration:
    if "calculate" in user_query.lower() or "run python" in user_query.lower():
        next_agent = "CodeExpert"
    elif "find out" in user_query.lower() or "latest news" in user_query.lower():
        next_agent = "ResearchAgent"
    else:
        next_agent = "FinalSynthesizer" # If neither, it can synthesize a final answer immediately

    print(f"**Supervisor:** Delegating task to: {next_agent}")
    return next_agent