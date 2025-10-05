# D:\cognito_ai_assistant\ai_core\speculative_executor.py

# Assume SAFE_TOOLS is a subset of all tools (e.g., just RAG and Calculator)
SAFE_TOOLS = [tool for tool in ALL_TOOLS if tool.name not in CRITICAL_TOOLS]
SPECULATIVE_TOOL_EXECUTOR = ToolExecutor(SAFE_TOOLS)

def execute_speculative_tasks(state: AgentState) -> AgentState:
    """
    Executes tasks in the speculative_queue in parallel and stores the results.
    """
    tasks_to_run = state.get("speculative_queue", [])
    if not tasks_to_run:
        return AgentState(status="no_speculative_work")

    new_results = state.get("speculative_results", {}).copy()
    
    # Use standard Python concurrency (e.g., threading or asyncio) to run the tool calls
    # For simplicity, we'll iterate synchronously here, but in production, this is concurrent.
    for task in tasks_to_run:
        try:
            # 1. LLM converts speculative text task into a safe Tool Call object
            tool_call_object = SPECULATIVE_LLM.invoke(f"Convert this task into a tool call: {task}")
            
            # 2. Execute the safe tool call
            result = SPECULATIVE_TOOL_EXECUTOR.invoke(tool_call_object)
            new_results[task] = f"SUCCESS: {result}"
        except Exception as e:
            new_results[task] = f"FAILURE: {str(e)}"

    print(f"**Speculative Executor:** Completed {len(tasks_to_run)} tasks.")
    
    # Clear the queue and store the new results
    return AgentState(speculative_queue=[], speculative_results=new_results, status="speculative_work_complete")