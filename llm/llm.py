from typing import Annotated
from typing_extensions import TypedDict
from langchain_openai import OpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from IPython.display import Image, display


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


def query_agent(state: State): # -> State["messages"]:
    llm = OpenAI(temperature=0)
    tools = [
        Tool(
            name="DummyTool",
            func=lambda x: "This is a dummy tool response.",
            description="A dummy tool to satisfy LangChain agent tool requirement."
        )
    ]
    agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
    return {"messages": [agent.invoke(state["messages"])]}
    # return agent.invoke({"question": question})

def draw_graph(graph: CompiledStateGraph):
    try:
        png_data = graph.get_graph().draw_mermaid_png()
        with open("llm_graph.png", "wb") as f:
            f.write(png_data)  
    except Exception:
        pass

def build_graph():
    uncompiled_state_graph = StateGraph(query_agent)
    uncompiled_state_graph.add_node("query_agent", query_agent)
    uncompiled_state_graph.add_edge(START, "query_agent")
    uncompiled_state_graph.add_edge("query_agent", END)
    graph = uncompiled_state_graph.compile()
    draw_graph(graph)
    return graph

def call(question: str):
    graph = build_graph()
    result = graph.invoke({"messages": [{"role": "user", "content": question}]})
    print(result)