"""
Dropbox Integration
File storage and sharing with Dropbox
"""

import os
from typing import Any, Dict, List, Optional

import aiohttp

from src.integrations import IntegrationBase, IntegrationCredentials
from src.core.logger import setup_logger


class DropboxIntegration(IntegrationBase):
    """Dropbox file storage integration"""
    
    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.logger = setup_logger("integrations.dropbox")
        self.access_token = credentials.api_key if credentials else os.getenv("DROPBOX_ACCESS_TOKEN")
        self.api_url = "https://api.dropboxapi.com/2"
        self.content_url = "https://content.dropboxapi.com/2"
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
    
    @property
    def service_name(self) -> str:
        return "dropbox"
    
    @property
    def supported_triggers(self) -> List[str]:
        return ["file_uploaded", "file_modified", "file_deleted"]
    
    @property
    def supported_actions(self) -> List[str]:
        return [
            "upload_file",
            "download_file",
            "create_folder",
            "delete_file",
            "share_file",
            "list_folder",
            "search_files",
        ]
    
    async def authenticate(self) -> bool:
        """Test Dropbox authentication"""
        return await self.test_connection()
    
    async def test_connection(self) -> bool:
        """Test Dropbox API connection"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/users/get_current_account",
                    headers=self.headers
                ) as response:
                    self.connected = response.status == 200
                    return self.connected
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Dropbox action"""
        action_map = {
            "upload_file": self.upload_file,
            "download_file": self.download_file,
            "create_folder": self.create_folder,
            "delete_file": self.delete_file,
            "share_file": self.share_file,
            "list_folder": self.list_folder,
            "search_files": self.search_files,
        }
        
        handler = action_map.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")
        
        return await handler(**parameters)
    
    async def upload_file(
        self,
        file_path: str,
        dropbox_path: str,
        mode: str = "add",
    ) -> Dict[str, Any]:
        """Upload file to Dropbox"""
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        headers = {
            **self.headers,
            "Dropbox-API-Arg": f'{{"path": "{dropbox_path}", "mode": "{mode}"}}',
            "Content-Type": "application/octet-stream",
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.content_url}/files/upload",
                headers=headers,
                data=file_data
            ) as response:
                return await response.json()
    
    async def download_file(self, dropbox_path: str, local_path: str) -> Dict[str, Any]:
        """Download file from Dropbox"""
        headers = {
            **self.headers,
            "Dropbox-API-Arg": f'{{"path": "{dropbox_path}"}}',
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.content_url}/files/download",
                headers=headers
            ) as response:
                if response.status == 200:
                    content = await response.read()
                    with open(local_path, 'wb') as f:
                        f.write(content)
                    return {"success": True, "path": local_path}
                return {"success": False}
    
    async def create_folder(self, path: str) -> Dict[str, Any]:
        """Create a folder"""
        data = {"path": path}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/files/create_folder_v2",
                headers={**self.headers, "Content-Type": "application/json"},
                json=data
            ) as response:
                return await response.json()
    
    async def delete_file(self, path: str) -> Dict[str, Any]:
        """Delete a file or folder"""
        data = {"path": path}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/files/delete_v2",
                headers={**self.headers, "Content-Type": "application/json"},
                json=data
            ) as response:
                return await response.json()
    
    async def share_file(
        self,
        path: str,
        access_level: str = "viewer",
    ) -> Dict[str, Any]:
        """Create a shared link for a file"""
        data = {
            "path": path,
            "settings": {"requested_visibility": "public", "access": access_level}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/sharing/create_shared_link_with_settings",
                headers={**self.headers, "Content-Type": "application/json"},
                json=data
            ) as response:
                return await response.json()
    
    async def list_folder(
        self,
        path: str = "",
        recursive: bool = False,
    ) -> List[Dict[str, Any]]:
        """List folder contents"""
        data = {"path": path, "recursive": recursive}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/files/list_folder",
                headers={**self.headers, "Content-Type": "application/json"},
                json=data
            ) as response:
                result = await response.json()
                return result.get("entries", [])
    
    async def search_files(
        self,
        query: str,
        max_results: int = 100,
    ) -> List[Dict[str, Any]]:
        """Search for files"""
        data = {
            "query": query,
            "options": {"max_results": max_results}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/files/search_v2",
                headers={**self.headers, "Content-Type": "application/json"},
                json=data
            ) as response:
                result = await response.json()
                return result.get("matches", [])
