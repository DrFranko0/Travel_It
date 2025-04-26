from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field

class AccommodationSearchCriteria(BaseModel):
    """Criteria for searching accommodations"""
    location: str
    check_in_date: date
    check_out_date: date
    guests: int = 1
    rooms: int = 1
    max_price_per_night: Optional[float] = None
    amenities: Optional[List[str]] = None
    accommodation_type: Optional[str] = None

class AccommodationDetails(BaseModel):
    """Details of an accommodation"""
    name: str
    address: str
    location: str
    check_in_date: date
    check_out_date: date
    price_per_night: float
    total_price: float
    currency: str = "USD"
    rating: Optional[float] = None
    amenities: List[str] = []
    accommodation_type: str
    is_refundable: bool = False
    description: Optional[str] = None
    booking_link: Optional[str] = None
