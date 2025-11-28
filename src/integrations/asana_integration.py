"""
Asana Integration for XENO
Support for project management, tasks, and team collaboration
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp

from . import IntegrationBase


class AsanaIntegration(IntegrationBase):
    """Asana API integration"""

    def __init__(self, credentials: Dict[str, Any]):
        super().__init__(credentials)
        self.access_token = credentials.get("access_token")
        self.base_url = "https://app.asana.com/api/1.0"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    @property
    def service_name(self) -> str:
        return "asana"

    @property
    def supported_triggers(self) -> List[str]:
        return ["task_created", "task_completed", "task_assigned", "due_date_approaching"]

    @property
    def supported_actions(self) -> List[str]:
        return [
            "create_task",
            "update_task",
            "complete_task",
            "create_project",
            "add_comment",
            "add_subtask",
            "assign_task",
            "set_due_date",
        ]

    async def authenticate(self) -> bool:
        """Test Asana authentication"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/users/me", headers=self.headers
                ) as response:
                    return response.status == 200
        except Exception:
            return False

    async def test_connection(self) -> bool:
        """Test Asana API connection"""
        return await self.authenticate()

    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Asana action"""
        actions = {
            "create_task": self.create_task,
            "update_task": self.update_task,
            "complete_task": self.complete_task,
            "create_project": self.create_project,
            "add_comment": self.add_comment,
            "add_subtask": self.add_subtask,
            "assign_task": self.assign_task,
            "set_due_date": self.set_due_date,
        }

        if action not in actions:
            raise ValueError(f"Unknown action: {action}")

        return await actions[action](**parameters)

    async def create_task(
        self,
        name: str,
        workspace: str,
        notes: Optional[str] = None,
        assignee: Optional[str] = None,
        projects: Optional[List[str]] = None,
        due_on: Optional[str] = None,
        start_on: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new task"""
        data = {"data": {"name": name, "workspace": workspace}}

        if notes:
            data["data"]["notes"] = notes
        if assignee:
            data["data"]["assignee"] = assignee
        if projects:
            data["data"]["projects"] = projects
        if due_on:
            data["data"]["due_on"] = due_on
        if start_on:
            data["data"]["start_on"] = start_on

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/tasks", headers=self.headers, json=data
            ) as response:
                result = await response.json()
                return {
                    "success": response.status == 201,
                    "task_id": result.get("data", {}).get("gid"),
                    "permalink_url": result.get("data", {}).get("permalink_url"),
                }

    async def update_task(
        self,
        task_id: str,
        name: Optional[str] = None,
        notes: Optional[str] = None,
        completed: Optional[bool] = None,
        due_on: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an existing task"""
        data = {"data": {}}

        if name:
            data["data"]["name"] = name
        if notes:
            data["data"]["notes"] = notes
        if completed is not None:
            data["data"]["completed"] = completed
        if due_on:
            data["data"]["due_on"] = due_on

        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{self.base_url}/tasks/{task_id}", headers=self.headers, json=data
            ) as response:
                return {"success": response.status == 200}

    async def complete_task(self, task_id: str) -> Dict[str, Any]:
        """Mark a task as complete"""
        return await self.update_task(task_id, completed=True)

    async def create_project(
        self,
        name: str,
        workspace: str,
        notes: Optional[str] = None,
        color: Optional[str] = None,
        public: bool = True,
    ) -> Dict[str, Any]:
        """Create a new project"""
        data = {"data": {"name": name, "workspace": workspace, "public": public}}

        if notes:
            data["data"]["notes"] = notes
        if color:
            data["data"]["color"] = color

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/projects", headers=self.headers, json=data
            ) as response:
                result = await response.json()
                return {
                    "success": response.status == 201,
                    "project_id": result.get("data", {}).get("gid"),
                    "permalink_url": result.get("data", {}).get("permalink_url"),
                }

    async def add_comment(self, task_id: str, text: str) -> Dict[str, Any]:
        """Add a comment to a task"""
        data = {"data": {"text": text}}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/tasks/{task_id}/stories", headers=self.headers, json=data
            ) as response:
                result = await response.json()
                return {
                    "success": response.status == 201,
                    "comment_id": result.get("data", {}).get("gid"),
                }

    async def add_subtask(
        self,
        parent_task_id: str,
        name: str,
        notes: Optional[str] = None,
        assignee: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a subtask to a task"""
        data = {"data": {"name": name, "parent": parent_task_id}}

        if notes:
            data["data"]["notes"] = notes
        if assignee:
            data["data"]["assignee"] = assignee

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/tasks", headers=self.headers, json=data
            ) as response:
                result = await response.json()
                return {
                    "success": response.status == 201,
                    "subtask_id": result.get("data", {}).get("gid"),
                }

    async def assign_task(self, task_id: str, assignee: str) -> Dict[str, Any]:
        """Assign a task to a user"""
        return await self.update_task(task_id, assignee=assignee)

    async def set_due_date(self, task_id: str, due_date: str) -> Dict[str, Any]:
        """Set task due date (YYYY-MM-DD format)"""
        return await self.update_task(task_id, due_on=due_date)

    async def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get task details"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/tasks/{task_id}", headers=self.headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("data", {})
                return {}

    async def list_tasks(
        self,
        project_id: Optional[str] = None,
        assignee: Optional[str] = None,
        workspace: Optional[str] = None,
        completed_since: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List tasks with filters"""
        params = {}

        if project_id:
            params["project"] = project_id
        if assignee:
            params["assignee"] = assignee
        if workspace:
            params["workspace"] = workspace
        if completed_since:
            params["completed_since"] = completed_since

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/tasks", headers=self.headers, params=params
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("data", [])
                return []

    async def list_projects(self, workspace: str) -> List[Dict[str, Any]]:
        """List all projects in workspace"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/projects", headers=self.headers, params={"workspace": workspace}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("data", [])
                return []

    def get_available_actions(self) -> List[Dict[str, Any]]:
        """Get list of available actions with metadata"""
        return [
            {
                "name": "create_task",
                "description": "Create a new task",
                "parameters": ["name", "workspace", "notes", "assignee", "projects", "due_on"],
            },
            {
                "name": "update_task",
                "description": "Update an existing task",
                "parameters": ["task_id", "name", "notes", "completed", "due_on"],
            },
            {
                "name": "add_comment",
                "description": "Add a comment to a task",
                "parameters": ["task_id", "text"],
            },
            {
                "name": "create_project",
                "description": "Create a new project",
                "parameters": ["name", "workspace", "notes", "color"],
            },
        ]
