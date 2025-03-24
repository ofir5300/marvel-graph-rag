from typing import Annotated, Sequence
from typing_extensions import TypedDict

from IPython.display import Image, display

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain.tools import Tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent

from dal.query import query_character


class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

def draw_graph(graph: CompiledStateGraph):
    try:
        png_data = graph.get_graph().draw_mermaid_png()
        with open("llm_graph.png", "wb") as f:
            f.write(png_data)  
    except Exception:
        pass

def build_graph():
    uncompiled_state_graph = StateGraph(State)
    uncompiled_state_graph.add_node("query_agent", query_agent)
    uncompiled_state_graph.add_edge(START, "query_agent")
    uncompiled_state_graph.add_edge("query_agent", END)
    graph = uncompiled_state_graph.compile()
    draw_graph(graph)
    return graph


def query_agent(state: State):
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    tools = [
        Tool(
            name="knowledge_graph_retriever",
            func=lambda character: query_character(character),
            description="Retrieve relevant data about a character and its connections from the knowledge graph."
        )
    ]
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an agent responsible for querying and retrieving data. You can call tool knowledge_graph_retriever to retrieve data about a character and its connections from the knowledge graph."),
        MessagesPlaceholder(variable_name="messages")
    ])
    
    agent = create_react_agent(model=llm, tools=tools,  prompt=prompt,debug=True)
    result = agent.invoke(state)
    content = result.get("messages", [])[-1].content if result and result.get("messages") else "No response generated"
    return {"messages": [AIMessage(content=str(content))]}


def call(question: str):
    try:    
        graph = build_graph()
        result = graph.invoke({"messages": [HumanMessage(content=question)]})
        answer = result['messages'][-1].content
        print(f"\nAnswer: \n\n{answer}")
        return answer 
    except Exception as e:
        print(e)
        return "No result"