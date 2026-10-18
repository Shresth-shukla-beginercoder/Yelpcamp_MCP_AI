import os

import httpx


class YelpCampClient:
    """Client for the YelpCamp Express read-only chat API.

    The base URL and service token come from the environment
    (``YELPCAMP_API_URL`` / ``YELPCAMP_CHAT_SERVICE_TOKEN``) and are never
    logged or returned to callers.
    """

    # Bounded result count requested from the API, matching the Express cap.
    DEFAULT_LIMIT = 50

    def __init__(self, base_url: str, service_token: str | None = None):
        self.base_url = base_url.rstrip("/")
        # Token is resolved lazily so tests can set the env after construction.
        self._service_token = service_token

    def _headers(self) -> dict:
        token = self._service_token or os.getenv("YELPCAMP_CHAT_SERVICE_TOKEN")
        if not token:
            raise RuntimeError(
                "YELPCAMP_CHAT_SERVICE_TOKEN is not configured. "
                "Set it in the MCP backend .env to call the Express chat API."
            )
        return {"Authorization": f"Bearer {token}"}

    async def search_campgrounds(
        self,
        keyword: str | None = None,
        location: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
    ) -> list[dict]:
        # Contract: GET /api/chat/campgrounds?keyword=...&location=...&minPrice=...&maxPrice=...&limit=...
        params: dict[str, str] = {"limit": str(self.DEFAULT_LIMIT)}
        if keyword:
            params["keyword"] = keyword
        if location:
            params["location"] = location
        if min_price is not None:
            params["minPrice"] = str(min_price)
        if max_price is not None:
            params["maxPrice"] = str(max_price)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/api/chat/campgrounds",
                params=params,
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()

    async def get_campground_details(self, campground_id: str) -> dict:
        # Contract: GET /api/chat/campgrounds/:id
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/api/chat/campgrounds/{campground_id}",
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()

    async def list_reviews(self, campground_id: str) -> list[str]:
        # Contract: GET /api/chat/campgrounds/:id/reviews
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/api/chat/campgrounds/{campground_id}/reviews",
                headers=self._headers(),
            )
            response.raise_for_status()
            return response.json()
