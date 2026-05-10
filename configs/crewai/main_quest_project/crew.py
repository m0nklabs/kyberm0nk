#!/usr/bin/env python3
"""Build and optionally run the Kyber main quest CrewAI crew from YAML config."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

import yaml
from crewai import Agent, Crew, LLM, Process, Task


CONFIG_DIR = Path(__file__).resolve().parent


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file as a dictionary."""
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not contain a YAML mapping")
    return data


def load_configs(config_dir: Path = CONFIG_DIR) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Load crew, agent, and task configuration files."""
    crew_config = load_yaml(config_dir / "crew.yaml")
    agents_config = load_yaml(config_dir / "agents.yaml")
    tasks_config = load_yaml(config_dir / "tasks.yaml")
    return crew_config, agents_config, tasks_config


def create_llm(provider_name: str, model: str, temperature: float, providers: dict[str, Any]) -> LLM:
    """Create a CrewAI LLM from provider policy."""
    provider = providers[provider_name]
    api_key = os.getenv(provider["api_key_env"], provider.get("default_api_key", ""))
    api_base = os.getenv(provider["api_base_env"], provider["default_api_base"])
    if not api_key:
        raise ValueError(f"Missing required API key env var: {provider['api_key_env']}")
    return LLM(model=model, temperature=temperature, api_key=api_key, base_url=api_base)


def build_agents(agents_config: dict[str, Any], providers: dict[str, Any]) -> dict[str, Agent]:
    """Build CrewAI agents from YAML config."""
    agents: dict[str, Agent] = {}
    for agent_name, config in agents_config["agents"].items():
        agents[agent_name] = Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            allow_delegation=config.get("allow_delegation", False),
            verbose=config.get("verbose", True),
            max_iter=config.get("max_iter", 25),
            cache=config.get("cache", True),
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
    crew_config, agents_config, tasks_config = load_configs(config_dir)
    providers = crew_config["providers"]
    crew_settings = crew_config["crew"]
    agents = build_agents(agents_config, providers)
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
    parser.add_argument("--operator-goal", default="Create the first playable slice for the current game.")
    parser.add_argument("--project-path", default="/workspace/project")
    parser.add_argument("--current-state", default="No current state supplied.")
    parser.add_argument("--operator-chat-guidance", default="Keep scope small and verify the result.")
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
