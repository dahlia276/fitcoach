from fastapi import Depends, FastAPI, HTTPException, status
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
    get_latest_plan,
    get_user,
    get_training_profile,
    save_plan,
    save_training_profile,
)
from app.auth import get_current_user_id
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


@app.post("/onboard")
def onboard(data: Onboard, user_id: str = Depends(get_current_user_id)):

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

    create_user({
        "id": user_id,
        "name": data.name,
        "age": data.age,
        "height": data.height,
        "weight": data.weight,
        "goal": data.goal,
        "experience": data.experience,
        "equipment": data.equipment,
        "injuries": data.injuries,
    })

    profile = build_training_profile(
        {
            **user_data,
            "training_days": data.training_days,
            "session_minutes": data.session_minutes,
        }
    )

    save_training_profile(user_id, profile)

    return {
        "training_profile": profile.model_dump(),
    }


@app.post("/program")
def generate_program(user_id: str = Depends(get_current_user_id)):
    profile = get_training_profile(user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Complete onboarding before generating a program.")
    program = generate_plan(profile)
    save_plan(user_id, program)
    return {
        "program": program,
    }


@app.get("/profile/me")
def get_profile(user_id: str = Depends(get_current_user_id)):
    profile = get_training_profile(user_id)
    return {"profile": profile.model_dump() if profile else None, "account": get_user(user_id)}


@app.get("/plan")
def get_plan(user_id: str = Depends(get_current_user_id)):
    return get_latest_plan(user_id)


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
def create_log(workout: WorkoutLog, user_id: str = Depends(get_current_user_id)):
    return log_workout({**workout.model_dump(), "user_id": user_id})


@app.get("/logs")
def logs(user_id: str = Depends(get_current_user_id)):
    return get_workouts(user_id)
