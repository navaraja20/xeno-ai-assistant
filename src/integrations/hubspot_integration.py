"""
HubSpot Integration
CRM and marketing automation
"""

import os
from typing import Any, Dict, List, Optional

import aiohttp

from src.integrations import IntegrationBase, IntegrationCredentials
from src.core.logger import setup_logger


class HubSpotIntegration(IntegrationBase):
    """HubSpot CRM integration"""
    
    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.logger = setup_logger("integrations.hubspot")
        self.access_token = credentials.api_key if credentials else os.getenv("HUBSPOT_ACCESS_TOKEN")
        self.base_url = "https://api.hubapi.com"
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
    
    @property
    def service_name(self) -> str:
        return "hubspot"
    
    @property
    def supported_triggers(self) -> List[str]:
        return ["contact_created", "deal_updated", "ticket_created"]
    
    @property
    def supported_actions(self) -> List[str]:
        return [
            "create_contact",
            "update_contact",
            "create_deal",
            "create_ticket",
            "search_contacts",
            "list_companies",
        ]
    
    async def authenticate(self) -> bool:
        """Test HubSpot authentication"""
        return await self.test_connection()
    
    async def test_connection(self) -> bool:
        """Test HubSpot API connection"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/crm/v3/objects/contacts?limit=1",
                    headers=self.headers
                ) as response:
                    self.connected = response.status == 200
                    return self.connected
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute HubSpot action"""
        action_map = {
            "create_contact": self.create_contact,
            "update_contact": self.update_contact,
            "create_deal": self.create_deal,
            "create_ticket": self.create_ticket,
            "search_contacts": self.search_contacts,
            "list_companies": self.list_companies,
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
        """Make HubSpot API call"""
        url = f"{self.base_url}/{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, headers=self.headers, json=data
            ) as response:
                if response.status >= 400:
                    error = await response.text()
                    raise Exception(f"API error: {error}")
                return await response.json()
    
    async def create_contact(
        self,
        email: str,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        properties: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Create a contact"""
        props = {"email": email}
        
        if firstname:
            props["firstname"] = firstname
        if lastname:
            props["lastname"] = lastname
        if properties:
            props.update(properties)
        
        data = {"properties": props}
        return await self._api_call("POST", "crm/v3/objects/contacts", data=data)
    
    async def update_contact(
        self,
        contact_id: str,
        properties: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a contact"""
        data = {"properties": properties}
        return await self._api_call("PATCH", f"crm/v3/objects/contacts/{contact_id}", data=data)
    
    async def create_deal(
        self,
        dealname: str,
        amount: Optional[float] = None,
        properties: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Create a deal"""
        props = {"dealname": dealname}
        
        if amount:
            props["amount"] = str(amount)
        if properties:
            props.update(properties)
        
        data = {"properties": props}
        return await self._api_call("POST", "crm/v3/objects/deals", data=data)
    
    async def create_ticket(
        self,
        subject: str,
        content: str,
        properties: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Create a ticket"""
        props = {
            "subject": subject,
            "content": content,
        }
        
        if properties:
            props.update(properties)
        
        data = {"properties": props}
        return await self._api_call("POST", "crm/v3/objects/tickets", data=data)
    
    async def search_contacts(
        self,
        query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search contacts"""
        data = {
            "query": query,
            "limit": limit,
        }
        
        result = await self._api_call("POST", "crm/v3/objects/contacts/search", data=data)
        return result.get("results", [])
    
    async def list_companies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List companies"""
        result = await self._api_call("GET", f"crm/v3/objects/companies?limit={limit}")
        return result.get("results", [])
