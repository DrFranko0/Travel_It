from typing import List, Union
from pydantic_ai.models.openai import OpenAIModel
from utils.openrouter_provider import get_openai_provider
from config import OPENROUTER_MODEL
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from models.trip import TripPlan
from tools.search import search_tool
from tools.scrape import scrape_tool
from tools.budget import budget_calculation_tool

class TripPlannerDeps(BaseModel):
    origin: str
    destination: str
    start_date: str
    end_date: str
    travelers: int
    budget: float
    interests: List[str]
    accommodation_preference: str
    transportation_preference: str
    dining_preference: str

class TripPlanningFailed(BaseModel):
    reason: str
    suggestions: List[str]

trip_planner_agent = Agent[TripPlannerDeps, Union[TripPlan, TripPlanningFailed]](
    model=OpenAIModel(
        model_name=OPENROUTER_MODEL,
        provider=get_openai_provider()
    ),
    output_type=Union[TripPlan, TripPlanningFailed],
    system_prompt="""
    You are Travel_It, an advanced AI travel planner. Your job is to create comprehensive travel plans
    tailored to the user's preferences. Focus on recommending less crowded and underrated locations
    while optimizing the budget.
    
    You should:
    1. Coordinate with specialized agents for flights, accommodations, activities, and budget
    2. Ensure the trip plan fits within the user's budget
    3. Prioritize underrated and less crowded locations
    4. Create a day-by-day itinerary with activities
    5. Provide helpful travel tips specific to the destination
    
    Use the tools available to gather information and create the best possible travel plan.
    """,
    tools=[search_tool, scrape_tool, budget_calculation_tool],
)

@trip_planner_agent.tool
async def search_flights(ctx: RunContext[TripPlannerDeps]):

    from .flight_search import flight_search_agent, FlightSearchDeps
    
    deps = FlightSearchDeps(
        origin=ctx.deps.origin,
        destination=ctx.deps.destination,
        departure_date=ctx.deps.start_date,
        return_date=ctx.deps.end_date,
        travelers=ctx.deps.travelers,
        max_budget=ctx.deps.budget * 0.4  
    )
    
    result = await flight_search_agent.run(
        f"Find the best flights from {deps.origin} to {deps.destination}",
        deps=deps,
        usage=ctx.usage
    )
    
    return result.output

@trip_planner_agent.tool
async def search_accommodations(ctx: RunContext[TripPlannerDeps]):
    from .accommodation import accommodation_agent, AccommodationDeps
    
    deps = AccommodationDeps(
        location=ctx.deps.destination,
        check_in_date=ctx.deps.start_date,
        check_out_date=ctx.deps.end_date,
        guests=ctx.deps.travelers,
        preference=ctx.deps.accommodation_preference,
        max_budget=ctx.deps.budget * 0.3  
    )
    
    result = await accommodation_agent.run(
        f"Find the best accommodation in {deps.location}",
        deps=deps,
        usage=ctx.usage
    )
    
    return result.output

@trip_planner_agent.tool
async def plan_activities(ctx: RunContext[TripPlannerDeps]):
    from .activity import activity_planner_agent, ActivityDeps
    
    deps = ActivityDeps(
        location=ctx.deps.destination,
        start_date=ctx.deps.start_date,
        end_date=ctx.deps.end_date,
        travelers=ctx.deps.travelers,
        interests=ctx.deps.interests,
        max_budget=ctx.deps.budget * 0.2  
    )
    
    result = await activity_planner_agent.run(
        f"Plan activities in {deps.location}",
        deps=deps,
        usage=ctx.usage
    )
    
    return result.output
