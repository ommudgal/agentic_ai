import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
from models.schemas import QueryInput, MCQQuestion, IntegerTypeQuestion
from services.tavily import search_tavily
from utils.parser import extract_json_from_text
from pydantic import ValidationError

# Load environment variables
load_dotenv(dotenv_path="api_key.env")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

ALLOWED_TOPICS = [
    "Probability",
    "Statistics",
    "Linear Algebra",
    "Vector 3D",
    "Basic C programming",
    "Basic Python programming",
    "Matrix",
    "Determinant",
]

client = AsyncOpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ_API_KEY)


async def generate_questions(query: QueryInput):
    if query.topic not in ALLOWED_TOPICS:
        return {
            "message": f"Topic '{query.topic}' is not allowed.",
            "allowed_topics": ALLOWED_TOPICS,
        }
    context_results = await search_tavily(query.topic)
    context_text = "\n".join([item["content"] for item in context_results])

    base_prompt = f"""
Context: {context_text}

Generate {query.number} {query.difficulty}-level {"MCQ" if query.type == "mcq" else "Integer-type"} questions strictly from the topic: {query.topic}.

Return JSON only in this format:
"""

    prompt = base_prompt + (
        """
[
  {
    "question": "...",
    "option_A": "...",
    "option_B": "...",
    "option_C": "...",
    "option_D": "...",
    "answer": "..."
  }
]
"""
        if query.type == "mcq"
        else """
[
  {
    "question": "...",
    "answer": 42
  }
]
"""
    )

    try:
        response = await client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[
                {
                    "role": "system",
                    "content": "You generate structured educational questions for Class 12.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
        )

        raw_output = response.choices[0].message.content
        if raw_output is None:
            return {"message": "No content received from model."}
        parsed_output = extract_json_from_text(raw_output)

        if parsed_output is None:
            return {"message": "Failed to extract JSON.", "raw_output": raw_output}

        if query.type == "mcq":
            questions = [MCQQuestion(**q) for q in parsed_output]
        else:
            questions = [IntegerTypeQuestion(**q) for q in parsed_output]

        return {
            "message": "Questions generated successfully",
            "topic": query.topic,
            "question_type": query.type,
            "questions": questions,
        }

    except ValidationError as ve:
        return {
            "message": "Validation failed",
            "errors": ve.errors(),
        }
    except Exception as e:
        return {"error": str(e)}
