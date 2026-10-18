# Local end-to-end integration for the chat flow, with Gemini mocked out.
#
# Boots the hermetic Express fixture server (no DB / no Neon) and drives:
#   browser -> FastAPI /chat -> (mocked) Gemini -> MCP tool ->
#   YelpCampAPIAdapter -> YelpCampClient -> Express /api/chat -> fixture data
#
# No live Gemini request is made. No production database is touched.
import asyncio
import os
import signal
import subprocess
import sys
import time
from unittest.mock import AsyncMock, MagicMock

import httpx

# --- Paths / config ---------------------------------------------------------
MCP_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
EXPRESS_DIR = os.environ.get(
    "YELPCAMP_EXPRESS_DIR",
    os.path.normpath(os.path.join(MCP_ROOT, "..", "YelpCamp_Project")),
)
FIXTURE_PORT = int(os.environ.get("FIXTURE_PORT", "3123"))
TOKEN = "dev-chat-service-token"

os.environ["YELPCAMP_API_URL"] = f"http://localhost:{FIXTURE_PORT}"
os.environ["YELPCAMP_CHAT_SERVICE_TOKEN"] = TOKEN

from tools.campground_tools import server  # noqa: E402


def _start_fixture_server():
    if not os.path.exists(EXPRESS_DIR):
        print(f"Express project not found at {EXPRESS_DIR}; skipping HTTP integration")
        return None
    script = os.path.join(EXPRESS_DIR, "tests", "integration", "express_fixture_server.js")
    env = dict(os.environ, FIXTURE_PORT=str(FIXTURE_PORT), NODE_ENV="test")
    proc = subprocess.Popen(
        ["node", script], cwd=EXPRESS_DIR, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    headers = {"Authorization": f"Bearer {TOKEN}"}
    deadline = time.time() + 20
    while time.time() < deadline:
        try:
            r = httpx.get(f"http://localhost:{FIXTURE_PORT}/api/chat/campgrounds",
                          headers=headers, timeout=1.0)
            if r.status_code == 200:
                return proc
        except Exception:
            pass
        time.sleep(0.25)
    proc.terminate()
    print("Fixture server did not become ready in time")
    return None


def _fake_gemini(service):
    """Patch GeminiChatService.get_model to issue one search function call,
    then a final text answer. No Gemini SDK / key is used."""
    mock_call = MagicMock()
    mock_call.name = "search_campgrounds"
    mock_call.args = {"keyword": "pine"}

    part = MagicMock()
    part.function_call = mock_call

    resp1 = MagicMock()
    resp1.candidates = [MagicMock()]
    resp1.candidates[0].content.parts = [part]

    resp2 = MagicMock()
    resp2.candidates = [MagicMock()]
    resp2.candidates[0].content.parts = []
    resp2.text = "Found campgrounds: Sunny Pines."

    fake_chat = MagicMock()
    fake_chat.send_message.side_effect = [resp1, resp2]
    fake_model = MagicMock()
    fake_model.start_chat.return_value = fake_chat
    service.get_model = AsyncMock(return_value=fake_model)
    return fake_chat


def main():
    results = {}
    proc = _start_fixture_server()
    try:
        # 1) MCP tools over REAL HTTP to the Express fixture (search/details/reviews)
        if proc is not None:
            async def http_tools():
                s = await server.call_tool("search_campgrounds", {})
                d = await server.call_tool("get_campground_details", {"campground_id": "1"})
                r = await server.call_tool("list_reviews", {"campground_id": "1"})
                return s, d, r

            s, d, r = asyncio.run(http_tools())
            sres = s.structured_content.get("result", s.structured_content)
            dres = d.structured_content.get("result", d.structured_content)
            rres = r.structured_content.get("result", r.structured_content)
            results["search"] = any(c.get("name") == "Sunny Pines" for c in sres)
            results["details"] = dres.get("name") == "Sunny Pines"
            results["reviews"] = "Great place!" in rres
        else:
            results["search"] = results["details"] = results["reviews"] = "skipped"

        # 2) FastAPI /chat with a mocked Gemini, in-process (no uvicorn, no Gemini)
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from app import main as main_mod
        from app.chat_service import GeminiChatService

        service = GeminiChatService()
        fake_chat = _fake_gemini(service)
        main_mod.chat_service = service  # the /chat endpoint reads this global

        mock_app = FastAPI()
        mock_app.post("/chat")(main_mod.chat)
        with TestClient(mock_app) as client:
            res = client.post("/chat", json={"message": "Find a camp with pine"})

        results["fastapi_status"] = res.status_code
        results["fastapi_response"] = res.json().get("response")

        # Confirm real fixture data reached the Gemini bridge: the 2nd
        # send_message call carries the function responses (tool results).
        sent = fake_chat.send_message.call_args_list
        second = sent[1].args[0] if len(sent) > 1 else None
        results["gemini_bridge_saw_data"] = (
            isinstance(second, list) and any("Sunny Pines" in str(x) for x in second)
        )
    finally:
        if proc is not None:
            proc.send_signal(signal.SIGINT if os.name != "nt" else signal.SIGTERM)
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()

    print("\n=== Integration results ===")
    for k, v in results.items():
        print(f"  {k}: {v}")

    ok = (
        all(v in (True, "skipped") for v in [results.get("search"), results.get("details"), results.get("reviews")])
        and results.get("fastapi_status") == 200
        and results.get("fastapi_response") == "Found campgrounds: Sunny Pines."
        and results.get("gemini_bridge_saw_data") is True
    )
    print("\nINTEGRATION", "PASSED" if ok else "FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
