# Offline check: the Gemini model must be built with the plain-text formatting
# rules in its system instruction. No Gemini API call is made — get_model just
# constructs a local model object, and the constructor is mocked to capture it.
import os
import asyncio
from unittest.mock import MagicMock, patch


def test_system_instruction_enforces_plain_format():
    with open(os.path.join(os.path.dirname(__file__), "..", ".env")) as f:
        key = next((ln.split("=", 1)[1].strip()
                    for ln in f if ln.startswith("GEMINI_API_KEY=")), "offline-test-key")

    from app.chat_service import GeminiChatService

    with patch("google.generativeai.configure"), \
         patch("google.generativeai.GenerativeModel") as mock_cls, \
         patch.dict(os.environ, {"GEMINI_API_KEY": key}, clear=False):
        mock_cls.return_value = MagicMock(model_name="mock-model")

        svc = GeminiChatService()
        svc._api_key = key  # bypass get_model's os.getenv read
        model = asyncio.run(svc.get_model())

    kwargs = mock_cls.call_args.kwargs
    assert kwargs.get("model_name"), "model name must be passed to the constructor"

    instructions = kwargs.get("system_instruction") or ""
    low = instructions.lower()
    assert "plain text only" in low
    assert "never invent" in low
    assert "no campgrounds match" in low
    assert "currency" in low
    assert "would you like details or reviews" in low
    # The numbered-list template with indented sub-lines must be present.
    assert "1. Forest Haven" in instructions
    assert "   Location:" in instructions
    # Decorative-format prohibitions must be explicit.
    assert "emoji" in low and "markdown" in low


if __name__ == "__main__":
    test_system_instruction_enforces_plain_format()
    print("System instruction tests passed!")
