from langchain_core.prompts import ChatPromptTemplate
from app.ai.llm import llm
from app.ai.prompts import SYSTEM_PROMPT
from app.ai.retriever import vectorstore
from app.models.training_profile import TrainingProfile
from app.models.workout_program import WorkoutProgram

planner = llm.with_structured_output(WorkoutProgram)

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
    Build a {profile.recommended_split} workout.
    Goal: {profile.goal}
    Primary equipment:
    {profile.equipment}
    Avoid exercises unsuitable for:
    {profile.injuries}
    """

    results = vectorstore.similarity_search(
    query=query,
    k=25,
    filter={
        "equipment": profile.equipment
    }
)

    docs = results

    print("\nRetrieved exercises:")
    print("=" * 40)

    for d in docs:
        print(
            f"{d.metadata['name']} | "
        f"{d.metadata.get('equipment')} | "
        f"{d.metadata.get('category')}"
    )

    context = "\n\n".join(
        f"""
    Exercise ID: {d.metadata["id"]}
    Exercise Name: {d.metadata["name"]}
    Equipment: {d.metadata.get("equipment","")}
    Level: {d.metadata.get("level","")}

    {d.page_content}
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

    return program.model_dump()