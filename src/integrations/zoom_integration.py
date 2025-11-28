"""
Zoom Integration
Video conferencing and meeting management
"""

import os
from typing import Any, Dict, List, Optional

import aiohttp

from src.core.logger import setup_logger
from src.integrations import IntegrationBase, IntegrationCredentials


class ZoomIntegration(IntegrationBase):
    """Zoom video conferencing integration"""

    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.logger = setup_logger("integrations.zoom")
        self.access_token = credentials.api_key if credentials else os.getenv("ZOOM_ACCESS_TOKEN")
        self.base_url = "https://api.zoom.us/v2"
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    @property
    def service_name(self) -> str:
        return "zoom"

    @property
    def supported_triggers(self) -> List[str]:
        return ["meeting_started", "meeting_ended", "participant_joined"]

    @property
    def supported_actions(self) -> List[str]:
        return [
            "create_meeting",
            "update_meeting",
            "delete_meeting",
            "list_meetings",
            "get_meeting",
            "create_webinar",
        ]

    async def authenticate(self) -> bool:
        """Test Zoom authentication"""
        return await self.test_connection()

    async def test_connection(self) -> bool:
        """Test Zoom API connection"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/users/me", headers=self.headers
                ) as response:
                    self.connected = response.status == 200
                    return self.connected
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Zoom action"""
        action_map = {
            "create_meeting": self.create_meeting,
            "update_meeting": self.update_meeting,
            "delete_meeting": self.delete_meeting,
            "list_meetings": self.list_meetings,
            "get_meeting": self.get_meeting,
            "create_webinar": self.create_webinar,
        }

        handler = action_map.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")

        return await handler(**parameters)

    async def _api_call(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make Zoom API call"""
        url = f"{self.base_url}/{endpoint}"

        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=self.headers, json=data) as response:
                if response.status >= 400:
                    error = await response.text()
                    raise Exception(f"API error: {error}")

                if response.status == 204:
                    return {"success": True}

                return await response.json()

    async def create_meeting(
        self,
        user_id: str = "me",
        topic: str = "XENO Meeting",
        start_time: Optional[str] = None,
        duration: int = 30,
        password: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a Zoom meeting"""
        data = {
            "topic": topic,
            "type": 2,  # Scheduled meeting
            "duration": duration,
            "settings": {
                "host_video": True,
                "participant_video": True,
                "join_before_host": False,
                "mute_upon_entry": False,
            },
        }

        if start_time:
            data["start_time"] = start_time

        if password:
            data["password"] = password

        return await self._api_call("POST", f"users/{user_id}/meetings", data=data)

    async def update_meeting(
        self,
        meeting_id: str,
        topic: Optional[str] = None,
        start_time: Optional[str] = None,
        duration: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Update a meeting"""
        data = {}

        if topic:
            data["topic"] = topic
        if start_time:
            data["start_time"] = start_time
        if duration:
            data["duration"] = duration

        return await self._api_call("PATCH", f"meetings/{meeting_id}", data=data)

    async def delete_meeting(self, meeting_id: str) -> Dict[str, Any]:
        """Delete a meeting"""
        return await self._api_call("DELETE", f"meetings/{meeting_id}")

    async def list_meetings(
        self,
        user_id: str = "me",
        type_: str = "scheduled",
    ) -> List[Dict[str, Any]]:
        """List user's meetings"""
        result = await self._api_call("GET", f"users/{user_id}/meetings?type={type_}")
        return result.get("meetings", [])

    async def get_meeting(self, meeting_id: str) -> Dict[str, Any]:
        """Get meeting details"""
        return await self._api_call("GET", f"meetings/{meeting_id}")

    async def create_webinar(
        self,
        user_id: str = "me",
        topic: str = "XENO Webinar",
        start_time: Optional[str] = None,
        duration: int = 60,
    ) -> Dict[str, Any]:
        """Create a webinar"""
        data = {
            "topic": topic,
            "type": 5,  # Webinar
            "duration": duration,
        }

        if start_time:
            data["start_time"] = start_time

        return await self._api_call("POST", f"users/{user_id}/webinars", data=data)
