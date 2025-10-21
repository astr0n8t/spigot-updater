"""
PaperMC download module
"""
import aiohttp
import aiofiles
from pathlib import Path
from utils.fs import path

async def download(bot):
    """Download approved Paper versions"""
    bot.log.info('Downloading approved Paper versions')
    
    session_db = bot.db['Session']()
    try:
        jars = session_db.query(bot.db['ServerJars']).filter_by(type='paper').all()
        
        for jar in jars:
            if not jar.approved_build or jar.downloaded == jar.approved_build:
                continue
            
            bot.log.info(f'Downloading Paper {jar.version} build {jar.approved_build}')
            
            # Create directory
            jar_dir = Path(path(f'data/servers/{jar.id}'))
            jar_dir.mkdir(parents=True, exist_ok=True)
            
            # Download file
            url = f'https://api.papermc.io/v2/projects/paper/versions/{jar.version}/builds/{jar.approved_build}/downloads/{jar.approved_file}'
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        async with aiofiles.open(jar_dir / 'server.jar', 'wb') as f:
                            await f.write(await response.read())
                        
                        jar.downloaded = jar.approved_build
                        session_db.commit()
                        bot.log.success(f'Downloaded Paper {jar.version} build {jar.approved_build}')
                    else:
                        bot.log.error(f'Failed to download Paper {jar.version}: HTTP {response.status}')
    
    finally:
        session_db.close()
