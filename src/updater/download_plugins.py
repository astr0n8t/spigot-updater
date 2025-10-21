"""
Download plugins
"""
from github import download as github_download
from jenkins import download as jenkins_download
from spigot import download as spigot_download
from bukkit import download as bukkit_download

async def download_plugins(bot):
    """Download approved plugin JARs"""
    await github_download.download(bot)
    await jenkins_download.download(bot)
    await spigot_download.download(bot)
    await bukkit_download.download(bot)
