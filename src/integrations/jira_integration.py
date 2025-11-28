"""
Jira Integration
Issue tracking and project management
"""

import os
from typing import Any, Dict, List, Optional

import aiohttp

from src.core.logger import setup_logger
from src.integrations import IntegrationBase, IntegrationCredentials


class JiraIntegration(IntegrationBase):
    """Jira issue tracking integration"""

    def __init__(self, credentials: Optional[IntegrationCredentials] = None):
        super().__init__(credentials)
        self.logger = setup_logger("integrations.jira")

        self.domain = (
            credentials.additional_data.get("domain") if credentials else os.getenv("JIRA_DOMAIN")
        )
        self.email = (
            credentials.additional_data.get("email") if credentials else os.getenv("JIRA_EMAIL")
        )
        self.api_token = credentials.api_key if credentials else os.getenv("JIRA_API_TOKEN")

        self.base_url = f"https://{self.domain}.atlassian.net/rest/api/3"
        self.auth = aiohttp.BasicAuth(self.email, self.api_token)

    @property
    def service_name(self) -> str:
        return "jira"

    @property
    def supported_triggers(self) -> List[str]:
        return ["issue_created", "issue_updated", "issue_completed"]

    @property
    def supported_actions(self) -> List[str]:
        return [
            "create_issue",
            "update_issue",
            "transition_issue",
            "add_comment",
            "assign_issue",
            "search_issues",
        ]

    async def authenticate(self) -> bool:
        """Test Jira authentication"""
        return await self.test_connection()

    async def test_connection(self) -> bool:
        """Test Jira API connection"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/myself", auth=self.auth) as response:
                    self.connected = response.status == 200
                    return self.connected
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Jira action"""
        action_map = {
            "create_issue": self.create_issue,
            "update_issue": self.update_issue,
            "transition_issue": self.transition_issue,
            "add_comment": self.add_comment,
            "assign_issue": self.assign_issue,
            "search_issues": self.search_issues,
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
        """Make Jira API call"""
        url = f"{self.base_url}/{endpoint}"

        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, auth=self.auth, json=data) as response:
                if response.status >= 400:
                    error = await response.text()
                    raise Exception(f"API error: {error}")
                return await response.json()

    async def create_issue(
        self,
        project_key: str,
        summary: str,
        description: str,
        issue_type: str = "Task",
        priority: str = "Medium",
    ) -> Dict[str, Any]:
        """Create a Jira issue"""
        data = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {"type": "paragraph", "content": [{"type": "text", "text": description}]}
                    ],
                },
                "issuetype": {"name": issue_type},
                "priority": {"name": priority},
            }
        }

        return await self._api_call("POST", "issue", data=data)

    async def update_issue(
        self,
        issue_key: str,
        summary: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a Jira issue"""
        fields = {}

        if summary:
            fields["summary"] = summary

        if description:
            fields["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": description}]}
                ],
            }

        data = {"fields": fields}
        return await self._api_call("PUT", f"issue/{issue_key}", data=data)

    async def transition_issue(
        self,
        issue_key: str,
        transition_id: str,
    ) -> Dict[str, Any]:
        """Transition issue to new status"""
        data = {"transition": {"id": transition_id}}
        return await self._api_call("POST", f"issue/{issue_key}/transitions", data=data)

    async def add_comment(
        self,
        issue_key: str,
        comment: str,
    ) -> Dict[str, Any]:
        """Add comment to issue"""
        data = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment}]}],
            }
        }

        return await self._api_call("POST", f"issue/{issue_key}/comment", data=data)

    async def assign_issue(
        self,
        issue_key: str,
        account_id: str,
    ) -> Dict[str, Any]:
        """Assign issue to user"""
        data = {"accountId": account_id}
        return await self._api_call("PUT", f"issue/{issue_key}/assignee", data=data)

    async def search_issues(
        self,
        jql: str,
        max_results: int = 50,
    ) -> List[Dict[str, Any]]:
        """Search issues using JQL"""
        data = {
            "jql": jql,
            "maxResults": max_results,
        }

        result = await self._api_call("POST", "search", data=data)
        return result.get("issues", [])
