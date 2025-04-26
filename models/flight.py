from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class FlightSearchCriteria(BaseModel):
    """Criteria for searching flights"""
    origin: str
    destination: str
    departure_date: date
    return_date: Optional[date] = None
    travelers: int = 1
    max_price: Optional[float] = None
    preferred_airlines: Optional[List[str]] = None
    direct_only: bool = False

class FlightDetails(BaseModel):
    """Details of a flight"""
    flight_number: str
    airline: str
    origin: str = Field(description='Three-letter airport code')
    destination: str = Field(description='Three-letter airport code')
    departure_date: date
    departure_time: datetime
    arrival_time: datetime
    price: float
    currency: str = "USD"
    duration_minutes: int
    stops: int = 0
    layovers: Optional[List[str]] = None
