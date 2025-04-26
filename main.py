import asyncio
import os
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv

from pydantic_ai.usage import Usage, UsageLimits

from agents.trip_planner import trip_planner_agent, TripPlannerDeps
from models.trip import TripPlan
from config import OPENROUTER_API_KEY


load_dotenv()


if not OPENROUTER_API_KEY:
    print("WARNING: OPENROUTER_API_KEY environment variable not set!")
    print("Set this variable to use the OpenRouter API.")

async def plan_trip(
    origin: str,
    destination: str,
    start_date: str,
    end_date: str,
    travelers: int,
    budget: float,
    interests: List[str],
    accommodation_preference: str,
    transportation_preference: str,
    dining_preference: str
) -> Optional[TripPlan]:
    usage = Usage()
    usage_limits = UsageLimits(request_limit=50)
    
    deps = TripPlannerDeps(
        origin=origin,
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        travelers=travelers,
        budget=budget,
        interests=interests,
        accommodation_preference=accommodation_preference,
        transportation_preference=transportation_preference,
        dining_preference=dining_preference
    )
    
    print(f"Planning trip from {origin} to {destination}...")
    result = await trip_planner_agent.run(
        f"Plan a trip from {origin} to {destination}",
        deps=deps,
        usage=usage,
        usage_limits=usage_limits
    )
    
    if hasattr(result, "output") and isinstance(result.output, TripPlan):
        print(f"Trip planning complete!")
        return result.output
    else:
        print(f"Trip planning failed: {result.output.reason}")
        print("Suggestions:")
        for suggestion in result.output.suggestions:
            print(f"- {suggestion}")
        return None

if __name__ == "__main__":
    asyncio.run(plan_trip(
        origin="New York",
        destination="Paris",
        start_date="2025-06-01",
        end_date="2025-06-07",
        travelers=2,
        budget=5000.0,
        interests=["art", "food", "history"],
        accommodation_preference="mid-range",
        transportation_preference="public",
        dining_preference="mid-range"
    ))
