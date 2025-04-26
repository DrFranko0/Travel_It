from typing import List, Optional, Union
from datetime import datetime
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from ..models.flight import FlightDetails, FlightSearchCriteria
from ..tools.search import search_tool
from ..tools.scrape import scrape_tool
from ..utils.openrouter_provider import OpenRouterConfig

class FlightSearchDeps(BaseModel):
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    travelers: int = 1
    max_budget: Optional[float] = None
    preferred_airlines: Optional[List[str]] = None

class FlightSearchFailed(BaseModel):
    reason: str
    suggestions: List[str]


flight_search_agent = Agent[FlightSearchDeps, Union[List[FlightDetails], FlightSearchFailed]](
    OpenRouterConfig(),  
    output_type=Union[List[FlightDetails], FlightSearchFailed],  # type: ignore
    system_prompt="""
    You are a flight search specialist. Your job is to find the best flight options based on the user's criteria.
    
    You should:
    1. Search for flights matching the origin, destination, dates, and number of travelers
    2. Consider budget constraints if provided
    3. Sort results by best value (considering price, duration, and stops)
    4. Provide details about each flight option
    
    Use the search and scrape tools to gather information about available flights.
    """,
    tools=[search_tool, scrape_tool],
)

@flight_search_agent.tool
async def format_flight_date(ctx: RunContext[FlightSearchDeps], date_str: str) -> str:
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        return date_str
