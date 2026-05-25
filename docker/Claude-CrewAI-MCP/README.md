# Claude-CrewAI-MCP
Model Context Protocol (MCP) server for Claude Desktop / Claude Code using [FastMCP](https://gofastmcp.com/getting-started/welcome).

In upstream form this server is mostly a CrewAI rulebook. In the KyberM0nk vendored variant it also exposes read-mostly project tools for the tracked local CrewAI setup, including:

- listing tracked Kyber CrewAI projects
- inspecting the current project config
- running the existing dry-run wrapper
- starting and stopping the tracked background run
- reading and updating persisted operator inputs
- restarting the tracked run with updated guidance
- checking direct CrewAI runtime and tracked run status
- previewing the live CrewAI log

The Kyber extension also carries two safety improvements for live NewNexus runs:

- persisted `repo_write_mode` and `github_target_branch` inputs, so a pilot can run in explicit no-write mode instead of pushing blindly to the default branch
- path-aware GitHub file lookup for the main quest crew, so queries like `NewNexus.uproject` return the actual Unreal file instead of a documentation mention

This keeps the first useful version safe enough while still being operational: Claude can inspect, validate, start, stop, steer between runs, and review the tracked CrewAI project wiring without needing full mid-run mutation tools yet.

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
