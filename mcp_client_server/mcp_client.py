import sys

from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

#--- Mcp - Client configuration ---#
class mcpclient:
    def __init__(self, domain: str):
        self.domain = domain
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
    #--- server connection configuration ---#
    async def connect_to_server(self, server_path: str):
        try:
            server_params = StdioServerParameters(
                command= 'python3.11',
                args= [server_path],
               
            )
            sys.stderr.write(f'Connecting To Server :{self.domain} .....\n')
            stdio_tranport= await self.exit_stack.enter_async_context(stdio_client(server_params))
            self.stdio, self.write = stdio_tranport
            self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
            await self.session.initialize()
            sys.stderr.write(f'Connected To Server :{self.domain}\n')
        except  Exception as e:
            sys.stderr.write(f'Failed to Connect to Server : {self.domain}')
            sys.stderr.write(f'Error Details {e}')

    #--- Tool session configuration ---#
    async def call_analysis(self, tool_name: str, args: dict ):
        if not self.session:
            raise RuntimeError("Mcp Session not Connected")
        response = await self.session.call_tool(tool_name,args)

    #--- existing async context ---#
    async def close_async_context(self):
        await self.exit_stack.aclose()