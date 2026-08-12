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
        "k": 25,
        "fetch_k": 40,
        "lambda_mult": 0.7,
    }

    if equipment in strict_equipment:
        search_kwargs["filter"] = {"equipment": profile.equipment}

    results = vectorstore.max_marginal_relevance_search(**search_kwargs)
    print("\n" + "=" * 60)
    print("FITCOACH RETRIEVAL DEBUG")
    print("=" * 60)
    print(f"Query:\n{query}")
    print(f"Equipment filter: {search_kwargs.get('filter')}")
    print(f"Raw retrieval count: {len(results)}")

    seen_ids = set()
    docs = []

    for doc in results:
        exercise_id = doc.metadata["id"]

        if exercise_id in seen_ids:
            continue

        seen_ids.add(exercise_id)
        docs.append(doc)
        if not docs:
            print("⚠️  Chroma returned ZERO exercises.")

    print("\nRetrieved exercises:")
    print("=" * 40)

    for d in docs:
        print(
            f"{d.metadata['name']} | "
            f"{d.metadata.get('equipment')} | "
            f"{d.metadata.get('category')}"
        )

    MAX_CONTENT_CHARS = 1200
    context = "\n\n".join(
        f"""
Exercise ID: {d.metadata["id"]}
Exercise Name: {d.metadata["name"]}
Primary Muscles: {d.metadata.get("primary_muscles", "")}
Secondary Muscles: {d.metadata.get("secondary_muscles", "")}
Category: {d.metadata.get("category", "")}
Mechanic: {d.metadata.get("mechanic", "")}
Force: {d.metadata.get("force", "")}
Equipment: {d.metadata.get("equipment", "")}
Level: {d.metadata.get("level", "")}

{d.page_content[:MAX_CONTENT_CHARS]}
"""
        for d in docs
    )

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

    program = planner.invoke(messages)
    program = validator.validate(program, profile)
    return program.model_dump()