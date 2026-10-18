# Offline: FastAPI /chat error mapping and validation boundary, no Gemini, no network.
# - Gemini quota exhaustion (ResourceExhausted) must surface as 503 so the
#   widget shows "temporarily unavailable" instead of the generic 200 string.
# - Message length validation: empty -> 400, 2000 chars -> accepted, 2001 -> 400.
from fastapi import FastAPI
from fastapi.testclient import TestClient
from google.api_core.exceptions import ResourceExhausted
from unittest.mock import AsyncMock, MagicMock, patch

from app import main as main_mod


def _client():
    main_mod.chat_service = None
    app = FastAPI()
    app.post("/chat")(main_mod.chat)
    return TestClient(app)


def test_resource_exhausted_maps_to_503():
    c = _client()
    service = MagicMock()
    service.chat = AsyncMock(side_effect=ResourceExhausted("429 quota exceeded"))
    main_mod.chat_service = service
    res = c.post("/chat", json={"message": "under 2500"})
    assert res.status_code == 503
    assert "rate limited" in res.json()["detail"]


def test_normal_response_passthrough():
    c = _client()
    service = MagicMock()
    service.chat = AsyncMock(return_value="Found 2 campgrounds under $2500:")
    main_mod.chat_service = service
    res = c.post("/chat", json={"message": "Find a camp under 2500"})
    assert res.status_code == 200
    assert res.json()["response"].startswith("Found 2 campgrounds")


def test_message_length_boundaries():
    c = _client()
    service = MagicMock()
    service.chat = AsyncMock(return_value="ok")
    main_mod.chat_service = service

    assert c.post("/chat", json={"message": ""}).status_code == 400
    assert c.post("/chat", json={"message": "hi"}).status_code == 200          # short message ok
    assert c.post("/chat", json={"message": "x" * 2000}).status_code == 200   # boundary accepted
    assert c.post("/chat", json={"message": "x" * 2001}).status_code == 400   # over the limit


if __name__ == "__main__":
    test_resource_exhausted_maps_to_503()
    test_normal_response_passthrough()
    test_message_length_boundaries()
    print("Endpoint error-mapping tests passed!")
