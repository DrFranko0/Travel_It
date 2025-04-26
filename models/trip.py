from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field

from .flight import FlightDetails
from .accommodation import AccommodationDetails
from .activity import ActivitySuggestion

class DailyItinerary(BaseModel):
    """Daily itinerary with activities and schedule"""
    day: int
    date: date
    activities: List[ActivitySuggestion]
    notes: Optional[str] = None

class TripPlan(BaseModel):
    """Complete trip plan with all details"""
    origin: str
    destination: str
    start_date: date
    end_date: date
    travelers: int
    budget: float
    currency: str = "USD"
    outbound_flight: Optional[FlightDetails] = None
    return_flight: Optional[FlightDetails] = None
    accommodation: Optional[AccommodationDetails] = None
    daily_itinerary: List[DailyItinerary]
    total_estimated_cost: float
    budget_breakdown: dict
    travel_tips: List[str]
    underrated_locations: List[str] = Field(
        description="Less crowded and underrated locations to visit"
    )
