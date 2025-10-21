"""
Pterodactyl API client
"""
from typing import List
from urllib.parse import urlparse, parse_qs, urlencode
from .http import PterodactylHTTP

class Pterodactyl:
    """Pterodactyl API class"""
    
    def __init__(self, host: str, key: str):
        if not host.endswith('/'):
            host += '/'
        self.host = host
        self.key = key
        self.client = self.host + 'api/client'
        self.http = PterodactylHTTP(self.key)
    
    async def get_power_state(self, server: str) -> str:
        """Get the power state of a server"""
        endpoint = f'{self.client}/servers/{server}/resources'
        response = await self.http.get_json(endpoint)
        return response['attributes']['current_state']
    
    async def change_power_state(self, server: str, state: str):
        """Change the power state of a server"""
        endpoint = f'{self.client}/servers/{server}/power'
        response = await self.http.post_json(endpoint, {'signal': state})
        return response
    
    async def kill(self, server: str):
        """Kill a server"""
        return await self.change_power_state(server, 'kill')
    
    async def stop(self, server: str):
        """Stop a server"""
        return await self.change_power_state(server, 'stop')
    
    async def start(self, server: str):
        """Start a server"""
        return await self.change_power_state(server, 'start')
    
    async def upload(self, server: str, path: str, files: List[str]):
        """Upload files to a server"""
        endpoint = f'{self.client}/servers/{server}/files/upload'
        response = await self.http.get_json(endpoint)
        
        url = response['attributes']['url']
        # Parse and update URL with directory parameter
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        params['directory'] = [path]
        new_query = urlencode(params, doseq=True)
        upload_url = f'{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}'
        
        return await self.http.upload_files(upload_url, files)
