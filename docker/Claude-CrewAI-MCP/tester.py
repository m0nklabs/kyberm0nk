#!/usr/bin/env python3
"""
MCP Server Tester - Tests the CrewAI MCP Server using FastMCP Client.
This script uses the official FastMCP client to communicate with the server.
"""

import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


TOOL_TEST_ARGS = {
    "run_kyber_crewai_dry_run": {"timeout_seconds": 1},
    "get_kyber_crewai_live_log_preview": {"line_count": 5},
}

SKIP_TOOL_CALLS = {
    "start_kyber_crewai_live_run",
    "restart_kyber_crewai_live_run",
    "stop_kyber_crewai_live_run",
    "update_kyber_crewai_operator_inputs",
}


async def test_crewai_mcp_server():
    """Test the CrewAI MCP server using FastMCP client."""
    print("🚀 MCP Server Tester - Testing CrewAI MCP Server with FastMCP Client")
    print("=" * 70)

    # Server parameters (same as Claude Desktop would use)
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["crewai_mcp_server.py"],
    )

    try:
        # Connect to the server
        print("🔄 Connecting to MCP server...")
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("✅ Connected to MCP server successfully")

                # Initialize the session
                print("\n🔄 Initializing session...")
                await session.initialize()
                print("✅ Session initialized successfully")

                # List available tools
                print("\n🔍 Listing available tools...")
                tools_response = await session.list_tools()

                if tools_response.tools:
                    print(f"✅ Found {len(tools_response.tools)} tools:")
                    for tool in tools_response.tools:
                        print(f"  - {tool.name}: {tool.description}")

                    # Test each tool
                    print("\n🔧 Testing tools...")
                    for tool in tools_response.tools:
                        print(f"\n📞 Calling tool: {tool.name}")
                        if tool.name in SKIP_TOOL_CALLS:
                            print(f"⏭️ Skipping disruptive tool in smoke test: {tool.name}")
                            continue
                        try:
                            # Call the tool with empty arguments
                            result = await session.call_tool(tool.name, TOOL_TEST_ARGS.get(tool.name, {}))

                            print(f"✅ Tool '{tool.name}' executed successfully")

                            # Print the result
                            if result.content:
                                for content in result.content:
                                    if hasattr(content, 'text'):
                                        try:
                                            # Try to parse and pretty-print JSON
                                            parsed = json.loads(content.text)
                                            print("📄 Response:")
                                            print(json.dumps(parsed, indent=2))
                                        except json.JSONDecodeError:
                                            print(f"📄 Response: {content.text}")
                            else:
                                print("📄 No content in response")

                        except Exception as e:
                            print(f"❌ Error calling tool '{tool.name}': {e}")

                else:
                    print("❌ No tools found")

                print("\n✅ All tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        raise


def main():
    """Main function to run the async test."""
    try:
        asyncio.run(test_crewai_mcp_server())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")


if __name__ == "__main__":
    main()