# D:\cognito_ai_assistant\ai_core\agent_state.py
from typing import TypedDict, List
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage

# Define the structure of the data passed around the LangGraph workflow
class AgentState(TypedDict):
    """
    Represents the state of our agent's workflow.
    The keys here are available to all nodes in the graph.
    """
    # History of the conversation/attempt, including tool calls and results
    messages: List[BaseMessage]

    # Status of the last executed step
    status: str # e.g., "tool_executed", "reflection_needed", "finished"

    # The LLM's self-critique/reflection on the last action
    reflection: str
    
    # Counter to prevent infinite loops during self-correction
    iterations: int