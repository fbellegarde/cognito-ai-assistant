# D:\cognito_ai_assistant\ai_core\meta_reflector.py

from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Literal

# Schema for the Reflector's structured output
class Reflection(BaseModel):
    """Structured analysis of why the previous task failed."""
    root_cause: Literal["FlawedInitialPlan", "IncorrectToolUsage", "ContextMisinterpretation", "ExternalDataError"] = Field(
        description="The fundamental reason the execution failed."
    )
    critique: str = Field(
        description="A detailed analysis explaining the planning or execution mistake."
    )
    recommendation: str = Field(
        description="A high-level instruction (1-2 sentences) for the PlanRewriter on how to fix the task plan."
    )

def reflection_node(state: AgentState) -> AgentState:
    """
    LLM analyzes the error state and previous steps to determine the root cause of failure.
    """
    # The full context for the Reflector LLM
    prompt = f"""
    CRITICAL REFLECTION: A multi-step task failed during execution.
    
    ORIGINAL GOAL: {state['user_query']}
    FAILED STEP: {state['task_plan'][state['current_step']]}
    EXECUTION HISTORY: {state['messages']} 
    ERROR/OBSERVATION: {state['system_error']}
    
    Analyze the above context. You MUST diagnose the root cause and provide a high-quality critique 
    and a clear, actionable recommendation for a new plan using the provided Pydantic schema.
    """
    
    # LLM invocation logic using Reflection schema
    # reflector_llm.with_structured_output(Reflection).invoke(prompt)
    
    # Mock Reflection for illustration:
    reflection_output = Reflection(
        root_cause="FlawedInitialPlan",
        critique="The original plan tried to perform Step 3 before gathering the required context from Step 2, leading to a tool error.",
        recommendation="Insert a new intermediate step to retrieve the prerequisite data before re-attempting the original failed step."
    )

    print(f"**Reflector:** Root Cause identified: {reflection_output.root_cause}")
    
    return AgentState(
        reflection=reflection_output,
        status="reflection_complete"
    )