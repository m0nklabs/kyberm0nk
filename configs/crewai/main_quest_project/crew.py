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


class GitHubRepoSearchInputSchema(BaseModel):
    """Input schema for GitHub repository search."""

    query: str = Field(..., description="Search query, file path, or repository question.")
    content_type: str = Field("code", description="One of code, issue, pr, repo, or all.")
    limit: int = Field(5, ge=1, le=10, description="Maximum number of results per content type.")


class GitHubRepoSearchTool(BaseTool):
    """Small GitHub REST search tool that avoids embedding-provider dependencies."""

    name: str = "GitHub repository search"
    description: str = "Search a GitHub repository for code, issues, pull requests, and repository metadata using the GitHub REST API."
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

    def _search_code(self, query: str, limit: int) -> dict[str, Any]:
        """Search repository code and include small file previews."""
        payload = self._get_json("/search/code", {"q": f"{query} repo:{self.github_repo}", "per_page": limit})
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
    if config["type"] != "github_search":
        raise ValueError(f"Unsupported tool type: {config['type']}")

    gh_token = os.getenv(config.get("token_env", "GITHUB_TOKEN")) or os.getenv(config.get("fallback_token_env", "GH_TOKEN"))
    if not gh_token:
        raise ValueError("Missing GitHub token env var: GITHUB_TOKEN or GH_TOKEN")

    return GitHubRepoSearchTool(
        github_repo=config["github_repo"],
        gh_token=gh_token,
        content_types=config.get("content_types") or ["code", "repo", "pr", "issue"],
    )


def build_agents(agents_config: dict[str, Any], providers: dict[str, Any], tools_config: dict[str, Any]) -> dict[str, Agent]:
    """Build CrewAI agents from YAML config."""
    agents: dict[str, Agent] = {}
    for agent_name, config in agents_config["agents"].items():
        tools = [create_tool(tool_name, tools_config) for tool_name in config.get("tools", [])]
        agents[agent_name] = Agent(
            role=config["role"],
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
        "manager_llm": create_llm(
            provider_name=manager["provider"],
            model=manager["model"],
            temperature=manager.get("temperature", 0.15),
            providers=providers,
        ),
    }

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
    args = parser.parse_args()

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
        }
    )
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
