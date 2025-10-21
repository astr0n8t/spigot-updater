"""
Minecraft utilities
"""
import asyncio
from mcstatus import JavaServer

async def get_player_count(bot, server_name: str) -> int:
    """Get current player count for a server"""
    try:
        server_config = bot.config['servers'].get(server_name)
        if not server_config or 'address' not in server_config:
            bot.log.warning(f'No address configured for {server_name}')
            return 0
        
        address = server_config['address']
        server = JavaServer.lookup(address)
        status = await asyncio.to_thread(server.status)
        return status.players.online
    except Exception as e:
        bot.log.error(f'Failed to get player count for {server_name}: {e}')
        return 0

def wait(milliseconds: int):
    """Wait for specified milliseconds"""
    return asyncio.sleep(milliseconds / 1000)
