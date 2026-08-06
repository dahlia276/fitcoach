from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import supabase
from pydantic import BaseModel
from app.ai.planner import generate_plan
from app.services.user_service import create_user, save_plan

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        "plan": plan,
    }


@app.get("/plan/{user_id}")
def get_plan(user_id: str):
    plan = (
        supabase.table("workout_plans")
        .select("*")
        .eq("user_id", user_id)
        .execute()
        .data
    )

    return plan

from app.services.exercise_service import load_exercises

@app.get("/exercises")
def exercises():
    return load_exercises()

from app.ai.retriever import retriever

@app.get("/search")
def search(q: str):

    docs = retriever.invoke(q)

    return [
        {
            "name": d.metadata["name"],
            "content": d.page_content,
        }
        for d in docs
    ]
    
from app.models.workout import WorkoutLog
from app.services.workout_service import (
    log_workout,
    get_workouts,
)

@app.post("/log")
def create_log(workout: WorkoutLog):
    return log_workout(workout.model_dump())


@app.get("/logs/{user_id}")
def logs(user_id: str):
    return get_workouts(user_id)