import os
from pydantic_ai.providers.openai import OpenAIProvider

def get_openai_provider():
    return OpenAIProvider(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY", ""),
    )