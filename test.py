from dotenv import load_dotenv
import os
import httpx
from fastapi import FastAPI
from openai import AsyncOpenAI
from pydantic import BaseModel


load_dotenv()
# TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

import asyncio
import time

async def search_tavily(topic: str):
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": "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",
        "query": topic,
        "search_depth": "basic"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        result = response.json()
        # return result
        return result.get("results", [])

if __name__ == "__main__":
    context_results = asyncio.run(search_tavily("probability"))
    # time.sleep(10)
    context = "\n".join([item["content"] for item in context_results])
    print(context)

# context_text = "\n".join([item["content"] for item in context_results["results"]])