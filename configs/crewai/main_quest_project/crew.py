#!/usr/bin/env python3
"""Build and optionally run the Kyber main quest CrewAI crew from YAML config."""

from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
from typing import Any, Optional, Type

import requests
import yaml
from crewai import Agent, Crew, LLM, Process, Task
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


CONFIG_DIR = Path(__file__).resolve().parent
REQUEST_TIMEOUT_SECONDS = 30
ERROR_PREVIEW_CHARS = 1000
FILE_PREVIEW_CHARS = 3000
DEFAULT_REPO_WRITE_MODE = "disabled"
DEFAULT_GITHUB_TARGET_BRANCH = "main"


class GitHubRepoSearchInputSchema(BaseModel):
    """Input schema for GitHub repository search."""

    query: str = Field(..., description="Search query, file path, or repository question.")
    content_type: str = Field("code", description="One of code, issue, pr, repo, or all.")
    limit: int = Field(5, ge=1, le=10, description="Maximum number of results per content type.")


class GitHubRepoSearchTool(BaseTool):
    """Small GitHub REST search tool that avoids embedding-provider dependencies."""

    name: str = "newnexus_github_search"
    description: str = "Search a GitHub repository for code, issues, pull requests, and repository metadata. ACTION INPUT MUST BE A VALID JSON DICTIONARY with keys: 'query' (string), 'content_type' (string: 'code', 'issue', 'pr', 'repo', or 'all'), and 'limit' (integer)."
    args_schema: Type[BaseModel] = GitHubRepoSearchInputSchema
    github_repo: str
    gh_token: str = Field(exclude=True)
    content_types: list[str] = Field(default_factory=lambda: ["code", "repo", "pr", "issue"])
    api_base: str = "https://api.github.com"

    def __init__(self, github_repo: str, gh_token: str, content_types: Optional[list[str]] = None, **kwargs: Any) -> None:
        """Initialize the tool with repository scope and token."""
        super().__init__(
            github_repo=github_repo,
            gh_token=gh_token,
            content_types=content_types or ["code", "repo", "pr", "issue"],
            **kwargs,
        )
        self._generate_description()

    def _headers(self) -> dict[str, str]:
        """Build GitHub API request headers."""
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.gh_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _get_json(self, endpoint: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Call a GitHub API endpoint and return a normalized JSON mapping."""
        response = requests.get(
            f"{self.api_base}{endpoint}",
            headers=self._headers(),
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if response.status_code >= 400:
            return {"status_code": response.status_code, "error": response.text[:ERROR_PREVIEW_CHARS]}
        payload = response.json()
        if isinstance(payload, dict):
            payload["status_code"] = response.status_code
            return payload
        return {"status_code": response.status_code, "items": payload}

    def _fetch_file_preview(self, api_url: str) -> Optional[str]:
        """Fetch a short text preview for a GitHub code-search result."""
        payload = self._get_json(api_url.replace(self.api_base, ""))
        if payload.get("status_code") != 200 or payload.get("encoding") != "base64":
            return None
        content = payload.get("content")
        if not isinstance(content, str):
            return None
        decoded = base64.b64decode(content).decode("utf-8", errors="replace")
        return decoded[:FILE_PREVIEW_CHARS]

    def _looks_like_file_query(self, query: str) -> bool:
        """Return whether a query looks like a specific repository file path/name."""
        normalized = query.strip()
        return bool(normalized and " " not in normalized and ("/" in normalized or "." in Path(normalized).name))

    def _fetch_exact_file_match(self, file_path: str) -> Optional[dict[str, Any]]:
        """Fetch one exact repository file match when the query is already a path."""
        payload = self._get_json(f"/repos/{self.github_repo}/contents/{file_path}")
        if payload.get("status_code") != 200 or payload.get("type") != "file":
            return None
        return {
            "name": payload.get("name"),
            "path": payload.get("path"),
            "html_url": payload.get("html_url"),
            "preview": self._fetch_file_preview(payload.get("url", "")),
        }

    def _search_code(self, query: str, limit: int) -> dict[str, Any]:
        """Search repository code and include small file previews."""
        normalized_query = query.strip()
        if self._looks_like_file_query(normalized_query):
            exact_match = self._fetch_exact_file_match(normalized_query)
            if exact_match is not None:
                return {
                    "status_code": 200,
                    "total_count": 1,
                    "match_mode": "exact_path",
                    "items": [exact_match],
                }
            search_query = f"filename:{Path(normalized_query).name} repo:{self.github_repo}"
        else:
            search_query = f"{normalized_query} repo:{self.github_repo}"

        payload = self._get_json("/search/code", {"q": search_query, "per_page": limit})
        items = []
        for item in payload.get("items", [])[:limit]:
            items.append(
                {
                    "name": item.get("name"),
                    "path": item.get("path"),
                    "html_url": item.get("html_url"),
                    "preview": self._fetch_file_preview(item.get("url", "")),
                }
            )
        return {"status_code": payload.get("status_code"), "total_count": payload.get("total_count"), "items": items}

    def _search_issues(self, query: str, limit: int, pull_requests: bool = False) -> dict[str, Any]:
        """Search repository issues or pull requests."""
        issue_type = "is:pr" if pull_requests else "is:issue"
        payload = self._get_json("/search/issues", {"q": f"{query} repo:{self.github_repo} {issue_type}", "per_page": limit})
        items = []
        for item in payload.get("items", [])[:limit]:
            items.append(
                {
                    "number": item.get("number"),
                    "title": item.get("title"),
                    "state": item.get("state"),
                    "html_url": item.get("html_url"),
                    "updated_at": item.get("updated_at"),
                }
            )
        return {"status_code": payload.get("status_code"), "total_count": payload.get("total_count"), "items": items}

    def _repo_metadata(self) -> dict[str, Any]:
        """Return basic repository metadata."""
        payload = self._get_json(f"/repos/{self.github_repo}")
        return {
            "status_code": payload.get("status_code"),
            "full_name": payload.get("full_name"),
            "default_branch": payload.get("default_branch"),
            "private": payload.get("private"),
            "html_url": payload.get("html_url"),
            "description": payload.get("description"),
            "updated_at": payload.get("updated_at"),
        }

    def _run(self, query: str, content_type: str = "code", limit: int = 5) -> str:
        """Run the requested GitHub repository search."""
        normalized_type = content_type.strip().lower()
        if normalized_type not in {"code", "issue", "pr", "repo", "all"}:
            normalized_type = "code"
        requested_types = self.content_types if normalized_type == "all" else [normalized_type]

        results: dict[str, Any] = {"github_repo": self.github_repo, "query": query, "results": {}}
        if "repo" in requested_types:
            results["results"]["repo"] = self._repo_metadata()
        if "code" in requested_types:
            results["results"]["code"] = self._search_code(query, limit)
        if "issue" in requested_types:
            results["results"]["issue"] = self._search_issues(query, limit, pull_requests=False)
        if "pr" in requested_types:
            results["results"]["pr"] = self._search_issues(query, limit, pull_requests=True)
        return json.dumps(results, indent=2)




import subprocess

class WindowsSSHCommandInputSchema(BaseModel):
    """Input schema for Windows SSH Command tool."""
    command: str = Field(..., description="The command to execute on the Windows PC via SSH. Will be executed in the UnrealProjects workspace.")

class WindowsSSHCommandTool(BaseTool):
    """Tool to execute commands on the Windows PC equipped with Unreal Engine via SSH."""
    name: str = "newnexus_windows_ssh"
    description: str = "Executes arbitrary commands on the Windows 11 PC (unreal-windows) over SSH. ACTION INPUT MUST BE A VALID JSON DICTIONARY with key 'command' (string)."
    args_schema: Type[BaseModel] = WindowsSSHCommandInputSchema

    def _run(self, command: str) -> str:
        # SECURITY GUARDRAILS
        if "C:" in command.upper() or "C\\" in command.upper():
            return "CRITICAL ERROR: Command rejected by Security Guardrail. Access to the C: drive is strictly prohibited."
        if "Remove-Item" in command and "*" in command:
            return "CRITICAL ERROR: Command rejected by Security Guardrail. Wildcard deletes are prohibited."

        # Force execution in the designated workspace to prevent default C:\Users\onyou disasters
        safe_workspace = "J:\\UnrealProjects" # Update to L:\\UnrealProjects if needed
        wrapped_command = f"powershell -NoProfile -Command \"Set-Location -Path '{safe_workspace}' -ErrorAction Stop; {command}\""

        try:
            # We use the unreal-windows SSH alias already configured in the container
            result = subprocess.run(
                ["ssh", "unreal-windows", wrapped_command],
                capture_output=True,
                text=True,
                check=False
            )
            output = result.stdout + "\n" + result.stderr
            if result.returncode == 0:
                return f"Success (Exit 0):\n{output}"
            else:
                return f"Failed (Exit {result.returncode}):\n{output}"
        except Exception as e:
            return f"Error executing SSH command: {str(e)}"

# Marker replacement
class GitHubRepoPushInputSchema(BaseModel):
    """Input schema for GitHub repository push file."""
    file_path: str = Field(..., description="The path to the file in the repository (e.g. 'src/main.py').")
    content: str = Field(..., description="The text content to commit.")
    commit_message: str = Field(..., description="The commit message.")
    branch: str = Field("main", description="The branch to commit to. Defaults to main.")

class GitHubRepoPushTool(BaseTool):
    """Small GitHub REST tool to create or update a file in a repository without a local git clone."""

    name: str = "newnexus_github_push"
    description: str = "Commit and push a single file's content to a GitHub repository. ACTION INPUT MUST BE A VALID JSON DICTIONARY with keys: 'file_path' (string), 'content' (string), 'commit_message' (string), and 'branch' (string)."
    args_schema: Type[BaseModel] = GitHubRepoPushInputSchema
    github_repo: str
    gh_token: str = Field(exclude=True)
    api_base: str = "https://api.github.com"
    allow_repo_writes: bool = False
    default_branch: str = DEFAULT_GITHUB_TARGET_BRANCH

    def __init__(self, github_repo: str, gh_token: str, allow_repo_writes: bool = False, default_branch: str = DEFAULT_GITHUB_TARGET_BRANCH, **kwargs: Any) -> None:
        super().__init__(
            github_repo=github_repo,
            gh_token=gh_token,
            allow_repo_writes=allow_repo_writes,
            default_branch=default_branch,
            **kwargs,
        )
        self._generate_description()

    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.gh_token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _get_repo_default_branch(self) -> str:
        """Return the repository default branch from the GitHub API."""
        response = requests.get(
            f"{self.api_base}/repos/{self.github_repo}",
            headers=self._headers(),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if response.status_code >= 400:
            raise RuntimeError(
                f"Failed to fetch repository metadata for {self.github_repo}: {response.status_code} {response.text[:ERROR_PREVIEW_CHARS]}"
            )
        payload = response.json()
        default_branch = str(payload.get("default_branch", "")).strip()
        return default_branch or DEFAULT_GITHUB_TARGET_BRANCH

    def _get_branch_head_sha(self, branch: str) -> Optional[str]:
        """Return the HEAD SHA for a branch, or None if it does not exist."""
        response = requests.get(
            f"{self.api_base}/repos/{self.github_repo}/git/ref/heads/{branch}",
            headers=self._headers(),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if response.status_code == 404:
            return None
        if response.status_code >= 400:
            raise RuntimeError(
                f"Failed to inspect branch {branch}: {response.status_code} {response.text[:ERROR_PREVIEW_CHARS]}"
            )
        payload = response.json()
        return str(payload.get("object", {}).get("sha", "")).strip() or None

    def _ensure_branch_exists(self, branch: str) -> tuple[str, bool]:
        """Ensure the target branch exists, creating it from the repo default branch when missing."""
        existing_sha = self._get_branch_head_sha(branch)
        if existing_sha:
            return branch, False

        base_branch = self._get_repo_default_branch()
        base_sha = self._get_branch_head_sha(base_branch)
        if not base_sha:
            raise RuntimeError(f"Could not resolve base SHA for default branch {base_branch}.")

        response = requests.post(
            f"{self.api_base}/repos/{self.github_repo}/git/refs",
            headers=self._headers(),
            json={"ref": f"refs/heads/{branch}", "sha": base_sha},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if response.status_code not in {201, 422}:
            raise RuntimeError(
                f"Failed to create branch {branch} from {base_branch}: {response.status_code} {response.text[:ERROR_PREVIEW_CHARS]}"
            )
        if response.status_code == 422:
            existing_sha = self._get_branch_head_sha(branch)
            if existing_sha:
                return branch, False
            raise RuntimeError(
                f"GitHub refused to create branch {branch}: {response.text[:ERROR_PREVIEW_CHARS]}"
            )
        return branch, True

    def _run(self, file_path: str, content: str, commit_message: str, branch: str = "") -> str:
        resolved_branch = (branch or self.default_branch or DEFAULT_GITHUB_TARGET_BRANCH).strip() or DEFAULT_GITHUB_TARGET_BRANCH
        if not self.allow_repo_writes:
            return (
                "Blocked: repository writes are disabled for this CrewAI run. "
                f"Prepare an exact patch plan instead of pushing. Requested target: {file_path} on branch {resolved_branch}."
            )

        try:
            resolved_branch, branch_created = self._ensure_branch_exists(resolved_branch)
        except RuntimeError as exc:
            return f"Failed to prepare target branch {resolved_branch}: {exc}"

        file_url = f"{self.api_base}/repos/{self.github_repo}/contents/{file_path}"
        get_response = requests.get(f"{file_url}?ref={resolved_branch}", headers=self._headers(), timeout=REQUEST_TIMEOUT_SECONDS)
        
        sha = None
        if get_response.status_code == 200:
            sha = get_response.json().get("sha")
            
        data = {
            "message": commit_message,
            "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
            "branch": resolved_branch
        }
        if sha:
            data["sha"] = sha
            
        put_response = requests.put(file_url, headers=self._headers(), json=data, timeout=REQUEST_TIMEOUT_SECONDS)
        
        if put_response.status_code in [200, 201]:
            branch_note = " (branch bootstrapped)" if branch_created else ""
            return f"Success! File '{file_path}' committed and pushed to {resolved_branch}{branch_note}."
        else:
            return f"Failed to commit file. Code: {put_response.status_code}, Resp: {put_response.text}"


def repo_writes_enabled() -> bool:
    """Return whether GitHub write actions are enabled for the current run."""
    value = os.getenv("KYBER_CREWAI_REPO_WRITE_MODE", DEFAULT_REPO_WRITE_MODE).strip().lower()
    return value in {"1", "true", "yes", "enabled"}


def target_branch() -> str:
    """Return the default GitHub branch for the current run."""
    return os.getenv("KYBER_CREWAI_GITHUB_TARGET_BRANCH", DEFAULT_GITHUB_TARGET_BRANCH).strip() or DEFAULT_GITHUB_TARGET_BRANCH

def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file as a dictionary."""
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not contain a YAML mapping")
    return data


def load_configs(config_dir: Path = CONFIG_DIR) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Load crew, agent, task, and tool configuration files."""
    crew_config = load_yaml(config_dir / "crew.yaml")
    agents_config = load_yaml(config_dir / "agents.yaml")
    tasks_config = load_yaml(config_dir / "tasks.yaml")
    tools_config = load_yaml(config_dir / "tools.yaml")
    return crew_config, agents_config, tasks_config, tools_config


def create_llm(provider_name: str, model: str, temperature: float, providers: dict[str, Any]) -> LLM:
    """Create a CrewAI LLM from provider policy."""
    provider = providers[provider_name]
    api_key = os.getenv(provider["api_key_env"], provider.get("default_api_key", ""))
    api_base = os.getenv(provider["api_base_env"], provider["default_api_base"])
    if not api_key:
        raise ValueError(f"Missing required API key env var: {provider['api_key_env']}")
    return LLM(model=model, temperature=temperature, api_key=api_key, base_url=api_base)


def create_tool(tool_name: str, tools_config: dict[str, Any]) -> Any:
    """Create a CrewAI tool from YAML config."""
    config = tools_config["tools"][tool_name]
    
    gh_token = os.getenv(config.get("token_env", "GITHUB_TOKEN")) or os.getenv(config.get("fallback_token_env", "GH_TOKEN"))
    if not gh_token:
        raise ValueError("Missing GitHub token env var: GITHUB_TOKEN or GH_TOKEN")

    if config["type"] == "github_search":
        return GitHubRepoSearchTool(
            github_repo=config["github_repo"],
            gh_token=gh_token,
            content_types=config.get("content_types") or ["code", "repo", "pr", "issue"],
        )
    elif config["type"] == "github_push":
        return GitHubRepoPushTool(
            github_repo=config["github_repo"],
            gh_token=gh_token,
            allow_repo_writes=repo_writes_enabled(),
            default_branch=target_branch(),
        )
    elif config["type"] == "windows_ssh_command":
        return WindowsSSHCommandTool()
    else:
        raise ValueError(f"Unsupported tool type: {config['type']}")


def build_agents(agents_config: dict[str, Any], providers: dict[str, Any], tools_config: dict[str, Any]) -> dict[str, Agent]:
    """Build CrewAI agents from YAML config."""
    agents: dict[str, Agent] = {}
    for agent_name, config in agents_config["agents"].items():
        tools = [create_tool(tool_name, tools_config) for tool_name in config.get("tools", [])]
        agents[agent_name] = Agent(
            role=f"{config['role']} [LLM: {config['provider']} - {config['model']}]",
            goal=config["goal"],
            backstory=config["backstory"],
            allow_delegation=config.get("allow_delegation", False),
            verbose=config.get("verbose", True),
            max_iter=config.get("max_iter", 25),
            cache=config.get("cache", True),
            tools=tools,
            llm=create_llm(
                provider_name=config["provider"],
                model=config["model"],
                temperature=config.get("temperature", 0.1),
                providers=providers,
            ),
        )
    return agents


def build_tasks(tasks_config: dict[str, Any], agents: dict[str, Agent]) -> list[Task]:
    """Build ordered CrewAI tasks from YAML config."""
    tasks_by_name: dict[str, Task] = {}
    ordered_tasks: list[Task] = []
    for task_name, config in tasks_config["tasks"].items():
        context = [tasks_by_name[name] for name in config.get("context", [])]
        task = Task(
            description=config["description"],
            expected_output=config["expected_output"],
            async_execution=config.get("async_execution", False),
            agent=agents[config["agent"]],
            context=context or None,
        )
        tasks_by_name[task_name] = task
        ordered_tasks.append(task)
    return ordered_tasks


def build_crew(config_dir: Path = CONFIG_DIR) -> Crew:
    """Build the Kyber main quest CrewAI crew."""
    crew_config, agents_config, tasks_config, tools_config = load_configs(config_dir)
    providers = crew_config["providers"]
    crew_settings = crew_config["crew"]
    agents = build_agents(agents_config, providers, tools_config)
    tasks = build_tasks(tasks_config, agents)

    manager = crew_settings["manager_llm"]
    planning = crew_settings.get("planning_llm")
    process_name = crew_settings.get("process", "sequential")
    process = Process.hierarchical if process_name == "hierarchical" else Process.sequential

    crew_args: dict[str, Any] = {
        "agents": list(agents.values()),
        "tasks": tasks,
        "process": process,
        "verbose": crew_settings.get("verbose", True),
        "memory": crew_settings.get("memory", False),
        "cache": crew_settings.get("cache", True),
        "planning": crew_settings.get("planning", False),
        "max_rpm": crew_settings.get("max_rpm", 30),
    }

    if manager:
        manager_llm_obj = create_llm(
            provider_name=manager["provider"],
            model=manager["model"],
            temperature=manager.get("temperature", 0.15),
            providers=providers,
        )
        try:
            from crewai.utilities.i18n import I18N
            i18n = I18N()
            role = f"{i18n.retrieve('hierarchical_manager_agent', 'role')} [LLM: {manager['provider']} - {manager['model']}]"
            goal = i18n.retrieve("hierarchical_manager_agent", "goal")
            backstory = i18n.retrieve("hierarchical_manager_agent", "backstory")
        except Exception:
            role = f"Crew Manager [LLM: {manager['provider']} - {manager['model']}]"
            goal = "Manage the crew to complete the task in the best way possible."
            backstory = "You are a seasoned manager with a knack for getting the best out of your team. You allow them to do the work. Even if you don't perform the tasks by yourself, you properly evaluate the work of your team members."
            
        crew_args["manager_agent"] = Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            allow_delegation=True,
            verbose=crew_settings.get("verbose", True),
            llm=manager_llm_obj,
        )

    if planning:
        crew_args["planning_llm"] = create_llm(
            provider_name=planning["provider"],
            model=planning["model"],
            temperature=planning.get("temperature", 0.2),
            providers=providers,
        )

    return Crew(**crew_args)


def main() -> int:
    """CLI entry point for dry-run validation or kickoff."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Build the crew without calling any model.")
    parser.add_argument("--operator-goal", default="Create the first playable NewNexus Unreal slice.")
    parser.add_argument("--project-path", default="/workspace/project/.agent-projects/NewNexus")
    parser.add_argument("--current-state", default="NewNexus is the Unreal Engine project in m0nklabs/NewNexus.")
    parser.add_argument("--operator-chat-guidance", default="Stay on Unreal Engine and NewNexus. Do not switch to Unity or generic 2D assumptions.")
    parser.add_argument("--repo-write-mode", choices=("disabled", "enabled"), default=DEFAULT_REPO_WRITE_MODE)
    parser.add_argument("--github-target-branch", default=DEFAULT_GITHUB_TARGET_BRANCH)
    args = parser.parse_args()

    os.environ["KYBER_CREWAI_REPO_WRITE_MODE"] = args.repo_write_mode
    os.environ["KYBER_CREWAI_GITHUB_TARGET_BRANCH"] = args.github_target_branch

    crew = build_crew()
    if args.dry_run:
        print(f"Built crew with {len(crew.agents)} agents and {len(crew.tasks)} tasks")
        return 0

    result = crew.kickoff(
        inputs={
            "operator_goal": args.operator_goal,
            "project_path": args.project_path,
            "current_state": args.current_state,
            "operator_chat_guidance": args.operator_chat_guidance,
            "repo_write_mode": args.repo_write_mode,
            "github_target_branch": args.github_target_branch,
        }
    )
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
