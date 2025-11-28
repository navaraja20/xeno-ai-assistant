"""
Smart Notifications System for XENO
Priority-based, time-aware, intelligent notification delivery
"""

import json
import logging
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from src.core.logger import setup_logger


class NotificationPriority(Enum):
    """Notification priority levels"""

    CRITICAL = 5  # Immediate delivery
    HIGH = 4  # Deliver within 1 min
    MEDIUM = 3  # Deliver within 5 min or bundle
    LOW = 2  # Bundle and deliver hourly
    INFO = 1  # Daily digest only


class NotificationType(Enum):
    """Types of notifications"""

    EMAIL = "email"
    CALENDAR = "calendar"
    TASK = "task"
    GITHUB = "github"
    LINKEDIN = "linkedin"
    SYSTEM = "system"
    AI = "ai"
    VOICE = "voice"


@dataclass
class Notification:
    """Notification data structure"""

    id: str
    title: str
    message: str
    type: NotificationType
    priority: NotificationPriority
    timestamp: datetime = field(default_factory=datetime.now)
    data: Dict[str, Any] = field(default_factory=dict)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    read: bool = False
    bundled: bool = False
    delivered: bool = False


@dataclass
class NotificationRule:
    """User-defined notification rule"""

    name: str
    condition: Callable[[Notification], bool]
    action: str  # 'deliver', 'bundle', 'silence', 'snooze'
    priority_override: Optional[NotificationPriority] = None
    time_window: Optional[tuple] = None  # (start_hour, end_hour)


class DoNotDisturbSchedule:
    """Do Not Disturb scheduler"""

    def __init__(self):
        self.logger = setup_logger("notifications.dnd")
        self.schedules = []  # List of (start_time, end_time, days)
        self.manual_dnd = False
        self.allow_critical = True

    def is_dnd_active(self) -> bool:
        """Check if DND is currently active"""
        if self.manual_dnd:
            return True

        now = datetime.now()
        current_time = now.time()
        current_day = now.weekday()

        for start_time, end_time, days in self.schedules:
            if current_day in days:
                if start_time <= current_time <= end_time:
                    return True

        return False

    def add_schedule(self, start_hour: int, end_hour: int, days: List[int]):
        """Add DND schedule (days: 0=Monday, 6=Sunday)"""
        from datetime import time

        start_time = time(start_hour, 0)
        end_time = time(end_hour, 0)
        self.schedules.append((start_time, end_time, days))

    def enable_manual_dnd(self, duration_minutes: Optional[int] = None):
        """Manually enable DND"""
        self.manual_dnd = True
        if duration_minutes:
            # Auto-disable after duration
            threading.Timer(duration_minutes * 60, self.disable_manual_dnd).start()

    def disable_manual_dnd(self):
        """Disable manual DND"""
        self.manual_dnd = False


class NotificationBundler:
    """Bundle similar notifications together"""

    def __init__(self, bundle_interval: int = 300):  # 5 minutes default
        self.logger = setup_logger("notifications.bundler")
        self.bundle_interval = bundle_interval
        self.pending_bundles: Dict[str, List[Notification]] = defaultdict(list)
        self.bundle_timer = None

    def add_to_bundle(self, notification: Notification):
        """Add notification to bundle queue"""
        bundle_key = f"{notification.type.value}_{notification.priority.value}"
        self.pending_bundles[bundle_key].append(notification)

        # Start timer if not running
        if not self.bundle_timer or not self.bundle_timer.is_alive():
            self.bundle_timer = threading.Timer(
                self.bundle_interval, self._flush_bundles
            )
            self.bundle_timer.start()

    def _flush_bundles(self):
        """Deliver all bundled notifications"""
        for bundle_key, notifications in self.pending_bundles.items():
            if len(notifications) > 1:
                # Create bundled notification
                bundled = self._create_bundled_notification(notifications)
                # Deliver via notification manager
                self.logger.info(
                    f"Delivering bundle: {len(notifications)} notifications"
                )
            elif len(notifications) == 1:
                # Deliver single notification
                notifications[0].delivered = True

        self.pending_bundles.clear()

    def _create_bundled_notification(
        self, notifications: List[Notification]
    ) -> Notification:
        """Create a single bundled notification"""
        first = notifications[0]
        count = len(notifications)

        bundled = Notification(
            id=f"bundle_{int(time.time())}",
            title=f"{count} {first.type.value} notifications",
            message=f"You have {count} new {first.type.value} notifications",
            type=first.type,
            priority=first.priority,
            bundled=True,
            data={"notifications": [n.id for n in notifications]},
        )

        return bundled


class SmartNotificationManager:
    """Main notification management system"""

    def __init__(self, data_dir: str = "data/notifications"):
        self.logger = setup_logger("notifications.manager")
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Components
        self.dnd = DoNotDisturbSchedule()
        self.bundler = NotificationBundler()

        # Storage
        self.notifications: List[Notification] = []
        self.rules: List[NotificationRule] = []
        self.history_file = self.data_dir / "history.json"

        # Callbacks
        self.delivery_callbacks: List[Callable[[Notification], None]] = []

        # Statistics
        self.stats = {
            "total_sent": 0,
            "bundled": 0,
            "silenced": 0,
            "critical_delivered": 0,
        }

        # Load configuration
        self._load_config()
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Setup default notification rules"""

        # Rule: Bundle low-priority emails
        self.add_rule(
            NotificationRule(
                name="Bundle low-priority emails",
                condition=lambda n: n.type == NotificationType.EMAIL
                and n.priority == NotificationPriority.LOW,
                action="bundle",
            )
        )

        # Rule: Critical notifications always deliver
        self.add_rule(
            NotificationRule(
                name="Always deliver critical",
                condition=lambda n: n.priority == NotificationPriority.CRITICAL,
                action="deliver",
            )
        )

        # Rule: Silence info during work hours
        self.add_rule(
            NotificationRule(
                name="Silence info 9-5",
                condition=lambda n: n.priority == NotificationPriority.INFO,
                action="silence",
                time_window=(9, 17),
            )
        )

    def send_notification(
        self,
        title: str,
        message: str,
        notification_type: NotificationType,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        actions: Optional[List[Dict[str, Any]]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Notification:
        """Send a notification through the smart system"""

        notification = Notification(
            id=f"notif_{int(time.time() * 1000)}",
            title=title,
            message=message,
            type=notification_type,
            priority=priority,
            actions=actions or [],
            data=data or {},
        )

        # Apply rules
        action = self._apply_rules(notification)

        # Handle based on action
        if action == "silence":
            self.stats["silenced"] += 1
            self.logger.debug(f"Silenced notification: {title}")
            return notification

        elif action == "bundle":
            self.bundler.add_to_bundle(notification)
            self.stats["bundled"] += 1
            return notification

        elif action == "snooze":
            # Snooze for 15 minutes
            threading.Timer(900, lambda: self.send_notification(title, message, notification_type, priority, actions, data)).start()
            return notification

        else:  # deliver
            return self._deliver_notification(notification)

    def _apply_rules(self, notification: Notification) -> str:
        """Apply notification rules to determine action"""

        # Check DND first
        if self.dnd.is_dnd_active():
            if notification.priority == NotificationPriority.CRITICAL:
                if self.dnd.allow_critical:
                    return "deliver"
            return "silence"

        # Apply custom rules
        for rule in self.rules:
            if rule.condition(notification):
                # Check time window
                if rule.time_window:
                    now = datetime.now().hour
                    start, end = rule.time_window
                    if not (start <= now <= end):
                        continue

                # Override priority if specified
                if rule.priority_override:
                    notification.priority = rule.priority_override

                return rule.action

        # Default: deliver
        return "deliver"

    def _deliver_notification(self, notification: Notification) -> Notification:
        """Actually deliver the notification"""

        notification.delivered = True
        self.notifications.append(notification)
        self.stats["total_sent"] += 1

        if notification.priority == NotificationPriority.CRITICAL:
            self.stats["critical_delivered"] += 1

        # Execute delivery callbacks
        for callback in self.delivery_callbacks:
            try:
                callback(notification)
            except Exception as e:
                self.logger.error(f"Delivery callback error: {e}")

        self.logger.info(f"Delivered: {notification.title} ({notification.priority.name})")

        # Save to history
        self._save_to_history(notification)

        return notification

    def add_delivery_callback(self, callback: Callable[[Notification], None]):
        """Register callback for notification delivery"""
        self.delivery_callbacks.append(callback)

    def add_rule(self, rule: NotificationRule):
        """Add custom notification rule"""
        self.rules.append(rule)

    def mark_read(self, notification_id: str):
        """Mark notification as read"""
        for notif in self.notifications:
            if notif.id == notification_id:
                notif.read = True
                break

    def get_unread(self) -> List[Notification]:
        """Get unread notifications"""
        return [n for n in self.notifications if not n.read]

    def get_by_type(self, notification_type: NotificationType) -> List[Notification]:
        """Get notifications by type"""
        return [n for n in self.notifications if n.type == notification_type]

    def get_recent(self, hours: int = 24) -> List[Notification]:
        """Get recent notifications"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [n for n in self.notifications if n.timestamp > cutoff]

    def clear_all(self):
        """Clear all notifications"""
        self.notifications.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get notification statistics"""
        unread_count = len(self.get_unread())
        type_breakdown = defaultdict(int)

        for notif in self.notifications:
            type_breakdown[notif.type.value] += 1

        return {
            **self.stats,
            "unread": unread_count,
            "total_stored": len(self.notifications),
            "by_type": dict(type_breakdown),
        }

    def _save_to_history(self, notification: Notification):
        """Save notification to history file"""
        try:
            history = []
            if self.history_file.exists():
                with open(self.history_file, "r") as f:
                    history = json.load(f)

            history.append(
                {
                    "id": notification.id,
                    "title": notification.title,
                    "message": notification.message,
                    "type": notification.type.value,
                    "priority": notification.priority.value,
                    "timestamp": notification.timestamp.isoformat(),
                    "read": notification.read,
                }
            )

            # Keep last 1000 notifications
            history = history[-1000:]

            with open(self.history_file, "w") as f:
                json.dump(history, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error saving to history: {e}")

    def _load_config(self):
        """Load notification configuration"""
        config_file = self.data_dir / "config.json"
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)

                # Load DND schedules
                for schedule in config.get("dnd_schedules", []):
                    self.dnd.add_schedule(
                        schedule["start_hour"],
                        schedule["end_hour"],
                        schedule["days"],
                    )

                self.logger.info("Notification config loaded")
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")


# Global notification manager instance
_notification_manager: Optional[SmartNotificationManager] = None


def get_notification_manager() -> SmartNotificationManager:
    """Get global notification manager"""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = SmartNotificationManager()
    return _notification_manager


def send_notification(
    title: str,
    message: str,
    notification_type: NotificationType = NotificationType.SYSTEM,
    priority: NotificationPriority = NotificationPriority.MEDIUM,
    **kwargs,
) -> Notification:
    """Quick function to send notification"""
    return get_notification_manager().send_notification(
        title, message, notification_type, priority, **kwargs
    )
