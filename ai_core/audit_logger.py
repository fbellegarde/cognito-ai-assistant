# D:\cognito_ai_assistant\ai_core\audit_logger.py

# Assume AUDIT_DB is a simple interface to a persistent database (e.g., SQLite, Postgres)
AUDIT_DB = initialize_audit_database()

def log_audit_entry(event_type: str, details: dict):
    """Persists a single, timestamped audit record to the database."""
    AUDIT_DB.insert({
        "timestamp": datetime.now().isoformat(),
        "thread_id": details.get("thread_id", "N/A"),
        "event_type": event_type,
        "details": details
    })
    
def audit_logger_node(state: AgentState) -> AgentState:
    """
    Logs the state of the graph, focusing on the most recent, critical transition.
    """
    # Identify the last critical action/status change
    last_status = state.get("status", "START")
    last_message = state["messages"][-1] if state["messages"] else None
    
    details = {
        "thread_id": state["thread_id"],
        "step_index": state["current_step"],
        "status": last_status,
        "LLM_Output_Type": last_message.type if last_message else "N/A",
        "LLM_Tool_Calls": [c.name for c in last_message.tool_calls] if last_message and last_message.tool_calls else "N/A",
        "Reflection_Critique": state.get("reflection", {}).get("critique")
    }

    log_audit_entry(f"TRANSITION_{last_status.upper()}", details)
    
    # This node does not modify the state and routes to the next step
    return state