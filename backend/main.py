from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.ai.planner import generate_plan
from app.ai.retriever import (
    initialize_vectorstore,
    vectorstore,
)
from app.db import supabase
from app.models.program_request import ProgramRequest
from app.models.workout import WorkoutLog
from app.services.assessment_service import build_training_profile
from app.services.exercise_service import get_exercise_library, load_exercises
from app.services.user_service import (
    create_user,
    get_latest_plan,
    get_user,
    get_training_profile,
    save_plan,
    save_training_profile,
)
from app.auth import get_current_user_id
from app.services import coach_memory_service
from app.services.coach_service import respond as coach_respond
from app.services.workout_service import (
    get_workouts,
    log_workout,
)

app = FastAPI()

@app.on_event("startup")
def startup():

    initialize_vectorstore()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://fitcoach-nine-beryl.vercel.app",
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


class CoachChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


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


@app.get("/exercises/library")
def exercise_library(ids: str):
    id_list = [i.strip() for i in ids.split(",") if i.strip()]
    return get_exercise_library(id_list)


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


@app.post("/coach/chat")
def coach_chat(data: CoachChatRequest, user_id: str = Depends(get_current_user_id)):
    try:
        return coach_respond(user_id, data.message, data.thread_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error


@app.get("/coach/chats")
def list_coach_chats(user_id: str = Depends(get_current_user_id)):
    return {"chats": coach_memory_service.list_chats(user_id)}


@app.get("/coach/chats/{chat_id}")
def get_coach_chat(chat_id: str, user_id: str = Depends(get_current_user_id)):
    try:
        return {"messages": coach_memory_service.retrieve_chat_messages(user_id, chat_id)}
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    
@app.get("/debug/chroma")
def debug_chroma():
    docs = vectorstore.similarity_search("bench press", k=5)

    return {
        "count": len(docs),
        "results": [
            {
                "id": d.metadata.get("id"),
                "name": d.metadata.get("name"),
            }
            for d in docs
        ],
    }
