from typing import List, Optional
from mcp.server.mcpserver import MCPServer
from tools.data_access import (
    search_campgrounds as data_search,
    get_campground_by_id,
    get_reviews,
    get_all_campgrounds
)

server = MCPServer("campground")

# NOTE: the data-access layer is async, so every tool that touches it must be
# `async def` and `await` the call. The MCP server awaits async tool callables.

@server.tool()
async def search_campgrounds(
    keyword: Optional[str] = None,
    location: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
) -> List[dict]:
    """Search campgrounds by keyword, location, and price range."""
    results = await data_search(keyword, location, min_price, max_price)
    return [c.__dict__ for c in results]

@server.tool()
async def get_campground_details(campground_id: str) -> Optional[dict]:
    """Retrieve details for a specific campground by ID."""
    c = await get_campground_by_id(campground_id)
    return c.__dict__ if c else None

@server.tool()
async def list_reviews(campground_id: str) -> List[str]:
    """Retrieve public reviews for a campground."""
    return await get_reviews(campground_id)

@server.tool()
async def recommend_campgrounds(
    location: Optional[str] = None,
    budget: Optional[float] = None,
    features: Optional[List[str]] = None
) -> List[dict]:
    """Recommend campgrounds based on location, budget, and features."""
    all_c = await get_all_campgrounds()
    results = all_c
    if location:
        results = [c for c in results if c.location.lower() == location.lower()]
    if budget:
        results = [c for c in results if c.price <= budget]
    if features:
        # The Express API does not expose a `features` list, so a feature
        # request that the data cannot satisfy yields no matches.
        results = [c for c in results if all(f in c.features for f in features)]
    return [c.__dict__ for c in results]

@server.tool()
def explain_yelpcamp() -> str:
    """Explains YelpCamp's purpose and usage."""
    return "YelpCamp is an AI-powered assistant designed to help you find and review the best camping spots based on your preferences, budget, and desired features."
