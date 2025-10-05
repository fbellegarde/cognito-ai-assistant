# D:\cognito_ai_assistant\ai_core\multi_agent_supervisor.py

from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Literal

# Schema for the Supervisor's structured output decision
class AgentDecision(BaseModel):
    """Router decision: which specialist agent to call next."""
    agent_name: Literal["Researcher", "DataAnalyzer", "CodeExecutor", "FinalSynthesizer", "ToolFailureHandler"] = Field(
        description="The name of the next specialist agent to route the task to."
    )
    reasoning: str = Field(
        description="Justification for selecting this agent based on the current task and available context."
    )

def supervisor_router(state: AgentState) -> str:
    """
    The Supervisor LLM reviews the task plan and context to determine the next agent.
    
    This function uses an LLM (bound to AgentDecision schema) to classify the task
    (e.g., 'Requires web search' -> Researcher, 'Requires calculation' -> DataAnalyzer).
    """
    messages = state["messages"]
    current_task = state["task_plan"][state["current_step"]]

    # (LLM Invocation Logic using AgentDecision Schema goes here)
    # The Supervisor LLM decides the 'agent_name' based on the messages and current_task.
    
    # Mock decision for illustration:
    if "calculate" in current_task.lower() or "analyze data" in current_task.lower():
        decision = "DataAnalyzer"
    elif "search" in current_task.lower() or "latest news" in current_task.lower():
        decision = "Researcher"
    else:
        decision = "FinalSynthesizer"
    
    return decision