from app.db import supabase

def log_workout(workout: dict):
    return (
        supabase
        .table("workout_logs")
        .insert(workout)
        .execute()
        .data[0]
    )


def get_workouts(user_id: str):
    return (
        supabase
        .table("workout_logs")
        .select("*")
        .eq("user_id", user_id)
        .order("completed_at", desc=True)
        .execute()
        .data
    )