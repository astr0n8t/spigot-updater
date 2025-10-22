"""
Upload files to Pterodactyl servers
"""
import asyncio
import os
import json
import sys
from pathlib import Path as PathLib

# Add src directory to path
sys.path.insert(0, str(PathLib(__file__).parent.parent))

from pterodactyl import Pterodactyl
from utils.minecraft import get_player_count, wait
from utils.fs import path
from utils.discord_utils import create_embed

async def upload_files(bot):
    """Upload approved updates to servers"""
    ptero_host = os.getenv('PTERO_HOST')
    ptero_key = os.getenv('PTERO_CLIENT_KEY')
    
    if not ptero_host or not ptero_key:
        return bot.log.error('Pterodactyl credentials not configured')
    
    panel = Pterodactyl(ptero_host, ptero_key)
    
    pinged = False
    
    for server_name, server_config in bot.config['servers'].items():
        pterodactyl_id = server_config.get('pterodactyl_id')
        if not pterodactyl_id:
            continue
        
        session_db = bot.db['Session']()
        try:
            # Get server record
            server = session_db.query(bot.db['Servers']).filter_by(name=server_name).first()
            if not server:
                server = bot.db['Servers'](name=server_name, plugins='{}')
                session_db.add(server)
                session_db.commit()
            
            # Get server jar record
            jar_type = server_config['jar']['type']
            jar_version = server_config['jar']['version']
            sjar = session_db.query(bot.db['ServerJars']).filter_by(
                type=jar_type,
                version=jar_version
            ).first()
            
            # Check which plugins need updating
            plugins_to_update = []
            server_plugins = server_config.get('plugins', [])
            current_plugins = json.loads(server.plugins or '{}')
            
            for plugin_name in server_plugins:
                plugin = session_db.query(bot.db['Plugins']).filter_by(name=plugin_name).first()
                if plugin and plugin.downloaded and current_plugins.get(plugin_name) != plugin.downloaded:
                    plugins_to_update.append(plugin_name)
            
            # Check if server jar needs updating
            jar_needs_updating = sjar and sjar.downloaded and server.current != sjar.downloaded
            
            if not plugins_to_update and not jar_needs_updating:
                bot.log.info(f'{server_name} has no updates pending')
                continue
            
            if not pinged:
                await bot.channel.send('@here')
                pinged = True
            
            # Check player count
            max_players = server_config.get('max_players', 0)
            current_players = await get_player_count(bot, server_name)
            
            # Create approval message
            if current_players > max_players:
                embed = create_embed(
                    title=f'⚠️ {server_name} needs to update, but there are more than {max_players} players online',
                    description=f'React with ⚠️ to update the server now, whilst there are **{current_players} players online**, react with ❌ to dismiss.',
                    color=0xFF0000  # Red
                )
            else:
                embed = create_embed(
                    title=f'📣 {server_name} needs to update',
                    description=f'React with ✅ to update the server now, whilst there are **{current_players} players online**, react with ❌ to dismiss.',
                    color=0xFFA500  # Orange
                )
            
            embed.add_field(
                name='Plugins',
                value=', '.join([f'`{p}`' for p in plugins_to_update]) or 'None'
            )
            
            message = await bot.channel.send(embed=embed)
            await message.add_reaction('⚠️' if current_players > max_players else '✅')
            await message.add_reaction('❌')
            
            # Wait for reaction (15 minutes timeout)
            def check(reaction, user):
                return (user != bot.user and 
                       reaction.message.id == message.id and
                       str(reaction.emoji) in ['✅', '⚠️', '❌'])
            
            try:
                reaction, user = await bot.wait_for('reaction_add', timeout=900, check=check)
                
                if str(reaction.emoji) == '❌':
                    bot.log.info(f'{user.name} blocked {server_name} from updating')
                    await message.edit(embed=create_embed(
                        title=embed.title,
                        description=f'Dismissed by {user.mention}.',
                        color=0x00FF00  # Green
                    ))
                    await message.clear_reactions()
                    continue
                
                # Approved - perform update
                bot.log.info(f'{user.name} authorized {server_name} to update')
                
                # Stop server
                await panel.stop(pterodactyl_id)
                
                # Upload server jar if needed
                if jar_needs_updating:
                    bot.log.info(f'Uploading server jar for {server_name}')
                    jar_path = path(f'data/servers/{sjar.id}/server.jar')
                    await panel.upload(pterodactyl_id, '/', [jar_path])
                    server.current = sjar.downloaded
                
                # Upload plugins if needed
                if plugins_to_update:
                    bot.log.info(f'Uploading {len(plugins_to_update)} plugins for {server_name}')
                    jar_paths = []
                    for plugin_name in plugins_to_update:
                        plugin_config = bot.config['plugins'].get(plugin_name)
                        if plugin_config:
                            jar_paths.append(path(f"data/plugins/{plugin_config['jar']}"))
                        plugin = session_db.query(bot.db['Plugins']).filter_by(name=plugin_name).first()
                        if plugin:
                            current_plugins[plugin_name] = plugin.downloaded
                    
                    if jar_paths:
                        await panel.upload(pterodactyl_id, '/plugins/', jar_paths)
                    
                    server.plugins = json.dumps(current_plugins)
                
                session_db.commit()
                
                # Restart server
                await wait(5000)
                power_state = await panel.get_power_state(pterodactyl_id)
                if power_state != 'offline':
                    await panel.kill(pterodactyl_id)
                await panel.start(pterodactyl_id)
                
                # Update message
                await message.edit(embed=create_embed(
                    title=f'✅ {server_name} has been updated',
                    description=f'Updated by {user.mention}.',
                    color=0x00FF00
                ))
                await message.clear_reactions()
                
            except asyncio.TimeoutError:
                bot.log.warning(f'Update approval timed out for {server_name}')
                await message.edit(embed=create_embed(
                    title=embed.title,
                    description='Timed out',
                    color=0x00FF00
                ))
                await message.clear_reactions()
            except Exception as e:
                bot.log.error(f'Error updating {server_name}: {e}')
                await message.edit(embed=create_embed(
                    title=embed.title,
                    description=f'Update failed: {str(e)}',
                    color=0xFF0000
                ))
                await message.clear_reactions()
        
        finally:
            session_db.close()
