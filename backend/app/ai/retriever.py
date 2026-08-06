from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

vectorstore = Chroma(
    collection_name="exercise_library",
    embedding_function=embeddings,
    persist_directory="./chroma",
)

retriever = vectorstore.as_retriever(
    search_kwargs={"k": 20}
)