"""
Slack Integration for XENO
Supports: Send messages, create channels, manage users, file uploads
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp

from . import IntegrationBase, IntegrationCredentials


class SlackIntegration(IntegrationBase):
    """Slack workspace integration"""

    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.api_token = credentials.credentials.get("api_token") if credentials else None
        self.base_url = "https://slack.com/api"

    @property
    def service_name(self) -> str:
        return "slack"

    @property
    def supported_triggers(self) -> List[str]:
        return ["new_message", "new_channel", "mention", "reaction_added"]

    @property
    def supported_actions(self) -> List[str]:
        return [
            "send_message",
            "send_dm",
            "create_channel",
            "upload_file",
            "set_status",
            "add_reaction",
            "pin_message",
            "archive_channel",
        ]

    async def authenticate(self) -> bool:
        """Authenticate with Slack API"""
        if not self.api_token:
            return False

        try:
            result = await self._api_call("auth.test")
            self.connected = result.get("ok", False)
            return self.connected
        except Exception as e:
            print(f"Slack authentication failed: {e}")
            return False

    async def test_connection(self) -> bool:
        """Test Slack connection"""
        return await self.authenticate()

    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Slack action"""
        action_map = {
            "send_message": self.send_message,
            "send_dm": self.send_dm,
            "create_channel": self.create_channel,
            "upload_file": self.upload_file,
            "set_status": self.set_status,
            "add_reaction": self.add_reaction,
            "pin_message": self.pin_message,
            "archive_channel": self.archive_channel,
        }

        handler = action_map.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")

        return await handler(**parameters)

    async def send_message(
        self,
        channel: str,
        text: str,
        blocks: Optional[List[Dict]] = None,
        thread_ts: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send message to channel"""
        payload = {"channel": channel, "text": text}

        if blocks:
            payload["blocks"] = blocks
        if thread_ts:
            payload["thread_ts"] = thread_ts

        return await self._api_call("chat.postMessage", payload)

    async def send_dm(self, user: str, text: str) -> Dict[str, Any]:
        """Send direct message to user"""
        # First, open DM channel
        dm_channel = await self._api_call("conversations.open", {"users": user})
        channel_id = dm_channel.get("channel", {}).get("id")

        if not channel_id:
            raise ValueError("Failed to open DM channel")

        return await self.send_message(channel_id, text)

    async def create_channel(self, name: str, is_private: bool = False) -> Dict[str, Any]:
        """Create a new channel"""
        method = "conversations.create"
        payload = {"name": name, "is_private": is_private}

        return await self._api_call(method, payload)

    async def upload_file(
        self,
        channels: str,
        file_path: str,
        title: Optional[str] = None,
        initial_comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload file to channel"""
        payload = {"channels": channels, "file": file_path}

        if title:
            payload["title"] = title
        if initial_comment:
            payload["initial_comment"] = initial_comment

        return await self._api_call("files.upload", payload)

    async def set_status(
        self,
        status_text: str,
        status_emoji: str = ":speech_balloon:",
        expiration: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Set user status"""
        profile = {"status_text": status_text, "status_emoji": status_emoji}

        if expiration:
            profile["status_expiration"] = expiration

        return await self._api_call("users.profile.set", {"profile": profile})

    async def add_reaction(self, channel: str, timestamp: str, emoji: str) -> Dict[str, Any]:
        """Add reaction to message"""
        payload = {"channel": channel, "timestamp": timestamp, "name": emoji}

        return await self._api_call("reactions.add", payload)

    async def pin_message(self, channel: str, timestamp: str) -> Dict[str, Any]:
        """Pin message in channel"""
        payload = {"channel": channel, "timestamp": timestamp}

        return await self._api_call("pins.add", payload)

    async def archive_channel(self, channel: str) -> Dict[str, Any]:
        """Archive a channel"""
        return await self._api_call("conversations.archive", {"channel": channel})

    async def get_channels(
        self, types: str = "public_channel,private_channel"
    ) -> List[Dict[str, Any]]:
        """Get list of channels"""
        result = await self._api_call("conversations.list", {"types": types})
        return result.get("channels", [])

    async def get_users(self) -> List[Dict[str, Any]]:
        """Get list of workspace users"""
        result = await self._api_call("users.list")
        return result.get("members", [])

    async def _api_call(self, method: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make API call to Slack"""
        url = f"{self.base_url}/{method}"
        headers = {"Authorization": f"Bearer {self.api_token}", "Content-Type": "application/json"}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data or {}, headers=headers) as response:
                result = await response.json()

                if not result.get("ok"):
                    raise Exception(f"Slack API error: {result.get('error')}")

                return result

    def get_available_actions(self) -> List[Dict[str, Any]]:
        """Get available actions with metadata"""
        return [
            {
                "action": "send_message",
                "name": "Send Message",
                "description": "Send a message to a channel",
                "parameters": [
                    {"name": "channel", "type": "string", "required": True},
                    {"name": "text", "type": "string", "required": True},
                    {"name": "blocks", "type": "array", "required": False},
                    {"name": "thread_ts", "type": "string", "required": False},
                ],
            },
            {
                "action": "send_dm",
                "name": "Send Direct Message",
                "description": "Send a DM to a user",
                "parameters": [
                    {"name": "user", "type": "string", "required": True},
                    {"name": "text", "type": "string", "required": True},
                ],
            },
            {
                "action": "create_channel",
                "name": "Create Channel",
                "description": "Create a new Slack channel",
                "parameters": [
                    {"name": "name", "type": "string", "required": True},
                    {"name": "is_private", "type": "boolean", "required": False},
                ],
            },
            {
                "action": "upload_file",
                "name": "Upload File",
                "description": "Upload a file to a channel",
                "parameters": [
                    {"name": "channels", "type": "string", "required": True},
                    {"name": "file_path", "type": "string", "required": True},
                    {"name": "title", "type": "string", "required": False},
                    {"name": "initial_comment", "type": "string", "required": False},
                ],
            },
            {
                "action": "set_status",
                "name": "Set Status",
                "description": "Update your Slack status",
                "parameters": [
                    {"name": "status_text", "type": "string", "required": True},
                    {"name": "status_emoji", "type": "string", "required": False},
                    {"name": "expiration", "type": "integer", "required": False},
                ],
            },
        ]
