import re

with open("/home/flip/kyberm0nk/configs/crewai/main_quest_project/crew.py", "r") as f:
    content = f.read()

# Update signature
content = content.replace(
    "def build_tasks(tasks_config: dict[str, Any], agents: dict[str, Agent]) -> list[Task]:",
    "def build_tasks(tasks_config: dict[str, Any], agents: dict[str, Agent], agents_config: dict[str, Any]) -> list[Task]:"
)

# Replace the task creation
old_task = """        task = Task(
            description=config["description"],"""

new_task = """        agent_def = agents_config["agents"][config["agent"]]
        llm_info = f"[LLM: {agent_def['provider']} - {agent_def['model']}]"
        task = Task(
            description=f"{llm_info}\\n{config['description']}","""

content = content.replace(old_task, new_task)

# Update the call
content = content.replace(
    "    tasks = build_tasks(tasks_config, agents)",
    "    tasks = build_tasks(tasks_config, agents, agents_config)"
)

with open("/home/flip/kyberm0nk/configs/crewai/main_quest_project/crew.py", "w") as f:
    f.write(content)
