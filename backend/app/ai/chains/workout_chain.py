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
User:

Goal: {goal}

Experience: {experience}

Equipment: {equipment}

Injuries: {injuries}

Relevant exercises:

{context}

Generate a structured 4-week workout plan.
""",
        ),
    ]
)


def generate(user):

    docs = retriever.invoke(
        f"""
Goal: {user['goal']}
Equipment: {user['equipment']}
Injuries: {user['injuries']}
"""
    )

    context = "\n\n".join(
        doc.page_content for doc in docs
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

    response = llm.invoke(messages)

    return response.content