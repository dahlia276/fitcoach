from fastapi import FastAPI
from app.db import supabase

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/users")
def users():
    return supabase.table("users").select("*").execute().data