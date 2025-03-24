from typing import List
from langchain.tools import Tool, StructuredTool
# from marshmallow import Schema
from openai import BaseModel
from pydantic import BaseModel, Field


from dal.query import query_character
from llm.embeddings import Embedder

def create_embeddings_tool() -> Tool:
    embedder = Embedder()
    retriever = embedder.vectorstore.as_retriever(search_kwargs={"k": 2, "score_threshold": 0.8})
    return Tool(
        name="search_character_info",
        description="Search for information about a character in the knowledge base. Input should be text includes a name of a character.",
        func=lambda query: retriever.invoke(query),
    )

def create_knowledge_graph_tool(embedder: Embedder = None) -> Tool:
    return Tool(
        name="knowledge_graph_retriever",
        #  todo init neo4j instance here??
        func=lambda character: query_character(character),
        description="Retrieve relevant data about a character and its relations from the knowledge graph."
    )

class CharacterDetectionSchema(BaseModel):
    """Detects characters in the entire conversation."""
    characters: List[str] = Field(description="List of characters to detected.")
# @tool(args_schema=CharacterDetectionSchema)
def create_characters_detection_tool() -> Tool:
    return Tool(
        name="characters_detection",
        args_schema=CharacterDetectionSchema,
        func=lambda characters: characters,
        description="Detects characters in the entire conversation."
    )