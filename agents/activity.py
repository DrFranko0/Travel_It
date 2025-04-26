from typing import List, Optional, Union
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
import requests

from ..models.activity import ActivitySuggestion, ActivitySearchCriteria
from ..tools.search import search_tool
from ..tools.scrape import scrape_tool
from ..utils.openrouter_provider import OpenRouterConfig

class ActivityDeps(BaseModel):
    location: str
    start_date: str
    end_date: str
    travelers: int = 1
    interests: List[str]
    max_budget: Optional[float] = None
    prefer_outdoor: bool = False
    prefer_underrated: bool = True

class ActivityPlanningFailed(BaseModel):
    reason: str
    suggestions: List[str]


activity_planner_agent = Agent[ActivityDeps, Union[List[ActivitySuggestion], ActivityPlanningFailed]](
    OpenRouterConfig(),
    output_type=Union[List[ActivitySuggestion], ActivityPlanningFailed],
    system_prompt="""
    You are an activity planning specialist. Your job is to create engaging itineraries with activities 
    based on the user's interests.
    
    You should:
    1. Find activities matching the user's location and interests
    2. Consider budget constraints if provided
    3. Prioritize less crowded and underrated locations/activities
    4. Create a balanced mix of popular must-see attractions and hidden gems
    5. Organize activities in a logical sequence, considering location proximity
    
    Use the search and scrape tools to gather information about available activities.
    """,
    tools=[search_tool, scrape_tool],
)

@activity_planner_agent.tool
async def find_underrated_locations(ctx: RunContext[ActivityDeps], location: str) -> List[dict]:
    underrated_locations = {
        "paris": [
            {
                "name": "Canal Saint-Martin",
                "description": "A picturesque canal with trendy boutiques and cafes",
                "category": "neighborhood",
                "estimated_cost": 0,
                "crowdedness": "low"
            },
            {
                "name": "Musée de la Vie Romantique",
                "description": "A charming museum in a historic house with beautiful gardens",
                "category": "museum",
                "estimated_cost": 8,
                "crowdedness": "very low"
            }
        ],
        "new york": [
            {
                "name": "Greenacre Park",
                "description": "A hidden pocket park with a waterfall",
                "category": "outdoor",
                "estimated_cost": 0,
                "crowdedness": "low"
            },
            {
                "name": "City Island",
                "description": "A small seaside community in the Bronx with great seafood",
                "category": "neighborhood",
                "estimated_cost": 20,
                "crowdedness": "moderate"
            }
        ]
    }
    
    location_lower = location.lower()
    for key in underrated_locations:
        if key in location_lower:
            return underrated_locations[key]
    
    return [
        {
            "name": "Local Parks",
            "description": "Check out smaller local parks for a more authentic experience",
            "category": "outdoor",
            "estimated_cost": 0,
            "crowdedness": "low"
        },
        {
            "name": "Neighborhood Cafes",
            "description": "Visit cafes in residential areas away from tourist centers",
            "category": "food",
            "estimated_cost": 10,
            "crowdedness": "low"
        }
    ]

@activity_planner_agent.tool
async def analyze_location_image(ctx: RunContext[ActivityDeps], image_url: str) -> dict:
    
    from ..config import get_openrouter_headers
    from ..config import OPENROUTER_MODEL
    
    headers = get_openrouter_headers()
    
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json={
                "model": OPENROUTER_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this location image and describe: 1) What type of location this is, 2) How crowded it appears, 3) What activities would be possible here, 4) Whether this seems like an underrated or popular tourist destination."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ]
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis_text = result["choices"][0]["message"]["content"]
            
            location_type = "unknown"
            crowdedness = "unknown"
            activities = []
            is_underrated = False
            
            # Simple parsing logic - in production would use more sophisticated NLP
            if "beach" in analysis_text.lower() or "coast" in analysis_text.lower():
                location_type = "beach"
            elif "mountain" in analysis_text.lower() or "hill" in analysis_text.lower():
                location_type = "mountain"
            elif "city" in analysis_text.lower() or "urban" in analysis_text.lower():
                location_type = "urban"
            elif "park" in analysis_text.lower() or "garden" in analysis_text.lower():
                location_type = "park"
            
            # Determine crowdedness
            if any(word in analysis_text.lower() for word in ["empty", "deserted", "quiet", "peaceful"]):
                crowdedness = "very low"
            elif any(word in analysis_text.lower() for word in ["few people", "not crowded", "sparse"]):
                crowdedness = "low"
            elif any(word in analysis_text.lower() for word in ["some people", "moderate"]):
                crowdedness = "moderate"
            elif any(word in analysis_text.lower() for word in ["crowded", "busy", "popular"]):
                crowdedness = "high"
            elif any(word in analysis_text.lower() for word in ["very crowded", "packed", "bustling"]):
                crowdedness = "very high"
            
            activity_keywords = {
                "hiking": ["hike", "hiking", "trail"],
                "swimming": ["swim", "swimming", "beach", "water"],
                "sightseeing": ["sightseeing", "view", "scenic"],
                "photography": ["photo", "photography", "picture"],
                "relaxing": ["relax", "relaxing", "peaceful"],
                "dining": ["eat", "dining", "food", "restaurant"],
                "shopping": ["shop", "shopping", "market"],
                "cultural": ["museum", "cultural", "history", "historic"]
            }
            
            for activity, keywords in activity_keywords.items():
                if any(keyword in analysis_text.lower() for keyword in keywords):
                    activities.append(activity)
            
            is_underrated = "underrated" in analysis_text.lower() or "hidden gem" in analysis_text.lower()
            
            return {
                "location_type": location_type,
                "crowdedness": crowdedness,
                "possible_activities": activities,
                "is_underrated": is_underrated,
                "raw_analysis": analysis_text
            }
        else:
            return {
                "error": f"Failed to analyze image: {response.status_code}",
                "location_type": "unknown",
                "crowdedness": "unknown",
                "possible_activities": [],
                "is_underrated": False
            }
    except Exception as e:
        return {
            "error": f"Exception while analyzing image: {str(e)}",
            "location_type": "unknown",
            "crowdedness": "unknown",
            "possible_activities": [],
            "is_underrated": False
        }
