from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Literal, Sequence, List
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    characters: List[str]
    handoff: Literal["relations", "information", "resolver"]
    sender: Literal["planner", "relations", "information", "resolver"]


@dataclass
class AgentName(Enum):
    PLANNER = "planner"
    RELATIONS = "relations"
    INFORMATION = "information"
    RESOLVER = "resolver"

def get_prompt_template(prompt: str):
    return ChatPromptTemplate.from_messages([
        ("system", prompt),
        MessagesPlaceholder(variable_name="messages")
    ])

def extract_content_from_state(state: State):
    return state.get("messages", [])[-1].content if state and state.get("messages") else "No response generated"