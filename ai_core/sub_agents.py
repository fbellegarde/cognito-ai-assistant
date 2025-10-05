# D:\cognito_ai_assistant\ai_core\sub_agents.py

from langchain_core.agents import create_react_agent
from langchain import hub
from langchain.tools import Tool
from tools.research_tools import web_search, rag_retriever # Assume these are defined
from tools.coding_tools import sandboxed_python_interpreter # Crucial safety tool

# --- 1. Research Agent (Access to external information) ---
RESEARCH_AGENT_TOOLS = [
    Tool(name="web_search", func=web_search, description="Tool for real-time internet search."),
    Tool(name="rag_retriever", func=rag_retriever, description="Tool for retrieving internal knowledge base documents."),
]
RESEARCH_PROMPT = hub.pull("hwchase17/react")
RESEARCH_PROMPT.messages[0].prompt.template = (
    "You are the RESEARCH AGENT. Your sole purpose is to gather information "
    "using your provided search and retrieval tools. You CANNOT write code, "
    "execute system commands, or provide final answers based on pure opinion."
)
ResearchAgent = create_react_agent(LLM_MODEL, RESEARCH_AGENT_TOOLS, RESEARCH_PROMPT)


# --- 2. Code Expert Agent (Access to sandboxed execution) ---
CODE_EXPERT_TOOLS = [
    Tool(name="python_interpreter", func=sandboxed_python_interpreter, description="Execute Python code in a secure, sandboxed environment.")
]
CODE_PROMPT = hub.pull("hwchase17/react")
CODE_PROMPT.messages[0].prompt.template = (
    "You are the CODE EXPERT. Your purpose is to write and execute code, fix bugs, "
    "and perform mathematical calculations. You CANNOT use external search or "
    "access any sensitive system files. Always use the sandboxed interpreter."
)
CodeExpert = create_react_agent(LLM_MODEL, CODE_EXPERT_TOOLS, CODE_PROMPT)

# Function to wrap the agent invocation for LangGraph
def research_node(state: AgentState):
    """Invokes the Research Agent."""
    result = ResearchAgent.invoke(state)
    return {"messages": [result["messages"][-1]]}

def code_node(state: AgentState):
    """Invokes the Code Expert Agent."""
    result = CodeExpert.invoke(state)
    return {"messages": [result["messages"][-1]]}