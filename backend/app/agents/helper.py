
import re
import json

def extract_json(text: str) -> dict:
    if not text:
        raise ValueError("Empty response from model")

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in response: {text}")

    return json.loads(match.group())