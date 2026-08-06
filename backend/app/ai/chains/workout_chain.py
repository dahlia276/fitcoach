from langchain_core.prompts import ChatPromptTemplate

from app.ai.llm import llm
from app.ai.prompts import SYSTEM_PROMPT
from app.ai.retriever import retriever

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            """
User

Goal: {goal}

Experience: {experience}

Equipment: {equipment}

Injuries: {injuries}

Relevant exercises:

{context}

Generate the workout.
""",
        ),
    ]
)


def generate(user):

    docs = retriever.invoke(
        f"""
Goal: {user["goal"]}

Equipment:
{user["equipment"]}

Injuries:
{user["injuries"]}
"""
    )

    context = "\n\n".join(
        d.page_content
        for d in docs
    )

    chain = prompt | llm

    response = chain.invoke(
        {
            "goal": user["goal"],
            "experience": user["experience"],
            "equipment": user["equipment"],
            "injuries": user["injuries"],
            "context": context,
        }
    )

    return response.content

