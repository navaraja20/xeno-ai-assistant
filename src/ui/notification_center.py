"""
Notification Center UI Widget
PyQt6-based notification display and management
"""

from datetime import datetime
from typing import Dict, List, Optional

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.core.logger import setup_logger
from src.modules.smart_notifications import (
    Notification,
    NotificationPriority,
    get_notification_manager,
)


class NotificationItem(QWidget):
    """Individual notification widget"""

    action_clicked = pyqtSignal(str, str)  # notification_id, action

    def __init__(self, notification: Notification, parent=None):
        super().__init__(parent)
        self.notification = notification
        self._setup_ui()

    def _setup_ui(self):
        """Setup notification item UI"""
        layout = QVBoxLayout(self)

        # Header (title + time + priority indicator)
        header = QHBoxLayout()

        # Priority indicator (color dot)
        priority_label = QLabel("●")
        priority_label.setStyleSheet(f"color: {self._get_priority_color()}; font-size: 16px;")
        header.addWidget(priority_label)

        # Title
        title = QLabel(self.notification.title)
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        header.addWidget(title, 1)

        # Time
        time_str = self._format_time()
        time_label = QLabel(time_str)
        time_label.setStyleSheet("color: #666; font-size: 11px;")
        header.addWidget(time_label)

        layout.addLayout(header)

        # Message
        message = QLabel(self.notification.message)
        message.setWordWrap(True)
        message.setStyleSheet("color: #333; font-size: 12px; padding: 5px 0;")
        layout.addWidget(message)

        # Actions
        if self.notification.actions:
            actions_layout = QHBoxLayout()
            for action in self.notification.actions:
                btn = QPushButton(action["label"])
                btn.setStyleSheet(
                    """
                    QPushButton {
                        background: #007ACC;
                        color: white;
                        border: none;
                        padding: 5px 12px;
                        border-radius: 3px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background: #005A9E;
                    }
                """
                )
                btn.clicked.connect(
                    lambda checked, a=action["action"]: self.action_clicked.emit(
                        self.notification.id, a
                    )
                )
                actions_layout.addWidget(btn)
            actions_layout.addStretch()
            layout.addLayout(actions_layout)

        # Styling
        self.setStyleSheet(
            """
            NotificationItem {
                background: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                margin: 5px 0;
            }
        """
        )

        if self.notification.read:
            self.setStyleSheet(
                self.styleSheet()
                + """
                NotificationItem {
                    background: #f5f5f5;
                    opacity: 0.8;
                }
            """
            )

    def _get_priority_color(self) -> str:
        """Get color for priority indicator"""
        colors = {
            NotificationPriority.CRITICAL: "#DC3545",  # Red
            NotificationPriority.HIGH: "#FFC107",  # Orange
            NotificationPriority.MEDIUM: "#28A745",  # Green
            NotificationPriority.LOW: "#6C757D",  # Gray
            NotificationPriority.INFO: "#17A2B8",  # Blue
        }
        return colors.get(self.notification.priority, "#999")

    def _format_time(self) -> str:
        """Format notification timestamp"""
        now = datetime.now()
        diff = now - self.notification.timestamp

        if diff.total_seconds() < 60:
            return "Just now"
        elif diff.total_seconds() < 3600:
            mins = int(diff.total_seconds() / 60)
            return f"{mins}m ago"
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h ago"
        else:
            days = int(diff.total_seconds() / 86400)
            return f"{days}d ago"

    def mark_as_read(self):
        """Mark notification as read"""
        self.notification.read = True
        self.setStyleSheet(self.styleSheet().replace("background: white;", "background: #f5f5f5;"))


class NotificationCenter(QWidget):
    """Main notification center widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger("notifications.ui")
        self.manager = get_notification_manager()

        # UI state
        self.notification_widgets: Dict[str, NotificationItem] = {}
        self.current_filter = "all"

        self._setup_ui()
        self._setup_callbacks()
        self._start_refresh_timer()

    def _setup_ui(self):
        """Setup notification center UI"""
        layout = QVBoxLayout(self)

        # Header
        header = QHBoxLayout()

        title = QLabel("🔔 Notifications")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        header.addWidget(title)

        # Unread count
        self.unread_badge = QLabel("0")
        self.unread_badge.setStyleSheet(
            """
            background: #DC3545;
            color: white;
            border-radius: 10px;
            padding: 2px 8px;
            font-size: 12px;
            font-weight: bold;
        """
        )
        header.addWidget(self.unread_badge)

        header.addStretch()

        # Mark all read button
        mark_read_btn = QPushButton("Mark All Read")
        mark_read_btn.clicked.connect(self._mark_all_read)
        mark_read_btn.setStyleSheet(
            """
            QPushButton {
                background: #6C757D;
                color: white;
                border: none;
                padding: 5px 12px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: #5A6268;
            }
        """
        )
        header.addWidget(mark_read_btn)

        # Clear all button
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self._clear_all)
        clear_btn.setStyleSheet(
            """
            QPushButton {
                background: #DC3545;
                color: white;
                border: none;
                padding: 5px 12px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: #C82333;
            }
        """
        )
        header.addWidget(clear_btn)

        layout.addLayout(header)

        # Filter bar
        filter_bar = QHBoxLayout()

        # Filter buttons
        filters = [
            ("All", "all"),
            ("Unread", "unread"),
            ("Critical", "critical"),
            ("Email", "email"),
            ("Calendar", "calendar"),
        ]

        for label, filter_type in filters:
            btn = QPushButton(label)
            btn.setCheckable(True)
            if filter_type == "all":
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, ft=filter_type: self._set_filter(ft))
            btn.setStyleSheet(
                """
                QPushButton {
                    border: 1px solid #ddd;
                    background: white;
                    padding: 5px 15px;
                    border-radius: 3px;
                }
                QPushButton:checked {
                    background: #007ACC;
                    color: white;
                    border: 1px solid #007ACC;
                }
            """
            )
            filter_bar.addWidget(btn)

        filter_bar.addStretch()

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search notifications...")
        self.search_box.textChanged.connect(self._on_search)
        self.search_box.setStyleSheet(
            """
            QLineEdit {
                padding: 5px 10px;
                border: 1px solid #ddd;
                border-radius: 3px;
                min-width: 200px;
            }
        """
        )
        filter_bar.addWidget(self.search_box)

        layout.addLayout(filter_bar)

        # Notifications list (scrollable)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #f9f9f9; }")

        self.notifications_container = QWidget()
        self.notifications_layout = QVBoxLayout(self.notifications_container)
        self.notifications_layout.addStretch()

        scroll.setWidget(self.notifications_container)
        layout.addWidget(scroll)

        # Stats footer
        footer = QHBoxLayout()
        self.stats_label = QLabel("No notifications")
        self.stats_label.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        footer.addWidget(self.stats_label)
        footer.addStretch()

        layout.addLayout(footer)

    def _setup_callbacks(self):
        """Setup notification manager callbacks"""

        def on_notification(notification: Notification):
            """Called when new notification arrives"""
            self._add_notification(notification)

        self.manager.add_delivery_callback(on_notification)

    def _start_refresh_timer(self):
        """Start periodic refresh timer"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_ui)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds

    def _add_notification(self, notification: Notification):
        """Add notification to UI"""
        if notification.id in self.notification_widgets:
            return

        widget = NotificationItem(notification)
        widget.action_clicked.connect(self._handle_action)

        # Insert at top
        self.notifications_layout.insertWidget(0, widget)
        self.notification_widgets[notification.id] = widget

        self._update_ui()

    def _handle_action(self, notification_id: str, action: str):
        """Handle notification action click"""
        self.logger.info(f"Action '{action}' clicked for notification {notification_id}")

        # Mark as read
        if notification_id in self.notification_widgets:
            self.notification_widgets[notification_id].mark_as_read()

        # Emit signal for action handling (can be connected by parent)
        # For now, just log
        if action == "archive":
            self._remove_notification(notification_id)

    def _remove_notification(self, notification_id: str):
        """Remove notification from UI"""
        if notification_id in self.notification_widgets:
            widget = self.notification_widgets.pop(notification_id)
            self.notifications_layout.removeWidget(widget)
            widget.deleteLater()
            self._update_ui()

    def _mark_all_read(self):
        """Mark all notifications as read"""
        for widget in self.notification_widgets.values():
            widget.mark_as_read()
        self._update_ui()

    def _clear_all(self):
        """Clear all notifications"""
        for notification_id in list(self.notification_widgets.keys()):
            self._remove_notification(notification_id)
        self.manager.history.clear()
        self._update_ui()

    def _set_filter(self, filter_type: str):
        """Set notification filter"""
        self.current_filter = filter_type
        self._apply_filter()

    def _apply_filter(self):
        """Apply current filter to notifications"""
        for widget in self.notification_widgets.values():
            visible = True

            if self.current_filter == "unread":
                visible = not widget.notification.read
            elif self.current_filter == "critical":
                visible = widget.notification.priority == NotificationPriority.CRITICAL
            elif self.current_filter in ["email", "calendar"]:
                visible = widget.notification.type.value == self.current_filter

            widget.setVisible(visible)

        self._update_ui()

    def _on_search(self, query: str):
        """Handle search query"""
        query_lower = query.lower()

        for widget in self.notification_widgets.values():
            text = f"{widget.notification.title} {widget.notification.message}".lower()
            widget.setVisible(query_lower in text)

    def _refresh_ui(self):
        """Refresh UI with latest notifications"""
        # Load recent notifications from manager
        recent = self.manager.get_recent_notifications(limit=50)

        # Add any new ones
        for notification in recent:
            if notification.id not in self.notification_widgets:
                self._add_notification(notification)

        self._update_ui()

    def _update_ui(self):
        """Update UI stats and badges"""
        # Count unread
        unread_count = sum(1 for w in self.notification_widgets.values() if not w.notification.read)

        self.unread_badge.setText(str(unread_count))
        self.unread_badge.setVisible(unread_count > 0)

        # Update stats
        total = len(self.notification_widgets)
        visible = sum(1 for w in self.notification_widgets.values() if w.isVisible())

        if total == 0:
            self.stats_label.setText("No notifications")
        else:
            self.stats_label.setText(
                f"Showing {visible} of {total} notifications • {unread_count} unread"
            )


# Demo/testing function
if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication

    from src.modules.smart_notifications import NotificationType, send_notification

    app = QApplication(sys.argv)

    # Create notification center
    center = NotificationCenter()
    center.resize(600, 800)
    center.show()

    # Send test notifications
    send_notification(
        "Test Critical",
        "This is a critical notification",
        NotificationType.SYSTEM,
        NotificationPriority.CRITICAL,
        actions=[{"label": "Acknowledge", "action": "ack"}],
    )

    send_notification(
        "New Email",
        "You have a new email from boss@company.com",
        NotificationType.EMAIL,
        NotificationPriority.HIGH,
        data={"sender": "boss@company.com"},
        actions=[
            {"label": "Reply", "action": "reply"},
            {"label": "Archive", "action": "archive"},
        ],
    )

    send_notification(
        "Calendar Reminder",
        "Meeting in 15 minutes: Team Standup",
        NotificationType.CALENDAR,
        NotificationPriority.MEDIUM,
        actions=[{"label": "Join", "action": "join"}, {"label": "Snooze", "action": "snooze"}],
    )

    sys.exit(app.exec())
