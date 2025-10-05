# D:\cognito_ai_assistant\ai_core\agent_nodes.py
import os
from typing import List
from langchain_core.messages import ToolMessage, HumanMessage, SystemMessage
# Assuming your LLM setup from the previous step is available here
from .views import tool_calling_llm
from .tools import search_web, execute_system_command, all_tools
from .agent_state import AgentState

# --- Tool Execution Mapping ---
TOOL_MAP = {
    "search_web": search_web,
    "execute_system_command": execute_system_command,
    # Add other tools here
}

def execute_agent_or_tool(state: AgentState) -> dict:
    """
    Node 1: LLM decides to generate a final answer or call a tool.
    """
    print("--- 1. ENTERING EXECUTION NODE ---")
    messages = state["messages"]
    
    # 1. Invoke the LLM with the current conversation history
    agent_response = tool_calling_llm.invoke(messages)
    
    # 2. Check for tool calls
    if agent_response.tool_calls:
        print(f"AI decided to call tool(s): {', '.join([tc['name'] for tc in agent_response.tool_calls])}")
        
        # Add the LLM's tool-request message to history
        messages.append(agent_response)
        
        # 3. Execute the tool(s) and create ToolMessage
        tool_outputs = []
        for tool_call in agent_response.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            tool_call_id = tool_call['id']
            
            # Use the actual function from the map
            tool_func = TOOL_MAP.get(tool_name)
            
            if tool_func:
                try:
                    tool_result = tool_func.invoke(tool_args)
                except Exception as e:
                    tool_result = f"TOOL EXECUTION ERROR: {str(e)}"
            else:
                tool_result = f"TOOL ERROR: Unknown tool '{tool_name}'."
                
            print(f"Tool {tool_name} result: {tool_result[:50]}...")
            
            # Create the ToolMessage containing the result
            tool_outputs.append(
                ToolMessage(
                    content=tool_result,
                    tool_call_id=tool_call_id
                )
            )
        
        # 4. Add all ToolMessage results to history
        messages.extend(tool_outputs)
        
        # 5. Transition to the reflection phase to critique the tool's result
        return {"messages": messages, "status": "tool_executed", "iterations": state["iterations"] + 1}
    
    else:
        # No tool call, LLM generated a final answer
        messages.append(agent_response)
        return {"messages": messages, "status": "finished"}

def reflect_and_critique(state: AgentState) -> dict:
    """
    Node 2: The LLM critiques the result of the last tool call or the attempt itself.
    This helps detect if the tool failed or if the result is insufficient.
    """
    print("--- 2. ENTERING REFLECTION NODE ---")
    messages = state["messages"]
    last_tool_message = messages[-1].content
    user_prompt = messages[0].content
    
    # Create a dedicated reflection prompt
    reflection_prompt = SystemMessage(f"""
    CRITIQUE AGENT: You are an expert AI self-critic. Your task is to critique the last action taken by the assistant.
    The original user goal was: '{user_prompt}'
    The result of the last action was (Tool Output): '{last_tool_message}'

    Analyze the tool output in the context of the user's goal.
    1. Did the tool successfully execute and provide the necessary information?
    2. Is the information enough to fully answer the user's request?
    3. If not, how should the assistant adjust its next plan/action?

    RESPOND ONLY with the reflection and advice (e.g., 'The tool failed because X. The assistant should now try Y.' or 'Success. Proceed to final answer.').
    """)
    
    # Invoke a simple LLM (or the same one) specifically for critique
    reflection_agent_llm = tool_calling_llm.base_model # Use base LLM without tools for pure critique
    reflection_response = reflection_agent_llm.invoke([reflection_prompt])
    
    reflection_text = reflection_response.content
    print(f"Reflection: {reflection_text[:100]}...")

    # Update state with the reflection and determine next status
    state["reflection"] = reflection_text
    
    if "Success. Proceed to final answer." in reflection_text:
        # Reflection confirms the data is good, move to generating the final response
        return {"messages": messages, "status": "proceed_to_answer", "reflection": reflection_text}
    
    # Otherwise, assume more work is needed (either re-plan or re-execute)
    # The next transition will decide whether to retry or fail
    return {"messages": messages, "status": "reflection_needed", "reflection": reflection_text}

def generate_final_answer(state: AgentState) -> dict:
    """
    Node 3: Generate the final, user-facing answer based on all preceding steps/results.
    """
    print("--- 3. ENTERING FINAL ANSWER NODE ---")
    messages = state["messages"]
    
    # Add a system prompt to synthesize the final answer
    final_prompt = SystemMessage("""
    FINAL ANSWER AGENT: Synthesize all information gathered in the previous steps (especially the latest tool output)
    and provide a single, clear, and comprehensive answer to the user's original request.
    DO NOT mention the reflection process.
    """)
    
    messages.append(final_prompt)
    final_response = tool_calling_llm.base_model.invoke(messages)
    
    messages.append(final_response)
    return {"messages": messages, "status": "final_answer_generated"}