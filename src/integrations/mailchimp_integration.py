"""
Mailchimp Integration
Email marketing and campaign management
"""

import os
from typing import Any, Dict, List, Optional

import aiohttp

from src.core.logger import setup_logger
from src.integrations import IntegrationBase, IntegrationCredentials


class MailchimpIntegration(IntegrationBase):
    """Mailchimp email marketing integration"""

    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.logger = setup_logger("integrations.mailchimp")
        self.api_key = credentials.api_key if credentials else os.getenv("MAILCHIMP_API_KEY")

        # Extract datacenter from API key (e.g., us1, us2)
        self.datacenter = self.api_key.split("-")[-1] if self.api_key else "us1"
        self.base_url = f"https://{self.datacenter}.api.mailchimp.com/3.0"
        self.auth = aiohttp.BasicAuth("anystring", self.api_key)

    @property
    def service_name(self) -> str:
        return "mailchimp"

    @property
    def supported_triggers(self) -> List[str]:
        return ["subscriber_added", "campaign_sent"]

    @property
    def supported_actions(self) -> List[str]:
        return [
            "add_subscriber",
            "update_subscriber",
            "create_campaign",
            "send_campaign",
            "list_campaigns",
            "get_lists",
        ]

    async def authenticate(self) -> bool:
        """Test Mailchimp authentication"""
        return await self.test_connection()

    async def test_connection(self) -> bool:
        """Test Mailchimp API connection"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/ping", auth=self.auth) as response:
                    self.connected = response.status == 200
                    return self.connected
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Mailchimp action"""
        action_map = {
            "add_subscriber": self.add_subscriber,
            "update_subscriber": self.update_subscriber,
            "create_campaign": self.create_campaign,
            "send_campaign": self.send_campaign,
            "list_campaigns": self.list_campaigns,
            "get_lists": self.get_lists,
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
        """Make Mailchimp API call"""
        url = f"{self.base_url}/{endpoint}"

        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, auth=self.auth, json=data) as response:
                if response.status >= 400:
                    error = await response.text()
                    raise Exception(f"API error: {error}")
                return await response.json()

    async def add_subscriber(
        self,
        list_id: str,
        email: str,
        status: str = "subscribed",
        merge_fields: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Add subscriber to list"""
        data = {
            "email_address": email,
            "status": status,
        }

        if merge_fields:
            data["merge_fields"] = merge_fields

        return await self._api_call("POST", f"lists/{list_id}/members", data=data)

    async def update_subscriber(
        self,
        list_id: str,
        subscriber_hash: str,
        email: Optional[str] = None,
        merge_fields: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Update subscriber"""
        data = {}

        if email:
            data["email_address"] = email
        if merge_fields:
            data["merge_fields"] = merge_fields

        return await self._api_call(
            "PATCH", f"lists/{list_id}/members/{subscriber_hash}", data=data
        )

    async def create_campaign(
        self,
        list_id: str,
        subject: str,
        from_name: str,
        reply_to: str,
    ) -> Dict[str, Any]:
        """Create email campaign"""
        data = {
            "type": "regular",
            "recipients": {"list_id": list_id},
            "settings": {
                "subject_line": subject,
                "from_name": from_name,
                "reply_to": reply_to,
            },
        }

        return await self._api_call("POST", "campaigns", data=data)

    async def send_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Send campaign"""
        return await self._api_call("POST", f"campaigns/{campaign_id}/actions/send")

    async def list_campaigns(self, count: int = 10) -> List[Dict[str, Any]]:
        """List campaigns"""
        result = await self._api_call("GET", f"campaigns?count={count}")
        return result.get("campaigns", [])

    async def get_lists(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get mailing lists"""
        result = await self._api_call("GET", f"lists?count={count}")
        return result.get("lists", [])
