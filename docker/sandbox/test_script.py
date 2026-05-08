import asyncio
import sys
from helpers import runtime, dotenv

sys.argv.extend(["--dockerized=true"])
runtime.initialize()
dotenv.load_dotenv()

import initialize
from agent import AgentContext, UserMessage

async def test():
    initialize.initialize_preload()
    initialize.initialize_mcp()
    agent = initialize.initialize_agent()
    # Let AZ's agent.py create it:
    ctx = AgentContext(agent, "test")
    print("Ready. Sending prompt...")
    task = ctx.communicate(UserMessage(message="Can you execute 'date', then 'uname -a' and then run a python command to print 1 to 5 with 1 second sleep in between using a loop?"))
    result = await task.result()
    print("\n\nFINISHED:", result)

asyncio.run(test())
