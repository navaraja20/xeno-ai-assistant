"""
Discord Integration for XENO
Supports: Send messages, create channels, manage roles, webhooks
"""

import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from . import IntegrationBase, IntegrationCredentials


class DiscordIntegration(IntegrationBase):
    """Discord server integration"""
    
    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.bot_token = credentials.credentials.get('bot_token') if credentials else None
        self.webhook_url = credentials.credentials.get('webhook_url') if credentials else None
        self.base_url = 'https://discord.com/api/v10'
    
    @property
    def service_name(self) -> str:
        return 'discord'
    
    @property
    def supported_triggers(self) -> List[str]:
        return ['message_received', 'member_joined', 'reaction_added', 'role_assigned']
    
    @property
    def supported_actions(self) -> List[str]:
        return [
            'send_message',
            'send_webhook',
            'create_channel',
            'send_dm',
            'add_role',
            'create_embed',
            'pin_message',
            'create_thread'
        ]
    
    async def authenticate(self) -> bool:
        """Authenticate with Discord API"""
        if not self.bot_token:
            return False
        
        try:
            await self._api_call('GET', '/users/@me')
            self.connected = True
            return True
        except Exception as e:
            print(f"Discord authentication failed: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test Discord connection"""
        return await self.authenticate()
    
    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Discord action"""
        action_map = {
            'send_message': self.send_message,
            'send_webhook': self.send_webhook,
            'create_channel': self.create_channel,
            'send_dm': self.send_dm,
            'add_role': self.add_role,
            'create_embed': self.create_embed,
            'pin_message': self.pin_message,
            'create_thread': self.create_thread
        }
        
        handler = action_map.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")
        
        return await handler(**parameters)
    
    async def send_message(self, channel_id: str, content: str, embed: Optional[Dict] = None,
                          tts: bool = False) -> Dict[str, Any]:
        """Send message to channel"""
        payload = {'content': content, 'tts': tts}
        
        if embed:
            payload['embeds'] = [embed]
        
        return await self._api_call('POST', f'/channels/{channel_id}/messages', payload)
    
    async def send_webhook(self, content: str, username: Optional[str] = None,
                          avatar_url: Optional[str] = None, embeds: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Send message via webhook"""
        if not self.webhook_url:
            raise ValueError("Webhook URL not configured")
        
        payload = {'content': content}
        
        if username:
            payload['username'] = username
        if avatar_url:
            payload['avatar_url'] = avatar_url
        if embeds:
            payload['embeds'] = embeds
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.webhook_url, json=payload) as response:
                if response.status == 204:
                    return {'success': True}
                return await response.json()
    
    async def create_channel(self, guild_id: str, name: str, channel_type: int = 0,
                            topic: Optional[str] = None, parent_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new channel"""
        payload = {
            'name': name,
            'type': channel_type  # 0=text, 2=voice, 4=category
        }
        
        if topic:
            payload['topic'] = topic
        if parent_id:
            payload['parent_id'] = parent_id
        
        return await self._api_call('POST', f'/guilds/{guild_id}/channels', payload)
    
    async def send_dm(self, user_id: str, content: str, embed: Optional[Dict] = None) -> Dict[str, Any]:
        """Send DM to user"""
        # Create DM channel
        dm_channel = await self._api_call('POST', '/users/@me/channels', {'recipient_id': user_id})
        channel_id = dm_channel['id']
        
        # Send message
        return await self.send_message(channel_id, content, embed)
    
    async def add_role(self, guild_id: str, user_id: str, role_id: str) -> Dict[str, Any]:
        """Add role to user"""
        await self._api_call('PUT', f'/guilds/{guild_id}/members/{user_id}/roles/{role_id}')
        return {'success': True}
    
    def create_embed(self, title: str, description: str, color: int = 0x5865F2,
                    fields: Optional[List[Dict]] = None, footer: Optional[str] = None,
                    thumbnail: Optional[str] = None, image: Optional[str] = None) -> Dict[str, Any]:
        """Create Discord embed"""
        embed = {
            'title': title,
            'description': description,
            'color': color
        }
        
        if fields:
            embed['fields'] = fields
        if footer:
            embed['footer'] = {'text': footer}
        if thumbnail:
            embed['thumbnail'] = {'url': thumbnail}
        if image:
            embed['image'] = {'url': image}
        
        return embed
    
    async def pin_message(self, channel_id: str, message_id: str) -> Dict[str, Any]:
        """Pin message in channel"""
        await self._api_call('PUT', f'/channels/{channel_id}/pins/{message_id}')
        return {'success': True}
    
    async def create_thread(self, channel_id: str, message_id: str, name: str,
                           auto_archive_duration: int = 1440) -> Dict[str, Any]:
        """Create thread from message"""
        payload = {
            'name': name,
            'auto_archive_duration': auto_archive_duration
        }
        
        return await self._api_call('POST', f'/channels/{channel_id}/messages/{message_id}/threads', payload)
    
    async def _api_call(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """Make API call to Discord"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Bot {self.bot_token}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, json=data, headers=headers) as response:
                if response.status >= 400:
                    error_data = await response.text()
                    raise Exception(f"Discord API error: {error_data}")
                
                if response.status == 204:
                    return {}
                
                return await response.json()
    
    def get_available_actions(self) -> List[Dict[str, Any]]:
        """Get available actions with metadata"""
        return [
            {
                'action': 'send_message',
                'name': 'Send Message',
                'description': 'Send a message to a Discord channel',
                'parameters': [
                    {'name': 'channel_id', 'type': 'string', 'required': True},
                    {'name': 'content', 'type': 'string', 'required': True},
                    {'name': 'embed', 'type': 'object', 'required': False},
                    {'name': 'tts', 'type': 'boolean', 'required': False}
                ]
            },
            {
                'action': 'send_webhook',
                'name': 'Send Webhook Message',
                'description': 'Send message via Discord webhook',
                'parameters': [
                    {'name': 'content', 'type': 'string', 'required': True},
                    {'name': 'username', 'type': 'string', 'required': False},
                    {'name': 'avatar_url', 'type': 'string', 'required': False},
                    {'name': 'embeds', 'type': 'array', 'required': False}
                ]
            },
            {
                'action': 'create_channel',
                'name': 'Create Channel',
                'description': 'Create a new Discord channel',
                'parameters': [
                    {'name': 'guild_id', 'type': 'string', 'required': True},
                    {'name': 'name', 'type': 'string', 'required': True},
                    {'name': 'channel_type', 'type': 'integer', 'required': False},
                    {'name': 'topic', 'type': 'string', 'required': False}
                ]
            },
            {
                'action': 'send_dm',
                'name': 'Send DM',
                'description': 'Send direct message to a user',
                'parameters': [
                    {'name': 'user_id', 'type': 'string', 'required': True},
                    {'name': 'content', 'type': 'string', 'required': True},
                    {'name': 'embed', 'type': 'object', 'required': False}
                ]
            }
        ]
