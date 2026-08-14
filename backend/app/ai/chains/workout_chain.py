from time import perf_counter

from langchain_core.prompts import ChatPromptTemplate

from app.ai.llm import llm
from app.ai.program_validator import ProgramValidator
from app.ai.prompts import SYSTEM_PROMPT
from app.ai.retriever import vectorstore
from app.models.training_profile import TrainingProfile
from app.models.workout_program import WorkoutProgram

planner = llm.with_structured_output(WorkoutProgram)
validator = ProgramValidator()

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

    equipment = (profile.equipment or "").strip().lower()

    strict_equipment = {
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

    search_kwargs = {
        "query": query,
        "k": 12,
        "fetch_k": 20,
        "lambda_mult": 0.7,
    }

    if equipment in strict_equipment:
        search_kwargs["filter"] = {"equipment": profile.equipment}

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

    program = validator.validate(program, profile)

    print(f"[Timing] Validation: {perf_counter() - validation_start:.2f}s")

    print(f"[Timing] Total: {perf_counter() - total_start:.2f}s")

    return program.model_dump()