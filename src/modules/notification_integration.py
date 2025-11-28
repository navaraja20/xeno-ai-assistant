"""
Notification System Integration
Connects notification system with existing XENO modules
"""

from typing import Optional

from src.core.logger import setup_logger
from src.modules.smart_notifications import (
    NotificationPriority,
    NotificationType,
    send_notification,
)


class NotificationIntegration:
    """Integration layer for XENO notifications"""

    def __init__(self):
        self.logger = setup_logger("notifications.integration")

    # Email Notifications
    def notify_new_email(
        self,
        sender: str,
        subject: str,
        snippet: str,
        email_id: str,
        is_important: bool = False,
    ):
        """Send notification for new email"""

        priority = (
            NotificationPriority.HIGH if is_important else NotificationPriority.MEDIUM
        )

        send_notification(
            title=f"📧 New Email from {sender}",
            message=f"{subject}\n{snippet[:100]}...",
            notification_type=NotificationType.EMAIL,
            priority=priority,
            data={"sender": sender, "email_id": email_id, "subject": subject},
            actions=[
                {"label": "Reply", "action": "reply"},
                {"label": "Archive", "action": "archive"},
                {"label": "Mark Read", "action": "mark_read"},
            ],
        )

    # Calendar Notifications
    def notify_calendar_event(
        self,
        event_title: str,
        start_time: str,
        location: Optional[str] = None,
        minutes_before: int = 15,
    ):
        """Send notification for calendar event"""

        message = f"Event starts in {minutes_before} minutes"
        if location:
            message += f"\nLocation: {location}"

        # More urgent as time approaches
        if minutes_before <= 5:
            priority = NotificationPriority.CRITICAL
        elif minutes_before <= 15:
            priority = NotificationPriority.HIGH
        else:
            priority = NotificationPriority.MEDIUM

        send_notification(
            title=f"📅 {event_title}",
            message=message,
            notification_type=NotificationType.CALENDAR,
            priority=priority,
            data={"event_title": event_title, "start_time": start_time},
            actions=[
                {"label": "Join", "action": "join"},
                {"label": "Snooze 5min", "action": "snooze_5"},
            ],
        )

    # Task Notifications
    def notify_task_due(
        self, task_name: str, due_time: str, project: Optional[str] = None
    ):
        """Send notification for due task"""

        message = f"Due: {due_time}"
        if project:
            message = f"Project: {project}\n{message}"

        send_notification(
            title=f"✅ Task Due: {task_name}",
            message=message,
            notification_type=NotificationType.TASK,
            priority=NotificationPriority.HIGH,
            data={"task_name": task_name, "due_time": due_time, "project": project},
            actions=[
                {"label": "Complete", "action": "complete"},
                {"label": "Postpone", "action": "postpone"},
            ],
        )

    # GitHub Notifications
    def notify_github_event(
        self, event_type: str, repo: str, title: str, url: str, actor: str = None
    ):
        """Send notification for GitHub event"""

        event_icons = {
            "issue": "🐛",
            "pr": "🔀",
            "review": "👀",
            "mention": "💬",
            "star": "⭐",
        }

        icon = event_icons.get(event_type, "📦")
        message = f"Repository: {repo}"
        if actor:
            message += f"\nBy: {actor}"

        # Mentions are more important
        priority = (
            NotificationPriority.HIGH
            if event_type == "mention"
            else NotificationPriority.MEDIUM
        )

        send_notification(
            title=f"{icon} {title}",
            message=message,
            notification_type=NotificationType.GITHUB,
            priority=priority,
            data={
                "event_type": event_type,
                "repo": repo,
                "url": url,
                "actor": actor,
            },
            actions=[
                {"label": "View", "action": "open_url"},
                {"label": "Dismiss", "action": "dismiss"},
            ],
        )

    # LinkedIn Notifications
    def notify_linkedin_event(
        self, event_type: str, title: str, description: str, url: str = None
    ):
        """Send notification for LinkedIn event"""

        event_icons = {
            "connection": "🤝",
            "message": "💬",
            "job_alert": "💼",
            "profile_view": "👀",
        }

        icon = event_icons.get(event_type, "💼")

        # Job alerts and messages are higher priority
        priority = (
            NotificationPriority.HIGH
            if event_type in ["message", "job_alert"]
            else NotificationPriority.LOW
        )

        actions = [{"label": "View", "action": "open_url"}]
        if event_type == "message":
            actions.insert(0, {"label": "Reply", "action": "reply"})

        send_notification(
            title=f"{icon} {title}",
            message=description,
            notification_type=NotificationType.LINKEDIN,
            priority=priority,
            data={"event_type": event_type, "url": url},
            actions=actions,
        )

    # System Notifications
    def notify_system_event(
        self, title: str, message: str, is_critical: bool = False
    ):
        """Send system notification"""

        priority = (
            NotificationPriority.CRITICAL
            if is_critical
            else NotificationPriority.MEDIUM
        )

        send_notification(
            title=f"⚙️ {title}",
            message=message,
            notification_type=NotificationType.SYSTEM,
            priority=priority,
        )

    # AI Assistant Notifications
    def notify_ai_response(self, query: str, response_preview: str):
        """Send notification for AI response"""

        send_notification(
            title=f"🤖 AI Response Ready",
            message=f"Query: {query}\n{response_preview[:100]}...",
            notification_type=NotificationType.AI,
            priority=NotificationPriority.LOW,
            actions=[{"label": "View", "action": "view_response"}],
        )

    # Voice Command Notifications
    def notify_voice_command(self, command: str, result: str, success: bool = True):
        """Send notification for voice command execution"""

        icon = "✅" if success else "❌"
        priority = (
            NotificationPriority.INFO
            if success
            else NotificationPriority.MEDIUM
        )

        send_notification(
            title=f"{icon} Voice Command: {command}",
            message=result,
            notification_type=NotificationType.VOICE,
            priority=priority,
        )


# Global integration instance
_integration: Optional[NotificationIntegration] = None


def get_notification_integration() -> NotificationIntegration:
    """Get global notification integration instance"""
    global _integration
    if _integration is None:
        _integration = NotificationIntegration()
    return _integration


# Convenience functions for quick access
def notify_email(sender: str, subject: str, snippet: str, email_id: str, **kwargs):
    """Quick email notification"""
    return get_notification_integration().notify_new_email(
        sender, subject, snippet, email_id, **kwargs
    )


def notify_calendar(event_title: str, start_time: str, **kwargs):
    """Quick calendar notification"""
    return get_notification_integration().notify_calendar_event(
        event_title, start_time, **kwargs
    )


def notify_task(task_name: str, due_time: str, **kwargs):
    """Quick task notification"""
    return get_notification_integration().notify_task_due(task_name, due_time, **kwargs)


def notify_github(event_type: str, repo: str, title: str, url: str, **kwargs):
    """Quick GitHub notification"""
    return get_notification_integration().notify_github_event(
        event_type, repo, title, url, **kwargs
    )


def notify_linkedin(event_type: str, title: str, description: str, **kwargs):
    """Quick LinkedIn notification"""
    return get_notification_integration().notify_linkedin_event(
        event_type, title, description, **kwargs
    )


def notify_system(title: str, message: str, **kwargs):
    """Quick system notification"""
    return get_notification_integration().notify_system_event(title, message, **kwargs)
