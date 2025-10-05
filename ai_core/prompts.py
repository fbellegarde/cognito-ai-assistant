# D:\cognito_ai_assistant\ai_core\prompts.py (or within the execution node)

def get_dynamic_system_prompt(state: AgentState) -> str:
    """Generates a precise system prompt based on the current state, step, AND meta_prompt."""
    
    # 1. Retrieve the learned core instructions
    meta_core = state["meta_prompt"] 
    
    current_step_index = state["current_step"]
    total_steps = len(state["task_plan"])
    current_task = state["task_plan"][current_step_index]
    
    if current_step_index < total_steps - 1:
        # PROMPT for INTERMEDIATE EXECUTION
        # The dynamic instructions (Step 1 of 3) are appended to the static core (Meta Prompt)
        step_instructions = f"""
        Current Step {current_step_index + 1} of {total_steps}: "{current_task}"
        Your focus is solely on completing this sub-task. You have the following tools available.
        Think step-by-step (Thought: ...) before deciding to use a tool or continuing.
        """
    else:
        # PROMPT for FINAL SYNTHESIS
        step_instructions = f"""
        FINAL STEP: "{current_task}". You have completed all research.
        DO NOT USE ANY MORE TOOLS. Synthesize all information gathered into one cohesive, cited answer.
        """
        
    return meta_core + "\n\n" + step_instructions

# --- In the execute_agent_or_tool node ---
def execute_agent_or_tool(state: AgentState) -> AgentState:
    # 1. Generate the dynamic prompt
    dynamic_prompt = get_dynamic_system_prompt(state)
    
    # 2. Bind the prompt to the LLM (using the existing chain)
    agent_chain = ChatPromptTemplate.from_messages([
        ("system", dynamic_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ]) | EXECUTION_LLM.bind_tools(filtered_tools)
    
    # ... (rest of the execution logic) ...