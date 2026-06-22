from langchain_core.tools import tool
from .llm import llm
from langgraph.graph import START, END, StateGraph
from langchain_core.messages.utils import trim_messages, count_tokens_approximately
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage
from typing import TypedDict, Annotated,Literal
from langgraph.prebuilt import ToolNode, tools_condition
from .system_prompt import PROMPT

@tool 
def retrieve_information(file_name: Literal[
    "about",
    "skills",
    "education",
    "contact",
    "projects",
    "project/agent-atlas",
    "project/orion-ai",
    "project/gen-ui",
    "project/orbit",
    ]):
    """
    Retrieve information from the specified file.
    """
    print(file_name)
    with open(f"app/info/{file_name}.txt", "r",encoding="utf-8") as f:
        return f.read()

tools = [retrieve_information]
toolnode = ToolNode(tools)

class MessagesState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat(state: MessagesState):
    stm = trim_messages(
        state["messages"],
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=4000,
        start_on=HumanMessage,
    )
    response = llm.bind_tools(tools).invoke([PROMPT, *stm])
    return {"messages": [response]}


graph = StateGraph(MessagesState)
graph.add_node("chat", chat)
graph.add_node("tools", toolnode)

graph.add_edge(START, "chat")
graph.add_conditional_edges("chat", tools_condition)
graph.add_edge("tools", "chat")
