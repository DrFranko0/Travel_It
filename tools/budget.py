from typing import Dict, List, Optional
from pydantic import BaseModel
from pydantic_ai import RunContext, Tool

class BudgetRequest(BaseModel):
    """Request to calculate budget for a trip"""
    destination: str
    duration_days: int
    travelers: int
    accommodation_type: str  # e.g., "budget", "mid-range", "luxury"
    transportation_type: str  # e.g., "public", "rental car", "taxi"
    dining_preference: str  # e.g., "budget", "mid-range", "fine dining"
    activities_budget: float  # per person per day
    flight_cost: Optional[float] = None  # If known

class BudgetBreakdown(BaseModel):
    """Detailed breakdown of a travel budget"""
    accommodation: float
    local_transportation: float
    food: float
    activities: float
    flights: float
    miscellaneous: float
    total: float
    currency: str = "USD"
    daily_average: float
    tips: List[str]

async def calculate_budget(ctx: RunContext, request: BudgetRequest) -> BudgetBreakdown:
    """Calculate a detailed budget for a trip"""
    # Mock implementation with realistic pricing logic
    print(f"Calculating budget for trip to {request.destination}")
    
    # Accommodation costs based on type
    accommodation_cost_per_night = {
        "budget": 50, "mid-range": 100, "luxury": 200
    }
    
    # Transportation costs based on type
    transportation_cost_per_day = {
        "public": 10, "rental car": 40, "taxi": 60
    }
    
    # Food costs based on preference
    food_cost_per_day = {
        "budget": 30, "mid-range": 60, "fine dining": 100
    }
    
    # Calculate costs
    accommodation_total = accommodation_cost_per_night.get(request.accommodation_type, 75) * request.duration_days
    transportation_total = transportation_cost_per_day.get(request.transportation_type, 20) * request.duration_days
    food_total = food_cost_per_day.get(request.dining_preference, 40) * request.duration_days * request.travelers
    activities_total = request.activities_budget * request.duration_days * request.travelers
    flight_cost = request.flight_cost if request.flight_cost else 500 * request.travelers
    miscellaneous = (accommodation_total + transportation_total + food_total + activities_total) * 0.1
    
    total = accommodation_total + transportation_total + food_total + activities_total + flight_cost + miscellaneous
    daily_average = total / (request.duration_days * request.travelers)
    
    tips = [
        f"Consider visiting {request.destination} during shoulder season for better prices",
        "Book accommodation with a kitchen to save on food costs",
        "Look for city passes that include multiple attractions",
        "Use public transportation to save on local travel costs",
        "Check for free walking tours or museum days"
    ]
    
    return BudgetBreakdown(
        accommodation=accommodation_total,
        local_transportation=transportation_total,
        food=food_total,
        activities=activities_total,
        flights=flight_cost,
        miscellaneous=miscellaneous,
        total=total,
        daily_average=daily_average,
        tips=tips
    )

# Create the budget calculation tool
budget_calculation_tool = Tool(calculate_budget)
