from typing import Dict, List, Optional, Union
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from ..tools.budget import budget_calculation_tool
from ..utils.openrouter_provider import OpenRouterConfig

class BudgetDeps(BaseModel):
    destination: str
    duration_days: int
    travelers: int
    total_budget: float
    accommodation_preference: str
    transportation_preference: str
    dining_preference: str

class BudgetOptimizationResult(BaseModel):
    breakdown: Dict[str, float]
    daily_average: float
    optimization_tips: List[str]
    savings_opportunities: List[Dict[str, str]]

class BudgetOptimizationFailed(BaseModel):
    reason: str
    suggestions: List[str]


budget_optimizer_agent = Agent[BudgetDeps, Union[BudgetOptimizationResult, BudgetOptimizationFailed]](
    OpenRouterConfig(), 
    output_type=Union[BudgetOptimizationResult, BudgetOptimizationFailed],  
    system_prompt="""
    You are a travel budget specialist. Your job is to optimize travel budgets to help users 
    make the most of their money.
    
    You should:
    1. Calculate detailed budget breakdowns for all aspects of travel
    2. Find opportunities to save money without sacrificing experience quality
    3. Provide specific tips for the destination to stretch the budget
    4. Suggest budget allocation across different categories
    
    Use the budget calculation tool to create detailed estimates.
    """,
    tools=[budget_calculation_tool],
)

@budget_optimizer_agent.tool
async def find_budget_alternatives(ctx: RunContext[BudgetDeps], category: str, preference: str) -> List[dict]:
    budget_alternatives = {
        "accommodation": {
            "luxury": [
                {"option": "Boutique hotels", "savings": "20-30%", 
                 "tip": "Smaller luxury boutique hotels often offer similar quality at lower prices"},
                {"option": "Luxury apartment rental", "savings": "30-40%", 
                 "tip": "High-end apartment rentals often have more space at a fraction of luxury hotel costs"}
            ],
            "mid-range": [
                {"option": "Guesthouses", "savings": "20-30%", 
                 "tip": "Local guesthouses offer authentic experiences at lower prices than chain hotels"},
                {"option": "B&Bs", "savings": "15-25%", 
                 "tip": "Bed and breakfasts include meals and often provide more personalized service"}
            ]
        },
    }
    
    if category in budget_alternatives and preference in budget_alternatives[category]:
        return budget_alternatives[category][preference]
    
    return [
        {"option": "Research free activities", "savings": "100%", 
         "tip": "Many destinations have free walking tours, museum days, and cultural events"},
        {"option": "Travel in shoulder season", "savings": "20-40%", 
         "tip": "Prices are lower just before or after peak season, but weather is often still good"}
    ]
