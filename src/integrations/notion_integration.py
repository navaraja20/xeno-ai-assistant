"""
Notion Integration for XENO
Supports: Create pages, update databases, query data, manage blocks
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp

from . import IntegrationBase, IntegrationCredentials


class NotionIntegration(IntegrationBase):
    """Notion workspace integration"""

    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.api_token = credentials.credentials.get("api_token") if credentials else None
        self.base_url = "https://api.notion.com/v1"
        self.version = "2022-06-28"

    @property
    def service_name(self) -> str:
        return "notion"

    @property
    def supported_triggers(self) -> List[str]:
        return ["page_created", "page_updated", "database_item_created"]

    @property
    def supported_actions(self) -> List[str]:
        return [
            "create_page",
            "update_page",
            "create_database",
            "query_database",
            "add_page_content",
            "search",
            "get_page",
            "get_database",
        ]

    async def authenticate(self) -> bool:
        """Authenticate with Notion API"""
        if not self.api_token:
            return False

        try:
            # Test by listing users
            await self._api_call("GET", "/users")
            self.connected = True
            return True
        except Exception as e:
            print(f"Notion authentication failed: {e}")
            return False

    async def test_connection(self) -> bool:
        """Test Notion connection"""
        return await self.authenticate()

    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Notion action"""
        action_map = {
            "create_page": self.create_page,
            "update_page": self.update_page,
            "create_database": self.create_database,
            "query_database": self.query_database,
            "add_page_content": self.add_page_content,
            "search": self.search,
            "get_page": self.get_page,
            "get_database": self.get_database,
        }

        handler = action_map.get(action)
        if not handler:
            raise ValueError(f"Unknown action: {action}")

        return await handler(**parameters)

    async def create_page(
        self,
        parent_id: str,
        title: str,
        properties: Optional[Dict] = None,
        content: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """Create a new page"""
        payload = {
            "parent": {"page_id": parent_id},
            "properties": {"title": {"title": [{"text": {"content": title}}]}},
        }

        if properties:
            payload["properties"].update(properties)

        if content:
            payload["children"] = content

        return await self._api_call("POST", "/pages", payload)

    async def update_page(self, page_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Update page properties"""
        payload = {"properties": properties}
        return await self._api_call("PATCH", f"/pages/{page_id}", payload)

    async def create_database(
        self, parent_id: str, title: str, properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new database"""
        payload = {
            "parent": {"page_id": parent_id},
            "title": [{"text": {"content": title}}],
            "properties": properties,
        }

        return await self._api_call("POST", "/databases", payload)

    async def query_database(
        self,
        database_id: str,
        filter: Optional[Dict] = None,
        sorts: Optional[List[Dict]] = None,
        start_cursor: Optional[str] = None,
        page_size: int = 100,
    ) -> Dict[str, Any]:
        """Query database"""
        payload = {"page_size": page_size}

        if filter:
            payload["filter"] = filter
        if sorts:
            payload["sorts"] = sorts
        if start_cursor:
            payload["start_cursor"] = start_cursor

        return await self._api_call("POST", f"/databases/{database_id}/query", payload)

    async def add_page_content(self, page_id: str, blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add content blocks to a page"""
        payload = {"children": blocks}
        return await self._api_call("PATCH", f"/blocks/{page_id}/children", payload)

    async def search(
        self,
        query: str,
        filter: Optional[Dict] = None,
        sort: Optional[Dict] = None,
        page_size: int = 100,
    ) -> Dict[str, Any]:
        """Search Notion"""
        payload = {"query": query, "page_size": page_size}

        if filter:
            payload["filter"] = filter
        if sort:
            payload["sort"] = sort

        return await self._api_call("POST", "/search", payload)

    async def get_page(self, page_id: str) -> Dict[str, Any]:
        """Get page details"""
        return await self._api_call("GET", f"/pages/{page_id}")

    async def get_database(self, database_id: str) -> Dict[str, Any]:
        """Get database details"""
        return await self._api_call("GET", f"/databases/{database_id}")

    def create_text_block(self, text: str, block_type: str = "paragraph") -> Dict[str, Any]:
        """Helper to create text block"""
        return {
            "object": "block",
            "type": block_type,
            block_type: {"rich_text": [{"text": {"content": text}}]},
        }

    def create_heading_block(self, text: str, level: int = 1) -> Dict[str, Any]:
        """Helper to create heading block"""
        heading_type = f"heading_{level}"
        return self.create_text_block(text, heading_type)

    def create_todo_block(self, text: str, checked: bool = False) -> Dict[str, Any]:
        """Helper to create to-do block"""
        return {
            "object": "block",
            "type": "to_do",
            "to_do": {"rich_text": [{"text": {"content": text}}], "checked": checked},
        }

    def create_code_block(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Helper to create code block"""
        return {
            "object": "block",
            "type": "code",
            "code": {"rich_text": [{"text": {"content": code}}], "language": language},
        }

    async def _api_call(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make API call to Notion"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Notion-Version": self.version,
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, json=data, headers=headers) as response:
                if response.status >= 400:
                    error_data = await response.json()
                    raise Exception(f"Notion API error: {error_data}")

                return await response.json()

    def get_available_actions(self) -> List[Dict[str, Any]]:
        """Get available actions with metadata"""
        return [
            {
                "action": "create_page",
                "name": "Create Page",
                "description": "Create a new Notion page",
                "parameters": [
                    {"name": "parent_id", "type": "string", "required": True},
                    {"name": "title", "type": "string", "required": True},
                    {"name": "properties", "type": "object", "required": False},
                    {"name": "content", "type": "array", "required": False},
                ],
            },
            {
                "action": "update_page",
                "name": "Update Page",
                "description": "Update page properties",
                "parameters": [
                    {"name": "page_id", "type": "string", "required": True},
                    {"name": "properties", "type": "object", "required": True},
                ],
            },
            {
                "action": "query_database",
                "name": "Query Database",
                "description": "Query a Notion database",
                "parameters": [
                    {"name": "database_id", "type": "string", "required": True},
                    {"name": "filter", "type": "object", "required": False},
                    {"name": "sorts", "type": "array", "required": False},
                    {"name": "page_size", "type": "integer", "required": False},
                ],
            },
            {
                "action": "add_page_content",
                "name": "Add Content",
                "description": "Add content blocks to a page",
                "parameters": [
                    {"name": "page_id", "type": "string", "required": True},
                    {"name": "blocks", "type": "array", "required": True},
                ],
            },
            {
                "action": "search",
                "name": "Search",
                "description": "Search Notion workspace",
                "parameters": [
                    {"name": "query", "type": "string", "required": True},
                    {"name": "filter", "type": "object", "required": False},
                    {"name": "page_size", "type": "integer", "required": False},
                ],
            },
        ]
