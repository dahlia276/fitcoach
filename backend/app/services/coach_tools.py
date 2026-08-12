"""Small, read-only coaching tools used exclusively by Coach Chat."""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from app.ai.retriever import vectorstore
from app.services.user_service import get_latest_plan, get_training_profile, get_user
from app.services.workout_service import get_workouts


def _json(value: object) -> str:
    return json.dumps(value, default=str)


def retrieve_training_profile(user_id: str) -> str:
    profile = get_training_profile(user_id)
    return _json({"account": get_user(user_id), "training_profile": profile.model_dump() if profile else None})


def retrieve_current_program(user_id: str) -> str:
    return _json(get_latest_plan(user_id) or {"plan": None})


def retrieve_workout_history(user_id: str, days: int = 28) -> str:
    cutoff = datetime.now(timezone.utc) - timedelta(days=max(1, min(days, 365)))
    logs = get_workouts(user_id)
    recent = [log for log in logs if _logged_at(log) >= cutoff]
    return _json(recent)


def search_exercises(query: str, limit: int = 5) -> str:
    docs = vectorstore.similarity_search(query, k=max(1, min(limit, 10)))
    return _json([{
        "id": doc.metadata.get("id"), "name": doc.metadata.get("name"),
        "equipment": doc.metadata.get("equipment"), "primary_muscles": doc.metadata.get("primary_muscles"),
        "description": doc.page_content[:500],
    } for doc in docs])


def explain_exercise(exercise_name: str) -> str:
    """The vector store is the canonical exercise library in the deployed service."""
    return search_exercises(f"exercise instructions and form for {exercise_name}", limit=1)


def suggest_substitutions(exercise_name: str, constraints: str = "") -> str:
    query = f"substitute for {exercise_name}. {constraints}".strip()
    return search_exercises(query, limit=5)


def calculate_weekly_volume(user_id: str) -> str:
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    volume_by_exercise: dict[str, float] = defaultdict(float)
    sets_by_exercise: dict[str, int] = defaultdict(int)
    for log in get_workouts(user_id):
        if _logged_at(log) >= cutoff:
            exercise = log.get("exercise_name", "Unknown")
            sets_by_exercise[exercise] += int(log.get("sets") or 0)
            volume_by_exercise[exercise] += int(log.get("sets") or 0) * int(log.get("reps") or 0) * float(log.get("weight") or 0)
    return _json({"period_days": 7, "sets_by_exercise": sets_by_exercise, "load_volume_by_exercise": volume_by_exercise})


def calculate_recovery(user_id: str) -> str:
    logs = get_workouts(user_id)
    if not logs:
        return _json({"status": "unknown", "reason": "No workout history has been logged yet."})
    latest = max((_logged_at(log) for log in logs), default=None)
    hours_since = round((datetime.now(timezone.utc) - latest).total_seconds() / 3600) if latest else None
    status = "ready" if hours_since is not None and hours_since >= 48 else "recovering"
    return _json({"status": status, "hours_since_last_logged_exercise": hours_since, "note": "This is a training-load estimate, not medical advice."})


def summarize_progress(user_id: str) -> str:
    logs = get_workouts(user_id)
    now = datetime.now(timezone.utc)
    current = [log for log in logs if _logged_at(log) >= now - timedelta(days=28)]
    previous = [log for log in logs if now - timedelta(days=56) <= _logged_at(log) < now - timedelta(days=28)]
    return _json({
        "current_28_day_entries": len(current), "previous_28_day_entries": len(previous),
        "change_in_logged_sets": sum(int(log.get("sets") or 0) for log in current) - sum(int(log.get("sets") or 0) for log in previous),
        "unique_exercises_current_period": len({log.get("exercise_name") for log in current}),
    })


def generate_next_program_block(user_id: str) -> str:
    """A deterministic, non-persisted progression proposal; it never mutates a plan."""
    current = get_latest_plan(user_id)
    if not current or not current.get("plan"):
        return _json({"proposal": None, "reason": "No current program exists."})
    proposal = current["plan"].copy()
    for day in proposal.get("days", []):
        for exercise in day.get("exercises", []):
            exercise["reps"] = int(exercise["reps"]) + 1
            exercise["notes"] = f"{exercise.get('notes', '').strip()} Progression: add one rep if all prescribed reps were completed.".strip()
    return _json({"proposal": proposal, "rule": "Each exercise receives one additional prescribed rep; no plan was saved."})


def _logged_at(log: dict) -> datetime:
    value = log.get("completed_at") or log.get("created_at")
    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
