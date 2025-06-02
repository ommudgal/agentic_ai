from fastapi import FastAPI
from pydantic import BaseModel
import httpx
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv(dotenv_path="api_key.env")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# openai.api_key = OPENAI_API_KEY

client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=groq_api_key  # Replace with your Groq API key
)

app = FastAPI()

class QueryInput(BaseModel):
    topic: str
    difficulty: str
    type: str  # e.g., "MCQ", "Descriptive"
    number : int 

@app.post("/query")
async def receive_query(query: QueryInput):
    # Step 1: Search Tavily
    context_results = await search_tavily(query.topic)
    context_text =  "\n".join([item["content"] for item in context_results])

    # Step 2: Generate Question with LLM
    prompt = f"""
You are a helpful educational agent .

Context: {context_text}

Generate {query.number}  {query.difficulty} level {query.type} question based on the above context.
Respond in JSON format like:
{{
  "question": "...",
  "answer": "..."
}}
"""
    response = await client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[
            {"role": "system", "content": "You generate questions for educational purposes."},
            {"role": "user", "content": prompt}
        ],
        # temperature=0.7,
        max_tokens=1000
    )

    llm_output= response.choices[0].message.content


    # llm_output = response["choices"][0]["message"]["content"]

    return {
        "message": "Question generated successfully",
        "topic": query.topic,
        "context": context_text,
        "question_generated": llm_output
    }

async def search_tavily(topic: str):
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": topic,
        "search_depth": "advanced"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        result = response.json()
        return result.get("results", [])