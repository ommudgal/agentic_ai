from fastapi import FastAPI
from models.schemas import QueryInput, MCQQuestion, IntegerTypeQuestion
from services.generator import generate_questions

app = FastAPI()


@app.post("/query")
async def receive_query(query: QueryInput):
    return await generate_questions(query)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
