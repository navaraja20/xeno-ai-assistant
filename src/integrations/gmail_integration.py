"""
Gmail Integration for XENO
Support for sending emails, reading inbox, managing labels
"""

import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

import aiohttp

from . import IntegrationBase


class GmailIntegration(IntegrationBase):
    """Gmail API integration"""

    def __init__(self, credentials: Dict[str, Any]):
        super().__init__(credentials)
        self.access_token = credentials.get("access_token")
        self.base_url = "https://gmail.googleapis.com/gmail/v1"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    @property
    def service_name(self) -> str:
        return "gmail"

    @property
    def supported_triggers(self) -> List[str]:
        return ["new_email", "labeled_email", "important_email"]

    @property
    def supported_actions(self) -> List[str]:
        return [
            "send_email",
            "send_with_attachment",
            "create_draft",
            "add_label",
            "archive_email",
            "mark_read",
            "mark_unread",
            "star_email",
            "delete_email",
        ]

    async def authenticate(self) -> bool:
        """Test Gmail authentication"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/users/me/profile", headers=self.headers
                ) as response:
                    return response.status == 200
        except Exception:
            return False

    async def test_connection(self) -> bool:
        """Test Gmail API connection"""
        return await self.authenticate()

    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Gmail action"""
        actions = {
            "send_email": self.send_email,
            "send_with_attachment": self.send_with_attachment,
            "create_draft": self.create_draft,
            "add_label": self.add_label,
            "archive_email": self.archive_email,
            "mark_read": self.mark_read,
            "mark_unread": self.mark_unread,
            "star_email": self.star_email,
            "delete_email": self.delete_email,
        }

        if action not in actions:
            raise ValueError(f"Unknown action: {action}")

        return await actions[action](**parameters)

    def create_message(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        html: bool = False,
    ) -> str:
        """Create MIME email message"""
        message = MIMEMultipart() if html else MIMEText(body)

        if isinstance(message, MIMEMultipart):
            message.attach(MIMEText(body, "html" if html else "plain"))

        message["to"] = to
        message["subject"] = subject

        if cc:
            message["cc"] = cc
        if bcc:
            message["bcc"] = bcc

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return raw

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        html: bool = False,
    ) -> Dict[str, Any]:
        """Send an email"""
        raw_message = self.create_message(to, subject, body, cc, bcc, html)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/users/me/messages/send",
                headers=self.headers,
                json={"raw": raw_message},
            ) as response:
                result = await response.json()
                return {
                    "success": response.status == 200,
                    "message_id": result.get("id"),
                    "thread_id": result.get("threadId"),
                }

    async def send_with_attachment(
        self,
        to: str,
        subject: str,
        body: str,
        attachment_path: str,
        attachment_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send email with attachment"""
        import os
        from email.mime.application import MIMEApplication

        message = MIMEMultipart()
        message["to"] = to
        message["subject"] = subject
        message.attach(MIMEText(body))

        # Attach file
        with open(attachment_path, "rb") as f:
            attachment = MIMEApplication(f.read())
            filename = attachment_name or os.path.basename(attachment_path)
            attachment.add_header("Content-Disposition", "attachment", filename=filename)
            message.attach(attachment)

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/users/me/messages/send", headers=self.headers, json={"raw": raw}
            ) as response:
                result = await response.json()
                return {"success": response.status == 200, "message_id": result.get("id")}

    async def create_draft(
        self, to: str, subject: str, body: str, html: bool = False
    ) -> Dict[str, Any]:
        """Create a draft email"""
        raw_message = self.create_message(to, subject, body, html=html)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/users/me/drafts",
                headers=self.headers,
                json={"message": {"raw": raw_message}},
            ) as response:
                result = await response.json()
                return {"success": response.status == 200, "draft_id": result.get("id")}

    async def add_label(self, message_id: str, label_ids: List[str]) -> Dict[str, Any]:
        """Add labels to email"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/users/me/messages/{message_id}/modify",
                headers=self.headers,
                json={"addLabelIds": label_ids},
            ) as response:
                return {"success": response.status == 200}

    async def archive_email(self, message_id: str) -> Dict[str, Any]:
        """Archive an email (remove from inbox)"""
        return await self.add_label(message_id, ["INBOX"])

    async def mark_read(self, message_id: str) -> Dict[str, Any]:
        """Mark email as read"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/users/me/messages/{message_id}/modify",
                headers=self.headers,
                json={"removeLabelIds": ["UNREAD"]},
            ) as response:
                return {"success": response.status == 200}

    async def mark_unread(self, message_id: str) -> Dict[str, Any]:
        """Mark email as unread"""
        return await self.add_label(message_id, ["UNREAD"])

    async def star_email(self, message_id: str) -> Dict[str, Any]:
        """Star an email"""
        return await self.add_label(message_id, ["STARRED"])

    async def delete_email(self, message_id: str) -> Dict[str, Any]:
        """Delete an email"""
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.base_url}/users/me/messages/{message_id}", headers=self.headers
            ) as response:
                return {"success": response.status == 204}

    async def list_messages(
        self,
        query: Optional[str] = None,
        max_results: int = 10,
        label_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """List messages in mailbox"""
        params = {"maxResults": max_results}

        if query:
            params["q"] = query
        if label_ids:
            params["labelIds"] = label_ids

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/users/me/messages", headers=self.headers, params=params
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("messages", [])
                return []

    async def get_message(self, message_id: str) -> Dict[str, Any]:
        """Get full message details"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/users/me/messages/{message_id}", headers=self.headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                return {}

    async def list_labels(self) -> List[Dict[str, Any]]:
        """List all labels"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/users/me/labels", headers=self.headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("labels", [])
                return []

    def get_available_actions(self) -> List[Dict[str, Any]]:
        """Get list of available actions with metadata"""
        return [
            {
                "name": "send_email",
                "description": "Send an email",
                "parameters": ["to", "subject", "body", "cc", "bcc", "html"],
            },
            {
                "name": "create_draft",
                "description": "Create a draft email",
                "parameters": ["to", "subject", "body", "html"],
            },
            {
                "name": "add_label",
                "description": "Add labels to email",
                "parameters": ["message_id", "label_ids"],
            },
            {
                "name": "mark_read",
                "description": "Mark email as read",
                "parameters": ["message_id"],
            },
            {"name": "star_email", "description": "Star an email", "parameters": ["message_id"]},
        ]
