import os
import asyncio
import httpx
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP('Cognition')

url  = "https://openrouter.ai/api/v1/chat/completions"
@mcp.tool()
async def llm_call(prompt: str):
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=data)
        return response.json()