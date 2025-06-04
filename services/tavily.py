import os
import httpx
from dotenv import load_dotenv

load_dotenv(dotenv_path="api_key.env")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


async def search_tavily(topic: str):
    url = "https://api.tavily.com/search"
    payload = {"api_key": TAVILY_API_KEY, "query": topic, "search_depth": "advanced"}

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(url, json=payload)
        result = response.json()
        return result.get("results", [])
