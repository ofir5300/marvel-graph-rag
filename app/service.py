from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from llm.llm import call
from dal.query import query_character

app = FastAPI(title="Marvel Knowledge Graph API")

class Question(BaseModel):
    text: str
    cache: bool = False

class CharacterResponse(BaseModel):
    character: str
    powers: List[str]
    genes: List[str]
    team: Optional[str]
    common_connections: List[object]

@app.post("/question")
async def ask_question(question: Question):
    try:
        response = call(question.text)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph/{character}")
async def get_character_info(character: str):
    try:
        result = query_character(character)
        if not result:
            raise HTTPException(status_code=404, detail=f"Character {character} not found")
        
        return CharacterResponse(
            character=result["Character"],
            powers=[p for p in result["Powers"] if p],
            genes=[g for g in result["Genes"] if g],
            team=result["Team"],
            common_connections=result[4]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
