# D:\cognito_ai_assistant\ai_core\plan_rewriter.py

from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List

# Schema for the Plan Rewriter's structured output
class NewPlan(BaseModel):
    """The new, revised sequence of task steps."""
    new_task_plan: List[str] = Field(
        description="A completely new list of sequential steps to achieve the original goal, incorporating the reflection's recommendations."
    )
    justification: str = Field(
        description="A brief explanation of how this new plan addresses the previous failure."
    )

def plan_rewrite_node(state: AgentState) -> AgentState:
    """
    Uses the critique from the Reflector to generate a new task plan.
    """
    reflection: Reflection = state['reflection']
    
    prompt = f"""
    TASK: Rewrite the entire task plan based on the following critique.
    
    ORIGINAL GOAL: {state['user_query']}
    CRITIQUE: {reflection.critique}
    RECOMMENDATION: {reflection.recommendation}
    
    Generate a complete, new task plan (a list of steps) that avoids the failure 
    and leads directly to the final answer. Use the Pydantic schema for output.
    """
    
    # LLM invocation logic using NewPlan schema
    # rewriter_llm.with_structured_output(NewPlan).invoke(prompt)
    
    # Mock NewPlan for illustration:
    new_plan_output = NewPlan(
        new_task_plan=["Step 1: Get the current stock price.", "Step 2: Retrieve the stock's 52-week high.", "Step 3: Calculate the percentage difference.", "Step 4: Synthesize final answer."],
        justification="The new plan explicitly retrieves the 52-week high (Step 2) before attempting calculation, preventing the missing data error."
    )

    print(f"**Plan Rewriter:** Successfully generated a revised plan.")

    # Reset state variables for the new run
    return AgentState(
        task_plan=new_plan_output.new_task_plan,
        current_step=0,         # Start from the first step of the new plan
        system_error=None,      # Clear the error
        status="replan_success" # Signal to restart execution
    )

# --- Update AgentState ---
# Add a key to hold the reflection object
class AgentState(TypedDict):
    # ... (existing keys) ...
    reflection: Reflection = Field(default=None)