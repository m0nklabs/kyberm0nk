import os
from crewai import Agent, Task, Crew, Process, LLM

# Configure LLM to point exactly to the host's 11434 Guardian proxy.
# We're running on host directly so localhost:11434 works.
GUARDIAN_API_KEY = os.environ.get("GUARDIAN_API_KEY", "kyberm0nk_2398a369e3e6ad0704d44ba85ea59ba7")
GUARDIAN_BASE_URL = os.environ.get("GUARDIAN_BASE_URL", "http://localhost:11434/v1")

# MUST use an uncensored base model without reasoning to prevent prefill 400 errors from Guardian/llama.cpp
llm = LLM(
    model="openai/qwen3-35b-uncensored",
    base_url=GUARDIAN_BASE_URL,
    api_key=GUARDIAN_API_KEY,
    temperature=0.1
)

# 1. Create a very simple agent
researcher = Agent(
    role="Senior AI Researcher",
    goal="Discover the most interesting facts about Aquaponics.",
    backstory="You are an expert on sustainable farming, especially Aquaponics and Hydroponics. You provide concise, factual, and interesting information.",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# 2. Create a simple task
task1 = Task(
    description="Write a 1-paragraph summary explaining the key benefit of Aquaponics over traditional soil farming.",
    expected_output="A 1-paragraph summary explaining the key benefits.",
    agent=researcher
)

# 3. Create the crew and run it
crew = Crew(
    agents=[researcher],
    tasks=[task1],
    process=Process.sequential
)

print("Starting CrewAI Local LLM Test...")
try:
    result = crew.kickoff()
    print("\n\n====== RESULT ======\n")
    print(result)
except Exception as e:
    print(f"\n\n====== ERROR ======\n{e}")

