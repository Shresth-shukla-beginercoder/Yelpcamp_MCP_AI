import asyncio
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from app.chat_service import GeminiChatService

async def run_live_tests():
    print("Starting live Gemini API tests...")

    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable not found.")
        return

    service = GeminiChatService()

    # Scenarios
    scenarios = [
        "Find campgrounds in Arizona costing at most $40 per night.",
        "Show details for campground ID c1.",
        "Recommend a campground under $60 with wifi and shower features."
    ]

    for i, message in enumerate(scenarios, 1):
        print(f"\n--- Scenario {i}: {message} ---")
        try:
            response = await service.chat(message)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error in scenario {i}: {e}")

if __name__ == "__main__":
    asyncio.run(run_live_tests())
