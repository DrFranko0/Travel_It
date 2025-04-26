from typing import Dict
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = "meta-llama/llama-4-maverick:free"
OPENROUTER_URL = "https://openrouter.ai/api/v1"

def get_openrouter_headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": OPENROUTER_URL,
        "X-Title": OPENROUTER_MODEL,
        "Content-Type": "application/json"
    }
