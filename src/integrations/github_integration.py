"""
GitHub Integration for XENO
Support for repository management, issues, PRs, and more
"""

from typing import Any, Dict, List, Optional

import aiohttp

from . import IntegrationBase


class GitHubIntegration(IntegrationBase):
    """GitHub API integration"""

    def __init__(self, credentials: Dict[str, Any]):
        super().__init__(credentials)
        self.api_token = credentials.get("api_token")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.api_token}",
            "Accept": "application/vnd.github.v3+json",
        }

    @property
    def service_name(self) -> str:
        return "github"

    @property
    def supported_triggers(self) -> List[str]:
        return ["push", "pull_request", "issue", "release", "star"]

    @property
    def supported_actions(self) -> List[str]:
        return [
            "create_issue",
            "create_pr",
            "add_comment",
            "create_repository",
            "update_issue",
            "merge_pr",
            "create_release",
            "star_repository",
        ]

    async def authenticate(self) -> bool:
        """Test GitHub authentication"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/user", headers=self.headers) as response:
                    return response.status == 200
        except Exception:
            return False

    async def test_connection(self) -> bool:
        """Test GitHub API connection"""
        return await self.authenticate()

    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GitHub action"""
        actions = {
            "create_issue": self.create_issue,
            "create_pr": self.create_pr,
            "add_comment": self.add_comment,
            "create_repository": self.create_repository,
            "update_issue": self.update_issue,
            "merge_pr": self.merge_pr,
            "create_release": self.create_release,
            "star_repository": self.star_repository,
        }

        if action not in actions:
            raise ValueError(f"Unknown action: {action}")

        return await actions[action](**parameters)

    async def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
        milestone: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a new issue"""
        data = {
            "title": title,
            "body": body or "",
        }

        if labels:
            data["labels"] = labels
        if assignees:
            data["assignees"] = assignees
        if milestone:
            data["milestone"] = milestone

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/repos/{owner}/{repo}/issues", headers=self.headers, json=data
            ) as response:
                result = await response.json()
                return {
                    "success": response.status == 201,
                    "issue_number": result.get("number"),
                    "url": result.get("html_url"),
                }

    async def create_pr(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str,
        body: Optional[str] = None,
        draft: bool = False,
    ) -> Dict[str, Any]:
        """Create a pull request"""
        data = {"title": title, "head": head, "base": base, "body": body or "", "draft": draft}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/repos/{owner}/{repo}/pulls", headers=self.headers, json=data
            ) as response:
                result = await response.json()
                return {
                    "success": response.status == 201,
                    "pr_number": result.get("number"),
                    "url": result.get("html_url"),
                }

    async def add_comment(
        self, owner: str, repo: str, issue_number: int, body: str
    ) -> Dict[str, Any]:
        """Add comment to issue or PR"""
        data = {"body": body}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/comments",
                headers=self.headers,
                json=data,
            ) as response:
                result = await response.json()
                return {"success": response.status == 201, "comment_id": result.get("id")}

    async def create_repository(
        self,
        name: str,
        description: Optional[str] = None,
        private: bool = False,
        auto_init: bool = True,
        gitignore_template: Optional[str] = None,
        license_template: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new repository"""
        data = {
            "name": name,
            "description": description or "",
            "private": private,
            "auto_init": auto_init,
        }

        if gitignore_template:
            data["gitignore_template"] = gitignore_template
        if license_template:
            data["license_template"] = license_template

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/user/repos", headers=self.headers, json=data
            ) as response:
                result = await response.json()
                return {
                    "success": response.status == 201,
                    "repo_name": result.get("full_name"),
                    "url": result.get("html_url"),
                }

    async def update_issue(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        state: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Update an existing issue"""
        data = {}

        if title:
            data["title"] = title
        if body:
            data["body"] = body
        if state:
            data["state"] = state
        if labels:
            data["labels"] = labels
        if assignees:
            data["assignees"] = assignees

        async with aiohttp.ClientSession() as session:
            async with session.patch(
                f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}",
                headers=self.headers,
                json=data,
            ) as response:
                result = await response.json()
                return {
                    "success": response.status == 200,
                    "issue_number": result.get("number"),
                    "url": result.get("html_url"),
                }

    async def merge_pr(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        commit_title: Optional[str] = None,
        commit_message: Optional[str] = None,
        merge_method: str = "merge",
    ) -> Dict[str, Any]:
        """Merge a pull request"""
        data = {"merge_method": merge_method}

        if commit_title:
            data["commit_title"] = commit_title
        if commit_message:
            data["commit_message"] = commit_message

        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/merge",
                headers=self.headers,
                json=data,
            ) as response:
                result = await response.json()
                return {
                    "success": response.status == 200,
                    "merged": result.get("merged", False),
                    "sha": result.get("sha"),
                }

    async def create_release(
        self,
        owner: str,
        repo: str,
        tag_name: str,
        name: str,
        body: Optional[str] = None,
        draft: bool = False,
        prerelease: bool = False,
    ) -> Dict[str, Any]:
        """Create a new release"""
        data = {
            "tag_name": tag_name,
            "name": name,
            "body": body or "",
            "draft": draft,
            "prerelease": prerelease,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/repos/{owner}/{repo}/releases", headers=self.headers, json=data
            ) as response:
                result = await response.json()
                return {
                    "success": response.status == 201,
                    "release_id": result.get("id"),
                    "url": result.get("html_url"),
                }

    async def star_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Star a repository"""
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{self.base_url}/user/starred/{owner}/{repo}", headers=self.headers
            ) as response:
                return {"success": response.status == 204}

    async def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/repos/{owner}/{repo}", headers=self.headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                return {}

    async def list_issues(
        self, owner: str, repo: str, state: str = "open", labels: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List repository issues"""
        params = {"state": state}
        if labels:
            params["labels"] = labels

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/repos/{owner}/{repo}/issues", headers=self.headers, params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                return []

    def get_available_actions(self) -> List[Dict[str, Any]]:
        """Get list of available actions with metadata"""
        return [
            {
                "name": "create_issue",
                "description": "Create a new issue",
                "parameters": ["owner", "repo", "title", "body", "labels", "assignees"],
            },
            {
                "name": "create_pr",
                "description": "Create a pull request",
                "parameters": ["owner", "repo", "title", "head", "base", "body", "draft"],
            },
            {
                "name": "add_comment",
                "description": "Add comment to issue/PR",
                "parameters": ["owner", "repo", "issue_number", "body"],
            },
            {
                "name": "create_repository",
                "description": "Create a new repository",
                "parameters": ["name", "description", "private", "auto_init"],
            },
            {
                "name": "merge_pr",
                "description": "Merge a pull request",
                "parameters": ["owner", "repo", "pr_number", "merge_method"],
            },
        ]
