# D:\cognito_ai_assistant\ai_core\schemas.py

from pydantic import BaseModel, Field
from typing import Literal, Optional
from ai_core.schemas import ToolCall # Import the new schema

# --- 1. Tool Call Schema (The Agent's Decision) ---
# This is the Pydantic schema the LLM MUST output when it decides to use a tool.
# This forces a clean, machine-readable JSON object.

class ToolCall(BaseModel):
    """A structured model for the agent's decision to call a specific tool."""
    
    # Restrict the possible tools to a known, safe list of names
    # You must manually list all your available tool names here for security
    tool_name: Literal[
        "search_web", 
        "search_knowledge_base",
        "get_user_data",
        # Add all your tool functions here!
        "execute_system_command" 
    ] = Field(description="The exact name of the tool function to call.")
    
    # The arguments must be provided as a dictionary (JSON object)
    tool_args: dict = Field(description="A dictionary of arguments to pass to the tool, e.g., {'query': 'latest stock price'}.")


# --- 2. Moderation/Safety Schema (The Guardrail Output) ---
# Used to classify the user's intent.

class ModerationResult(BaseModel):
    """Structured output for the safety/moderation agent."""
    
    # Determines if the input is safe to process
    is_safe: bool = Field(description="True if the user's prompt is safe, compliant, and does not violate policy. False otherwise.")
    
    # Provides the final response if the query is UNSAFE
    refusal_reason: Optional[str] = Field(description="If is_safe is False, provide a brief, polite refusal message.")

    def execute_agent_or_tool(state: AgentState) -> AgentState:
    """
    The Main Agent generates an action (tool call) or the final answer.
    It is now forced to use the Pydantic ToolCall schema for tool decisions.
    """
    
    # 1. Update the prompt to force structured output
    # We use a wrapper to bind the LLM to the ToolCall schema
    
    # The 'ToolCall' schema will automatically be injected into the prompt
    # instructing the LLM to output a JSON object conforming to the schema.
    structured_llm = llm.with_structured_output(ToolCall)
    
    # 2. Get the LLM to generate the next step (ToolCall or Final Answer)
    # The prompt should be heavily focused on deciding *what* to do next.
    prompt_messages = [
        # ... Your existing System Prompt/History ...
        ("user", "Based on the conversation and the critique (if any), generate your next action. You MUST use the `ToolCall` JSON schema if you decide to use a tool, otherwise provide the final answer as text."),
        # Append reflection if in a retry loop
        ("system", f"CRITIQUE from previous step: {state.get('reflection', 'None')}")
    ]
    
    # The response will be an instance of ToolCall (if a tool is called) or a regular AIMessage (if final answer)
    response = structured_llm.invoke(prompt_messages)
    
    # 3. Check the response type and update the state
    if isinstance(response, ToolCall):
        # The LLM decided to use a tool, and the output is a validated Pydantic object!
        tool_name = response.tool_name
        tool_args = response.tool_args
        
        # ... logic to run the tool and update the state ...
        
        # Example of tool execution (assuming a utility function 'run_tool_by_name'):
        tool_output = run_tool_by_name(tool_name, **tool_args)
        
        # ... The rest of the logic to update 'messages' and set 'status' to 'tool_executed' ...
        return AgentState(messages=state["messages"] + [ToolMessage(content=tool_output)], status="tool_executed", iterations=state["iterations"] + 1)
        
    else:
        # The LLM decided to return the final answer (a regular string)
        return AgentState(messages=state["messages"] + [response], status="finished")