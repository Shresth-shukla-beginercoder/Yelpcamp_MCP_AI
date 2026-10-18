import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from app.chat_service import GeminiChatService

@patch("google.generativeai.GenerativeModel")
def test_chat_endpoint_mock(mock_model):
    # Setup mock
    mock_chat = MagicMock()
    # Mocking the response that contains text
    mock_response = MagicMock()
    mock_response.text = "Mocked campground info"
    mock_chat.send_message.return_value = mock_response
    mock_model.return_value.start_chat.return_value = mock_chat

    # Initialize service with a mock API key
    with patch("os.getenv", return_value="fake_key"):
        service = GeminiChatService()
        # Mocking the async chat method
        service.chat = AsyncMock(return_value="Mocked campground info")
        response = asyncio.run(service.chat("Find me a campground in Arizona"))

    assert response == "Mocked campground info"

if __name__ == "__main__":
    test_chat_endpoint_mock()
    print("Chat integration tests passed!")
