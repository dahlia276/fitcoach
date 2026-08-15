from time import perf_counter
import json
from langchain_core.prompts import ChatPromptTemplate
from app.ai.llm import llm
from app.ai.program_validator import ProgramValidator
from app.ai.prompts import SYSTEM_PROMPT
from app.ai.retriever import vectorstore
from app.models.training_profile import TrainingProfile
from app.models.workout_program import WorkoutProgram

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

Exercise Library

{context}
""",
        ),
    ]
)


def generate_program(profile: TrainingProfile):

    total_start = perf_counter()

    query = f"""
Build a {profile.recommended_split} workout program.

Training goal:
{profile.goal}

Experience level:
{profile.experience}

Available equipment:
{profile.equipment}

Avoid exercises unsuitable for:
{profile.injuries}

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
            "injuries": profile.injuries,
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


def modify_program(profile: TrainingProfile, current_plan: dict, instructions: str) -> dict:
    """Edit an existing saved program based on a natural-language instruction.

    Reuses the same retrieval -> structured-output -> validation pipeline as
    generate_program, so any new/replacement exercises are grounded in the
    real exercise library rather than invented, and pass the same duplicate/
    duration checks a freshly generated program does.
    """

    query = f"""
{instructions}

Training goal:
{profile.goal}

Available equipment:
{profile.equipment}

Avoid exercises unsuitable for:
{profile.injuries}
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
            "injuries": profile.injuries,
            "context": context,
        }
    )

    program = planner.invoke(messages)
    program = validator.validate(program, profile)

    return program.model_dump()