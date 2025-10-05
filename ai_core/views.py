# D:\cognito_ai_assistant\ai_core\views.py - NEW CORE LOGIC

import json
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# Use the async decorator for the view
from django.views.decorators.http import require_http_methods
from langchain_core.messages import HumanMessage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from langchain_community.llms import HuggingFaceHub
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from .tools import all_tools # Import your tools list
from .agent_state import AgentState
from .agent_nodes import execute_agent_or_tool, reflect_and_critique, generate_final_answer


# --- Setup LLM and Tool Chain (Re-use from previous step) ---
# NOTE: Replace with your actual LLM setup (e.g., OpenAI(model="gpt-4o"))
llm = HuggingFaceHub(
    repo_id="HuggingFaceH4/zephyr-7b-beta",
    huggingfacehub_api_token="YOUR_HUGGINGFACE_TOKEN", # Set this token
    model_kwargs={"temperature": 0.1, "max_length": 1024}
)
tool_calling_llm = llm.bind_tools(all_tools)


# --- Conditional Router Function ---
def should_continue(state: AgentState) -> str:
    """
    Defines the next step based on the last action's status and reflection.
    """
    if state["status"] == "finished":
        return END # LLM generated a final answer immediately (no tools needed)
    
    if state["status"] == "proceed_to_answer":
        return "final_answer" # Reflection approved the tool result

    if state["status"] == "reflection_needed":
        if state["iterations"] >= 3:
            return "final_answer" # Retry limit reached: use the best info available
        
        # If reflection suggests a retry/re-plan, loop back to execution
        return "execute" 
    
    # Default path after an initial tool execution
    return "reflect"


# --- Build the LangGraph Workflow ---
workflow = StateGraph(AgentState)

# 1. Add the nodes (actions)
workflow.add_node("execute", execute_agent_or_tool)
workflow.add_node("reflect", reflect_and_critique)
workflow.add_node("final_answer", generate_final_answer)

# 2. Set the entry point
workflow.set_entry_point("execute")

# 3. Add the conditional edges (the dynamic flow)
# After execution, either finish or go to reflection
workflow.add_conditional_edges(
    "execute", # FROM node
    should_continue, # The router function
    {
        END: END,           # Case 1: Finished immediately
        "reflect": "reflect" # Case 2: Tool called, must reflect
    }
)

# After reflection, either finish (generate answer) or loop back to re-execute
workflow.add_conditional_edges(
    "reflect", 
    should_continue,
    {
        "proceed_to_answer": "final_answer", # Case 1: Reflection successful
        "execute": "execute",                # Case 2: Reflection suggests re-plan/retry
        "final_answer": "final_answer"       # Case 3: Retry limit reached, just generate best answer
    }
)

# After generating the final answer, the graph always ends
workflow.add_edge("final_answer", END)

# Compile the final application graph
app = workflow.compile()


@csrf_exempt
def chat_response(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_prompt = data.get('prompt', '')
            if not user_prompt:
                return JsonResponse({'response': "Please provide a prompt."}, status=400)

            # --- Initialize the State ---
            initial_state = AgentState(
                messages=[HumanMessage(user_prompt)],
                status="start",
                reflection="",
                iterations=0
            )

            # --- Run the Agent Workflow ---
            # app.stream() is better for production, but app.invoke() is simpler for demonstration
            final_state = app.invoke(initial_state)

            # The final answer is the content of the last message in the list
            final_response_text = final_state["messages"][-1].content
            
            return JsonResponse({'response': final_response_text})

        except json.JSONDecodeError:
            return JsonResponse({'response': 'Invalid JSON format in request.'}, status=400)
        except Exception as e:
            # Print the exception to the server console for debugging
            print(f"Agent Execution Error: {e}")
            return JsonResponse({'response': f'An unexpected error occurred during agent execution: {str(e)}'}, status=500)

    return JsonResponse({'response': 'Invalid request method.'}, status=405)

# The setup for llm, tool_calling_llm, workflow, and app remains the same as before

# Use the async decorator and require POST method
@csrf_exempt
@require_http_methods(["POST"])
async def chat_response(request):
    """
    Handles an incoming request and runs the LangGraph agent asynchronously.
    """
    try:
        data = json.loads(request.body)
        user_prompt = data.get('prompt', '')
        if not user_prompt:
            return JsonResponse({'response': "Please provide a prompt."}, status=400)

        # --- Initialize the State ---
        initial_state = AgentState(
            messages=[HumanMessage(content=user_prompt)],
            status="start",
            reflection="",
            iterations=0
        )

        # --- Run the Agent Workflow Asynchronously ---
        # Note the 'await' keyword and the use of 'app.ainvoke'
        final_state = await app.ainvoke(initial_state)

        # The final answer is the content of the last message in the list
        final_response_text = final_state["messages"][-1].content
        
        return JsonResponse({'response': final_response_text})

    except json.JSONDecodeError:
        return JsonResponse({'response': 'Invalid JSON format in request.'}, status=400)
    except Exception as e:
        # In a production environment, you would log 'e'
        return JsonResponse({'response': f'An unexpected error occurred during agent execution: {str(e)}'}, status=500)