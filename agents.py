import os
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

load_dotenv()

together_key = os.getenv("TOGETHER_API_KEY")
model = OpenAIModel(
    "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    provider=OpenAIProvider(
        base_url="https://api.together.xyz/v1",
        api_key=together_key
    )
)

intent_agent = Agent(model,
    system_prompt=(
        "Classify the user query into exactly one of: "
        "Live Status, Delay Analysis, Trip Planning. "
        "Respond with the single label."
    )
)

status_agent = Agent(model,
    system_prompt=(
        "You are a flight-status assistant. Given flight+weather+traffic data, "
        "generate a concise, user-friendly status summary."
    )
)
delay_agent = Agent(model,
    system_prompt=(
        "You are a delay analyst. Given a list of historical flight delays, "
        "summarize the delay trends."
    )
)
trip_agent = Agent(model,
    system_prompt=(
        "You are a trip-planning assistant. Given flight departure time, traffic, and weather, "
        "advise when the user should leave to catch their flight."
    )
)
