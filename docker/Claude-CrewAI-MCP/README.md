# Claude-CrewAI-MCP
Model Context Protocol (MCP) server for the Claude Desktop that instructs it how to properly code Python projects using CrewAI. Uses [FastMCP](https://gofastmcp.com/getting-started/welcome).

## Installation
```
{
  "mcpServers": {
    "CrewaiMcpServer": {
      "command": "path/to/venv/with/installed/fastmcp",
      "args": ["path/to/crewai_mcp_server.py"]
    }
  }
}
```

## Quick Start
Add the Claude-CrewAI-MCP configuration to the claude_desktop_config.json and restart Claude Desktop completely. Detailed instructions are available [here](https://modelcontextprotocol.io/quickstart/user).

## Contributing

We welcome collaboration!

If you're interested in contributing, here's how you can get involved:

1. **Fork the repository**
2. **Create a branch** for your feature or fix
3. **Commit your changes**
4. **Open a Pull Request**

We also welcome ideas, feedback, and discussion in [Issues](https://github.com/NahumKorda/Claude-CrewAI-MCP/issues).

### Want to join as a collaborator?

If you'd like to be added as a direct collaborator (with push access), please reach out by:

* Opening an issue and introducing yourself
* Or contacting me directly via [GitHub](https://github.com/NahumKorda)
