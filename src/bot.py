"""
Discord bot implementation
"""
import os
import asyncio
import discord
from discord.ext import tasks
from dotenv import load_dotenv
from pathlib import Path
import sys

# Add config to path
config_path = Path(__file__).parent.parent / 'config'
sys.path.insert(0, str(config_path))

from database import init_database
from updater import Updater
from utils.discord_utils import create_embed, capitalise

# Load environment variables
load_dotenv()

class SpigotUpdaterBot(discord.Client):
    """Main Discord bot class"""
    
    def __init__(self, log):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.message_content = True
        intents.guild_messages = True
        intents.reactions = True
        
        super().__init__(intents=intents)
        
        self.log = log
        self.messages = {}
        
        # Load config
        try:
            from config import config as main_config
            from servers import servers
            from plugins import plugins
            
            self.config = {
                **main_config,
                'servers': servers,
                'plugins': plugins
            }
        except ImportError as e:
            self.log.error(f'Failed to load config: {e}')
            self.log.error('Make sure config/config.py, config/servers.py, and config/plugins.py exist')
            raise
        
        # Initialize database
        self.db = init_database(log)
        
        # Channel will be set on ready
        self.channel = None
        
        # Updater
        self.updater = None
    
    async def setup_hook(self):
        """Setup tasks"""
        # Start background tasks
        self.check_task.start()
        self.download_task.start()
        self.upload_task.start()
    
    async def on_ready(self):
        """Called when bot is ready"""
        self.log.success(f'Authenticated as {self.user.name}#{self.user.discriminator}')
        self.log.success('Connected to Discord API')
        
        # Get channel
        channel_id = self.config.get('channel_id')
        if not channel_id:
            self.log.error('channel_id not configured')
            return
        
        self.channel = self.get_channel(int(channel_id))
        if not self.channel:
            self.log.warning(f'Could not get channel with ID {channel_id}')
            return
        
        await self.channel.send('❗ The bot will not respond to reactions on any messages before this.')
        
        # Create updater
        self.updater = Updater(self)
        
        # Run initial checks
        await self.updater.check()
        await self.updater.download()
        await self.updater.run()
    
    @tasks.loop(hours=24)
    async def check_task(self):
        """Daily update check"""
        if self.updater:
            await self.updater.check()
    
    @tasks.loop(hours=1)
    async def download_task(self):
        """Hourly download task"""
        if self.updater:
            await self.updater.download()
    
    @tasks.loop(hours=12)
    async def upload_task(self):
        """Bi-daily upload task"""
        if self.updater:
            await self.updater.run()
    
    @check_task.before_loop
    @download_task.before_loop
    @upload_task.before_loop
    async def before_tasks(self):
        """Wait until bot is ready"""
        await self.wait_until_ready()
    
    async def on_reaction_add(self, reaction, user):
        """Handle reaction additions"""
        if user == self.user:
            return
        
        message = reaction.message
        if reaction.emoji != '✅' or message.channel.id != int(self.config.get('channel_id', 0)):
            return
        
        data = self.messages.get(message.id)
        if not data:
            return
        
        session_db = self.db['Session']()
        try:
            if 'server_jar' in data:
                # Server jar approval
                jar_data = data['server_jar']
                jar = session_db.query(self.db['ServerJars']).filter_by(
                    type=jar_data['type'],
                    version=jar_data['version']
                ).first()
                
                if jar:
                    jar.approved_version = jar_data['actual_version']
                    jar.approved_build = jar_data['build']
                    jar.approved_file = jar_data['file']
                    jar.approved_checksum = jar_data['checksum']
                    session_db.commit()
                    
                    self.log.info(f"{user.name} approved an update for {capitalise(jar_data['type'])} {jar_data['version']}")
                    
                    embed = create_embed(
                        title=f"✅ Update approved for {capitalise(jar_data['type'])} {jar_data['version']}",
                        description=f'Approved by {user.mention}.\nThis will be updated during the next upload task.',
                        color=0x00FF00
                    )
                    await message.edit(embed=embed)
                    await message.clear_reactions()
            
            elif 'plugin' in data:
                # Plugin approval
                plugin_data = data['plugin']
                plugin = session_db.query(self.db['Plugins']).filter_by(
                    name=plugin_data['name']
                ).first()
                
                if plugin:
                    plugin.approved = plugin_data['version']
                    session_db.commit()
                    
                    self.log.info(f"{user.name} approved an update for {plugin_data['name']}")
                    
                    embed = create_embed(
                        title=f"✅ Update approved for {plugin_data['name']}",
                        description=f'Approved by {user.mention}.\nThis will be updated during the next upload task.',
                        color=0x00FF00
                    )
                    await message.edit(embed=embed)
                    await message.clear_reactions()
            
            # Remove from messages map
            del self.messages[message.id]
        
        finally:
            session_db.close()
    
    async def run(self):
        """Run the bot"""
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            self.log.error('DISCORD_TOKEN not set in environment')
            return
        
        self.log.info('Connecting to Discord API')
        await self.start(token)
