"""
Airtable Integration
Manage databases and records in Airtable
"""

import os
from typing import Any, Dict, List, Optional

import aiohttp

from src.core.logger import setup_logger
from src.integrations import IntegrationBase, IntegrationCredentials


class AirtableIntegration(IntegrationBase):
    """Airtable database integration"""

    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.logger = setup_logger("integrations.airtable")
        self.api_key = credentials.api_key if credentials else os.getenv("AIRTABLE_API_KEY")
        self.base_url = "https://api.airtable.com/v0"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    @property
    def service_name(self) -> str:
        return "airtable"

    @property
    def supported_triggers(self) -> List[str]:
        return ["record_created", "record_updated"]

    @property
    def supported_actions(self) -> List[str]:
        return [
            "create_record",
            "update_record",
            "delete_record",
            "get_record",
            "list_records",
            "search_records",
        ]

    async def authenticate(self) -> bool:
        """Test Airtable authentication"""
        if not self.api_key:
            return False

        # Airtable doesn't have auth endpoint, test with bases list
        return await self.test_connection()

    async def test_connection(self) -> bool:
        """Test Airtable API connection"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.airtable.com/v0/meta/bases", headers=self.headers
                ) as response:
                    return response.status == 200
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Airtable action"""
        action_map = {
            "create_record": self.create_record,
            "update_record": self.update_record,
            "delete_record": self.delete_record,
            "get_record": self.get_record,
            "list_records": self.list_records,
            "search_records": self.search_records,
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
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make Airtable API call"""
        url = f"{self.base_url}/{endpoint}"

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, headers=self.headers, json=data, params=params
            ) as response:
                if response.status >= 400:
                    error = await response.text()
                    raise Exception(f"API error: {error}")
                return await response.json()

    async def create_record(
        self,
        base_id: str,
        table_name: str,
        fields: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a record in Airtable table"""
        data = {"fields": fields}
        return await self._api_call("POST", f"{base_id}/{table_name}", data=data)

    async def update_record(
        self,
        base_id: str,
        table_name: str,
        record_id: str,
        fields: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a record"""
        data = {"fields": fields}
        return await self._api_call("PATCH", f"{base_id}/{table_name}/{record_id}", data=data)

    async def delete_record(
        self,
        base_id: str,
        table_name: str,
        record_id: str,
    ) -> Dict[str, Any]:
        """Delete a record"""
        return await self._api_call("DELETE", f"{base_id}/{table_name}/{record_id}")

    async def get_record(
        self,
        base_id: str,
        table_name: str,
        record_id: str,
    ) -> Dict[str, Any]:
        """Get a specific record"""
        return await self._api_call("GET", f"{base_id}/{table_name}/{record_id}")

    async def list_records(
        self,
        base_id: str,
        table_name: str,
        max_records: int = 100,
        view: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List records from a table"""
        params = {"maxRecords": max_records}
        if view:
            params["view"] = view

        result = await self._api_call("GET", f"{base_id}/{table_name}", params=params)
        return result.get("records", [])

    async def search_records(
        self,
        base_id: str,
        table_name: str,
        formula: str,
        max_records: int = 100,
    ) -> List[Dict[str, Any]]:
        """Search records using formula"""
        params = {
            "filterByFormula": formula,
            "maxRecords": max_records,
        }

        result = await self._api_call("GET", f"{base_id}/{table_name}", params=params)
        return result.get("records", [])
