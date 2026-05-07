import aiohttp
import os
from helpers import runtime

URL = os.environ.get("A0_SEARXNG_URL", "http://searxng:8080/search")

async def search(query:str):
    return await runtime.call_development_function(_search, query=query)

async def _search(query:str):
    async with aiohttp.ClientSession() as session:
        async with session.post(URL, data={"q": query, "format": "json"}) as response:
            return await response.json()
