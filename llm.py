import requests
import os
import time
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT

load_dotenv()

API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL   = "openai/gpt-oss-20b"
TOKEN   = os.getenv("HF_TOKEN")

if not TOKEN:
    raise ValueError("HF_TOKEN not found. Check your .env file.")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def call_llm(prompt: str, max_tokens: int, temperature: float) -> str:
    """
    Single API call. Always returns a non-empty string.
    Never raises. Returns a descriptive error string on failure.
    """
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    try:
        res = requests.post(API_URL, headers=HEADERS, json=payload, timeout=120)

        if res.status_code != 200:
            return f"API Error {res.status_code}: {res.text[:200]}"

        content = res.json()["choices"][0]["message"]["content"]

        if not content or not content.strip():
            return "Error: Model returned an empty response. Please try again."

        return content.strip()

    except requests.exceptions.Timeout:
        return "Error: Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return "Error: Cannot reach HuggingFace API. Check your internet connection."
    except (KeyError, IndexError) as e:
        return f"Error: Unexpected API response format — {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


def call_with_retry(prompt: str, max_tokens: int, temperature: float, retries: int = 2) -> str:
    """Retries on error responses, with a pause between attempts."""
    for attempt in range(retries):
        result = call_llm(prompt, max_tokens, temperature)
        if not result.startswith("Error:"):
            return result
        if attempt < retries - 1:
            time.sleep(5)
    return result


def get_health_analysis(prompt: str) -> str:
    """Stage 1 — health analysis. 1500 tokens is sufficient."""
    return call_with_retry(prompt, max_tokens=1500, temperature=0.5)


def get_meal_suggestions(prompt: str) -> str:
    """
    Stage 2 — 3 dish suggestions for one meal type.
    3 focused recipes fit easily within 2000 tokens — no truncation.
    """
    return call_with_retry(prompt, max_tokens=2000, temperature=0.8)