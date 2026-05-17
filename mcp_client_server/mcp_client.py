import asyncio

from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

#--- Mcp - Client configuration ---
class mcpclient:
    def __init__(self):
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
    
    async def connect_to_server(self, server_path: str):
        server_params = StdioServerParameters(
            command= 'python3.11',
            args= [server_path],
            env= None
        )

        stdio_tranport= await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_tranport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()

    async def call_analysis(self):
        cont =None