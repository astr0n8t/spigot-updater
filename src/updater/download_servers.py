"""
Download servers
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from paper.download import download as paper_download
from serverjars.download import download as serverjars_download

async def download_servers(bot):
    """Download approved server JARs"""
    await paper_download(bot)
    await serverjars_download(bot)
