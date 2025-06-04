import json
import re


def extract_json_from_text(text: str):
    print("RAW LLM OUTPUT:\n", text)
    try:
        match = re.search(r"\[\s*{.*?}\s*]", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(text.strip())
    except Exception as e:
        print("JSON Parsing Error:", e)
        return None
