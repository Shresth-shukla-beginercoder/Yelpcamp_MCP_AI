from typing import List, Optional, Protocol
from dataclasses import dataclass
import os

@dataclass
class Campground:
    id: str
    name: str
    location: str
    price: float
    description: str
    features: List[str]
    reviews: List[str]

class DataAdapter(Protocol):
    async def search_campgrounds(self, keyword: Optional[str] = None, location: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None) -> List[Campground]: ...
    async def get_campground_by_id(self, campground_id: str) -> Optional[Campground]: ...
    async def get_reviews(self, campground_id: str) -> List[str]: ...
    async def get_all_campgrounds(self) -> List[Campground]: ...

# Mock Adapter
class MockAdapter:
    _MOCK_DATA = [
        Campground("c1", "Sunny Pines", "California", 50.0, "Beautiful pine forest.", ["wifi", "shower"], ["Great place!", "Wifi was spotty."]),
        Campground("c2", "Desert Oasis", "Arizona", 30.0, "Stunning desert views.", ["firepit"], ["Loved the stars.", "No shade."]),
        Campground("c3", "Mountain View", "Colorado", 75.0, "High altitude camping.", ["wifi", "shower", "hiking"], ["Amazing views.", "Quiet."]),
    ]

    async def get_all_campgrounds(self) -> List[Campground]:
        return self._MOCK_DATA

    async def get_campground_by_id(self, campground_id: str) -> Optional[Campground]:
        for c in self._MOCK_DATA:
            if c.id == campground_id:
                return c
        return None

    async def search_campgrounds(self, keyword: Optional[str] = None, location: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None) -> List[Campground]:
        results = self._MOCK_DATA
        if keyword:
            results = [c for c in results if keyword.lower() in c.name.lower() or keyword.lower() in c.description.lower()]
        if location:
            results = [c for c in results if c.location.lower() == location.lower()]
        if min_price:
            results = [c for c in results if c.price >= min_price]
        if max_price:
            results = [c for c in results if c.price <= max_price]
        return results

    async def get_reviews(self, campground_id: str) -> List[str]:
        c = await self.get_campground_by_id(campground_id)
        return c.reviews if c else []

# Helper to build a Campground from an API dict, tolerating missing optional
# fields (the Express API omits `features` and, in list responses, `reviews`).
def _to_campground(item: dict) -> "Campground":
    return Campground(
        id=str(item.get("id", "")),
        name=item.get("name", ""),
        location=item.get("location", ""),
        price=float(item.get("price", 0) or 0),
        description=item.get("description", ""),
        features=list(item.get("features", [])),
        reviews=list(item.get("reviews", [])),
    )

# Real API Adapter
class YelpCampAPIAdapter:
    def __init__(self, base_url: str):
        from app.yelpcamp_client import YelpCampClient
        self.client = YelpCampClient(base_url)

    async def search_campgrounds(self, keyword: Optional[str] = None, location: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None) -> List[Campground]:
        data = await self.client.search_campgrounds(keyword, location, min_price, max_price)
        return [_to_campground(item) for item in data]

    async def get_campground_by_id(self, campground_id: str) -> Optional[Campground]:
        data = await self.client.get_campground_details(campground_id)
        return _to_campground(data) if data else None

    async def get_reviews(self, campground_id: str) -> List[str]:
        return await self.client.list_reviews(campground_id)

    async def get_all_campgrounds(self) -> List[Campground]:
        return await self.search_campgrounds()

# Factory to get adapter based on config
def get_adapter() -> DataAdapter:
    api_url = os.getenv("YELPCAMP_API_URL")
    if api_url:
        return YelpCampAPIAdapter(api_url)
    return MockAdapter()

# Proxy functions to the selected adapter
async def get_all_campgrounds() -> List[Campground]:
    return await get_adapter().get_all_campgrounds()

async def get_campground_by_id(campground_id: str) -> Optional[Campground]:
    return await get_adapter().get_campground_by_id(campground_id)

async def search_campgrounds(keyword: Optional[str] = None, location: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None) -> List[Campground]:
    return await get_adapter().search_campgrounds(keyword, location, min_price, max_price)

async def get_reviews(campground_id: str) -> List[str]:
    return await get_adapter().get_reviews(campground_id)
