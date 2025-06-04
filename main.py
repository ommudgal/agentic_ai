from fastapi import FastAPI
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv
import os
import json
import re
from openai import AsyncOpenAI

# Load environment variables
load_dotenv(dotenv_path="api_key.env")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY
)

app = FastAPI()

class QueryInput(BaseModel):
    topic: str
    difficulty: str
    type: str  # "mcq" or "integer"
    number: int

class MCQQuestion(BaseModel):
    question: str
    option_A: str
    option_B: str
    option_C: str
    option_D: str
    answer: str

class IntegerTypeQuestion(BaseModel):
    question: str
    answer: float

# Improved extractor
def extract_json_from_text(text: str):
    print("RAW LLM OUTPUT:\n", text) 
    match = re.search(r"(\[\s*{.*?}\s*])", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError as e:
            print("JSON decode error:", e)
            return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print("Fallback JSON decode error:", e)
        return None

@app.post("/query")
async def receive_query(query: QueryInput):
    context_results = await search_tavily(query.topic)
    context_text = "\n".join([item["content"] for item in context_results])

    if query.type.lower() == "mcq":
        prompt = f"""
You are a helpful educational agent that generates MCQ-type questions for CBSE Class 12 students.

Context: {context_text}

Generate {query.number} {query.difficulty}-level MCQ questions strictly from the following topics:
- Probability
- Statistics
- Linear Algebra
- Vector 3D
- Basic C programming
- Basic Python programming
- Matrix
- Determinant


Use only content from the context relevant to these topics.

Return a raw JSON list in this format:
[
  {{
    "question": "...",
    "option_A": "...",
    "option_B": "...",
    "option_C": "...",
    "option_D": "...",
    "answer": "..."
  }}
]

Do not include explanations, markdown, or headings. Output only JSON.
"""
    elif query.type.lower() == "integer":
        prompt = f"""
You are a helpful educational agent that generates Integer-type questions for CBSE Class 12 students.

Context: {context_text}

Generate {query.number} {query.difficulty}-level Integer-type questions strictly from the following topics:
- Probability
- Statistics
- Linear Algebra
- Vector 3D
- Basic C programming
- Basic Python programming
- Matrix
- Determinant

Use only content from the context relevant to these topics.

Return a raw JSON list in this format:
[
  {{
    "question": "...",
    "answer": 42
  }}
]

Do not include explanations, markdown, or headings. Output only JSON.
"""
    else:
        return {"error": "Invalid question type. Use 'mcq' or 'integer'."}

    response = await client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[
            {"role": "system", "content": "You generate structured educational questions for Class 12."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500
    )

    raw_output = response.choices[0].message.content
    parsed_output = extract_json_from_text(raw_output)

    # If no JSON found
    if parsed_output is None:
        return {
            "message": "Failed to extract JSON. Check model output.",
            "raw_output": raw_output
        }

    # Try Pydantic validation
    try:
        if query.type.lower() == "mcq":
            questions = [MCQQuestion(**q) for q in parsed_output]
        else:
            questions = [IntegerTypeQuestion(**q) for q in parsed_output]
    except Exception as e:
        return {
            "message": "Validation failed",
            "error": str(e),
            "raw_output": parsed_output
        }

    return {
        "message": "Questions generated successfully",
        "topic": query.topic,
        "question_type": query.type,
        "questions": questions
    }

# Tavily Search
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
