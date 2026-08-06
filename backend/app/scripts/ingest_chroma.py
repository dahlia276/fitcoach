from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from app.db import supabase

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

vectorstore = Chroma(
    collection_name="exercise_library",
    embedding_function=embedding_model,
    persist_directory="./chroma",
)

rows = (
    supabase
    .table("exercise_library")
    .select("*")
    .execute()
    .data
)

documents = []

for row in rows:

    doc = Document(
        page_content=row["search_text"],
        metadata={
            "id": row["id"],
            "name": row["name"],
            "equipment": row["equipment"],
            "category": row["category"],
        },
    )

    documents.append(doc)

vectorstore.add_documents(documents)

print(f"Embedded {len(documents)} exercises.")