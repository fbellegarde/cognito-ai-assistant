# D:\cognito_ai_assistant\ai_core\meta_cognitive_agent.py

from langchain_core.prompts import ChatPromptTemplate

# Use a highly reflective LLM for this task
REVISER_LLM = ChatOpenAI(model="gpt-4-turbo", temperature=0.1) 

def revise_meta_prompt(state: AgentState) -> AgentState:
    """
    Analyzes severe errors in the failure log and generates a better, 
    more resilient meta_prompt for future runs.
    """
    # Only run if there's a recent, un-processed critical failure
    if not state["failure_log"]:
        return AgentState(status="meta_prompt_unchanged")

    # Get the critical error that triggered the failure loop
    last_error_detail = state["failure_log"][-1]
    
    revision_prompt = f"""
    You are an AI System Architect responsible for refining the operational instructions 
    (the 'Meta Prompt') of the main AI agent. The agent recently encountered a critical failure.
    
    ---
    CURRENT META PROMPT: {state["meta_prompt"]}
    
    CRITICAL FAILURE LOG: {last_error_detail}
    ---

    Analyze the failure. Your goal is to generate a new, improved Meta Prompt that 
    explicitly guides the agent to avoid this exact mistake in the future. 
    The new prompt must be concise, integrate the current 'professional and safe' role, 
    and add specific, instructional guidance based on the error.
    
    NEW META PROMPT (Start with 'You are a professional...'):
    """

    # We don't use a structured output here; we want the LLM to generate the free-form prompt text.
    new_prompt_text = REVISER_LLM.invoke(revision_prompt).content
    
    # Clear the failure log after processing
    return AgentState(
        meta_prompt=new_prompt_text.strip(),
        failure_log=[], 
        status="meta_prompt_revised" 
    )