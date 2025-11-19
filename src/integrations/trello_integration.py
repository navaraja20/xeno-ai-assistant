"""
Trello Integration for XENO
Supports: Create boards, lists, cards, manage members, attachments
"""

import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
from . import IntegrationBase, IntegrationCredentials


class TrelloIntegration(IntegrationBase):
    """Trello board integration"""
    
    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.api_key = credentials.credentials.get('api_key') if credentials else None
        self.api_token = credentials.credentials.get('api_token') if credentials else None
        self.base_url = 'https://api.trello.com/1'
    
    @property
    def service_name(self) -> str:
        return 'trello'
    
    @property
    def supported_triggers(self) -> List[str]:
        return ['card_created', 'card_moved', 'card_due_soon', 'member_added']
    
    @property
    def supported_actions(self) -> List[str]:
        return [
            'create_board',
            'create_list',
            'create_card',
            'update_card',
            'move_card',
            'add_comment',
            'add_attachment',
            'add_label',
            'add_member',
            'set_due_date'
        ]
    
    async def authenticate(self) -> bool:
        """Authenticate with Trello API"""
        if not self.api_key or not self.api_token:
            return False
        
        try:
            # Test by getting member info
            await self._api_call('GET', '/members/me')
            self.connected = True
            return True
        except Exception as e:
            print(f"Trello authentication failed: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test Trello connection"""
        return await self.authenticate()
    
    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Trello action"""
        action_map = {
            'create_board': self.create_board,
            'create_list': self.create_list,
            'create_card': self.create_card,
            'update_card': self.update_card,
            'move_card': self.move_card,
            'add_comment': self.add_comment,
            'add_attachment': self.add_attachment,
            'add_label': self.add_label,
            'add_member': self.add_member,
            'set_due_date': self.set_due_date
        }
        
        handler = action_map.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")
        
        return await handler(**parameters)
    
    async def create_board(self, name: str, desc: Optional[str] = None,
                          default_lists: bool = True) -> Dict[str, Any]:
        """Create a new board"""
        params = {
            'name': name,
            'defaultLists': default_lists
        }
        
        if desc:
            params['desc'] = desc
        
        return await self._api_call('POST', '/boards', params)
    
    async def create_list(self, board_id: str, name: str, pos: str = 'bottom') -> Dict[str, Any]:
        """Create a new list on a board"""
        params = {
            'name': name,
            'idBoard': board_id,
            'pos': pos
        }
        
        return await self._api_call('POST', '/lists', params)
    
    async def create_card(self, list_id: str, name: str, desc: Optional[str] = None,
                         due: Optional[str] = None, labels: Optional[List[str]] = None,
                         members: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a new card"""
        params = {
            'name': name,
            'idList': list_id
        }
        
        if desc:
            params['desc'] = desc
        if due:
            params['due'] = due
        if labels:
            params['idLabels'] = ','.join(labels)
        if members:
            params['idMembers'] = ','.join(members)
        
        return await self._api_call('POST', '/cards', params)
    
    async def update_card(self, card_id: str, **updates) -> Dict[str, Any]:
        """Update card properties"""
        return await self._api_call('PUT', f'/cards/{card_id}', updates)
    
    async def move_card(self, card_id: str, list_id: str, pos: str = 'bottom') -> Dict[str, Any]:
        """Move card to different list"""
        params = {
            'idList': list_id,
            'pos': pos
        }
        
        return await self._api_call('PUT', f'/cards/{card_id}', params)
    
    async def add_comment(self, card_id: str, text: str) -> Dict[str, Any]:
        """Add comment to card"""
        params = {'text': text}
        return await self._api_call('POST', f'/cards/{card_id}/actions/comments', params)
    
    async def add_attachment(self, card_id: str, url: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Add attachment to card"""
        params = {'url': url}
        if name:
            params['name'] = name
        
        return await self._api_call('POST', f'/cards/{card_id}/attachments', params)
    
    async def add_label(self, card_id: str, color: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Add label to card"""
        # First create label if name provided
        if name:
            board_id = (await self.get_card(card_id))['idBoard']
            label = await self._api_call('POST', '/labels', {
                'name': name,
                'color': color,
                'idBoard': board_id
            })
            label_id = label['id']
        else:
            # Use existing label by color
            board_id = (await self.get_card(card_id))['idBoard']
            labels = await self._api_call('GET', f'/boards/{board_id}/labels')
            label_id = next((l['id'] for l in labels if l['color'] == color), None)
        
        if label_id:
            return await self._api_call('POST', f'/cards/{card_id}/idLabels', {'value': label_id})
        
        raise ValueError(f"Label not found with color: {color}")
    
    async def add_member(self, card_id: str, member_id: str) -> Dict[str, Any]:
        """Add member to card"""
        return await self._api_call('POST', f'/cards/{card_id}/idMembers', {'value': member_id})
    
    async def set_due_date(self, card_id: str, due: str, due_complete: bool = False) -> Dict[str, Any]:
        """Set card due date"""
        params = {
            'due': due,
            'dueComplete': due_complete
        }
        
        return await self._api_call('PUT', f'/cards/{card_id}', params)
    
    async def get_card(self, card_id: str) -> Dict[str, Any]:
        """Get card details"""
        return await self._api_call('GET', f'/cards/{card_id}')
    
    async def get_board(self, board_id: str) -> Dict[str, Any]:
        """Get board details"""
        return await self._api_call('GET', f'/boards/{board_id}')
    
    async def get_lists(self, board_id: str) -> List[Dict[str, Any]]:
        """Get all lists on a board"""
        return await self._api_call('GET', f'/boards/{board_id}/lists')
    
    async def get_cards(self, list_id: str) -> List[Dict[str, Any]]:
        """Get all cards in a list"""
        return await self._api_call('GET', f'/lists/{list_id}/cards')
    
    async def _api_call(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make API call to Trello"""
        url = f"{self.base_url}{endpoint}"
        
        # Add auth params
        auth_params = {
            'key': self.api_key,
            'token': self.api_token
        }
        
        if params:
            auth_params.update(params)
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, params=auth_params) as response:
                if response.status >= 400:
                    error_data = await response.text()
                    raise Exception(f"Trello API error: {error_data}")
                
                return await response.json()
    
    def get_available_actions(self) -> List[Dict[str, Any]]:
        """Get available actions with metadata"""
        return [
            {
                'action': 'create_board',
                'name': 'Create Board',
                'description': 'Create a new Trello board',
                'parameters': [
                    {'name': 'name', 'type': 'string', 'required': True},
                    {'name': 'desc', 'type': 'string', 'required': False},
                    {'name': 'default_lists', 'type': 'boolean', 'required': False}
                ]
            },
            {
                'action': 'create_list',
                'name': 'Create List',
                'description': 'Create a new list on a board',
                'parameters': [
                    {'name': 'board_id', 'type': 'string', 'required': True},
                    {'name': 'name', 'type': 'string', 'required': True},
                    {'name': 'pos', 'type': 'string', 'required': False}
                ]
            },
            {
                'action': 'create_card',
                'name': 'Create Card',
                'description': 'Create a new card in a list',
                'parameters': [
                    {'name': 'list_id', 'type': 'string', 'required': True},
                    {'name': 'name', 'type': 'string', 'required': True},
                    {'name': 'desc', 'type': 'string', 'required': False},
                    {'name': 'due', 'type': 'string', 'required': False},
                    {'name': 'labels', 'type': 'array', 'required': False},
                    {'name': 'members', 'type': 'array', 'required': False}
                ]
            },
            {
                'action': 'move_card',
                'name': 'Move Card',
                'description': 'Move card to a different list',
                'parameters': [
                    {'name': 'card_id', 'type': 'string', 'required': True},
                    {'name': 'list_id', 'type': 'string', 'required': True},
                    {'name': 'pos', 'type': 'string', 'required': False}
                ]
            },
            {
                'action': 'add_comment',
                'name': 'Add Comment',
                'description': 'Add a comment to a card',
                'parameters': [
                    {'name': 'card_id', 'type': 'string', 'required': True},
                    {'name': 'text', 'type': 'string', 'required': True}
                ]
            }
        ]
