from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from llm.agent import create_agent
from llm.shared import AgentName, State


def draw_graph(graph: CompiledStateGraph):
    try:
        png_data = graph.get_graph().draw_mermaid_png()
        with open("llm_graph.png", "wb") as f:
            f.write(png_data)  
    except Exception:
        pass

def build_graph():
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    uncompiled_state_graph = StateGraph(State)
    
    # Add agent nodes
    uncompiled_state_graph.add_node(AgentName.PLANNER.value, create_agent(llm, AgentName.PLANNER))
    uncompiled_state_graph.add_node(AgentName.RELATIONS.value, create_agent(llm, AgentName.RELATIONS)) 
    uncompiled_state_graph.add_node(AgentName.INFORMATION.value, create_agent(llm, AgentName.INFORMATION))
    uncompiled_state_graph.add_node(AgentName.RESOLVER.value, create_agent(llm, AgentName.RESOLVER))
    #  start with planner and decide about the next step
    uncompiled_state_graph.add_edge(START, AgentName.PLANNER.value)
    uncompiled_state_graph.add_conditional_edges(
        AgentName.PLANNER.value,
        lambda state: state["handoff"],
        {
            AgentName.RELATIONS.value: AgentName.RELATIONS.value,
            AgentName.INFORMATION.value: AgentName.INFORMATION.value,
            AgentName.RESOLVER.value: AgentName.RESOLVER.value
        }
    )
    
    # Both agents route back to PLANNER
    uncompiled_state_graph.add_edge(AgentName.RELATIONS.value, AgentName.PLANNER.value)
    uncompiled_state_graph.add_edge(AgentName.INFORMATION.value, AgentName.PLANNER.value)
    
    #  resolver is the last agent and will return the answer
    uncompiled_state_graph.add_edge(AgentName.RESOLVER.value, END)

    graph = uncompiled_state_graph.compile()
    draw_graph(graph)
    return graph
