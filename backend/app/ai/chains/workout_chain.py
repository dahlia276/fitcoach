from langchain_core.prompts import ChatPromptTemplate

from app.ai.llm import llm
from app.ai.prompts import SYSTEM_PROMPT
from app.ai.retriever import retriever
from app.models.workout_plan import WorkoutPlan

planner = llm.with_structured_output(WorkoutPlan)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            """
User Profile

Goal: {goal}
Experience: {experience}
Equipment: {equipment}
Injuries: {injuries}

Available Exercises

{context}

Generate a personalized workout plan.
""",
        ),
    ]
)


def generate(user):

    query = " ".join(
        filter(
            None,
            [
                user["goal"],
                user["experience"],
                user["equipment"],
                user["injuries"],
            ],
        )
    )

    docs = retriever.invoke(query)

    print("\nRetrieved exercises:")
    for doc in docs:
        print(f"- {doc.metadata['name']} ({doc.metadata['id']})")

    context = "\n\n".join(
        f"""
Exercise ID: {doc.metadata["id"]}
Exercise Name: {doc.metadata["name"]}
Equipment: {doc.metadata.get("equipment", "")}
Level: {doc.metadata.get("level", "")}

{doc.page_content}
"""
        for doc in docs
    )

    messages = prompt.invoke(
        {
            "goal": user["goal"],
            "experience": user["experience"],
            "equipment": user["equipment"],
            "injuries": user["injuries"],
            "context": context,
        }
    )

    plan = planner.invoke(messages)

    return plan.model_dump()