# D:\cognito_ai_assistant\ai_core\human_in_the_loop.py

from langgraph.types import Interrupt, Command
from typing import Literal

# List of tools that require human sign-off
CRITICAL_TOOLS = ["code_executor", "send_email", "delete_database_record"]

def check_approval(state: AgentState) -> Command[Literal["execute_tool", "reject_tool_call", "continue_planning"]]:
    """
    Checks the proposed tool calls. If a critical tool is requested, 
    it interrupts the graph and requests human approval.
    """
    messages = state["messages"]
    last_message = messages[-1]

    # Check if the last LLM response requested a tool call
    if not last_message.tool_calls:
        # No tool call, just continue the planning/execution loop
        return Command(goto="continue_planning") # Routes back to the Supervisor/Planner
    
    # Check if any requested tool is on the critical list
    requires_approval = any(
        call.name.lower() in CRITICAL_TOOLS for call in last_message.tool_calls
    )

    if requires_approval:
        # --- PAUSE EXECUTION AND REQUEST APPROVAL ---
        # The interrupt function pauses the graph and returns an InterruptionMetadata object
        # The return value of interrupt() will be the human's input upon resume
        
        tool_call_summary = "\n".join([
            f"- Tool: {call.name}\n  Args: {call.args}" 
            for call in last_message.tool_calls
        ])
        
        # This payload is what the UI/CLI must present to the human
        human_decision = Interrupt(
            payload={
                "action_type": "Critical Action Approval Required",
                "tool_calls": tool_call_summary,
                "risk_reasoning": "This action is irreversible or costly."
            }
        )
        
        # When resumed, the graph will continue from this point.
        # The resume input should be a string like "APPROVE" or "REJECT".
        
        # The decision logic is now dependent on the external human input.
        # For the script, we assume the input is available on resume.
        if human_decision.lower() == "approve":
            return Command(goto="execute_tool") # Continue to the Tool Node
        else:
            return Command(goto="reject_tool_call") # Route to a node that informs the agent of the rejection

    else:
        # Non-critical tool, allow direct execution
        return Command(goto="execute_tool")
    # D:\cognito_ai_assistant\ai_core\human_in_the_loop.py

from langchain_core.messages import ToolMessage

def reject_tool_call(state: AgentState) -> AgentState:
    """Informs the agent that its proposed critical tool call was rejected by the human."""
    
    # Create a ToolMessage with a denial to feed back into the LLM's context
    rejection_message = ToolMessage(
        content="Human Oversight: The requested critical action was REJECTED. You must re-evaluate your strategy and propose a safer action or continue the planning phase.",
        tool_call_id=state["messages"][-1].tool_calls[0].id, # Use the original tool call ID
    )
    
    # Add the rejection to the message history
    return AgentState(messages=state["messages"] + [rejection_message], status="replan_after_rejection")