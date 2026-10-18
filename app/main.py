import os
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.api_core.exceptions import ResourceExhausted

from app.models import ChatRequest, ChatResponse
from app.chat_service import GeminiChatService

# Load GEMINI_API_KEY, YELPCAMP_API_URL and YELPCAMP_CHAT_SERVICE_TOKEN from .env.
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("yelpcamp.chat")

app = FastAPI(title="YelpCamp AI Assistant")
chat_service = None

# Allow the YelpCamp web app (served by Express) to call /chat from the browser.
# Origins are configurable; the Gemini key and service token stay server-side.
allowed_origins = [o.strip() for o in os.getenv("CHAT_ALLOWED_ORIGINS", "http://localhost:3000").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["POST"],
    allow_headers=["*"],
    allow_credentials=False,
)


@app.on_event("startup")
def startup_event():
    global chat_service
    chat_service = GeminiChatService()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message or len(request.message) > 2000:
        raise HTTPException(status_code=400, detail="Invalid message length")
    try:
        if chat_service is None:
            raise ValueError("Service not initialized")
        response = await chat_service.chat(request.message)
        return ChatResponse(response=response)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ResourceExhausted:
        # Gemini quota (free tier: a few requests per minute/day). Return 503 so
        # the widget's "temporarily unavailable" path shows instead of a generic
        # 200 error string, and the server log still records the traceback.
        logger.exception("Gemini quota exceeded for message of length %s", len(request.message))
        raise HTTPException(status_code=503, detail="The AI assistant is temporarily rate limited. Please try again in a few minutes.")
    except Exception:
        # Log the real error server-side so failures are traceable; the client
        # still only sees a generic message (no internal details leaked).
        logger.exception("Chat request failed for message of length %s", len(request.message))
        return ChatResponse(response="Sorry, I encountered an error processing your request.")
