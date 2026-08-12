"""Persistence and retrieval for Coach Chat's short- and long-term memory."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from app.db import supabase

_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "can", "do", "for", "from",
    "how", "i", "in", "is", "it", "me", "my", "of", "on", "or", "please",
    "the", "this", "to", "was", "what", "with", "you", "your",
}


def _terms(text: str) -> set[str]:
    return {
        term for term in re.findall(r"[a-zA-Z][a-zA-Z'-]+", text.lower())
        if term not in _STOP_WORDS
    }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _truncate_title(text: str, limit: int = 60) -> str:
    normalized = " ".join(text.split())
    if not normalized:
        return "New chat"
    return normalized if len(normalized) <= limit else f"{normalized[:limit - 1].rstrip()}…"


def _legacy_chat_summary(user_id: str) -> dict[str, str] | None:
    latest = (
        supabase.table("coach_messages")
        .select("created_at")
        .eq("user_id", user_id)
        .is_("thread_id", "null")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
        .data
    )
    if not latest:
        return None
    title_row = (
        supabase.table("coach_messages")
        .select("content")
        .eq("user_id", user_id)
        .is_("thread_id", "null")
        .eq("role", "user")
        .order("created_at")
        .limit(1)
        .execute()
        .data
    )
    title_source = title_row[0]["content"] if title_row else "Previous chat"
    return {
        "id": "legacy",
        "title": _truncate_title(title_source),
        "updated_at": latest[0]["created_at"],
    }


def create_chat(user_id: str, opening_message: str) -> dict[str, str]:
    created = (
        supabase.table("coach_threads")
        .insert({
            "user_id": user_id,
            "title": _truncate_title(opening_message),
            "updated_at": _now_iso(),
        })
        .execute()
        .data
    )
    return created[0]


def list_chats(user_id: str) -> list[dict[str, str]]:
    result = (
        supabase.table("coach_threads")
        .select("id, title, updated_at")
        .eq("user_id", user_id)
        .order("updated_at", desc=True)
        .execute()
    )
    chats = result.data or []
    legacy = _legacy_chat_summary(user_id)
    if legacy:
        chats.append(legacy)
    return sorted(chats, key=lambda chat: chat["updated_at"], reverse=True)


def chat_exists(user_id: str, chat_id: str) -> bool:
    if chat_id == "legacy":
        return _legacy_chat_summary(user_id) is not None
    result = (
        supabase.table("coach_threads")
        .select("id")
        .eq("user_id", user_id)
        .eq("id", chat_id)
        .limit(1)
        .execute()
        .data
    )
    return bool(result)


def retrieve_chat_messages(user_id: str, chat_id: str) -> list[dict[str, str]]:
    if not chat_exists(user_id, chat_id):
        raise ValueError("Chat not found.")
    query = (
        supabase.table("coach_messages")
        .select("role, content, created_at")
        .eq("user_id", user_id)
        .order("created_at")
    )
    if chat_id == "legacy":
        query = query.is_("thread_id", "null")
    else:
        query = query.eq("thread_id", chat_id)
    return query.execute().data or []


def save_message(user_id: str, role: str, content: str, thread_id: str | None = None) -> None:
    supabase.table("coach_messages").insert({
        "user_id": user_id,
        "thread_id": thread_id,
        "role": role,
        "content": content,
    }).execute()
    if thread_id:
        supabase.table("coach_threads").update({"updated_at": _now_iso()}).eq("id", thread_id).eq("user_id", user_id).execute()


def retrieve_recent_messages(user_id: str, thread_id: str | None, limit: int = 8) -> list[dict[str, str]]:
    query = (
        supabase.table("coach_messages")
        .select("role, content, created_at")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
    )
    if thread_id is None:
        return []
    if thread_id == "legacy":
        query = query.is_("thread_id", "null")
    else:
        query = query.eq("thread_id", thread_id)
    result = query.execute()
    return list(reversed(result.data or []))


def retrieve_relevant_memories(user_id: str, query: str, limit: int = 8) -> list[dict[str, str]]:
    """Retrieve only memories related to this turn instead of injecting all history."""
    result = (
        supabase.table("coach_memories")
        .select("category, content, updated_at")
        .eq("user_id", user_id)
        .order("updated_at", desc=True)
        .limit(100)
        .execute()
    )
    query_terms = _terms(query)

    def score(memory: dict[str, str]) -> tuple[int, str]:
        overlap = len(query_terms & _terms(memory["content"]))
        return (overlap, memory.get("updated_at", ""))

    ranked = sorted(result.data or [], key=score, reverse=True)
    relevant = [memory for memory in ranked if score(memory)[0] > 0]
    # Recent durable preferences remain useful when a message has no keyword overlap.
    return (relevant or ranked)[:limit]


def resolve_thread_id(user_id: str, chat_id: str | None) -> str | None:
    if chat_id is None:
        return None
    if not chat_exists(user_id, chat_id):
        raise ValueError("Chat not found.")
    return None if chat_id == "legacy" else chat_id


def remember(user_id: str, category: str, content: str) -> None:
    normalized_content = " ".join(content.split())
    if not normalized_content:
        return
    existing = (
        supabase.table("coach_memories")
        .select("id")
        .eq("user_id", user_id)
        .eq("category", category)
        .eq("content", normalized_content)
        .limit(1)
        .execute()
        .data
    )
    timestamp = _now_iso()
    if existing:
        supabase.table("coach_memories").update({"updated_at": timestamp}).eq("id", existing[0]["id"]).execute()
        return
    supabase.table("coach_memories").insert({
        "user_id": user_id,
        "category": category,
        "content": normalized_content,
        "updated_at": timestamp,
    }).execute()


def extract_durable_memories(user_id: str, message: str) -> None:
    """Store explicit user facts deterministically; avoid inferring sensitive details."""
    lowered = message.lower()
    categories: list[str] = []
    if any(word in lowered for word in ("hurt", "pain", "injury", "injured", "sore")):
        categories.append("injury_feedback")
    if any(word in lowered for word in ("prefer", "don't like", "do not like", "hate", "love")):
        categories.append("preference")
    if any(word in lowered for word in ("goal", "stronger", "lose weight", "build muscle", "hypertrophy")):
        categories.append("goal")
    if any(word in lowered for word in ("swap", "substitute", "replace")):
        categories.append("substitution")
    for category in categories:
        remember(user_id, category, message)
