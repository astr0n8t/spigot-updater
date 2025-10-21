"""
GitHub Releases update checker
"""
import aiohttp
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.discord_utils import create_embed

async def check(bot):
    """Check for GitHub release updates"""
    plugins = {k: v for k, v in bot.config['plugins'].items()
               if v.get('source', '').lower() == 'github'}
    
    if not plugins:
        return bot.log.info('No GitHub plugins need to be checked')
    
    bot.log.info('Checking for updates for plugins on GitHub')
    
    async with aiohttp.ClientSession() as session:
        for plugin_name, plugin_config in plugins.items():
            try:
                repo = plugin_config.get('repo')
                if not repo:
                    continue
                
                url = f'https://api.github.com/repos/{repo}/releases/latest'
                async with session.get(url) as response:
                    data = await response.json()
                    latest = data['tag_name']
                
                # Check database
                session_db = bot.db['Session']()
                try:
                    plugin = session_db.query(bot.db['Plugins']).filter_by(name=plugin_name).first()
                    
                    if not plugin:
                        plugin = bot.db['Plugins'](name=plugin_name)
                        session_db.add(plugin)
                    
                    if plugin.approved == latest:
                        continue
                    
                    plugin.latest = latest
                    session_db.commit()
                    
                    bot.log.info(f'Found an update for {plugin_name}')
                    
                    affected = ', '.join([f'`{s}`' for s, cfg in bot.config['servers'].items() 
                                        if plugin_name in cfg.get('plugins', [])])
                    
                    embed = create_embed(
                        title=f'🆕 A new version of {plugin_name} is available',
                        description='React with ✅ to approve this update and add it to the queue.',
                        color=0xFFA500
                    )
                    embed.add_field(name='Version', value=latest, inline=True)
                    embed.add_field(name='Changelog', 
                                  value=f'[View on GitHub](https://github.com/{repo}/releases/tag/{latest})', 
                                  inline=False)
                    embed.add_field(name='Affected servers', value=affected or 'None', inline=False)
                    
                    msg = await bot.channel.send(embed=embed)
                    await msg.add_reaction('✅')
                    
                    bot.messages[msg.id] = {
                        'plugin': {
                            'name': plugin_name,
                            'version': latest
                        }
                    }
                finally:
                    session_db.close()
                    
            except Exception as e:
                bot.log.error(f'Error checking GitHub plugin {plugin_name}: {e}')
