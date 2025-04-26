from typing import Optional, List
from pydantic import BaseModel
from pydantic_ai import RunContext, Tool

class SearchQuery(BaseModel):
    """Search query with parameters"""
    query: str
    num_results: int = 5

class SearchResult(BaseModel):
    """Single search result"""
    title: str
    snippet: str
    url: Optional[str] = None

async def search_web(ctx: RunContext, query: SearchQuery) -> List[SearchResult]:
    """Search the web for information"""
    # This is a mock implementation
    # In production, integrate with a real search API
    print(f"Searching for: {query.query}")
    
    # For demonstration purposes, return mock data
    if "flight" in query.query.lower():
        return [
            SearchResult(
                title="Cheap Flights to Popular Destinations",
                snippet="Find the best deals on flights to popular destinations.",
                url="https://example.com/flights"
            ),
            SearchResult(
                title="Last Minute Flight Deals",
                snippet="Save on last-minute flights. Book now for the best prices.",
                url="https://example.com/last-minute-flights"
            )
        ]
    elif "accommodation" in query.query.lower():
        return [
            SearchResult(
                title="Top-rated Hotels and Accommodations",
                snippet="Discover the best places to stay at your destination.",
                url="https://example.com/hotels"
            ),
            SearchResult(
                title="Budget Accommodations Guide",
                snippet="Find affordable places to stay without compromising on quality.",
                url="https://example.com/budget-accommodations"
            )
        ]
    # Add more cases as needed
    else:
        return [SearchResult(
            title="Travel Guide",
            snippet="Comprehensive travel guide with tips and recommendations.",
            url="https://example.com/travel-guide"
        )]

# Create the search tool
search_tool = Tool(search_web)
