from fastapi import FastAPI
from app.db import supabase
from pydantic import BaseModel
from app.ai.llm import llm
from app.ai.prompts import SYSTEM_PROMPT

app = FastAPI()


class Onboard(BaseModel):
    age: int
    weight: float
    goal: str
    experience: str
    equipment: str
    injuries: str

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/users")
def users():
    return supabase.table("users").select("*").execute().data

@app.post("/generate-plan")
def generate_plan(data: Onboard):

    prompt = f"""
{SYSTEM_PROMPT}

Age: {data.age}
Weight: {data.weight}
Goal: {data.goal}
Experience: {data.experience}
Equipment: {data.equipment}
Injuries: {data.injuries}
"""

    response = llm.invoke(prompt)

    return {
        "plan": response.content
    }