import re

with open("/home/flip/kyberm0nk/configs/crewai/main_quest_project/crew.py", "r") as f:
    content = f.read()

# Fix the manager agent initialization in build_crew
old_manager = """    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.hierarchical if crew_settings.get("process") == "hierarchical" else Process.sequential,
        manager_llm=create_llm(manager["provider"], manager["model"], manager.get("temperature", 0.1), providers) if manager else None,"""

new_manager = """
    manager_agent = None
    if manager:
        from crewai import Agent
        manager_agent = Agent(
            role=f"Crew Manager [LLM: {manager['provider']} - {manager['model']}]",
            goal="Manage the crew to complete the tasks.",
            backstory="You are the expert manager of this crew.",
            allow_delegation=True,
            llm=create_llm(manager["provider"], manager["model"], manager.get("temperature", 0.1), providers)
        )

    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.hierarchical if crew_settings.get("process") == "hierarchical" else Process.sequential,
        manager_agent=manager_agent,"""

content = content.replace(old_manager, new_manager)

with open("/home/flip/kyberm0nk/configs/crewai/main_quest_project/crew.py", "w") as f:
    f.write(content)
