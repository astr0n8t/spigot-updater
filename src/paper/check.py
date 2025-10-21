"""
PaperMC update checker
"""
import aiohttp
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.discord_utils import capitalise, create_embed

async def check(bot):
    """Check for PaperMC updates"""
    servers = {k: v for k, v in bot.config['servers'].items() 
               if v['jar']['type'].lower() == 'paper'}
    
    if not servers:
        return bot.log.info('No Paper servers need to be checked')
    
    bot.log.info('Checking for updates for Paper servers')
    
    async with aiohttp.ClientSession() as session:
        for server_name, server_config in servers.items():
            version = server_config['jar']['version']
            
            try:
                # Get latest build
                url = f'https://api.papermc.io/v2/projects/paper/versions/{version}'
                async with session.get(url) as response:
                    data = await response.json()
                    latest_build = data['builds'][-1]
                
                # Get build details
                url = f'https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{latest_build}'
                async with session.get(url) as response:
                    build_data = await response.json()
                    download = build_data['downloads']['application']
                    filename = download['name']
                    checksum = download['sha256']
                
                # Check database
                session_db = bot.db['Session']()
                try:
                    jar = session_db.query(bot.db['ServerJars']).filter_by(
                        type='paper',
                        version=version
                    ).first()
                    
                    if not jar:
                        jar = bot.db['ServerJars'](type='paper', version=version)
                        session_db.add(jar)
                    
                    if jar.approved_build == str(latest_build):
                        continue
                    
                    # Update latest info
                    jar.latest_version = version
                    jar.latest_build = str(latest_build)
                    jar.latest_file = filename
                    jar.latest_checksum = checksum
                    session_db.commit()
                    
                    # Notify about update
                    bot.log.info(f'Found an update for Paper {version}')
                    
                    affected = ', '.join([f'`{s}`' for s in servers.keys()])
                    
                    embed = create_embed(
                        title=f'🆕 A new version of Paper {version} is available',
                        description='React with ✅ to approve this update and add it to the queue.',
                        color=0xFFA500  # Orange
                    )
                    embed.add_field(name='Build', value=f'#{latest_build}', inline=True)
                    embed.add_field(name='Changelog', 
                                  value=f'[View on PaperMC](https://papermc.io/downloads/paper)', 
                                  inline=False)
                    embed.add_field(name='Affected servers', value=affected, inline=False)
                    
                    msg = await bot.channel.send(embed=embed)
                    await msg.add_reaction('✅')
                    
                    bot.messages[msg.id] = {
                        'server_jar': {
                            'type': 'paper',
                            'version': version,
                            'actual_version': version,
                            'build': str(latest_build),
                            'file': filename,
                            'checksum': checksum
                        }
                    }
                    
                finally:
                    session_db.close()
                    
            except Exception as e:
                bot.log.error(f'Error checking Paper {version}: {e}')
