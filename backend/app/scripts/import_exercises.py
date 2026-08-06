from pathlib import Path
import json

from tqdm import tqdm

from app.db import supabase

ROOT = Path(__file__).parent.parent / "data" / "raw" / "exercises.json" / "exercises"

exercise_files = list(ROOT.rglob("exercise.json"))

print(f"Found {len(exercise_files)} exercises")

for file in tqdm(exercise_files):

    with open(file, "r") as f:
        exercise = json.load(f)

    search_text = f"""
Name: {exercise.get('name', '')}

Category: {exercise.get('category', '')}

Force: {exercise.get('force', '')}

Level: {exercise.get('level', '')}

Mechanic: {exercise.get('mechanic', '')}

Equipment: {exercise.get('equipment', '')}

Primary muscles:
{", ".join(exercise.get("primaryMuscles", []))}

Secondary muscles:
{", ".join(exercise.get("secondaryMuscles", []))}

Instructions:
{" ".join(exercise.get("instructions", []))}
"""

    row = {
        "id": file.parent.name,
        "name": exercise.get("name"),
        "force": exercise.get("force"),
        "level": exercise.get("level"),
        "mechanic": exercise.get("mechanic"),
        "equipment": exercise.get("equipment"),
        "primary_muscles": exercise.get("primaryMuscles"),
        "secondary_muscles": exercise.get("secondaryMuscles"),
        "instructions": exercise.get("instructions"),
        "category": exercise.get("category"),
        "images": [],
        "search_text": search_text,
    }

    print(file.parent.name)

    supabase.table("exercise_library").upsert(
        row,
        on_conflict="id"
    ).execute()

print("Import complete.")