from app.db import supabase
from app.models.training_profile import TrainingProfile


def create_user(user):
    return (
        supabase
        .table("users")
        .upsert(user, on_conflict="id")
        .execute()
        .data[0]
    )


def save_training_profile(user_id, profile):
    payload = profile.model_dump()
    existing = supabase.table("training_profiles").select("id").eq("user_id", user_id).limit(1).execute().data
    if existing:
        return supabase.table("training_profiles").update(payload).eq("id", existing[0]["id"]).execute()
    return supabase.table("training_profiles").insert({"user_id": user_id, **payload}).execute()


def get_training_profile(user_id) -> TrainingProfile | None:
    result = (
        supabase
        .table("training_profiles")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    if not result.data:
        return None
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


def get_latest_plan(user_id):
    result = (
        supabase.table("workout_plans").select("plan, created_at").eq("user_id", user_id)
        .order("created_at", desc=True).limit(1).execute()
    )
    return result.data[0] if result.data else None
