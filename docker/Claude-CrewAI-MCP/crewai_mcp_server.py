import json
import subprocess
import sys
from collections import deque
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
import yaml


SERVER_NAME = "CrewaiMcpServer"
REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIGS_DIR = REPO_ROOT / "configs" / "crewai"
SCRIPTS_DIR = REPO_ROOT / "scripts"
LOGS_DIR = REPO_ROOT / "logs"
LIVE_LOG_PATH = LOGS_DIR / "crewai_live.log"
DEFAULT_PROJECT_ID = "main_quest_project"
DEFAULT_WEB_CONTAINER = "crewai_studio_kyber"
OUTPUT_PREVIEW_CHARS = 12000
DEFAULT_LOG_LINES = 80
MAX_LOG_LINES = 200

PROJECT_SCRIPTS = {
    "main_quest_project": {
        "control": SCRIPTS_DIR / "crewai_main_quest_control.py",
        "dry_run": SCRIPTS_DIR / "crewai_main_quest_dry_run.sh",
        "live_run": SCRIPTS_DIR / "crewai_main_quest_run.sh",
    }
}

mcp = FastMCP(SERVER_NAME)


def json_response(payload: dict[str, Any]) -> str:
    """Serialize a response payload consistently."""
    return json.dumps(payload, indent=2)


def preview_text(value: Any) -> str:
    """Normalize subprocess output into a bounded UTF-8 string preview."""
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")[:OUTPUT_PREVIEW_CHARS]
    return str(value)[:OUTPUT_PREVIEW_CHARS]


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML document into a dictionary."""
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if isinstance(payload, dict):
        return payload
    return {}


def load_env_file(path: Path) -> dict[str, str]:
    """Load a simple KEY=VALUE env file into a dictionary."""
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def resolve_project_dir(project_id: str) -> Path:
    """Resolve a tracked CrewAI project directory by id."""
    project_dir = CONFIGS_DIR / project_id
    if not project_dir.exists() or not project_dir.is_dir():
        raise ValueError(f"Unknown CrewAI project id: {project_id}")
    return project_dir


def resolve_project_scripts(project_id: str) -> dict[str, Path]:
    """Return the script mapping for a tracked CrewAI project."""
    return PROJECT_SCRIPTS.get(project_id, {})


def run_control_command(
    project_id: str,
    action: str,
    timeout_seconds: int = 120,
    output: str = "json",
    extra_args: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the CrewAI control script and parse its JSON output."""
    scripts = resolve_project_scripts(project_id)
    control_script = scripts.get("control")
    if not control_script or not control_script.exists():
        return {
            "success": False,
            "project_id": project_id,
            "error": f"No control script is registered for project {project_id}.",
        }

    command = [sys.executable, str(control_script), action, "--project-id", project_id, "--output", output]
    for key, value in (extra_args or {}).items():
        option = f"--{key.replace('_', '-') }"
        if isinstance(value, bool):
            if value:
                command.append(option)
            continue
        if value is None or value == "":
            continue
        command.extend([option, str(value)])

    result = run_command(command, timeout_seconds=timeout_seconds)
    combined_output = (result["stdout"] + "\n" + result["stderr"]).strip()[:OUTPUT_PREVIEW_CHARS]
    if not result["success"]:
        return {
            "success": False,
            "project_id": project_id,
            "returncode": result["returncode"],
            "timed_out": result["timed_out"],
            "output_preview": combined_output,
            "error": result["error"] or combined_output,
        }

    try:
        payload = json.loads(result["stdout"])
    except json.JSONDecodeError:
        return {
            "success": False,
            "project_id": project_id,
            "error": "Control script did not return JSON output.",
            "output_preview": combined_output,
        }

    if not isinstance(payload, dict):
        return {
            "success": False,
            "project_id": project_id,
            "error": "Control script returned a non-object payload.",
            "output_preview": combined_output,
        }
    return payload


def load_runtime_settings() -> dict[str, str]:
    """Load CrewAI runtime settings from the repo and optional Studio env."""
    root_env = load_env_file(REPO_ROOT / ".env")
    crewai_studio_dir = Path(root_env.get("CREWAI_STUDIO_DIR", REPO_ROOT / ".agent-projects" / "CrewAI-Studio"))
    studio_env = load_env_file(crewai_studio_dir / ".env")
    container_name = studio_env.get("CREWAI_STUDIO_WEB_CONTAINER") or root_env.get("CREWAI_STUDIO_WEB_CONTAINER") or DEFAULT_WEB_CONTAINER

    return {
        "crewai_studio_dir": str(crewai_studio_dir),
        "crewai_studio_web_container": container_name,
    }


def run_command(command: list[str], timeout_seconds: int | None = None) -> dict[str, Any]:
    """Run a subprocess and return a normalized result mapping."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = preview_text(exc.stdout)
        stderr = preview_text(exc.stderr)
        return {
            "success": False,
            "returncode": None,
            "stdout": stdout,
            "stderr": stderr,
            "timed_out": True,
            "error": f"Command timed out after {timeout_seconds} seconds.",
        }

    return {
        "success": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout[:OUTPUT_PREVIEW_CHARS],
        "stderr": result.stderr[:OUTPUT_PREVIEW_CHARS],
        "timed_out": False,
        "error": "",
    }


def discover_projects() -> list[dict[str, Any]]:
    """Discover tracked CrewAI projects under configs/crewai."""
    projects: list[dict[str, Any]] = []
    for child in sorted(CONFIGS_DIR.iterdir()):
        if not child.is_dir():
            continue
        if not (child / "crew.yaml").exists():
            continue
        crew_config = load_yaml(child / "crew.yaml")
        agents_config = load_yaml(child / "agents.yaml") if (child / "agents.yaml").exists() else {}
        tasks_config = load_yaml(child / "tasks.yaml") if (child / "tasks.yaml").exists() else {}
        tools_config = load_yaml(child / "tools.yaml") if (child / "tools.yaml").exists() else {}
        scripts = resolve_project_scripts(child.name)
        projects.append(
            {
                "project_id": child.name,
                "crew_name": crew_config.get("crew", {}).get("name", child.name),
                "process": crew_config.get("crew", {}).get("process", ""),
                "agent_count": len(agents_config.get("agents", {})),
                "task_count": len(tasks_config.get("tasks", {})),
                "tool_count": len(tools_config.get("tools", {})),
                "has_control_script": bool(scripts.get("control") and scripts["control"].exists()),
                "has_dry_run": bool(scripts.get("dry_run") and scripts["dry_run"].exists()),
                "has_live_run_script": bool(scripts.get("live_run") and scripts["live_run"].exists()),
            }
        )
    return projects


def inspect_project(project_id: str) -> dict[str, Any]:
    """Return a structured summary for one tracked CrewAI project."""
    project_dir = resolve_project_dir(project_id)
    crew_config = load_yaml(project_dir / "crew.yaml")
    agents_config = load_yaml(project_dir / "agents.yaml") if (project_dir / "agents.yaml").exists() else {}
    tasks_config = load_yaml(project_dir / "tasks.yaml") if (project_dir / "tasks.yaml").exists() else {}
    tools_config = load_yaml(project_dir / "tools.yaml") if (project_dir / "tools.yaml").exists() else {}
    scripts = resolve_project_scripts(project_id)

    return {
        "project_id": project_id,
        "project_dir": str(project_dir),
        "crew": crew_config.get("crew", {}),
        "providers": sorted(crew_config.get("providers", {}).keys()),
        "agents": sorted(agents_config.get("agents", {}).keys()),
        "tasks": sorted(tasks_config.get("tasks", {}).keys()),
        "tools": sorted(tools_config.get("tools", {}).keys()),
        "script_paths": {name: str(path) for name, path in scripts.items()},
        "live_log_path": str(LIVE_LOG_PATH),
    }


def tail_lines(path: Path, line_count: int) -> list[str]:
    """Return the last N lines from a text file."""
    capped = max(1, min(line_count, MAX_LOG_LINES))
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return list(deque((line.rstrip("\n") for line in handle), maxlen=capped))


def get_container_status(container_name: str) -> dict[str, Any]:
    """Inspect the configured CrewAI Studio web container."""
    inspect_result = run_command(["docker", "inspect", "-f", "{{.State.Running}}", container_name], timeout_seconds=20)
    if not inspect_result["success"]:
        return {
            "exists": False,
            "running": False,
            "error": inspect_result["stderr"] or inspect_result["stdout"] or inspect_result["error"],
            "active_project_processes": [],
        }

    running = inspect_result["stdout"].strip().lower() == "true"
    active_processes: list[str] = []
    if running:
        process_result = run_command(["docker", "exec", container_name, "ps", "-eo", "pid,args"], timeout_seconds=20)
        if process_result["success"]:
            for line in process_result["stdout"].splitlines():
                if "kyber-main-quest-project/crew.py" in line:
                    active_processes.append(line.strip())

    return {
        "exists": True,
        "running": running,
        "error": "",
        "active_project_processes": active_processes,
    }


@mcp.tool(name="get_environment_setup_rules",
          description="Provide simple instructions for environment setup and best practices.")
def get_environment_setup_rules() -> str:
    """Provide simple instructions for environment setup and best practices."""

    instructions = [
        "To access environment variables always use the load_dotenv() function from the dotenv library."
        "Never hardcode API keys.",
        "Do not check whether environment variables are available."
    ]

    return json_response({
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

    return json_response({
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

    return json_response({
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

    return json_response({
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

    return json_response({
        "success": True,
        "instructions": instructions,
        "example_usage": {
            "workflow": "Claude should call this tool before integrating external tools with CrewAI",
            "purpose": "Get guidelines for tool integration, API connections, and custom tool creation",
            "when_to_use": "Before adding external tools or APIs to CrewAI agents"
        }
    })


@mcp.tool(name="list_kyber_crewai_projects",
          description="List tracked Kyber CrewAI projects that this MCP can inspect or dry-run.")
def list_kyber_crewai_projects() -> str:
    """List tracked Kyber CrewAI projects available to the MCP server."""
    return json_response({
        "success": True,
        "server_name": SERVER_NAME,
        "project_count": len(discover_projects()),
        "projects": discover_projects(),
    })


@mcp.tool(name="inspect_kyber_crewai_project",
          description="Inspect one tracked Kyber CrewAI project config, including crew/provider/agent/task/tool summary.")
def inspect_kyber_crewai_project(project_id: str = DEFAULT_PROJECT_ID) -> str:
    """Inspect a tracked Kyber CrewAI project configuration."""
    try:
        project_summary = inspect_project(project_id)
    except ValueError as exc:
        return json_response({
            "success": False,
            "project_id": project_id,
            "error": str(exc),
        })

    return json_response({
        "success": True,
        **project_summary,
    })


@mcp.tool(name="run_kyber_crewai_dry_run",
          description="Run the tracked Kyber CrewAI dry-run script for a project and return bounded stdout/stderr.")
def run_kyber_crewai_dry_run(project_id: str = DEFAULT_PROJECT_ID, timeout_seconds: int = 300) -> str:
    """Run a tracked Kyber CrewAI dry run."""
    scripts = resolve_project_scripts(project_id)
    dry_run_script = scripts.get("dry_run")
    if not dry_run_script or not dry_run_script.exists():
        return json_response({
            "success": False,
            "project_id": project_id,
            "error": f"No dry-run script is registered for project {project_id}.",
        })

    result = run_command(["bash", str(dry_run_script)], timeout_seconds=timeout_seconds)
    combined_output = (result["stdout"] + "\n" + result["stderr"]).strip()[:OUTPUT_PREVIEW_CHARS]
    return json_response({
        "success": result["success"],
        "project_id": project_id,
        "script": str(dry_run_script),
        "returncode": result["returncode"],
        "timed_out": result["timed_out"],
        "output_preview": combined_output,
        "error": result["error"],
    })


@mcp.tool(name="get_kyber_crewai_run_status",
          description="Inspect CrewAI Studio container health, active Kyber project processes, and live-log metadata.")
def get_kyber_crewai_run_status(project_id: str = DEFAULT_PROJECT_ID) -> str:
    """Return live CrewAI run status for a tracked Kyber project."""
    try:
        project_summary = inspect_project(project_id)
    except ValueError as exc:
        return json_response({
            "success": False,
            "project_id": project_id,
            "error": str(exc),
        })

    runtime = load_runtime_settings()
    container_status = get_container_status(runtime["crewai_studio_web_container"])
    controller_status = run_control_command(project_id=project_id, action="status", timeout_seconds=60)
    log_exists = LIVE_LOG_PATH.exists()
    return json_response({
        "success": True,
        "project_id": project_id,
        "crew_name": project_summary["crew"].get("name", project_id),
        "container": {
            "name": runtime["crewai_studio_web_container"],
            **container_status,
        },
        "log": {
            "path": str(LIVE_LOG_PATH),
            "exists": log_exists,
            "size_bytes": LIVE_LOG_PATH.stat().st_size if log_exists else 0,
            "last_modified": LIVE_LOG_PATH.stat().st_mtime if log_exists else None,
        },
        "controller": controller_status,
        "scripts": project_summary["script_paths"],
    })


@mcp.tool(name="start_kyber_crewai_live_run",
          description="Start a Kyber CrewAI run in the background through the tracked control script.")
def start_kyber_crewai_live_run(
    project_id: str = DEFAULT_PROJECT_ID,
    kickoff_mode: str = "live",
    operator_goal: str = "",
    project_path: str = "",
    current_state: str = "",
    operator_chat_guidance: str = "",
) -> str:
    """Start a Kyber CrewAI background run."""
    payload = run_control_command(
        project_id=project_id,
        action="start",
        timeout_seconds=120,
        extra_args={
            "kickoff_mode": kickoff_mode,
            "operator_goal": operator_goal,
            "project_path": project_path,
            "current_state": current_state,
            "operator_chat_guidance": operator_chat_guidance,
        },
    )
    return json_response(payload)


@mcp.tool(name="stop_kyber_crewai_live_run",
          description="Stop an active Kyber CrewAI background run through the tracked control script.")
def stop_kyber_crewai_live_run(project_id: str = DEFAULT_PROJECT_ID, force: bool = False) -> str:
    """Stop a Kyber CrewAI background run."""
    payload = run_control_command(
        project_id=project_id,
        action="stop",
        timeout_seconds=60,
        extra_args={"force": force},
    )
    return json_response(payload)


@mcp.tool(name="get_kyber_crewai_live_log_preview",
          description="Return the last N lines from the Kyber CrewAI live log for operator review.")
def get_kyber_crewai_live_log_preview(line_count: int = DEFAULT_LOG_LINES) -> str:
    """Return a bounded preview from the Kyber CrewAI live log."""
    if not LIVE_LOG_PATH.exists():
        return json_response({
            "success": False,
            "error": f"Live log does not exist at {LIVE_LOG_PATH}.",
        })

    lines = tail_lines(LIVE_LOG_PATH, line_count)
    return json_response({
        "success": True,
        "path": str(LIVE_LOG_PATH),
        "line_count": len(lines),
        "lines": lines,
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
        },
        {
            "name": "list_kyber_crewai_projects",
            "description": "List tracked Kyber CrewAI projects that can be inspected or dry-run through this MCP server.",
            "purpose": "Returns the project ids, crew names, and available run surfaces exposed by the local Kyber repo."
        },
        {
            "name": "inspect_kyber_crewai_project",
            "description": "Inspect one tracked Kyber CrewAI project configuration.",
            "purpose": "Returns crew, provider, agent, task, tool, and script metadata for a project such as main_quest_project."
        },
        {
            "name": "run_kyber_crewai_dry_run",
            "description": "Run a tracked Kyber CrewAI dry run and return bounded output.",
            "purpose": "Validates the CrewAI project wiring through the existing dry-run script before spending model tokens."
        },
        {
            "name": "get_kyber_crewai_run_status",
            "description": "Inspect CrewAI Studio container state and live-run metadata for Kyber projects.",
            "purpose": "Shows whether the web container is up, whether a Kyber crew process appears active, and whether the live log exists."
        },
        {
            "name": "start_kyber_crewai_live_run",
            "description": "Start a Kyber CrewAI background run through the tracked control script.",
            "purpose": "Starts a project-aware background run with optional operator inputs and returns the persisted controller state."
        },
        {
            "name": "stop_kyber_crewai_live_run",
            "description": "Stop an active Kyber CrewAI background run.",
            "purpose": "Stops the tracked background run cleanly and reports the resulting controller state."
        },
        {
            "name": "get_kyber_crewai_live_log_preview",
            "description": "Read the tail of the Kyber CrewAI live log.",
            "purpose": "Returns the latest operator-visible lines from logs/crewai_live.log for quick review without opening the file directly."
        },
        {
            "name": "list_server_tools",
            "description": "List all available tools provided by this CrewAI MCP server.",
            "purpose": "Returns a machine-readable catalog of every guidance and Kyber project tool exposed by this server."
        }
    ]

    return json_response({
        "success": True,
        "server_name": SERVER_NAME,
        "total_tools": len(tools),
        "tools": tools
    })


if __name__ == "__main__":
    print("CrewAI MCP Server running stdio")
    mcp.run(transport="stdio")