import re

with open("/home/flip/kyberm0nk/configs/crewai/main_quest_project/crew.py", "r") as f:
    content = f.read()

# Revert the old task description patch if present
if "agent_def = agents_config" in content:
    content = re.sub(
        r'        agent_def = agents_config\["agents"\]\[config\["agent"\]\].*?task = Task\(\n            description=f"\{llm_info\}\\n\{config\[\'description\'\]\}",',
        r'        task = Task(\n            description=config["description"],',
        content, flags=re.DOTALL
    )

if "def build_tasks(tasks_config: dict[str, Any], agents: dict[str, Agent], agents_config: dict[str, Any]) -> list[Task]:" in content:
    content = content.replace(
        "def build_tasks(tasks_config: dict[str, Any], agents: dict[str, Agent], agents_config: dict[str, Any]) -> list[Task]:",
        "def build_tasks(tasks_config: dict[str, Any], agents: dict[str, Agent]) -> list[Task]:"
    )
    content = content.replace(
        "tasks = build_tasks(tasks_config, agents, agents_config)",
        "tasks = build_tasks(tasks_config, agents)"
    )

# Inject into build_agents -> role
# Look for: role=config["role"],
content = content.replace(
    'role=config["role"],',
    'role=f"{config[\'role\']} [LLM: {config[\'provider\']} - {config[\'model\']}]",'
)

with open("/home/flip/kyberm0nk/configs/crewai/main_quest_project/crew.py", "w") as f:
    f.write(content)
