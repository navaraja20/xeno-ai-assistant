"""
Demo: API Mega-Pack
Demonstrates 20+ service integrations
"""

import asyncio
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from src.core.logger import setup_logger
from src.integrations.api_registry import get_integration_registry


class APIDemo(QMainWindow):
    """API Mega-Pack demo"""

    def __init__(self):
        super().__init__()

        self.logger = setup_logger("demo.api")
        self.registry = get_integration_registry()

        self.setWindowTitle("XENO API Mega-Pack - 20+ Integrations")
        self.setGeometry(100, 100, 1200, 800)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)

        # Title
        title = QLabel("🔌 API Mega-Pack")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ffff;")
        layout.addWidget(title)

        # Statistics
        stats_group = self._create_stats_section()
        layout.addWidget(stats_group)

        # Main content
        content_layout = QHBoxLayout()

        # Left: Integration list
        list_group = self._create_list_section()
        content_layout.addWidget(list_group, 1)

        # Right: Details
        details_group = self._create_details_section()
        content_layout.addWidget(details_group, 2)

        layout.addLayout(content_layout)

        self.logger.info("API demo initialized")

    def _create_stats_section(self) -> QGroupBox:
        """Create statistics section"""
        group = QGroupBox("Statistics")
        layout = QHBoxLayout(group)

        stats = self.registry.get_statistics()

        stats_labels = [
            f"📊 Total: {stats['total_integrations']}",
            f"💬 Communication: {stats['communication']}",
            f"📝 Productivity: {stats['productivity']}",
            f"💻 Development: {stats['development']}",
            f"📈 Marketing: {stats['marketing']}",
            f"💰 Finance: {stats['finance']}",
            f"🎵 Entertainment: {stats['entertainment']}",
            f"⚡ Automation: {stats['automation']}",
        ]

        for stat_text in stats_labels:
            label = QLabel(stat_text)
            label.setStyleSheet("color: #00ff00; font-weight: bold; font-size: 14px;")
            layout.addWidget(label)

        return group

    def _create_list_section(self) -> QGroupBox:
        """Create integration list"""
        group = QGroupBox("Available Integrations")
        layout = QVBoxLayout(group)

        # Category filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Category:"))

        self.category_filter = QComboBox()
        self.category_filter.addItem("All")
        for category in self.registry.get_categories():
            self.category_filter.addItem(category.title())
        self.category_filter.currentTextChanged.connect(self._filter_integrations)
        filter_layout.addWidget(self.category_filter)

        layout.addLayout(filter_layout)

        # Integration list
        self.integration_list = QListWidget()
        self.integration_list.itemClicked.connect(self._show_integration_details)
        layout.addWidget(self.integration_list)

        # Populate list
        self._filter_integrations("All")

        return group

    def _create_details_section(self) -> QGroupBox:
        """Create details section"""
        group = QGroupBox("Integration Details")
        layout = QVBoxLayout(group)

        self.details_browser = QTextBrowser()
        self.details_browser.setHtml(
            """
        <h2>Welcome to API Mega-Pack</h2>
        <p>Select an integration from the list to see details.</p>

        <h3>Features:</h3>
        <ul>
            <li><b>20+ Integrations</b>: Connect to popular services</li>
            <li><b>Unified API</b>: Consistent interface for all services</li>
            <li><b>Async Support</b>: Non-blocking API calls</li>
            <li><b>Auto-retry</b>: Automatic retry on failures</li>
            <li><b>Type Safety</b>: Full type hints</li>
        </ul>

        <h3>Categories:</h3>
        <ul>
            <li><b>Communication</b>: Slack, Discord, Gmail, Zoom, Calendly</li>
            <li><b>Productivity</b>: Notion, Trello, Todoist, Asana, Airtable, Jira, Google Drive, Dropbox</li>
            <li><b>Development</b>: GitHub</li>
            <li><b>Marketing</b>: Mailchimp, HubSpot, Twitter</li>
            <li><b>Finance</b>: Stripe</li>
            <li><b>Entertainment</b>: Spotify</li>
            <li><b>Automation</b>: Zapier</li>
        </ul>
        """
        )
        layout.addWidget(self.details_browser)

        return group

    def _filter_integrations(self, category: str):
        """Filter integrations by category"""
        self.integration_list.clear()

        if category == "All":
            integrations = self.registry.list_integrations()
        else:
            integrations = self.registry.list_by_category(category.lower())

        # Get icons for categories
        icons = {
            "slack": "💬",
            "discord": "🎮",
            "gmail": "📧",
            "zoom": "📹",
            "calendly": "📅",
            "notion": "📝",
            "trello": "📋",
            "todoist": "✅",
            "asana": "📊",
            "airtable": "🗂️",
            "jira": "🎫",
            "google_drive": "☁️",
            "dropbox": "📦",
            "github": "💻",
            "mailchimp": "📨",
            "hubspot": "🎯",
            "twitter": "🐦",
            "stripe": "💳",
            "spotify": "🎵",
            "zapier": "⚡",
        }

        for integration in sorted(integrations):
            icon = icons.get(integration, "🔌")
            self.integration_list.addItem(f"{icon} {integration.title()}")

    def _show_integration_details(self, item):
        """Show details for selected integration"""
        # Extract service name from item text
        service_name = item.text().split(" ", 1)[1].lower()

        try:
            integration_class = self.registry.get_integration(service_name)

            # Create instance to get properties
            instance = integration_class()

            html = f"""
            <h2>🔌 {service_name.title()}</h2>

            <h3>Service Information:</h3>
            <ul>
                <li><b>Class</b>: {integration_class.__name__}</li>
                <li><b>Module</b>: {integration_class.__module__}</li>
            </ul>

            <h3>Supported Triggers:</h3>
            <ul>
            """

            for trigger in instance.supported_triggers:
                html += f"<li>{trigger}</li>"

            html += """
            </ul>

            <h3>Supported Actions:</h3>
            <ul>
            """

            for action in instance.supported_actions:
                html += f"<li>{action}</li>"

            html += f"""
            </ul>

            <h3>Usage Example:</h3>
            <pre>
from src.integrations.api_registry import get_integration_registry

# Get integration
registry = get_integration_registry()
IntegrationClass = registry.get_integration("{service_name}")

# Create instance
integration = IntegrationClass(credentials)

# Test connection
await integration.test_connection()

# Execute action
result = await integration.execute_action(
    "{instance.supported_actions[0] if instance.supported_actions else 'action'}",
    parameters={{"param": "value"}}
)
            </pre>

            <h3>Environment Variables:</h3>
            <p>Add to your <code>.env</code> file:</p>
            <pre>
{service_name.upper()}_API_KEY=your_api_key_here
            </pre>
            """

            self.details_browser.setHtml(html)

        except Exception as e:
            self.logger.error(f"Error showing details: {e}")


def main():
    """Run API demo"""
    app = QApplication(sys.argv)

    # Dark theme
    app.setStyleSheet(
        """
        QMainWindow, QWidget {
            background: #1e1e2e;
            color: #ffffff;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #00ffff;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            color: #00ffff;
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QListWidget {
            background: #2b2d31;
            border: 1px solid #00ffff;
            border-radius: 3px;
            font-size: 14px;
        }
        QListWidget::item {
            padding: 8px;
        }
        QListWidget::item:selected {
            background: #5865F2;
        }
        QTextBrowser {
            background: #2b2d31;
            border: 1px solid #00ffff;
            padding: 10px;
        }
        QComboBox {
            background: #2b2d31;
            border: 1px solid #00ffff;
            padding: 5px;
            border-radius: 3px;
        }
    """
    )

    demo = APIDemo()
    demo.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
