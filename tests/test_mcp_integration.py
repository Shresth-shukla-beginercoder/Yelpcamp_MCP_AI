import asyncio
from tools.campground_tools import server

async def run_mcp_integration_test():
    print("Verifying MCP server tools...")

    # 1. List tools
    tools = await server.list_tools()
    tool_names = [tool.name for tool in tools]
    print(f"Tools found: {tool_names}")

    assert "search_campgrounds" in tool_names
    assert "get_campground_details" in tool_names
    assert "recommend_campgrounds" in tool_names

    # 2. Call search_campgrounds
    print("\nTesting search_campgrounds...")
    # call_tool returns a CallToolResult
    result = await server.call_tool("search_campgrounds", arguments={"location": "Arizona"})
    print(f"Search result: {result}")
    # Extract data from structured_content (dict containing the result key)
    data = result.structured_content['result']
    assert len(data) == 1
    assert data[0]['name'] == "Desert Oasis"

    # 3. Call get_campground_details
    print("\nTesting get_campground_details...")
    result = await server.call_tool("get_campground_details", arguments={"campground_id": "c1"})
    print(f"Details result: {result}")
    data = result.structured_content['result']
    assert data['name'] == "Sunny Pines"

    print("\nMCP integration tests passed!")

if __name__ == "__main__":
    asyncio.run(run_mcp_integration_test())
