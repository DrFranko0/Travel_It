from typing import List, Optional
from pydantic import BaseModel, Field

class ActivitySearchCriteria(BaseModel):
    """Criteria for searching activities"""
    location: str
    interests: List[str]
    max_price: Optional[float] = None
    outdoor_only: bool = False
    family_friendly: bool = False
    underrated: bool = True  # Preference for less crowded, underrated locations

class ActivitySuggestion(BaseModel):
    """Suggested activity details"""
    name: str
    location: str
    description: str
    category: str  # e.g., "outdoor", "cultural", "food", etc.
    estimated_cost: Optional[float] = None
    currency: str = "USD"
    duration_hours: float
    best_time: Optional[str] = None
    crowdedness: str = Field(
        description="Indication of how crowded this place typically is"
    )
    is_underrated: bool = Field(
        description="Whether this is a less-known, underrated location"
    )
    tips: Optional[List[str]] = None
