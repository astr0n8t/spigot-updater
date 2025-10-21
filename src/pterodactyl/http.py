"""
Pterodactyl API HTTP client
"""
import aiohttp
import aiofiles
from typing import List

class PterodactylHTTP:
    """HTTP client for Pterodactyl API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    
    async def get_json(self, url: str):
        """Make GET request"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                return await response.json()
    
    async def post_json(self, url: str, data: dict):
        """Make POST request"""
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=data) as response:
                return response
    
    async def upload_files(self, url: str, files: List[str]):
        """Upload files to Pterodactyl"""
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            
            for file_path in files:
                async with aiofiles.open(file_path, 'rb') as f:
                    content = await f.read()
                    filename = file_path.split('/')[-1]
                    data.add_field('files', content, filename=filename)
            
            async with session.post(url, data=data) as response:
                return response
