from time import perf_counter
import json
from langchain_core.prompts import ChatPromptTemplate
from app.ai.llm import llm
from app.ai.program_validator import ProgramValidator
from app.ai.prompts import SYSTEM_PROMPT
from app.ai.retriever import vectorstore
from app.models.training_profile import TrainingProfile
from app.models.workout_program import WorkoutProgram
from app.services import coach_memory_service
from app.services.user_service import get_plan_history
from app.services.workout_service import get_workouts

planner = llm.with_structured_output(WorkoutProgram)
validator = ProgramValidator()

STRICT_EQUIPMENT = {
    "barbell",
    "dumbbell",
    "kettlebell",
    "cable",
    "machine",
    "bands",
    "medicine ball",
    "exercise ball",
    "ez curl bar",
    "body only",
}

EXPERIENCE_TO_LEVEL = {
    "beginner": "beginner",
    "intermediate": "intermediate",
    "advanced": "expert",
    "expert": "expert",
}


def _level_for_experience(experience: str) -> str | None:
    return EXPERIENCE_TO_LEVEL.get((experience or "").strip().lower())


def _build_metadata_filter(profile: TrainingProfile) -> dict | None:
    """Builds the Chroma `where` filter so retrieval only ever returns
    exercises matching the user's equipment and experience level."""

    conditions = []

    equipment = (profile.equipment or "").strip().lower()
    if equipment in STRICT_EQUIPMENT:
        conditions.append({"equipment": profile.equipment})

    level = _level_for_experience(profile.experience)
    if level:
        conditions.append({"level": level})

    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def _effective_injuries(profile: TrainingProfile, user_id: str | None) -> str:
    """Merges the profile's injuries field with any injury/pain mentions
    captured from chat, so a limitation raised mid-conversation constrains
    generation/modification even if the user never went back and edited
    their profile."""

    base = (profile.injuries or "").strip()
    if not user_id:
        return base

    chat_notes = coach_memory_service.retrieve_injury_notes(user_id)
    if not chat_notes:
        return base

    notes = "; ".join(chat_notes)
    if base:
        return f"{base}\nAlso mentioned in chat: {notes}"
    return f"Mentioned in chat: {notes}"


def _latest_logs_by_exercise(user_id: str) -> dict:
    """Most recent logged weight/reps/RPE per exercise, keyed by exercise_id.

    get_workouts() returns rows ordered most-recent-first, so the first row
    seen for a given exercise is its latest logged performance.
    """

    latest = {}
    for log in get_workouts(user_id):
        exercise_id = log.get("exercise_id")
        if not exercise_id or exercise_id in latest:
            continue
        latest[exercise_id] = log
    return latest


def _previous_program_summary(user_id: str | None) -> str:
    """A compact summary of the user's most recently saved program - including
    the actual weight/reps/RPE they logged against each exercise, where
    available - so a freshly generated program can apply progressive overload
    based on real performance instead of just repeating the planned numbers."""

    if not user_id:
        return "None - this is the user's first program."

    history = get_plan_history(user_id, limit=1)
    if not history:
        return "None - this is the user's first program."

    latest_logs = _latest_logs_by_exercise(user_id)

    lines = []
    for day in history[0]["plan"].get("days", []):
        exercise_parts = []
        for exercise in day.get("exercises", []):
            part = f"{exercise['exercise_name']} planned {exercise['sets']}x{exercise['reps']}"
            log = latest_logs.get(exercise.get("exercise_id"))
            if log and log.get("weight"):
                rpe = log.get("rpe")
                rpe_part = f" @ RPE {rpe}" if rpe else ""
                part += f" (actually logged {log['sets']}x{log['reps']} @ {log['weight']}lb{rpe_part})"
            exercise_parts.append(part)
        lines.append(f"{day.get('name', 'Day')}: {', '.join(exercise_parts)}")
    return "\n".join(lines)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            """
Training Profile

Goal:
{goal}

Split:
{split}

Training Days:
{training_days}

Equipment:
{equipment}

Injuries:
{injuries}

Previous Program (for progressive overload reference)
{previous_program}

Exercise Library

{context}
""",
        ),
    ]
)


def generate_program(profile: TrainingProfile, user_id: str | None = None):

    total_start = perf_counter()

    injuries = _effective_injuries(profile, user_id)
    previous_program = _previous_program_summary(user_id)

    query = f"""
Build a {profile.recommended_split} workout program.

Training goal:
{profile.goal}

Experience level:
{profile.experience}

Available equipment:
{profile.equipment}

Avoid exercises unsuitable for:
{injuries}

Prioritize effective compound movements and balanced exercise selection.
"""

    search_kwargs = {
        "query": query,
        "k": 12,
        "fetch_k": 20,
        "lambda_mult": 0.7,
    }

    metadata_filter = _build_metadata_filter(profile)
    if metadata_filter:
        search_kwargs["filter"] = metadata_filter

    retrieval_start = perf_counter()

    results = vectorstore.max_marginal_relevance_search(**search_kwargs)

    print(f"[Timing] Retrieval: {perf_counter() - retrieval_start:.2f}s")

    print("\n" + "=" * 60)
    print("FITCOACH RETRIEVAL DEBUG")
    print("=" * 60)
    print(f"Equipment filter: {search_kwargs.get('filter')}")
    print(f"Retrieved: {len(results)} exercises")

    seen_ids = set()
    docs = []

    for doc in results:
        exercise_id = doc.metadata["id"]

        if exercise_id in seen_ids:
            continue

        seen_ids.add(exercise_id)
        docs.append(doc)

    if not docs:
        print("⚠️ Chroma returned ZERO exercises.")

    print("\nRetrieved exercises")
    print("=" * 40)

    for d in docs:
        print(
            f"{d.metadata['name']} | "
            f"{d.metadata.get('equipment')} | "
            f"{d.metadata.get('category')}"
        )

    context_start = perf_counter()

    context = "\n\n".join(
        f"""
Exercise ID: {d.metadata["id"]}
Exercise Name: {d.metadata["name"]}
Primary Muscles: {d.metadata.get("primary_muscles", "")}
Equipment: {d.metadata.get("equipment", "")}

Exercise Summary:
{d.page_content[:250]}
"""
        for d in docs
    )

    print(f"[Timing] Context build: {perf_counter() - context_start:.2f}s")

    messages = prompt.invoke(
        {
            "goal": profile.goal,
            "split": profile.recommended_split,
            "training_days": profile.training_days,
            "equipment": profile.equipment,
            "injuries": injuries,
            "previous_program": previous_program,
            "context": context,
        }
    )

    llm_start = perf_counter()

    program = planner.invoke(messages)

    print(f"[Timing] LLM: {perf_counter() - llm_start:.2f}s")

    validation_start = perf_counter()

    program = validator.validate(program, profile, valid_exercise_ids=seen_ids)

    print(f"[Timing] Validation: {perf_counter() - validation_start:.2f}s")

    print(f"[Timing] Total: {perf_counter() - total_start:.2f}s")

    return program.model_dump()


MODIFY_SYSTEM_PROMPT = SYSTEM_PROMPT + """

You are now MODIFYING an existing saved program based on a specific user request - not creating one from scratch.

Modification Rules

- Preserve every day and exercise that the request doesn't affect. Do not regenerate the whole program from first principles.
- Change only what the request requires.
- Any new or replacement exercise MUST use an exact exercise_id from the provided Exercise Library below - never invent one.
- If the request adds or removes a day, keep the remaining days internally consistent (balanced muscle groups, no unintentional duplicates).
- If the request is vague (e.g. "make it harder"), make a reasonable, conservative interpretation and note what you changed in the notes field of the affected exercises.
- Return the COMPLETE updated program, including the unchanged days, not just the edited parts.
"""

modify_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", MODIFY_SYSTEM_PROMPT),
        (
            "human",
            """
Current Program (JSON)
{current_program}

Requested Change
{instructions}

Training Profile

Goal:
{goal}

Equipment:
{equipment}

Injuries:
{injuries}

Exercise Library (use for any new or replacement exercises)

{context}
""",
        ),
    ]
)


def modify_program(profile: TrainingProfile, current_plan: dict, instructions: str, user_id: str | None = None) -> dict:
    """Edit an existing saved program based on a natural-language instruction.

    Reuses the same retrieval -> structured-output -> validation pipeline as
    generate_program, so any new/replacement exercises are grounded in the
    real exercise library rather than invented, and pass the same duplicate/
    duration checks a freshly generated program does.
    """

    injuries = _effective_injuries(profile, user_id)

    query = f"""
{instructions}

Training goal:
{profile.goal}

Available equipment:
{profile.equipment}

Avoid exercises unsuitable for:
{injuries}
"""

    search_kwargs = {
        "query": query,
        "k": 12,
        "fetch_k": 20,
        "lambda_mult": 0.7,
    }

    metadata_filter = _build_metadata_filter(profile)
    if metadata_filter:
        search_kwargs["filter"] = metadata_filter

    results = vectorstore.max_marginal_relevance_search(**search_kwargs)

    seen_ids = set()
    docs = []
    for doc in results:
        exercise_id = doc.metadata["id"]
        if exercise_id in seen_ids:
            continue
        seen_ids.add(exercise_id)
        docs.append(doc)

    context = "\n\n".join(
        f"""
Exercise ID: {d.metadata["id"]}
Exercise Name: {d.metadata["name"]}
Primary Muscles: {d.metadata.get("primary_muscles", "")}
Equipment: {d.metadata.get("equipment", "")}

Exercise Summary:
{d.page_content[:250]}
"""
        for d in docs
    )

    messages = modify_prompt.invoke(
        {
            "current_program": json.dumps(current_plan),
            "instructions": instructions,
            "goal": profile.goal,
            "equipment": profile.equipment,
            "injuries": injuries,
            "context": context,
        }
    )

    program = planner.invoke(messages)
    program = validator.validate(program, profile)

    return program.model_dump()