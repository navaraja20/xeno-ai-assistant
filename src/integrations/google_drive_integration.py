"""
Google Drive Integration for XENO
Support for file management, folder operations, sharing
"""

import aiohttp
from typing import Dict, Any, List, Optional
from . import IntegrationBase


class GoogleDriveIntegration(IntegrationBase):
    """Google Drive API integration"""
    
    def __init__(self, credentials: Dict[str, Any]):
        super().__init__(credentials)
        self.access_token = credentials.get('access_token')
        self.base_url = 'https://www.googleapis.com/drive/v3'
        self.upload_url = 'https://www.googleapis.com/upload/drive/v3'
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    @property
    def service_name(self) -> str:
        return 'google_drive'
    
    @property
    def supported_triggers(self) -> List[str]:
        return ['file_created', 'file_modified', 'file_shared']
    
    @property
    def supported_actions(self) -> List[str]:
        return [
            'upload_file',
            'create_folder',
            'move_file',
            'copy_file',
            'share_file',
            'delete_file',
            'download_file',
            'search_files'
        ]
    
    async def authenticate(self) -> bool:
        """Test Google Drive authentication"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f'{self.base_url}/about?fields=user',
                    headers=self.headers
                ) as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def test_connection(self) -> bool:
        """Test Google Drive API connection"""
        return await self.authenticate()
    
    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Google Drive action"""
        actions = {
            'upload_file': self.upload_file,
            'create_folder': self.create_folder,
            'move_file': self.move_file,
            'copy_file': self.copy_file,
            'share_file': self.share_file,
            'delete_file': self.delete_file,
            'download_file': self.download_file,
            'search_files': self.search_files
        }
        
        if action not in actions:
            raise ValueError(f"Unknown action: {action}")
        
        return await actions[action](**parameters)
    
    async def upload_file(
        self,
        file_path: str,
        name: Optional[str] = None,
        parent_folder_id: Optional[str] = None,
        mime_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload a file to Google Drive"""
        import os
        import mimetypes
        
        # Determine file name and MIME type
        file_name = name or os.path.basename(file_path)
        if not mime_type:
            mime_type, _ = mimetypes.guess_type(file_path)
            mime_type = mime_type or 'application/octet-stream'
        
        # Create file metadata
        metadata = {'name': file_name}
        if parent_folder_id:
            metadata['parents'] = [parent_folder_id]
        
        # Read file content
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Upload file
        async with aiohttp.ClientSession() as session:
            # Create multipart upload
            boundary = '-------314159265358979323846'
            headers = self.headers.copy()
            headers['Content-Type'] = f'multipart/related; boundary={boundary}'
            
            body = (
                f'--{boundary}\r\n'
                f'Content-Type: application/json; charset=UTF-8\r\n\r\n'
                f'{{"name": "{file_name}", "parents": {metadata.get("parents", [])}}}\r\n'
                f'--{boundary}\r\n'
                f'Content-Type: {mime_type}\r\n\r\n'
            ).encode()
            
            body += file_content
            body += f'\r\n--{boundary}--'.encode()
            
            async with session.post(
                f'{self.upload_url}/files?uploadType=multipart',
                headers=headers,
                data=body
            ) as response:
                result = await response.json()
                return {
                    'success': response.status == 200,
                    'file_id': result.get('id'),
                    'name': result.get('name'),
                    'web_view_link': result.get('webViewLink')
                }
    
    async def create_folder(
        self,
        name: str,
        parent_folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new folder"""
        metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_folder_id:
            metadata['parents'] = [parent_folder_id]
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{self.base_url}/files',
                headers=self.headers,
                json=metadata
            ) as response:
                result = await response.json()
                return {
                    'success': response.status == 200,
                    'folder_id': result.get('id'),
                    'name': result.get('name')
                }
    
    async def move_file(
        self,
        file_id: str,
        new_parent_id: str,
        current_parent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Move a file to a different folder"""
        params = {'addParents': new_parent_id}
        if current_parent_id:
            params['removeParents'] = current_parent_id
        
        async with aiohttp.ClientSession() as session:
            async with session.patch(
                f'{self.base_url}/files/{file_id}',
                headers=self.headers,
                params=params
            ) as response:
                return {
                    'success': response.status == 200
                }
    
    async def copy_file(
        self,
        file_id: str,
        new_name: Optional[str] = None,
        parent_folder_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Copy a file"""
        metadata = {}
        if new_name:
            metadata['name'] = new_name
        if parent_folder_id:
            metadata['parents'] = [parent_folder_id]
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{self.base_url}/files/{file_id}/copy',
                headers=self.headers,
                json=metadata
            ) as response:
                result = await response.json()
                return {
                    'success': response.status == 200,
                    'file_id': result.get('id'),
                    'name': result.get('name')
                }
    
    async def share_file(
        self,
        file_id: str,
        email: str,
        role: str = 'reader',
        notify: bool = True
    ) -> Dict[str, Any]:
        """Share a file with someone"""
        permission = {
            'type': 'user',
            'role': role,
            'emailAddress': email
        }
        
        params = {'sendNotificationEmail': str(notify).lower()}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{self.base_url}/files/{file_id}/permissions',
                headers=self.headers,
                json=permission,
                params=params
            ) as response:
                result = await response.json()
                return {
                    'success': response.status == 200,
                    'permission_id': result.get('id')
                }
    
    async def delete_file(self, file_id: str) -> Dict[str, Any]:
        """Delete a file"""
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f'{self.base_url}/files/{file_id}',
                headers=self.headers
            ) as response:
                return {
                    'success': response.status == 204
                }
    
    async def download_file(
        self,
        file_id: str,
        destination_path: str
    ) -> Dict[str, Any]:
        """Download a file"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'{self.base_url}/files/{file_id}?alt=media',
                headers=self.headers
            ) as response:
                if response.status == 200:
                    with open(destination_path, 'wb') as f:
                        f.write(await response.read())
                    return {
                        'success': True,
                        'path': destination_path
                    }
                return {'success': False}
    
    async def search_files(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for files"""
        params = {
            'q': query,
            'pageSize': max_results,
            'fields': 'files(id, name, mimeType, createdTime, modifiedTime, webViewLink)'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f'{self.base_url}/files',
                headers=self.headers,
                params=params
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('files', [])
                return []
    
    async def list_files(
        self,
        folder_id: Optional[str] = None,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """List files in a folder or root"""
        query = f"'{folder_id}' in parents" if folder_id else "trashed = false"
        return await self.search_files(query, max_results)
    
    def get_available_actions(self) -> List[Dict[str, Any]]:
        """Get list of available actions with metadata"""
        return [
            {
                'name': 'upload_file',
                'description': 'Upload a file to Google Drive',
                'parameters': ['file_path', 'name', 'parent_folder_id']
            },
            {
                'name': 'create_folder',
                'description': 'Create a new folder',
                'parameters': ['name', 'parent_folder_id']
            },
            {
                'name': 'share_file',
                'description': 'Share a file with someone',
                'parameters': ['file_id', 'email', 'role', 'notify']
            },
            {
                'name': 'search_files',
                'description': 'Search for files',
                'parameters': ['query', 'max_results']
            }
        ]
