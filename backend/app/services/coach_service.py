"""Bounded tool-calling orchestration for the personal training chat."""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

from app.ai.llm import llm
from app.services import coach_memory_service as memory
from app.services import coach_tools

SYSTEM_PROMPT = """You are FitCoach, a practical personal trainer. Answer only with the information needed to help the user.
Use a tool whenever the answer depends on their profile, current program, history, exercise details, recovery, progress, or a program-block proposal. Do not claim you retrieved information unless a tool returned it.
For pain or injury: encourage stopping painful movements and appropriate clinical assessment for severe, persistent, sudden, or worsening symptoms. Never diagnose.
Program changes are proposals unless the user explicitly asks to save one; this chat cannot save plans. Keep advice concise, empathetic, and actionable."""


def _tool_definitions(user_id: str):
    @tool
    def retrieve_training_profile() -> str:
        """Get the user's account details and training profile."""
        return coach_tools.retrieve_training_profile(user_id)

    @tool
    def retrieve_current_program() -> str:
        """Get the user's currently saved workout program."""
        return coach_tools.retrieve_current_program(user_id)

    @tool
    def retrieve_workout_history(days: int = 28) -> str:
        """Get completed workout entries from the requested number of days."""
        return coach_tools.retrieve_workout_history(user_id, days)

    @tool
    def search_exercise_library(query: str, limit: int = 5) -> str:
        """Search the Chroma exercise library for exercises matching a need or constraint."""
        return coach_tools.search_exercises(query, limit)

    @tool
    def suggest_exercise_substitutions(exercise_name: str, constraints: str = "") -> str:
        """Find suitable alternatives for an exercise."""
        return coach_tools.suggest_substitutions(exercise_name, constraints)

    @tool
    def explain_exercise(exercise_name: str) -> str:
        """Look up exercise instructions and details."""
        return coach_tools.explain_exercise(exercise_name)

    @tool
    def calculate_weekly_volume() -> str:
        """Calculate logged sets and load volume for the last seven days."""
        return coach_tools.calculate_weekly_volume(user_id)

    @tool
    def calculate_recovery() -> str:
        """Estimate recovery from the spacing of logged training sessions."""
        return coach_tools.calculate_recovery(user_id)

    @tool
    def summarize_progress() -> str:
        """Summarize current versus prior 28-day logged training activity."""
        return coach_tools.summarize_progress(user_id)

    @tool
    def generate_next_program_block() -> str:
        """Create a deterministic, unsaved next-block progression proposal from the active program."""
        return coach_tools.generate_next_program_block(user_id)

    return [
        retrieve_training_profile, retrieve_current_program, retrieve_workout_history,
        search_exercise_library, suggest_exercise_substitutions, explain_exercise,
        calculate_weekly_volume, calculate_recovery, summarize_progress, generate_next_program_block,
    ]


def respond(user_id: str, message: str, chat_id: str | None = None) -> dict[str, Any]:
    clean_message = message.strip()
    if not clean_message:
        raise ValueError("A message is required.")

    thread_id = memory.resolve_thread_id(user_id, chat_id)
    if thread_id is None and chat_id is None:
        thread_id = memory.create_chat(user_id, clean_message)["id"]

    memories = memory.retrieve_relevant_memories(user_id, clean_message)
    recent_messages = memory.retrieve_recent_messages(user_id, chat_id if chat_id == "legacy" else thread_id)
    memory_context = "\n".join(f"- [{item['category']}] {item['content']}" for item in memories) or "None retrieved."
    messages = [
        SystemMessage(content=f"{SYSTEM_PROMPT}\n\nRelevant long-term memory:\n{memory_context}"),
        *[HumanMessage(content=item["content"]) if item["role"] == "user" else AIMessage(content=item["content"]) for item in recent_messages],
        HumanMessage(content=clean_message),
    ]
    tools = _tool_definitions(user_id)
    tools_by_name = {item.name: item for item in tools}
    model = llm.bind_tools(tools)
    tools_used: list[str] = []

    # This is deliberately bounded orchestration, not an unrestricted agent loop.
    for _ in range(3):
        response = model.invoke(messages)
        messages.append(response)
        if not response.tool_calls:
            answer = str(response.content).strip()
            break
        for call in response.tool_calls:
            tool_name = call["name"]
            selected_tool = tools_by_name.get(tool_name)
            if not selected_tool:
                continue
            result = selected_tool.invoke(call["args"])
            messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))
            tools_used.append(tool_name)
    else:
        answer = "I have the relevant training details, but I could not complete that request in this turn. Please try a more specific question."

    memory.save_message(user_id, "user", clean_message, thread_id)
    memory.save_message(user_id, "assistant", answer, thread_id)
    memory.extract_durable_memories(user_id, clean_message)
    return {"reply": answer, "tools_used": tools_used, "thread_id": thread_id or "legacy"}
