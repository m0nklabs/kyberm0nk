import json

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("CrewaiMcpServer")


@mcp.tool(name="get_environment_setup_rules",
          description="Provide simple instructions for environment setup and best practices.")
def get_environment_setup_rules() -> str:
    """Provide simple instructions for environment setup and best practices."""

    instructions = [
        "To access environment variables always use the load_dotenv() function from the dotenv library."
        "Never hardcode API keys.",
        "Do not check whether environment variables are available."
    ]

    return json.dumps({
        "success": True,
        "instructions": instructions,
        "example_usage": {
            "workflow": "Claude should call this tool before writing CrewAI Python scripts",
            "purpose": "Get coding guidelines and best practices for CrewAI development",
            "when_to_use": "Before starting any CrewAI project or when setting up environment variables"
        }
    })


@mcp.tool(name="get_agent_definition_rules",
          description="Provide guidelines for defining CrewAI agents with proper roles, goals, and backstories.")
def get_agent_definition_rules() -> str:
    """Provide guidelines for defining CrewAI agents with proper roles, goals, and backstories."""

    instructions = [
        "Input variables must be listed in the agent's role field.",
        """Example:
        role: {input variable 1} {input variable 2} <definition of role>""",
        "Add critical behavioral instructions (like no-hallucination rules) to both agent backstories AND task descriptions for reinforcement.",
    ]

    return json.dumps({
        "success": True,
        "instructions": instructions,
        "example_usage": {
            "workflow": "Claude should call this tool before creating CrewAI agents",
            "purpose": "Get guidelines for agent role definition, goal setting, and backstory creation",
            "when_to_use": "Before defining Agent objects in CrewAI scripts"
        }
    })


@mcp.tool(name="get_task_definition_rules",
          description="Provide guidelines for defining CrewAI tasks with clear descriptions, expected outputs, and agent assignments.")
def get_task_definition_rules() -> str:
    """Provide guidelines for defining CrewAI tasks with clear descriptions, expected outputs, and agent assignments."""

    instructions = [
        """If the requested output is JSON, always specify the following fields:
        expected_output=<definition of the expected output>,
        output_json=<Pydantic class that provides the schema for the JSON output>,
        output_format="json"
        """,
        """If Serper is specified as the tool, make sure to explicitly instruct CrewAI how to interface Serper:
        ✅ Formulate the desired queries (e.g., "cybersecurity startup industry benchmarks cash burn rate venture debt 2024")
        ✅ Ensure that the input for the tool is a key/value dictionary""",
        "When adding validation rules, integrate them directly into existing task descriptions rather than restructuring.",
        "Add critical behavioral instructions (like no-hallucination rules) to both agent backstories AND task descriptions for reinforcement.",
        "Keep instruction additions focused and specific rather than comprehensive rewrites.",
        "Prioritize data integrity and accuracy features over user experience or maintainability improvements.",
    ]

    return json.dumps({
        "success": True,
        "instructions": instructions,
        "example_usage": {
            "workflow": "Claude should call this tool before creating CrewAI tasks",
            "purpose": "Get guidelines for task description, output specification, and agent assignment",
            "when_to_use": "Before defining Task objects in CrewAI scripts"
        }
    })


@mcp.tool(name="get_crew_setup_rules",
          description="Provide guidelines for setting up CrewAI crews, including agent coordination and workflow management.")
def get_crew_setup_rules() -> str:
    """Provide guidelines for setting up CrewAI crews, including agent coordination and workflow management."""

    instructions = [
        "All functionalities must be executed by the CrewAI agents, tasks and their tools. No processing code is needed besides CrewAI components.",
        "The output of the kick0ff() function is not a string, but rather an instance of the CrewOutput class.",
        "If the intended output is JSON, use the .json property of the CrewOutput class to obtain a JSON-formatted string and then convert it to a dictionary using the json Python library.",
        "Do not parse JSON output. If you specify a Pydantic class for output, the output will be guaranteed valid JSON.",
        """If agents use a Model Context Protocol (MCP) server, always use StdioServerParameters and MCPServerAdapter classes:
    
    server_params=StdioServerParameters(
        command="",
        args=[""],
        env={""},
    )
    
    with MCPServerAdapter(server_params) as mcp_tools:
        agent = self._create_some_agent(mcp_tools)
        ...
        
        """
    ]

    return json.dumps({
        "success": True,
        "instructions": instructions,
        "example_usage": {
            "workflow": "Claude should call this tool before creating CrewAI crews",
            "purpose": "Get guidelines for crew composition, agent coordination, and workflow setup",
            "when_to_use": "Before defining Crew objects and orchestrating multi-agent workflows"
        }
    })


@mcp.tool(name="get_general_rules",
          description="Provide guidelines for integrating external tools and APIs with CrewAI agents.")
def get_general_rules() -> str:
    """Provide guidelines for integrating external tools and APIs with CrewAI agents."""

    instructions = [
        "Keep the code as simple as possible and as readable as possible.",
        "Avoid all interaction with the user. The input data should be hardcoded in the main() function for testing and passed as arguments to the kickoff() function of the Crew class.",
        "Do not code any fallback simulated outputs as an alternative for the crew output.",
        "Always code a single crew and never split the code into separate crews.",
        "Never code any RegEx.",
        "Do not include any logging. Do not print anything to stdout. CrewaAI is sufficiently verbose.",
        "Remove all unused imports from the code.",
        "Keep code structure minimal and focused - avoid adding main() functions, extensive documentation, or example usage unless explicitly requested.",
        "Preserve existing method names and class structure - **only modify what's specifically requested**.",
        "Do not generate mockup data for testing.",
        "Don't add comprehensive docstrings or comments unless the user asks for documentation improvements.",
        "Avoid suggesting 'best practices' that add complexity like retry logic, configuration management, or extensive error handling unless the user identifies these as problems.",
    ]

    return json.dumps({
        "success": True,
        "instructions": instructions,
        "example_usage": {
            "workflow": "Claude should call this tool before integrating external tools with CrewAI",
            "purpose": "Get guidelines for tool integration, API connections, and custom tool creation",
            "when_to_use": "Before adding external tools or APIs to CrewAI agents"
        }
    })


@mcp.tool(name="list_server_tools", description="List all available tools provided by this CrewAI MCP server.")
def list_server_tools() -> str:
    """List all available tools provided by this CrewAI MCP server."""

    tools = [
        {
            "name": "get_environment_setup_rules",
            "description": "Provide simple instructions for environment setup and best practices.",
            "purpose": "Returns comprehensive guidelines for setting up environment variables, API keys, and configuration management."
        },
        {
            "name": "get_agent_definition_rules",
            "description": "Provide guidelines for defining CrewAI agents with proper roles, goals, and backstories.",
            "purpose": "Returns guidelines for creating well-defined agents with clear responsibilities and characteristics."
        },
        {
            "name": "get_task_definition_rules",
            "description": "Provide guidelines for defining CrewAI tasks with clear descriptions, expected outputs, and agent assignments.",
            "purpose": "Returns guidelines for creating structured tasks with proper specifications and agent assignments."
        },
        {
            "name": "get_crew_setup_rules",
            "description": "Provide guidelines for setting up CrewAI crews, including agent coordination and workflow management.",
            "purpose": "Returns guidelines for orchestrating multi-agent crews and managing workflows effectively."
        },
        {
            "name": "get_general_rules",
            "description": "Provide general guidelines for writing Python code using the CrewAI framework.",
            "purpose": "Returns guidelines for writing Python applications based on the CrewAI crews, agents, tasks and tools."
        }
    ]

    return json.dumps({
        "success": True,
        "server_name": "CrewaiMcpServer",
        "total_tools": len(tools),
        "tools": tools
    })


if __name__ == "__main__":
    print("CrewAI MCP Server running stdio")
    mcp.run(transport="stdio")