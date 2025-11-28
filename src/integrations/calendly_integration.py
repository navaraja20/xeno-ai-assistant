"""
Calendly Integration
Meeting scheduling automation
"""

import os
from typing import Any, Dict, List, Optional

import aiohttp

from src.integrations import IntegrationBase, IntegrationCredentials
from src.core.logger import setup_logger


class CalendlyIntegration(IntegrationBase):
    """Calendly scheduling integration"""
    
    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.logger = setup_logger("integrations.calendly")
        self.access_token = credentials.api_key if credentials else os.getenv("CALENDLY_ACCESS_TOKEN")
        self.base_url = "https://api.calendly.com"
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
    
    @property
    def service_name(self) -> str:
        return "calendly"
    
    @property
    def supported_triggers(self) -> List[str]:
        return ["invitee_created", "invitee_canceled"]
    
    @property
    def supported_actions(self) -> List[str]:
        return [
            "get_user",
            "list_event_types",
            "list_scheduled_events",
            "cancel_event",
            "get_invitee",
        ]
    
    async def authenticate(self) -> bool:
        """Test Calendly authentication"""
        return await self.test_connection()
    
    async def test_connection(self) -> bool:
        """Test Calendly API connection"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/users/me",
                    headers=self.headers
                ) as response:
                    self.connected = response.status == 200
                    return self.connected
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Calendly action"""
        action_map = {
            "get_user": self.get_user,
            "list_event_types": self.list_event_types,
            "list_scheduled_events": self.list_scheduled_events,
            "cancel_event": self.cancel_event,
            "get_invitee": self.get_invitee,
        }
        
        handler = action_map.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")
        
        return await handler(**parameters)
    
    async def _api_call(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make Calendly API call"""
        url = f"{self.base_url}/{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, headers=self.headers, params=params
            ) as response:
                if response.status >= 400:
                    error = await response.text()
                    raise Exception(f"API error: {error}")
                return await response.json()
    
    async def get_user(self) -> Dict[str, Any]:
        """Get current user"""
        result = await self._api_call("GET", "users/me")
        return result.get("resource", {})
    
    async def list_event_types(self, user_uri: str) -> List[Dict[str, Any]]:
        """List user's event types"""
        params = {"user": user_uri}
        result = await self._api_call("GET", "event_types", params=params)
        return result.get("collection", [])
    
    async def list_scheduled_events(
        self,
        user_uri: str,
        status: str = "active",
    ) -> List[Dict[str, Any]]:
        """List scheduled events"""
        params = {"user": user_uri, "status": status}
        result = await self._api_call("GET", "scheduled_events", params=params)
        return result.get("collection", [])
    
    async def cancel_event(self, event_uuid: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """Cancel a scheduled event"""
        # Note: Cancellation requires a separate API call
        return {"message": "Cancellation not implemented in API v2"}
    
    async def get_invitee(self, invitee_uuid: str) -> Dict[str, Any]:
        """Get invitee details"""
        result = await self._api_call("GET", f"scheduled_events/{invitee_uuid}/invitees")
        return result.get("resource", {})
