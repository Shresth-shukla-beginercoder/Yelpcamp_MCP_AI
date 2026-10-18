# Local integration: YelpCamp Express + FastAPI chat

This document covers how to run the full chat flow locally, and how to verify
it without a live Gemini request or a production/Neon database.

## Components
- **Express app** (`YelpCamp_Project`) — serves the site and the read-only
  chat API at `/api/chat/*`. Port `3000` (or `PORT`).
- **FastAPI / MCP backend** (`Yelpcamp_AI_MCP`) — the `/chat` endpoint that
  calls Gemini (tool-calling) and, through the MCP tools, the Express chat
  API. Port `8000`.
- **Browser chat widget** — the floating button in
  `views/layouts/boilerplate.ejs`; it only ever talks to the FastAPI `/chat`
  endpoint. The Gemini key and the Express service token never reach it.

## 1. Environment
Both projects keep secrets in their own git-ignored `.env` files.

`YelpCamp_Project/.env`
```
YELPCAMP_CHAT_SERVICE_TOKEN=dev-chat-service-token   # validates /api/chat auth
CHAT_API_URL=http://localhost:8000                   # (optional) widget target
# ... DB_*, CLOUDINARY_*, MAPTILER_API_KEY ...
```

`Yelpcamp_AI_MCP/.env`
```
GEMINI_API_KEY=...                    # Gemini, server-side only
GEMINI_MODEL=gemini-3.8-flash         # optional; defaults to gemini-3.8-flash in code
YELPCAMP_API_URL=http://localhost:3000
YELPCAMP_CHAT_SERVICE_TOKEN=dev-chat-service-token  # MUST match Express
```

> **Troubleshooting:** If `/chat` replies "Sorry, I encountered an error…"
> for a valid message, the server log now prints the real traceback (it was
> previously swallowed). A `404 models/… is not found` means the configured
> `GEMINI_MODEL` is retired — pick a model that appears in `gemini-2.5-flash`-style
> listings (never `gemini-1.5-flash`).

The two `YELPCAMP_CHAT_SERVICE_TOKEN` values must be identical.

## 2. Startup sequence
```bash
# 1) Express (DB-backed site + chat API)
cd YelpCamp_Project
npm start                      # http://localhost:3000

# 2) FastAPI (chat) — use the project virtualenv
cd ../Yelpcamp_AI_MCP
.venv/Scripts/python -m uvicorn app.main:app --port 8000   # http://localhost:8000

# 3) Open the site, click the floating chat button, and ask a question.
```

The browser widget reads the FastAPI base URL from
`window.YELPCAMP_CHAT_API` (injected in the layout, default
`http://localhost:8000`).

## 3. Verification (no live Gemini, no Neon)
```bash
# a) Express chat API unit tests (mocked DB pool)
cd YelpCamp_Project && npm test

# b) Python offline tests (mock adapter, no network)
cd ../Yelpcamp_AI_MCP
.venv/Scripts/python -m tests.test_tools
.venv/Scripts/python -m tests.test_mcp_integration
.venv/Scripts/python -m tests.test_chat_service
.venv/Scripts/python -m tests.test_adapter_api

# c) End-to-end with a hermetic Express fixture server + mocked Gemini
#    (boots a Node fixture server on :3123, drives FastAPI /chat, no DB/Neon/Gemini)
.venv/Scripts/python -m tests.test_live_integration
```

## Security
- `YELPCAMP_CHAT_SERVICE_TOKEN` and `GEMINI_API_KEY` are server-side only.
- The widget sends a plain user message to FastAPI; it never sends or stores
  the service token or the Gemini key.
- All API errors are generic JSON; internal details are not leaked to callers.
