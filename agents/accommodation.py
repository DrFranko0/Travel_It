from typing import List, Optional, Union
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from ..models.accommodation import AccommodationDetails, AccommodationSearchCriteria
from ..tools.search import search_tool
from ..tools.scrape import scrape_tool
from ..utils.openrouter_provider import OpenRouterConfig

class AccommodationDeps(BaseModel):
    location: str
    check_in_date: str
    check_out_date: str
    guests: int = 1
    rooms: int = 1
    preference: str 
    max_budget: Optional[float] = None
    amenities: Optional[List[str]] = None

class AccommodationSearchFailed(BaseModel):
    reason: str
    suggestions: List[str]

accommodation_agent = Agent[AccommodationDeps, Union[List[AccommodationDetails], AccommodationSearchFailed]](
    OpenRouterConfig(),  
    output_type=Union[List[AccommodationDetails], AccommodationSearchFailed], 
    system_prompt="""
    You are an accommodation specialist. Your job is to find the best accommodation options based on the user's criteria.
    
    You should:
    1. Search for accommodations matching the location, dates, and number of guests
    2. Consider budget constraints and preferences (budget, mid-range, luxury)
    3. Sort results by best value considering price, location, and amenities
    4. Prioritize accommodations that are in good locations but away from overly touristy areas
    
    Use the search and scrape tools to gather information about available accommodations.
    """,
    tools=[search_tool, scrape_tool],
)

@accommodation_agent.tool
async def estimate_location_quality(ctx: RunContext[AccommodationDeps], location_description: str) -> dict:
    quality_metrics = {
        "tourist_density": 0.0, 
        "convenience": 0.0,      
        "safety": 0.0,          
        "underrated": False,     
    }
    
    tourist_keywords = ["tourist", "popular", "crowded", "famous", "busy"]
    convenience_keywords = ["central", "downtown", "close to", "nearby", "walking distance"]
    safety_keywords = ["safe", "secure", "quiet", "residential", "peaceful"]
    underrated_keywords = ["hidden gem", "off the beaten path", "local favorite", "underrated", "undiscovered"]
    
    description_lower = location_description.lower()
    
    tourist_count = sum(1 for keyword in tourist_keywords if keyword in description_lower)
    quality_metrics["tourist_density"] = min(tourist_count / len(tourist_keywords), 1.0)
    
    convenience_count = sum(1 for keyword in convenience_keywords if keyword in description_lower)
    quality_metrics["convenience"] = min(convenience_count / len(convenience_keywords), 1.0)
    
    safety_count = sum(1 for keyword in safety_keywords if keyword in description_lower)
    quality_metrics["safety"] = min(safety_count / len(safety_keywords), 1.0)
    
    quality_metrics["underrated"] = any(keyword in description_lower for keyword in underrated_keywords)
    
    return quality_metrics
