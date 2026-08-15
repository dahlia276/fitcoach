import json
from pathlib import Path

from app.db import supabase

DATA_PATH = Path(__file__).parent.parent / "data" / "exercises.json"


def load_exercises():
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def get_exercise_library(ids: list[str]):
    if not ids:
        return []
    return (
        supabase
        .table("exercise_library")
        .select("*")
        .in_("id", ids)
        .execute()
        .data
    )