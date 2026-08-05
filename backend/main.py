from fastapi import FastAPI
from app.db import supabase
from pydantic import BaseModel
from app.ai.planner import generate_plan
from app.services.user_service import create_user, save_plan

app = FastAPI()


class Onboard(BaseModel):
    name: str
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

@app.post("/onboard")
def onboard(data: Onboard):

    user = create_user(data.model_dump())

    plan = generate_plan(user)

    save_plan(user["id"], plan)

    return {
        "user_id": user["id"],
        "plan": plan
    }
    
@app.get("/plan/{user_id}")
def get_plan(user_id: str):

    plan = (
        supabase
        .table("workout_plans")
        .select("*")
        .eq("user_id", user_id)
        .execute()
        .data
    )

    return plan