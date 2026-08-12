from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from app.db import supabase

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

vectorstore = Chroma(
    collection_name="exercise_library",
    embedding_function=embeddings,
    persist_directory="./chroma",
)


def initialize_vectorstore():
    """
    Ensure the Chroma vector store is populated.

    If the collection is empty (e.g. first Railway deployment),
    rebuild it from the exercise_library table in Supabase.
    """

    existing = vectorstore.get()

    if existing["ids"]:
        print(f"✓ Loaded existing Chroma index ({len(existing['ids'])} exercises)")
        return

    print("\nBuilding Chroma index from Supabase...")

    exercises = (
        supabase
        .table("exercise_library")
        .select("*")
        .execute()
        .data
    )

    documents = []

    ids = []

    for exercise in exercises:

        instructions = "\n".join(exercise.get("instructions") or [])

        document = Document(
            page_content=f"""
{exercise["name"]}

Primary muscles:
{", ".join(exercise.get("primary_muscles") or [])}

Secondary muscles:
{", ".join(exercise.get("secondary_muscles") or [])}

Instructions

{instructions}
""",
            metadata={
                "id": exercise["id"],
                "name": exercise["name"],
                "equipment": exercise.get("equipment") or "",
                "category": exercise.get("category") or "",
                "level": exercise.get("level") or "",
                "force": exercise.get("force") or "",
                "mechanic": exercise.get("mechanic") or "",
                "primary_muscles": ", ".join(exercise.get("primary_muscles") or []),
                "secondary_muscles": ", ".join(exercise.get("secondary_muscles") or []),
            },
        )

        documents.append(document)
        ids.append(exercise["id"])

    vectorstore.add_documents(
        documents=documents,
        ids=ids,
    )

    print(f"✓ Indexed {len(documents)} exercises into Chroma.")