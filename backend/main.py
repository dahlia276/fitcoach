from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.ai.planner import generate_plan
from app.ai.retriever import vectorstore
from app.db import supabase
from app.models.program_request import ProgramRequest
from app.models.workout import WorkoutLog
from app.services.assessment_service import build_training_profile
from app.services.exercise_service import load_exercises
from app.services.user_service import (
    create_user,
    get_training_profile,
    save_plan,
    save_training_profile,
)
from app.services.workout_service import (
    get_workouts,
    log_workout,
)

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
    height: float
    weight: float
    goal: str
    experience: str
    equipment: str
    injuries: str
    training_days: int | None = None
    session_minutes: int | None = None


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/users")
def users():
    return supabase.table("users").select("*").execute().data


@app.post("/onboard")
def onboard(data: Onboard):

    user_data = {
        "name": data.name,
        "age": data.age,
        "height": data.height,
        "weight": data.weight,
        "goal": data.goal,
        "experience": data.experience,
        "equipment": data.equipment,
        "injuries": data.injuries,
    }

    user = create_user(user_data)

    profile = build_training_profile(
        {
            **user_data,
            "training_days": data.training_days,
            "session_minutes": data.session_minutes,
        }
    )

    save_training_profile(user["id"], profile)

    return {
        "user_id": user["id"],
        "training_profile": profile.model_dump(),
    }


@app.post("/program")
def generate_program(request: ProgramRequest):
    profile = get_training_profile(request.user_id)
    program = generate_plan(profile)
    save_plan(request.user_id, program)
    return {
        "program": program,
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


@app.get("/exercises")
def exercises():
    return load_exercises()


@app.get("/search")
def search(q: str):
    docs = vectorstore.similarity_search(q, k=10)
    return [
        {
            "name": d.metadata["name"],
            "content": d.page_content,
        }
        for d in docs
    ]


@app.post("/log")
def create_log(workout: WorkoutLog):
    return log_workout(workout.model_dump())


@app.get("/logs/{user_id}")
def logs(user_id: str):
    return get_workouts(user_id)