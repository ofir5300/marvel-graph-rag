from functools import partial
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langgraph.prebuilt import create_react_agent
from langchain.tools import StructuredTool


from llm.prompts import INFORMATION_PROMPT, PLANNER_PROMPT, RELATIONS_PROMPT, RESOLVER_PROMPT
from llm.shared import AgentName, State, extract_content_from_state, get_prompt_template
from llm.tools import create_characters_detection_tool, create_embeddings_tool, create_knowledge_graph_tool

def retriever_agent(llm: ChatOpenAI, agent_name: AgentName, tools: List[StructuredTool], promptStr: str, state: State):
    prompt = get_prompt_template(promptStr)
    agent = create_react_agent(model=llm, tools=tools,  prompt=prompt, name=agent_name.value)
    result = agent.invoke(state)
    content = extract_content_from_state(result)
    print(f"Agent: {agent_name.value} - {content}")
    return {"messages": [AIMessage(content=str(content))], "sender": agent_name.value}

def resolver_agent(llm: ChatOpenAI, state: State):
    prompt = get_prompt_template(RESOLVER_PROMPT)
    result = prompt.pipe(llm).invoke(state)
    content = result.content
    print(f"Agent: {AgentName.RESOLVER.value} - {content}")
    return {"messages": [AIMessage(content=str(content))], "sender": AgentName.RESOLVER.value}

def planner_agent(llm: ChatOpenAI, state: State)-> State:
    prompt = get_prompt_template(PLANNER_PROMPT)
    extract_characters = lambda input: input.tool_calls[-1].get("args", {}).get("characters", []) if input.tool_calls and input.tool_calls[-1].get("name") == "characters_detection" else []
    
    runnable = prompt.pipe(llm.bind_tools([create_characters_detection_tool()])).pipe(extract_characters)
    characters: List[str] = runnable.invoke(state)
    
    sender_is_relations = state.get("sender") == AgentName.RELATIONS.value
    new_charcters_detected = characters is not None and state.get("characters") is not None and not all(char in characters for char in state.get("characters"))
    if sender_is_relations or new_charcters_detected:
        handoff = "information"
    elif len(state["messages"]) >=3: # both agents have already answered
        handoff = "resolver"
    else:
        handoff = "relations"

    print(f"Agent: {AgentName.PLANNER.value} - characters: {characters} - next: {handoff}")
    return {"characters": characters,"sender": AgentName.PLANNER.value,"handoff": handoff}


def create_agent(llm: ChatOpenAI, agent_name: AgentName):
    if agent_name.value == AgentName.PLANNER.value:
        return partial(planner_agent, llm)
    elif agent_name.value == AgentName.RELATIONS.value:
        return partial(retriever_agent, llm, agent_name, [create_knowledge_graph_tool()], RELATIONS_PROMPT)
    elif agent_name.value == AgentName.INFORMATION.value:
        return partial(retriever_agent, llm, agent_name, [create_embeddings_tool()], INFORMATION_PROMPT)
    elif agent_name.value == AgentName.RESOLVER.value:
        return partial(resolver_agent, llm)