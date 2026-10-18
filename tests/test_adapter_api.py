# Offline verification that the real-API client/adapter matches the Express
# chat contract: correct paths, Bearer auth header, price/limit params, and
# tolerant mapping of the public response shape. No network, no live Express.
import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

from app.yelpcamp_client import YelpCampClient
from tools.data_access import YelpCampAPIAdapter

os.environ["YELPCAMP_CHAT_SERVICE_TOKEN"] = "dev-chat-service-token"


class _Resp:
    def __init__(self, payload):
        self.payload = payload
        self.status_code = 200

    def raise_for_status(self):
        pass

    def json(self):
        return self.payload


# Express public shapes: list items have no `features`/`reviews`; details adds
# `reviews`; `id` is numeric.
LIST_ITEM = {"id": 1, "name": "Sunny Pines", "location": "California", "price": 50, "description": "d"}
DETAIL = {**LIST_ITEM, "reviews": ["Great place!", "Wifi was spotty."]}


def test_client_paths_auth_and_params():
    """Capture the exact URL / params / headers the client sends."""
    seen = {}

    class _MockClient:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def get(self, url, params=None, headers=None):
            seen["url"] = url
            seen["params"] = params
            seen["headers"] = headers
            return _Resp([LIST_ITEM])

    with patch("app.yelpcamp_client.httpx.AsyncClient", _MockClient):
        client = YelpCampClient("http://localhost:3000/")
        result = asyncio.run(client.search_campgrounds(keyword="pine", location="California", min_price=40, max_price=100))

    assert seen["url"].endswith("/api/chat/campgrounds")
    assert seen["params"]["keyword"] == "pine"
    assert seen["params"]["location"] == "California"
    assert str(seen["params"]["minPrice"]) == "40"
    assert str(seen["params"]["maxPrice"]) == "100"
    assert "limit" in seen["params"]
    assert seen["headers"]["Authorization"] == "Bearer dev-chat-service-token"
    assert result == [LIST_ITEM]


def test_client_details_and_reviews_paths():
    seen = {}

    class _MockClient:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def get(self, url, params=None, headers=None):
            seen["url"] = url
            payload = DETAIL if "/reviews" not in url else [r["reviews"] for r in [DETAIL]][0]
            return _Resp(payload)

    with patch("app.yelpcamp_client.httpx.AsyncClient", _MockClient):
        client = YelpCampClient("http://localhost:3000")
        asyncio.run(client.get_campground_details(1))
        assert seen["url"].endswith("/api/chat/campgrounds/1")
        reviews = asyncio.run(client.list_reviews(1))
        assert seen["url"].endswith("/api/chat/campgrounds/1/reviews")
        assert reviews == ["Great place!", "Wifi was spotty."]


def test_missing_token_raises():
    client = YelpCampClient("http://localhost:3000")
    os.environ.pop("YELPCAMP_CHAT_SERVICE_TOKEN", None)
    try:
        client._headers()
        assert False, "expected RuntimeError without a token"
    except RuntimeError:
        pass


def test_adapter_maps_public_shape_to_campground():
    """The adapter must tolerate Express' public shape (no features/reviews on list)."""
    adapter = YelpCampAPIAdapter("http://localhost:3000")

    class _StubClient:
        async def search_campgrounds(self, keyword=None, location=None, min_price=None, max_price=None):
            return [LIST_ITEM]

        async def get_campground_details(self, cid):
            return DETAIL

        async def list_reviews(self, cid):
            return ["Great place!"]

    adapter.client = _StubClient()

    camps = asyncio.run(adapter.search_campgrounds(keyword="pine"))
    assert len(camps) == 1
    c = camps[0]
    assert c.id == "1"
    assert c.name == "Sunny Pines"
    assert c.price == 50.0
    assert c.features == []      # absent in list response -> default
    assert c.reviews == []      # absent in list response -> default

    detail = asyncio.run(adapter.get_campground_by_id("1"))
    assert detail.reviews == ["Great place!", "Wifi was spotty."]

    reviews = asyncio.run(adapter.get_reviews("1"))
    assert reviews == ["Great place!"]


if __name__ == "__main__":
    test_client_paths_auth_and_params()
    test_client_details_and_reviews_paths()
    test_missing_token_raises()
    test_adapter_maps_public_shape_to_campground()
    print("API adapter tests passed!")
