"""
Download plugins
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from github.download import download as github_download
from jenkins.download import download as jenkins_download
from spigot.download import download as spigot_download
from bukkit.download import download as bukkit_download

async def download_plugins(bot):
    """Download approved plugin JARs"""
    await github_download(bot)
    await jenkins_download(bot)
    await spigot_download(bot)
    await bukkit_download(bot)
