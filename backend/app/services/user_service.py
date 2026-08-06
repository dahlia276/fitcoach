from app.db import supabase


def create_user(user):
    return (
        supabase
        .table("users")
        .insert(user)
        .execute()
        .data[0]
    )


def save_plan(user_id, plan):
    return (
        supabase
        .table("workout_plans")
        .insert(
            {
                "user_id": user_id,
                "plan": plan,
            }
        )
        .execute()
    )