"""
Download servers
"""
from paper import download as paper_download
from serverjars import download as serverjars_download

async def download_servers(bot):
    """Download approved server JARs"""
    await paper_download.download(bot)
    await serverjars_download.download(bot)
