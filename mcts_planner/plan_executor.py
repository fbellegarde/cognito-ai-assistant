# D:\cognito_ai_assistant\mcts_planner\plan_executor.py

def plan_executor_node(state: AgentState) -> str:
    """
    Executes the next step of the MCTS-generated plan.
    Returns the name of the next agent to route to.
    """
    plan = state["current_plan"]
    index = state["current_step_index"]
    
    if index >= len(plan):
        # Plan is complete
        return "FinalSynthesizer" 

    next_step = plan[index]
    
    # IMPORTANT: Update the state with the specific instruction for the sub-agent
    # The sub-agent must now read 'next_agent_input' instead of 'user_query'
    state["next_agent_input"] = next_step.task_description 
    
    print(f"**Plan Executor:** Executing Step {index + 1}: {next_step.agent_name} - {next_step.task_description[:30]}...")
    
    # Return the name of the agent to route to in the graph
    return next_step.agent_name

# --- Update AgentState (Add new key) ---
class AgentState(TypedDict):
    # ... (existing keys) ...
    next_agent_input: str = Field(default="")