"""
Todoist Integration for XENO
Supports: Create tasks, projects, manage labels, sync data
"""

import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
from . import IntegrationBase, IntegrationCredentials


class TodoistIntegration(IntegrationBase):
    """Todoist task management integration"""
    
    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.api_token = credentials.credentials.get('api_token') if credentials else None
        self.base_url = 'https://api.todoist.com/rest/v2'
    
    @property
    def service_name(self) -> str:
        return 'todoist'
    
    @property
    def supported_triggers(self) -> List[str]:
        return ['task_created', 'task_completed', 'task_due_today', 'project_created']
    
    @property
    def supported_actions(self) -> List[str]:
        return [
            'create_task',
            'update_task',
            'complete_task',
            'create_project',
            'add_comment',
            'add_label',
            'get_tasks',
            'get_projects'
        ]
    
    async def authenticate(self) -> bool:
        """Authenticate with Todoist API"""
        if not self.api_token:
            return False
        
        try:
            await self._api_call('GET', '/projects')
            self.connected = True
            return True
        except Exception as e:
            print(f"Todoist authentication failed: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test Todoist connection"""
        return await self.authenticate()
    
    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Todoist action"""
        action_map = {
            'create_task': self.create_task,
            'update_task': self.update_task,
            'complete_task': self.complete_task,
            'create_project': self.create_project,
            'add_comment': self.add_comment,
            'add_label': self.add_label,
            'get_tasks': self.get_tasks,
            'get_projects': self.get_projects
        }
        
        handler = action_map.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")
        
        return await handler(**parameters)
    
    async def create_task(self, content: str, description: Optional[str] = None,
                         project_id: Optional[str] = None, due_string: Optional[str] = None,
                         priority: int = 1, labels: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a new task"""
        payload = {
            'content': content,
            'priority': priority
        }
        
        if description:
            payload['description'] = description
        if project_id:
            payload['project_id'] = project_id
        if due_string:
            payload['due_string'] = due_string
        if labels:
            payload['labels'] = labels
        
        return await self._api_call('POST', '/tasks', payload)
    
    async def update_task(self, task_id: str, **updates) -> Dict[str, Any]:
        """Update task properties"""
        return await self._api_call('POST', f'/tasks/{task_id}', updates)
    
    async def complete_task(self, task_id: str) -> Dict[str, Any]:
        """Mark task as complete"""
        await self._api_call('POST', f'/tasks/{task_id}/close')
        return {'success': True}
    
    async def create_project(self, name: str, color: Optional[str] = None,
                            is_favorite: bool = False) -> Dict[str, Any]:
        """Create a new project"""
        payload = {
            'name': name,
            'is_favorite': is_favorite
        }
        
        if color:
            payload['color'] = color
        
        return await self._api_call('POST', '/projects', payload)
    
    async def add_comment(self, task_id: str, content: str) -> Dict[str, Any]:
        """Add comment to task"""
        payload = {
            'task_id': task_id,
            'content': content
        }
        
        return await self._api_call('POST', '/comments', payload)
    
    async def add_label(self, name: str, color: Optional[str] = None) -> Dict[str, Any]:
        """Create a new label"""
        payload = {'name': name}
        
        if color:
            payload['color'] = color
        
        return await self._api_call('POST', '/labels', payload)
    
    async def get_tasks(self, project_id: Optional[str] = None,
                       label: Optional[str] = None, filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get tasks"""
        params = {}
        
        if project_id:
            params['project_id'] = project_id
        if label:
            params['label'] = label
        if filter:
            params['filter'] = filter
        
        return await self._api_call('GET', '/tasks', params)
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects"""
        return await self._api_call('GET', '/projects')
    
    async def get_labels(self) -> List[Dict[str, Any]]:
        """Get all labels"""
        return await self._api_call('GET', '/labels')
    
    async def _api_call(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """Make API call to Todoist"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            if method == 'GET':
                async with session.get(url, params=data, headers=headers) as response:
                    if response.status >= 400:
                        error_data = await response.text()
                        raise Exception(f"Todoist API error: {error_data}")
                    return await response.json()
            else:
                async with session.request(method, url, json=data, headers=headers) as response:
                    if response.status >= 400:
                        error_data = await response.text()
                        raise Exception(f"Todoist API error: {error_data}")
                    
                    if response.status == 204:
                        return {}
                    
                    return await response.json()
    
    def get_available_actions(self) -> List[Dict[str, Any]]:
        """Get available actions with metadata"""
        return [
            {
                'action': 'create_task',
                'name': 'Create Task',
                'description': 'Create a new Todoist task',
                'parameters': [
                    {'name': 'content', 'type': 'string', 'required': True},
                    {'name': 'description', 'type': 'string', 'required': False},
                    {'name': 'project_id', 'type': 'string', 'required': False},
                    {'name': 'due_string', 'type': 'string', 'required': False},
                    {'name': 'priority', 'type': 'integer', 'required': False},
                    {'name': 'labels', 'type': 'array', 'required': False}
                ]
            },
            {
                'action': 'complete_task',
                'name': 'Complete Task',
                'description': 'Mark a task as complete',
                'parameters': [
                    {'name': 'task_id', 'type': 'string', 'required': True}
                ]
            },
            {
                'action': 'create_project',
                'name': 'Create Project',
                'description': 'Create a new Todoist project',
                'parameters': [
                    {'name': 'name', 'type': 'string', 'required': True},
                    {'name': 'color', 'type': 'string', 'required': False},
                    {'name': 'is_favorite', 'type': 'boolean', 'required': False}
                ]
            },
            {
                'action': 'add_comment',
                'name': 'Add Comment',
                'description': 'Add comment to a task',
                'parameters': [
                    {'name': 'task_id', 'type': 'string', 'required': True},
                    {'name': 'content', 'type': 'string', 'required': True}
                ]
            },
            {
                'action': 'get_tasks',
                'name': 'Get Tasks',
                'description': 'Get tasks with optional filters',
                'parameters': [
                    {'name': 'project_id', 'type': 'string', 'required': False},
                    {'name': 'label', 'type': 'string', 'required': False},
                    {'name': 'filter', 'type': 'string', 'required': False}
                ]
            }
        ]
