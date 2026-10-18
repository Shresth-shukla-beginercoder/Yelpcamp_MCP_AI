import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from app.chat_service import GeminiChatService

def test_manual_loop():
    # Setup mocks
    mock_model = MagicMock()
    mock_chat = MagicMock()

    # 1. Round 1: Model asks for tool
    mock_call = MagicMock()
    mock_call.name = "search_campgrounds"
    mock_call.args = {"location": "California"}

    mock_part = MagicMock()
    mock_part.function_call = mock_call

    mock_response1 = MagicMock()
    mock_response1.candidates = [MagicMock()]
    mock_response1.candidates[0].content.parts = [mock_part]

    # 2. Round 2: Final response
    mock_response2 = MagicMock()
    mock_response2.text = "Found Sunny Pines."

    # Configure mock chat
    mock_chat.send_message.side_effect = [mock_response1, mock_response2]
    mock_model.start_chat.return_value = mock_chat

    # Test service
    with patch("os.getenv", return_value="fake_key"), \
         patch("google.generativeai.GenerativeModel", return_value=mock_model), \
         patch("tools.campground_tools.server.call_tool", new_callable=AsyncMock) as mock_call_tool:

        # Setup mock MCP response
        mock_mcp_result = MagicMock()
        mock_mcp_result.is_error = False
        mock_mcp_result.structured_content = {'result': [{'name': 'Sunny Pines'}]}
        mock_call_tool.return_value = mock_mcp_result

        service = GeminiChatService()
        # Mock get_model to avoid actually calling the SDK and the loop
        service.get_model = AsyncMock(return_value=mock_model)

        response = asyncio.run(service.chat("Find camping in California"))

        # The function-result round must be wrapped in `function_response` for
        # the (deprecated) genai SDK's send_message — assert the exact shape sent,
        # so a regression back to {"name","response"} is caught offline.
        second = mock_chat.send_message.call_args_list[1].args[0]
        assert isinstance(second, list), "function results must be sent as a list"
        assert second[0]["function_response"]["name"] == "search_campgrounds"
        assert second[0]["function_response"]["response"] == {"result": [{'name': 'Sunny Pines'}]}

    assert response == "Found Sunny Pines."
    mock_call_tool.assert_called_with("search_campgrounds", {"location": "California"})

if __name__ == "__main__":
    test_manual_loop()
    print("Chat service loop tests passed!")
