import os
import asyncio
from typing import List, Dict, Any
import google.generativeai as genai
from google.protobuf.json_format import MessageToDict
from tools.campground_tools import server
from app.schema_converter import normalize_schema


def _fc_args_to_dict(fc) -> Dict[str, Any]:
    """Convert a Gemini FunctionCall's args to a plain dict the MCP server can
    parse. The current SDK returns args as a protobuf MapComposite (not a dict);
    MessageToDict normalizes it (and any nested/list values) to JSON-friendly
    Python types. Falls back to the raw value when already a plain dict."""
    if isinstance(fc.args, dict):
        return fc.args
    try:
        return MessageToDict(fc).get("args", {})
    except Exception:
        try:
            return dict(fc.args)
        except Exception:
            return {}

class GeminiChatService:
    def __init__(self):
        self.server = server
        self._model = None
        self._api_key = os.getenv("GEMINI_API_KEY")

    async def get_model(self):
        if not self._model:
            if not self._api_key:
                raise ValueError("GEMINI_API_KEY is not set. Please configure it in .env")
            genai.configure(api_key=self._api_key)

            system_instruction = """
You are a helpful AI assistant for YelpCamp.
Use the provided tools to search, get details, list reviews, or recommend campgrounds.

Accuracy rules:
- Base every answer strictly on tool results. Never invent campgrounds, prices, locations, reviews, or features.
- If a tool returns no matches, say so plainly (for example: "No campgrounds match that in our data.") and suggest broadening the search. Do not fill gaps with made-up listings.
- Keep the currency and location the user asked for. Never convert currencies, and never swap a requested location for another region.
- If details or reviews are missing for a listing, say they are not available instead of guessing.

Reply format:
- Sound like a helpful person: short, plain sentences with clear spacing.
- Plain text only. Do not use bold, asterisks, emoji, decorative symbols, horizontal lines, tables, or other markdown.
- For campground search results, use this exact shape:

Found 3 campgrounds under $200 per night:

1. Forest Haven
   Location: Wayanad, Kerala
   Price: $100/night
   A peaceful campsite surrounded by greenery.

2. Pine Ridge Camp
   Location: Manali, Himachal Pradesh
   Price: $120/night
   A mountain campsite surrounded by pine trees.

Would you like details or reviews for any of these?

- Use "Name - location, $price" lines only when the user asks for a quick summary; otherwise use the numbered list above.
- For details or reviews, use a short paragraph followed by the plain list or quotation; no headers, no separators.
- End with at most one short follow-up question when it helps.
"""

            tools = await self._get_bridged_tools()
            model_name = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
            self._model = genai.GenerativeModel(
                model_name=model_name,
                tools=tools,
                system_instruction=system_instruction
            )
        return self._model

    async def _get_bridged_tools(self) -> List[Dict[str, Any]]:
        mcp_tools = await self.server.list_tools()

        bridged = []
        for tool in mcp_tools:
            normalized_params = normalize_schema(tool.input_schema)
            bridged.append({
                "function_declarations": [{
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": normalized_params
                }]
            })
        return bridged

    async def chat(self, message: str) -> str:
        model = await self.get_model()
        chat = model.start_chat(enable_automatic_function_calling=False)

        response = chat.send_message(message)

        for _ in range(5):
            if not response.candidates[0].content.parts:
                break

            parts = response.candidates[0].content.parts
            function_calls = [part.function_call for part in parts if part.function_call]

            if not function_calls:
                break

            function_responses = []
            for fc in function_calls:
                if fc.name not in ["search_campgrounds", "get_campground_details", "list_reviews", "recommend_campgrounds", "explain_yelpcamp"]:
                    raise ValueError(f"Unknown tool: {fc.name}")

                args = _fc_args_to_dict(fc)
                mcp_result = await self.server.call_tool(fc.name, args)

                response_data = mcp_result.structured_content.get('result', mcp_result.structured_content) if not mcp_result.is_error else {"error": str(mcp_result.content)}

                function_responses.append({
                    "function_response": {
                        "name": fc.name,
                        "response": {"result": response_data}
                    }
                })

            response = chat.send_message(function_responses)

        text = getattr(response, "text", None)
        return text or "I couldn't get a result for that. Please try rephrasing your request."
