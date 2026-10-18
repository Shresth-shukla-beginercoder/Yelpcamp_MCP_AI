import asyncio
from unittest.mock import MagicMock, AsyncMock
from tools.data_access import Campground

# Create a mock for the client
class MockYelpCampClient:
    async def search_campgrounds(self, keyword=None, location=None):
        return [
            {"id": "c1", "name": "Sunny Pines", "location": "California", "price": 50.0, "description": "Beautiful pine forest.", "features": ["wifi", "shower"], "reviews": ["Great place!"]},
        ]
    async def get_campground_details(self, campground_id):
        if campground_id == "c1":
            return {"id": "c1", "name": "Sunny Pines", "location": "California", "price": 50.0, "description": "Beautiful pine forest.", "features": ["wifi", "shower"], "reviews": ["Great place!"]}
        return None
    async def list_reviews(self, campground_id):
        if campground_id == "c1":
            return ["Great place!", "Wifi was spotty."]
        return []

async def test_client():
    client = MockYelpCampClient()

    # Test search
    results = await client.search_campgrounds(location="California")
    assert len(results) == 1
    assert results[0]["name"] == "Sunny Pines"
    print("Search test passed")

    # Test details
    details = await client.get_campground_details("c1")
    assert details["name"] == "Sunny Pines"
    print("Details test passed")

    # Test reviews
    reviews = await client.list_reviews("c1")
    assert len(reviews) == 2
    print("Reviews test passed")

if __name__ == "__main__":
    asyncio.run(test_client())
