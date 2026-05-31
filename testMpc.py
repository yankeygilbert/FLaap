import asyncio
from mcp_client_server.mcp_client import mcpclient

connectlogical = mcpclient("logical")
connectStructural = mcpclient("structural")
connectTheoritcal = mcpclient("Theoritcal")
    
async def connect():    
    try:
        await asyncio.gather(
            connectlogical.connect_to_server("mcp_client_server/logicalserver.py"),
            connectStructural.connect_to_server("mcp_client_server/Structuralserver.py"),
            connectTheoritcal.connect_to_server("mcp_client_server/theoriticalserver.py")
        )
    finally:
        await asyncio.gather(
            connectlogical.close_async_context(),
            connectStructural.close_async_context(),
            connectTheoritcal.close_async_context(),
            return_exceptions= True
        )



if __name__ == "__main__":
  asyncio.run(connect())
    