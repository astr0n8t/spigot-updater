"""
Main entry point for the Spigot Updater application.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from bot import SpigotUpdaterBot
from utils.logger import setup_logger
from utils.fs import ensure_directories

def main():
    """Main entry point"""
    # Setup logging
    log = setup_logger('Server updater')
    
    # Ensure required directories exist
    ensure_directories(log)
    
    # Create and run bot
    try:
        bot = SpigotUpdaterBot(log)
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        log.info('Shutting down...')
    except Exception as error:
        log.error(f'Fatal error: {error}')
        raise

if __name__ == '__main__':
    main()
