"""
Updater orchestration class
"""
from .check_for_updates import check_for_updates
from .download_servers import download_servers
from .download_plugins import download_plugins
from .upload_files import upload_files

class Updater:
    """Main updater class that coordinates all update operations"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def check(self):
        """Run daily update check task"""
        message = 'Running daily update check task'
        self.bot.log.info(message)
        await check_for_updates(self.bot)
    
    async def download(self):
        """Run hourly download task"""
        message = 'Running hourly download task'
        self.bot.log.info(message)
        await download_servers(self.bot)
        await download_plugins(self.bot)
    
    async def run(self):
        """Run bi-daily upload task"""
        message = 'Running bi-daily upload task'
        self.bot.log.info(message)
        await upload_files(self.bot)
