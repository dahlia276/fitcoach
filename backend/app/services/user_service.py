from app.db import supabase
from app.models.training_profile import TrainingProfile


def create_user(user):
    return (
        supabase
        .table("users")
        .insert(user)
        .execute()
        .data[0]
    )


def save_training_profile(user_id, profile):
    return (
        supabase
        .table("training_profiles")
        .insert(
            {
                "user_id": user_id,
                **profile.model_dump(),
            }
        )
        .execute()
    )


def get_training_profile(user_id) -> TrainingProfile:
    result = (
        supabase
        .table("training_profiles")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    profile = result.data[0]
    profile.pop("id", None)
    profile.pop("user_id", None)
    profile.pop("created_at", None)
    return TrainingProfile(**profile)


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