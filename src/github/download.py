"""
GitHub Releases download module
"""
import aiohttp
import aiofiles
from pathlib import Path
from utils.fs import path

async def download(bot):
    """Download approved GitHub releases"""
    bot.log.info('Downloading approved GitHub releases')
    
    session_db = bot.db['Session']()
    try:
        plugins = session_db.query(bot.db['Plugins']).all()
        
        for plugin in plugins:
            if not plugin.approved or plugin.downloaded == plugin.approved:
                continue
            
            # Check if this is a GitHub plugin
            plugin_config = bot.config['plugins'].get(plugin.name)
            if not plugin_config or plugin_config.get('source', '').lower() != 'github':
                continue
            
            bot.log.info(f'Downloading {plugin.name} {plugin.approved}')
            
            repo = plugin_config.get('repo')
            jar_name = plugin_config.get('jar')
            
            try:
                # Get release assets
                url = f'https://api.github.com/repos/{repo}/releases/tags/{plugin.approved}'
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        data = await response.json()
                        
                        # Find the JAR asset
                        asset = None
                        for a in data.get('assets', []):
                            if a['name'].endswith('.jar'):
                                asset = a
                                break
                        
                        if not asset:
                            bot.log.warning(f'No JAR found for {plugin.name}')
                            continue
                        
                        # Download the JAR
                        download_url = asset['browser_download_url']
                        async with session.get(download_url) as dl_response:
                            if dl_response.status == 200:
                                jar_path = Path(path(f'data/plugins/{jar_name}'))
                                jar_path.parent.mkdir(parents=True, exist_ok=True)
                                
                                async with aiofiles.open(jar_path, 'wb') as f:
                                    await f.write(await dl_response.read())
                                
                                plugin.downloaded = plugin.approved
                                session_db.commit()
                                bot.log.success(f'Downloaded {plugin.name} {plugin.approved}')
                            else:
                                bot.log.error(f'Failed to download {plugin.name}: HTTP {dl_response.status}')
            
            except Exception as e:
                bot.log.error(f'Error downloading {plugin.name}: {e}')
    
    finally:
        session_db.close()
