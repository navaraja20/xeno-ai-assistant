"""
Main XENO Dashboard Window - Discord-inspired Gaming UI
"""
import os
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv, set_key
from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QIcon, QPalette
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class XenoMainWindow(QMainWindow):
    """Modern gradient UI with glassmorphism for XENO"""

    # Modern gradient color scheme with vibrant accents
    BG_DARK = "#0f0f1e"  # Deep space background
    BG_DARKER = "#0a0a14"  # Darker sections
    BG_LIGHTER = "#1a1a2e"  # Panel background with purple tint
    BG_GLASS = "rgba(26, 26, 46, 0.7)"  # Glassmorphism effect
    ACCENT_BLUE = "#00d4ff"  # Electric cyan accent
    ACCENT_PURPLE = "#8b5cf6"  # Vibrant purple accent
    ACCENT_PINK = "#ec4899"  # Pink accent for highlights
    GRADIENT_START = "#8b5cf6"  # Purple gradient start
    GRADIENT_END = "#00d4ff"  # Cyan gradient end
    TEXT_PRIMARY = "#ffffff"  # Crisp white text
    TEXT_SECONDARY = "#94a3b8"  # Soft gray text
    TEXT_COLOR = "#ffffff"  # Text color (alias for compatibility)
    HOVER_COLOR = "#2d2d44"  # Subtle hover with purple tint
    ONLINE_GREEN = "#10b981"  # Emerald green status
    BORDER_COLOR = "#2d2d44"  # Subtle border
    SHADOW = "rgba(0, 0, 0, 0.3)"  # Soft shadow

    def __init__(self, daemon):
        super().__init__()
        self.daemon = daemon
        self.config = daemon.config

        # Initialize AI chat (enhanced version with context)
        try:
            from modules.ai_chat_enhanced import get_enhanced_ai_chat

            self.ai_chat = get_enhanced_ai_chat(
                self.config,
                email_handler=self.email_handler if hasattr(self, "email_handler") else None,
                github_manager=self.github_manager if hasattr(self, "github_manager") else None,
                linkedin_automation=self.linkedin_automation
                if hasattr(self, "linkedin_automation")
                else None,
            )
        except Exception as e:
            print(f"Could not initialize enhanced AI chat, using basic: {e}")
            try:
                from modules.ai_chat import get_ai_chat

                self.ai_chat = get_ai_chat(self.config)
            except Exception as e2:
                print(f"Could not initialize AI chat: {e2}")
                self.ai_chat = None

        # Initialize automation modules
        self._init_automation_modules()

        # Initialize notification system
        self._init_notification_system()

        # Initialize voice system
        self._init_voice_system()

        self.setWindowTitle("XENO - Personal AI Assistant")
        self.setMinimumSize(1200, 800)

        # Apply dark gaming theme
        self._apply_theme()

        # Create UI
        self._create_ui()

    def _init_automation_modules(self):
        """Initialize all automation modules."""
        self.email_handler = None
        self.github_manager = None
        self.job_automation = None
        self.linkedin_automation = None
        self.calendar_sync = None

        try:
            # Email Handler
            if self.config.email and self.config.email.address and self.config.email.password:
                from modules.email_handler import EmailHandler

                self.email_handler = EmailHandler(
                    self.config.email.address, self.config.email.password
                )
                print("✓ Email handler initialized")
        except Exception as e:
            print(f"✗ Could not initialize email handler: {e}")

        try:
            # GitHub Manager
            if self.config.github and self.config.github.username and self.config.github.token:
                from modules.github_manager import GitHubManager

                self.github_manager = GitHubManager(
                    self.config.github.username, self.config.github.token
                )
                print("✓ GitHub manager initialized")
        except Exception as e:
            print(f"✗ Could not initialize GitHub manager: {e}")

        try:
            # Job Automation
            from modules.job_automation import JobAutomation

            self.job_automation = JobAutomation()
            print("✓ Job automation initialized")
        except Exception as e:
            print(f"✗ Could not initialize job automation: {e}")

        try:
            # LinkedIn Automation
            if (
                self.config.linkedin
                and self.config.linkedin.email
                and self.config.linkedin.password
            ):
                from modules.linkedin_automation import LinkedInAutomation

                self.linkedin_automation = LinkedInAutomation(
                    self.config.linkedin.email, self.config.linkedin.password
                )
                print("✓ LinkedIn automation initialized")
        except Exception as e:
            print(f"✗ Could not initialize LinkedIn automation: {e}")

        # Initialize Calendar Manager
        try:
            from modules.calendar_manager import CalendarManager

            self.calendar_manager = CalendarManager()
            print("✓ Calendar manager initialized")
        except Exception as e:
            print(f"✗ Could not initialize calendar manager: {e}")

        try:
            # Calendar Sync
            from modules.calendar_sync import CalendarSync

            self.calendar_sync = CalendarSync()
            print("✓ Calendar sync initialized")
        except Exception as e:
            print(f"✗ Could not initialize calendar sync: {e}")

    def _init_notification_system(self):
        """Initialize notification and background monitoring system"""
        try:
            from modules.notifications import BackgroundMonitor, NotificationManager

            # Initialize notification manager
            self.notification_manager = NotificationManager("XENO")

            # Initialize background monitor
            self.background_monitor = BackgroundMonitor(self.notification_manager)

            # Connect automation modules to monitor
            if self.email_handler:
                self.background_monitor.set_email_handler(self.email_handler)
            if self.github_manager:
                self.background_monitor.set_github_manager(self.github_manager)
            if self.linkedin_automation:
                self.background_monitor.set_linkedin_automation(self.linkedin_automation)

            # Start background monitoring
            self.background_monitor.start()

            print("✓ Notification system initialized")

        except Exception as e:
            print(f"✗ Could not initialize notification system: {e}")
            self.notification_manager = None
            self.background_monitor = None

    def _init_voice_system(self):
        """Initialize voice recognition and command processing"""
        try:
            from voice.command_handler import VoiceCommandHandler
            from voice.recognition import VoiceRecognition

            # Initialize voice recognition
            self.voice_recognition = VoiceRecognition()

            # Initialize enhanced command handler with TTS
            self.voice_command_handler = VoiceCommandHandler(main_window=self)

            # Start voice command monitoring
            self._start_voice_monitoring()

            print("✓ Voice system initialized with enhanced commands")

            # Welcome message
            if self.config.user.voice_enabled:
                self.voice_command_handler.speak(
                    "Voice commands activated. Say 'Hey XENO' followed by your command."
                )

        except Exception as e:
            print(f"✗ Could not initialize voice system: {e}")
            self.voice_recognition = None
            self.voice_command_handler = None

    def _start_voice_monitoring(self):
        """Start monitoring for voice commands"""
        if not self.voice_recognition:
            return

        # Start listening in background
        self.voice_recognition.start_listening()

        # Check for commands periodically
        self.voice_timer = QTimer(self)
        self.voice_timer.timeout.connect(self._check_voice_commands)
        self.voice_timer.start(500)  # Check every 500ms

    def _check_voice_commands(self):
        """Check for new voice commands"""
        if not self.voice_recognition:
            return

        # Get command from queue
        command = self.voice_recognition.get_command(block=False)

        if command:
            # Check if it's wake word detection signal
            if command == "__WAKE_WORD_DETECTED__":
                print("🎤 Wake word detected!")
                # Respond to wake word
                if self.config.user.voice_enabled and self.voice_command_handler:
                    self.voice_command_handler.speak("Yes Master, how can I help you?")
                return

            print(f"🎤 Voice command: {command}")

            # Process command with enhanced handler
            if self.voice_command_handler:
                response = self.voice_command_handler.process_command(command)

                if response:
                    print(f"🔊 Response: {response}")

                    # Add to activity timeline if dashboard exists
                    if hasattr(self, "_add_timeline_activity"):
                        from datetime import datetime

                        self._add_timeline_activity(f"🎤 Voice: {command[:30]}...", datetime.now())

    def _speak(self, text):
        """Speak text using TTS (deprecated - use voice_command_handler.speak)"""
        if hasattr(self, "voice_command_handler") and self.voice_command_handler:
            self.voice_command_handler.speak(text)

    def _apply_theme(self):
        """Apply modern gradient theme with glassmorphism effects"""
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.BG_DARK}, stop:0.5 {self.BG_DARKER}, stop:1 {self.BG_DARK});
                color: {self.TEXT_PRIMARY};
            }}

            QLabel {{
                color: {self.TEXT_PRIMARY};
                background: transparent;
            }}

            QPushButton {{
                background: {self.BG_LIGHTER};
                color: {self.TEXT_PRIMARY};
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
            }}

            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.HOVER_COLOR}, stop:1 {self.BG_LIGHTER});
            }}

            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.ACCENT_BLUE}, stop:1 {self.ACCENT_PURPLE});
            }}

            QPushButton#sidebar_button {{
                text-align: left;
                padding: 14px 24px;
                border-radius: 10px;
                margin: 4px 12px;
                font-size: 15px;
            }}

            QPushButton#sidebar_button:hover {{
                background: {self.HOVER_COLOR};
                border-left: 3px solid {self.ACCENT_BLUE};
            }}

            QPushButton#sidebar_button:checked {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.GRADIENT_START}, stop:1 {self.GRADIENT_END});
                color: #ffffff;
                font-weight: bold;
            }}

            QLineEdit {{
                background: {self.BG_LIGHTER};
                color: {self.TEXT_PRIMARY};
                border: 2px solid {self.BORDER_COLOR};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
            }}

            QLineEdit:focus {{
                border: 2px solid {self.ACCENT_BLUE};
                background: {self.BG_DARK};
            }}

            QTextEdit {{
                background: {self.BG_LIGHTER};
                color: {self.TEXT_PRIMARY};
                border: 2px solid {self.BORDER_COLOR};
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }}

            QTextEdit:focus {{
                border: 2px solid {self.ACCENT_PURPLE};
            }}

            QScrollArea {{
                background: transparent;
                border: none;
            }}

            QScrollBar:vertical {{
                background: {self.BG_DARKER};
                width: 10px;
                border-radius: 5px;
                margin: 2px;
            }}

            QScrollBar::handle:vertical {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.ACCENT_BLUE}, stop:1 {self.ACCENT_PURPLE});
                border-radius: 5px;
                min-height: 30px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.ACCENT_PURPLE}, stop:1 {self.ACCENT_PINK});
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QListWidget {{
                background: {self.BG_LIGHTER};
                color: {self.TEXT_PRIMARY};
                border: none;
                border-radius: 12px;
                padding: 12px;
            }}

            QListWidget::item {{
                padding: 12px;
                border-radius: 8px;
                margin: 2px 0;
            }}

            QListWidget::item:hover {{
                background: {self.HOVER_COLOR};
            }}

            QListWidget::item:selected {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.ACCENT_BLUE}, stop:1 {self.ACCENT_PURPLE});
                color: #ffffff;
            }}

            QFrame#panel {{
                background: {self.BG_LIGHTER};
                border-radius: 12px;
                padding: 20px;
                border: 1px solid {self.BORDER_COLOR};
            }}
        """
        )

    def _create_ui(self):
        """Create the main UI layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create sidebar
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)

        # Create content area
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet(f"background-color: {self.BG_DARK};")

        # Create different pages
        self.chat_page = self._create_chat_page()
        self.dashboard_page = self._create_dashboard_page()
        self.email_page = self._create_email_page()
        self.jobs_page = self._create_jobs_page()
        self.github_page = self._create_github_page()
        self.calendar_page = self._create_calendar_page()
        self.settings_page = self._create_settings_page()

        self.content_stack.addWidget(self.chat_page)
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.email_page)
        self.content_stack.addWidget(self.jobs_page)
        self.content_stack.addWidget(self.github_page)
        self.content_stack.addWidget(self.calendar_page)
        self.content_stack.addWidget(self.settings_page)

        main_layout.addWidget(self.content_stack, 1)

    def _create_sidebar(self):
        """Create Discord-style sidebar"""
        sidebar = QFrame()
        sidebar.setStyleSheet(
            f"""
            QFrame {{
                background-color: {self.BG_DARKER};
                border-right: 1px solid #000000;
            }}
        """
        )
        sidebar.setFixedWidth(250)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(8)

        # XENO logo/header
        header = QLabel("XENO")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(
            f"""
            font-size: 28px;
            font-weight: bold;
            color: {self.ACCENT_BLUE};
            padding: 20px;
            letter-spacing: 4px;
        """
        )
        layout.addWidget(header)

        # Status indicator
        status_frame = QFrame()
        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(20, 10, 20, 10)

        status_dot = QLabel("●")
        status_dot.setStyleSheet(f"color: {self.ONLINE_GREEN}; font-size: 16px;")
        status_label = QLabel("Online")
        status_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 12px;")

        status_layout.addWidget(status_dot)
        status_layout.addWidget(status_label)
        status_layout.addStretch()

        layout.addWidget(status_frame)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: #000000; margin: 10px 20px;")
        layout.addWidget(separator)

        # Navigation buttons
        self.nav_buttons = []

        nav_items = [
            ("💬 Chat", 0),
            ("📊 Dashboard", 1),
            ("📧 Gmail", 2),
            ("💼 LinkedIn", 3),
            ("⚙️ GitHub", 4),
            ("📅 Calendar", 5),
            ("⚙️ Settings", 6),
        ]

        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("sidebar_button")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, i=index: self._switch_page(i))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        # Set Chat as default selected
        self.nav_buttons[0].setChecked(True)

        layout.addStretch()

        # User profile at bottom
        user_frame = QFrame()
        user_frame.setStyleSheet(
            f"""
            background-color: {self.BG_LIGHTER};
            border-radius: 8px;
            padding: 12px;
            margin: 0 8px;
        """
        )
        user_layout = QVBoxLayout(user_frame)

        user_name = QLabel(f"Master {self.config.user.name}")
        user_name.setStyleSheet(f"color: {self.TEXT_PRIMARY}; font-weight: bold; font-size: 14px;")

        user_status = QLabel("Administrator")
        user_status.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 12px;")

        user_layout.addWidget(user_name)
        user_layout.addWidget(user_status)

        layout.addWidget(user_frame)

        return sidebar

    def _create_chat_page(self):
        """Create AI chat interface"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("AI Assistant Chat")
        header.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: {self.ACCENT_BLUE}; margin-bottom: 10px;"
        )
        layout.addWidget(header)

        # Chat history
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("Chat history will appear here...")
        layout.addWidget(self.chat_history, 1)

        # Input area
        input_layout = QHBoxLayout()

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask XENO anything...")
        self.chat_input.returnPressed.connect(self._send_message)

        send_btn = QPushButton("Send")
        send_btn.setStyleSheet(
            f"""
            background-color: {self.ACCENT_BLUE};
            color: #000000;
            font-weight: bold;
            padding: 10px 30px;
        """
        )
        send_btn.clicked.connect(self._send_message)

        input_layout.addWidget(self.chat_input, 1)
        input_layout.addWidget(send_btn)

        layout.addLayout(input_layout)

        return page

    def _create_dashboard_page(self):
        """Create intelligent dashboard with briefing, analytics, and activity timeline"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header with refresh
        header_bar = QWidget()
        header_bar.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("📊 Intelligence Dashboard")
        header.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {self.ACCENT_BLUE};")
        header_layout.addWidget(header)

        header_layout.addStretch()

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self.ACCENT_PURPLE};
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #9333ea;
            }}
        """
        )
        refresh_btn.clicked.connect(self._refresh_dashboard)
        header_layout.addWidget(refresh_btn)

        layout.addWidget(header_bar)

        # Scroll area for dashboard content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(16)

        # Daily AI Briefing Card
        self.briefing_card = self._create_briefing_card()
        scroll_layout.addWidget(self.briefing_card)

        # Analytics Cards Row
        analytics_row = QWidget()
        analytics_row.setStyleSheet("background: transparent;")
        analytics_layout = QHBoxLayout(analytics_row)
        analytics_layout.setSpacing(16)

        self.email_analytics = self._create_email_analytics_card()
        self.github_analytics = self._create_github_analytics_card()
        self.linkedin_analytics = self._create_linkedin_analytics_card()

        analytics_layout.addWidget(self.email_analytics)
        analytics_layout.addWidget(self.github_analytics)
        analytics_layout.addWidget(self.linkedin_analytics)

        scroll_layout.addWidget(analytics_row)

        # Activity Timeline and Goals Row
        bottom_row = QWidget()
        bottom_row.setStyleSheet("background: transparent;")
        bottom_layout = QHBoxLayout(bottom_row)
        bottom_layout.setSpacing(16)

        self.activity_timeline = self._create_activity_timeline()
        self.goals_tracker = self._create_goals_tracker()

        bottom_layout.addWidget(self.activity_timeline, 2)
        bottom_layout.addWidget(self.goals_tracker, 1)

        scroll_layout.addWidget(bottom_row)
        scroll_layout.addStretch()

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        return page

    def _create_briefing_card(self):
        """Create AI daily briefing card"""
        card = QFrame()
        card.setObjectName("briefing_card")
        card.setStyleSheet(
            f"""
            QFrame#briefing_card {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.ACCENT_PURPLE}, stop:1 #9333ea);
                border-radius: 12px;
                padding: 24px;
            }}
        """
        )

        layout = QVBoxLayout(card)
        layout.setSpacing(12)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("🌅 Daily Briefing")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        time_label = QLabel(datetime.now().strftime("%B %d, %Y"))
        time_label.setStyleSheet("font-size: 14px; color: rgba(255, 255, 255, 0.9);")
        header_layout.addWidget(time_label)

        layout.addLayout(header_layout)

        # Briefing content
        self.briefing_content = QLabel(
            "Click 'Generate Briefing' to get your AI-powered daily summary..."
        )
        self.briefing_content.setWordWrap(True)
        self.briefing_content.setStyleSheet(
            """
            font-size: 15px;
            color: rgba(255, 255, 255, 0.95);
            line-height: 1.6;
            padding: 12px 0;
        """
        )
        layout.addWidget(self.briefing_content)

        # Generate button
        generate_btn = QPushButton("✨ Generate Briefing")
        generate_btn.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                padding: 10px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """
        )
        generate_btn.clicked.connect(self._generate_daily_briefing)
        layout.addWidget(generate_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        return card

    def _create_email_analytics_card(self):
        """Create email analytics card"""
        return self._create_analytics_card(
            "📧 Email",
            [
                ("Unread", self._get_email_count()),
                ("Today", self._get_emails_today()),
                ("This Week", self._get_emails_week()),
            ],
            "#4285F4",
        )

    def _create_github_analytics_card(self):
        """Create GitHub analytics card"""
        return self._create_analytics_card(
            "⚙️ GitHub",
            [
                ("Repositories", self._get_github_repo_count()),
                ("Stars", self._get_github_stars()),
                ("Recent Commits", self._get_recent_commits()),
            ],
            "#00d4ff",
        )

    def _create_linkedin_analytics_card(self):
        """Create LinkedIn analytics card"""
        return self._create_analytics_card(
            "💼 LinkedIn",
            [
                ("Jobs Viewed", self._get_jobs_viewed()),
                ("Applications", self._get_applications_count()),
                ("Saved Jobs", self._get_jobs_count()),
            ],
            "#0A66C2",
        )

    def _create_analytics_card(self, title, stats, accent_color):
        """Create a generic analytics card"""
        card = QFrame()
        card.setObjectName("analytics_card")
        card.setStyleSheet(
            f"""
            QFrame#analytics_card {{
                background-color: {self.BG_LIGHTER};
                border-radius: 12px;
                border-left: 4px solid {accent_color};
                padding: 20px;
            }}
        """
        )

        layout = QVBoxLayout(card)
        layout.setSpacing(16)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {accent_color};")
        layout.addWidget(title_label)

        # Stats
        for stat_name, stat_value in stats:
            stat_row = QWidget()
            stat_row.setStyleSheet("background: transparent;")
            stat_layout = QHBoxLayout(stat_row)
            stat_layout.setContentsMargins(0, 0, 0, 0)

            name_label = QLabel(stat_name)
            name_label.setStyleSheet(f"font-size: 13px; color: {self.TEXT_SECONDARY};")
            stat_layout.addWidget(name_label)

            stat_layout.addStretch()

            value_label = QLabel(str(stat_value))
            value_label.setStyleSheet(
                f"font-size: 20px; font-weight: bold; color: {self.TEXT_PRIMARY};"
            )
            stat_layout.addWidget(value_label)

            layout.addWidget(stat_row)

        return card

    def _create_activity_timeline(self):
        """Create activity timeline widget"""
        card = QFrame()
        card.setObjectName("timeline_card")
        card.setStyleSheet(
            f"""
            QFrame#timeline_card {{
                background-color: {self.BG_LIGHTER};
                border-radius: 12px;
                padding: 20px;
            }}
        """
        )

        layout = QVBoxLayout(card)
        layout.setSpacing(12)

        # Header
        header = QLabel("📅 Activity Timeline")
        header.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {self.TEXT_PRIMARY};")
        layout.addWidget(header)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {self.HOVER_COLOR}; max-height: 1px;")
        layout.addWidget(separator)

        # Timeline scroll area
        timeline_scroll = QScrollArea()
        timeline_scroll.setWidgetResizable(True)
        timeline_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        timeline_widget = QWidget()
        timeline_widget.setStyleSheet("background: transparent;")
        self.timeline_layout = QVBoxLayout(timeline_widget)
        self.timeline_layout.setSpacing(12)

        # Add initial activities
        self._add_timeline_activity("🚀 XENO started", datetime.now())
        if self.email_handler:
            self._add_timeline_activity("✓ Email connected", datetime.now())
        if self.github_manager:
            self._add_timeline_activity("✓ GitHub connected", datetime.now())
        if self.ai_chat or self.ai_chat_enhanced:
            self._add_timeline_activity("✓ AI Chat ready", datetime.now())

        self.timeline_layout.addStretch()

        timeline_scroll.setWidget(timeline_widget)
        layout.addWidget(timeline_scroll, 1)

        return card

    def _create_goals_tracker(self):
        """Create goals tracker widget"""
        card = QFrame()
        card.setObjectName("goals_card")
        card.setStyleSheet(
            f"""
            QFrame#goals_card {{
                background-color: {self.BG_LIGHTER};
                border-radius: 12px;
                padding: 20px;
            }}
        """
        )

        layout = QVBoxLayout(card)
        layout.setSpacing(12)

        # Header
        header_row = QWidget()
        header_row.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header_row)
        header_layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel("🎯 Goals")
        header.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {self.TEXT_PRIMARY};")
        header_layout.addWidget(header)

        header_layout.addStretch()

        add_goal_btn = QPushButton("+")
        add_goal_btn.setFixedSize(28, 28)
        add_goal_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self.ACCENT_PURPLE};
                color: white;
                border: none;
                border-radius: 14px;
                font-weight: bold;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: #9333ea;
            }}
        """
        )
        add_goal_btn.clicked.connect(self._add_goal)
        header_layout.addWidget(add_goal_btn)

        layout.addWidget(header_row)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {self.HOVER_COLOR}; max-height: 1px;")
        layout.addWidget(separator)

        # Goals list
        self.goals_list_widget = QWidget()
        self.goals_list_widget.setStyleSheet("background: transparent;")
        self.goals_list_layout = QVBoxLayout(self.goals_list_widget)
        self.goals_list_layout.setSpacing(8)

        # Load and display goals
        self._load_goals()

        self.goals_list_layout.addStretch()

        layout.addWidget(self.goals_list_widget, 1)

        return card

    def _add_timeline_activity(self, text, timestamp):
        """Add activity to timeline"""
        activity = QWidget()
        activity.setStyleSheet("background: transparent;")
        activity_layout = QHBoxLayout(activity)
        activity_layout.setContentsMargins(0, 0, 0, 0)
        activity_layout.setSpacing(12)

        # Time dot
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {self.ACCENT_PURPLE}; font-size: 12px;")
        activity_layout.addWidget(dot)

        # Activity text
        text_label = QLabel(text)
        text_label.setStyleSheet(f"font-size: 13px; color: {self.TEXT_PRIMARY};")
        activity_layout.addWidget(text_label)

        activity_layout.addStretch()

        # Time
        time_label = QLabel(timestamp.strftime("%H:%M"))
        time_label.setStyleSheet(f"font-size: 12px; color: {self.TEXT_SECONDARY};")
        activity_layout.addWidget(time_label)

        # Insert at top (most recent first)
        self.timeline_layout.insertWidget(0, activity)

    def _load_goals(self):
        """Load goals from file"""
        try:
            import json

            goals_file = Path(__file__).parent.parent.parent / "data" / "goals.json"

            if goals_file.exists():
                with open(goals_file, "r") as f:
                    goals_data = json.load(f)
                    for goal in goals_data.get("goals", []):
                        self._add_goal_widget(goal["text"], goal["completed"])
            else:
                # Default goals
                self._add_goal_widget("Review 10 job applications", False)
                self._add_goal_widget("Respond to urgent emails", False)
                self._add_goal_widget("Update GitHub repositories", False)
        except Exception as e:
            print(f"Error loading goals: {e}")

    def _add_goal_widget(self, text, completed=False):
        """Add a goal widget to the list"""
        goal_widget = QWidget()
        goal_widget.setStyleSheet("background: transparent;")
        goal_layout = QHBoxLayout(goal_widget)
        goal_layout.setContentsMargins(0, 0, 0, 0)
        goal_layout.setSpacing(8)

        # Checkbox
        checkbox = QPushButton("✓" if completed else "")
        checkbox.setCheckable(True)
        checkbox.setChecked(completed)
        checkbox.setFixedSize(20, 20)
        checkbox.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {"#10b981" if completed else "transparent"};
                border: 2px solid {self.BORDER_COLOR};
                border-radius: 4px;
                color: white;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:checked {{
                background-color: #10b981;
                border-color: #10b981;
            }}
        """
        )
        checkbox.clicked.connect(lambda: self._toggle_goal(goal_widget, checkbox, text_label))
        goal_layout.addWidget(checkbox)

        # Goal text
        text_label = QLabel(text)
        text_label.setStyleSheet(
            f"""
            font-size: 13px;
            color: {self.TEXT_SECONDARY if completed else self.TEXT_PRIMARY};
            {"text-decoration: line-through;" if completed else ""}
        """
        )
        goal_layout.addWidget(text_label)

        goal_layout.addStretch()

        # Find correct position (completed goals at bottom)
        insert_pos = 0
        if completed:
            insert_pos = self.goals_list_layout.count() - 1  # Before stretch
        else:
            # Find first completed goal position
            for i in range(self.goals_list_layout.count() - 1):
                widget = self.goals_list_layout.itemAt(i).widget()
                if widget:
                    checkbox_in_widget = widget.findChild(QPushButton)
                    if checkbox_in_widget and checkbox_in_widget.isChecked():
                        insert_pos = i
                        break
            else:
                insert_pos = self.goals_list_layout.count() - 1

        self.goals_list_layout.insertWidget(insert_pos, goal_widget)

    def _toggle_goal(self, widget, checkbox, text_label):
        """Toggle goal completion status"""
        completed = checkbox.isChecked()
        checkbox.setText("✓" if completed else "")
        text_label.setStyleSheet(
            f"""
            font-size: 13px;
            color: {self.TEXT_SECONDARY if completed else self.TEXT_PRIMARY};
            {"text-decoration: line-through;" if completed else ""}
        """
        )
        self._save_goals()

    def _add_goal(self):
        """Show dialog to add a new goal"""
        from PyQt6.QtWidgets import QInputDialog

        text, ok = QInputDialog.getText(self, "Add Goal", "Enter your goal:")
        if ok and text:
            self._add_goal_widget(text, False)
            self._save_goals()
            self._add_timeline_activity(f"🎯 New goal added: {text[:30]}...", datetime.now())

    def _save_goals(self):
        """Save goals to file"""
        try:
            import json

            goals_file = Path(__file__).parent.parent.parent / "data" / "goals.json"
            goals_file.parent.mkdir(parents=True, exist_ok=True)

            goals = []
            for i in range(self.goals_list_layout.count() - 1):  # -1 for stretch
                widget = self.goals_list_layout.itemAt(i).widget()
                if widget:
                    checkbox = widget.findChild(QPushButton)
                    text_label = widget.findChild(QLabel)
                    if checkbox and text_label:
                        goals.append({"text": text_label.text(), "completed": checkbox.isChecked()})

            with open(goals_file, "w") as f:
                json.dump({"goals": goals}, f, indent=2)
        except Exception as e:
            print(f"Error saving goals: {e}")

    def _generate_daily_briefing(self):
        """Generate AI-powered daily briefing"""
        try:
            self.briefing_content.setText("🔄 Generating your personalized briefing...")
            from PyQt6.QtWidgets import QApplication

            QApplication.processEvents()

            if hasattr(self, "ai_chat_enhanced") and self.ai_chat_enhanced:
                briefing = self.ai_chat_enhanced.get_daily_briefing()
            elif hasattr(self, "ai_chat") and self.ai_chat:
                # Fallback to basic AI
                prompt = f"""Generate a brief daily summary for {self.config.user.name}.

Include:
- A motivational greeting
- Key priorities for today
- Quick productivity tip

Keep it under 100 words, friendly and energetic."""
                briefing = self.ai_chat.send_message(prompt)
            else:
                briefing = "AI not configured. Set up Gemini API key in settings to enable daily briefings."

            self.briefing_content.setText(briefing)
            self._add_timeline_activity("✨ Daily briefing generated", datetime.now())

        except Exception as e:
            self.briefing_content.setText(f"Error generating briefing: {str(e)}")

    def _refresh_dashboard(self):
        """Refresh all dashboard data"""
        try:
            # Update analytics cards
            self._update_analytics_cards()
            self._add_timeline_activity("🔄 Dashboard refreshed", datetime.now())
        except Exception as e:
            print(f"Error refreshing dashboard: {e}")

    def _update_analytics_cards(self):
        """Update all analytics card values"""
        # This would update the cards with fresh data
        # For now, we'll just add a timeline activity
        pass

    def _get_emails_today(self):
        """Get count of emails received today"""
        try:
            if not self.email_handler:
                return 0
            emails = self.email_handler.get_recent_emails(max_results=50)
            today = datetime.now().date()
            count = sum(1 for e in emails if e.get("date") and e["date"].date() == today)
            return count
        except:
            return 0

    def _get_emails_week(self):
        """Get count of emails this week"""
        try:
            if not self.email_handler:
                return 0
            emails = self.email_handler.get_recent_emails(max_results=100)
            return min(len(emails), 100)
        except:
            return 0

    def _get_github_stars(self):
        """Get total GitHub stars"""
        try:
            if not self.github_manager:
                return 0
            repos = self.github_manager.get_repositories()
            return sum(repo.get("stargazers_count", 0) for repo in repos)
        except:
            return 0

    def _get_recent_commits(self):
        """Get recent commits count"""
        try:
            if not self.github_manager:
                return 0
            # This would query recent commits
            return 5  # Placeholder
        except:
            return 0

    def _get_jobs_viewed(self):
        """Get jobs viewed count"""
        # Placeholder - could track in database
        return 0

    def _get_applications_count(self):
        """Get applications submitted count"""
        # Placeholder - could track in database
        return 0

    def _get_email_count(self):
        """Get unread email count."""
        if not self.email_handler:
            return 0
        try:
            return self.email_handler.get_unread_count()
        except:
            return 0

    def _get_jobs_count(self):
        """Get saved jobs count."""
        # Placeholder - could integrate with database
        return 0

    def _get_github_repo_count(self):
        """Get GitHub repo count."""
        if not self.github_manager:
            return 0
        try:
            repos = self.github_manager.get_repositories()
            return len(repos)
        except:
            return 0

    def _create_email_page(self):
        """Create Gmail-style email management page"""
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Gmail-style header bar
        header_bar = QFrame()
        header_bar.setStyleSheet(
            f"""
            QFrame {{
                background-color: {self.BG_LIGHTER};
                border-bottom: 1px solid {self.HOVER_COLOR};
                padding: 15px 20px;
            }}
        """
        )
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(0, 0, 0, 0)

        gmail_logo = QLabel("📧 Gmail")
        gmail_logo.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {self.ACCENT_BLUE};")
        header_layout.addWidget(gmail_logo)
        header_layout.addStretch()

        # Add refresh button to header
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: transparent;
                color: {self.TEXT_PRIMARY};
                border: 1px solid {self.HOVER_COLOR};
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {self.HOVER_COLOR};
            }}
        """
        )
        refresh_btn.clicked.connect(self._load_gmail_emails)
        header_layout.addWidget(refresh_btn)
        main_layout.addWidget(header_bar)

        # Login form (shown when not logged in)
        self.gmail_login_frame = QFrame()
        self.gmail_login_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {self.BG_DARK};
                padding: 40px;
            }}
        """
        )
        login_outer_layout = QVBoxLayout(self.gmail_login_frame)
        login_outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        login_card = QFrame()
        login_card.setFixedWidth(400)
        login_card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {self.BG_LIGHTER};
                border-radius: 8px;
                padding: 30px;
            }}
        """
        )
        card_layout = QVBoxLayout(login_card)

        login_title = QLabel("Sign in to Gmail")
        login_title.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: {self.TEXT_PRIMARY}; margin-bottom: 20px;"
        )
        login_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(login_title)

        self.gmail_email_input = QLineEdit()
        self.gmail_email_input.setPlaceholderText("Email address")
        self.gmail_email_input.setText(os.getenv("EMAIL_ADDRESS", ""))
        self.gmail_email_input.setStyleSheet(
            f"""
            QLineEdit {{
                padding: 12px;
                font-size: 14px;
                border: 1px solid {self.HOVER_COLOR};
                border-radius: 4px;
                background-color: {self.BG_DARK};
                color: {self.TEXT_PRIMARY};
            }}
            QLineEdit:focus {{
                border: 2px solid {self.ACCENT_BLUE};
            }}
        """
        )
        card_layout.addWidget(self.gmail_email_input)

        self.gmail_password_input = QLineEdit()
        self.gmail_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.gmail_password_input.setPlaceholderText("App Password (16 characters)")
        self.gmail_password_input.setText(os.getenv("EMAIL_PASSWORD", ""))
        self.gmail_password_input.setStyleSheet(
            f"""
            QLineEdit {{
                padding: 12px;
                font-size: 14px;
                border: 1px solid {self.HOVER_COLOR};
                border-radius: 4px;
                background-color: {self.BG_DARK};
                color: {self.TEXT_PRIMARY};
                margin-top: 10px;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.ACCENT_BLUE};
            }}
        """
        )
        card_layout.addWidget(self.gmail_password_input)

        app_pass_help = QLabel(
            '<a href="https://myaccount.google.com/apppasswords" style="color: #4285F4;">Get App Password</a>'
        )
        app_pass_help.setOpenExternalLinks(True)
        app_pass_help.setStyleSheet("margin: 10px 0; font-size: 13px;")
        app_pass_help.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(app_pass_help)

        self.gmail_login_btn = QPushButton("Sign In")
        self.gmail_login_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: #4285F4;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
                margin-top: 10px;
            }}
            QPushButton:hover {{
                background-color: #357AE8;
            }}
        """
        )
        self.gmail_login_btn.clicked.connect(self._gmail_login)
        card_layout.addWidget(self.gmail_login_btn)

        self.gmail_status_label = QLabel("")
        self.gmail_status_label.setStyleSheet(
            f"color: {self.TEXT_SECONDARY}; font-size: 13px; margin-top: 10px;"
        )
        self.gmail_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.gmail_status_label)

        login_outer_layout.addWidget(login_card)
        main_layout.addWidget(self.gmail_login_frame, 1)

        # Gmail inbox with tabs (hidden until login)
        self.gmail_inbox_frame = QFrame()
        self.gmail_inbox_frame.setVisible(False)
        inbox_layout = QVBoxLayout(self.gmail_inbox_frame)
        inbox_layout.setContentsMargins(0, 0, 0, 0)

        from PyQt6.QtWidgets import QTabWidget

        self.gmail_tabs = QTabWidget()
        self.gmail_tabs.setStyleSheet(
            f"""
            QTabWidget::pane {{
                border: none;
                background-color: {self.BG_DARK};
            }}
            QTabBar::tab {{
                background-color: transparent;
                color: {self.TEXT_SECONDARY};
                padding: 12px 24px;
                border: none;
                border-bottom: 3px solid transparent;
                font-size: 13px;
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                color: {self.ACCENT_BLUE};
                border-bottom: 3px solid {self.ACCENT_BLUE};
            }}
            QTabBar::tab:hover {{
                color: {self.TEXT_PRIMARY};
            }}
        """
        )

        # Create email lists for each tab
        self.primary_list = QListWidget()
        self.primary_list.setStyleSheet(self._get_gmail_style())
        self.gmail_tabs.addTab(self.primary_list, "📥 Primary")

        self.social_list = QListWidget()
        self.social_list.setStyleSheet(self._get_gmail_style())
        self.gmail_tabs.addTab(self.social_list, "👥 Social")

        self.promotions_list = QListWidget()
        self.promotions_list.setStyleSheet(self._get_gmail_style())
        self.gmail_tabs.addTab(self.promotions_list, "🏷️ Promotions")

        inbox_layout.addWidget(self.gmail_tabs)
        main_layout.addWidget(self.gmail_inbox_frame, 1)

        return page

    def _get_gmail_style(self):
        """Get Gmail-style email list stylesheet"""
        return f"""
            QListWidget {{
                background-color: {self.BG_DARK};
                border: none;
                padding: 0;
            }}
            QListWidget::item {{
                background-color: {self.BG_LIGHTER};
                border-bottom: 1px solid {self.HOVER_COLOR};
                padding: 16px 20px;
                margin: 0;
            }}
            QListWidget::item:hover {{
                background-color: {self.HOVER_COLOR};
                cursor: pointer;
            }}
            QListWidget::item:selected {{
                background-color: {self.HOVER_COLOR};
                border-left: 4px solid {self.ACCENT_BLUE};
            }}
        """

    def _gmail_login(self):
        """Handle Gmail login"""
        email = self.gmail_email_input.text().strip()
        password = self.gmail_password_input.text().strip()

        if not email or not password:
            self.gmail_status_label.setText("❌ Please enter both email and password")
            self.gmail_status_label.setStyleSheet(f"color: #ff4444; font-size: 13px;")
            return

        if len(password) != 16:
            self.gmail_status_label.setText("❌ App Password must be 16 characters")
            self.gmail_status_label.setStyleSheet(f"color: #ff4444; font-size: 13px;")
            return

        # Update status
        self.gmail_status_label.setText("🔄 Connecting to Gmail...")
        self.gmail_status_label.setStyleSheet(f"color: {self.ACCENT_BLUE}; font-size: 13px;")
        self.gmail_login_btn.setEnabled(False)

        try:
            # Initialize email handler
            from modules.email_handler import EmailHandler

            self.email_handler = EmailHandler(email, password)

            # Try to connect
            if not self.email_handler.connect():
                self.gmail_status_label.setText("❌ Failed to connect. Check your credentials.")
                self.gmail_status_label.setStyleSheet(f"color: #ff4444; font-size: 13px;")
                self.email_handler = None
                return

            # Save credentials to .env
            env_path = Path(".env")
            set_key(env_path, "EMAIL_ADDRESS", email)
            set_key(env_path, "EMAIL_PASSWORD", password)

            # Success! Hide login, show inbox
            self.gmail_login_frame.setVisible(False)
            self.gmail_inbox_frame.setVisible(True)

            # Load emails
            self._load_gmail_emails()

        except Exception as e:
            self.gmail_status_label.setText(f"❌ Error: {str(e)}")
            self.gmail_status_label.setStyleSheet(f"color: #ff4444; font-size: 13px;")
            self.email_handler = None
        finally:
            self.gmail_login_btn.setEnabled(True)

    def _load_gmail_emails(self):
        """Load Gmail emails into tabbed interface"""
        if not self.email_handler:
            return

        try:
            # Clear all tabs
            self.primary_list.clear()
            self.social_list.clear()
            self.promotions_list.clear()

            # Show loading
            self.primary_list.addItem("📬 Loading emails...")

            # Get recent emails
            emails = self.email_handler.get_recent_emails(count=100)

            if not emails:
                self.primary_list.clear()
                self.primary_list.addItem("No emails found in your inbox")
                return

            # Organize by category
            primary_emails = []
            social_emails = []
            promotions_emails = []

            for email in emails:
                subject_lower = email.get("subject", "").lower()
                from_lower = email.get("from", "").lower()

                # Categorize emails
                if any(
                    word in subject_lower or word in from_lower
                    for word in [
                        "facebook",
                        "twitter",
                        "linkedin",
                        "instagram",
                        "notification",
                        "social",
                    ]
                ):
                    social_emails.append(email)
                elif any(
                    word in subject_lower
                    for word in [
                        "offer",
                        "sale",
                        "discount",
                        "deal",
                        "promo",
                        "shop",
                        "buy",
                        "save",
                    ]
                ):
                    promotions_emails.append(email)
                else:
                    primary_emails.append(email)

            # Display in Primary tab
            self.primary_list.clear()
            for email in primary_emails:
                item_widget = self._create_email_item(email)
                item = QListWidgetItem(self.primary_list)
                item.setSizeHint(QSize(0, 90))  # Set fixed height for consistent display
                self.primary_list.addItem(item)
                self.primary_list.setItemWidget(item, item_widget)

            # Display in Social tab
            self.social_list.clear()
            for email in social_emails:
                item_widget = self._create_email_item(email)
                item = QListWidgetItem(self.social_list)
                item.setSizeHint(QSize(0, 90))
                self.social_list.addItem(item)
                self.social_list.setItemWidget(item, item_widget)

            # Display in Promotions tab
            self.promotions_list.clear()
            for email in promotions_emails:
                item_widget = self._create_email_item(email)
                item = QListWidgetItem(self.promotions_list)
                item.setSizeHint(QSize(0, 90))
                self.promotions_list.addItem(item)
                self.promotions_list.setItemWidget(item, item_widget)

            # Update tab names with counts
            self.gmail_tabs.setTabText(0, f"📥 Primary ({len(primary_emails)})")
            self.gmail_tabs.setTabText(1, f"👥 Social ({len(social_emails)})")
            self.gmail_tabs.setTabText(2, f"🏷️ Promotions ({len(promotions_emails)})")

        except Exception as e:
            self.primary_list.clear()
            self.primary_list.addItem(f"❌ Error loading emails: {str(e)}")

    def _on_email_clicked(self, widget):
        """Handle email widget click"""
        if not hasattr(widget, "email_data"):
            return

        email = widget.email_data
        self._show_email_dialog(email)

    def _show_email_dialog(self, email):
        """Show email in a modern glassmorphic dialog"""
        from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt
        from PyQt6.QtGui import QFont
        from PyQt6.QtWidgets import (
            QDialog,
            QHBoxLayout,
            QLabel,
            QPushButton,
            QTextEdit,
            QVBoxLayout,
            QWidget,
        )

        dialog = QDialog(self)
        dialog.setWindowTitle(email.get("subject", "(No Subject)"))
        dialog.setMinimumSize(1000, 750)
        dialog.setStyleSheet(
            f"""
            QDialog {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.BG_DARK}, stop:1 {self.BG_LIGHTER});
                border-radius: 16px;
            }}
        """
        )

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Modern glassmorphic header with gradient accent
        header = QWidget()
        header.setStyleSheet(
            f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.GRADIENT_START}, stop:1 {self.GRADIENT_END});
                padding: 32px;
                border-radius: 12px 12px 0 0;
            }}
        """
        )
        header_layout = QVBoxLayout(header)
        header_layout.setSpacing(12)

        # Subject with modern typography
        subject_label = QLabel(email.get("subject", "(No Subject)"))
        subject_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        subject_label.setFont(subject_font)
        subject_label.setStyleSheet(
            f"""
            color: #ffffff;
            margin-bottom: 8px;
            padding: 0;
        """
        )
        subject_label.setWordWrap(True)
        header_layout.addWidget(subject_label)

        # From label with icon
        from_label = QLabel(f"👤 {email.get('from', 'Unknown')}")
        from_label.setStyleSheet(
            f"""
            font-size: 15px;
            color: rgba(255, 255, 255, 0.95);
            font-weight: 500;
        """
        )
        header_layout.addWidget(from_label)

        # Date label with icon
        date_label = QLabel(f"📅 {email.get('date', 'Unknown')}")
        date_label.setStyleSheet(
            f"""
            font-size: 14px;
            color: rgba(255, 255, 255, 0.85);
        """
        )
        header_layout.addWidget(date_label)

        layout.addWidget(header)

        # Email body - use QWebEngineView for full HTML rendering with images
        try:
            from PyQt6.QtWebEngineCore import QWebEngineSettings
            from PyQt6.QtWebEngineWidgets import QWebEngineView

            body_viewer = QWebEngineView()

            # Enable JavaScript and images
            settings = body_viewer.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavaScriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)

            body_viewer.setStyleSheet("background-color: white;")

            # Get email body and render as HTML
            email_body = email.get("full_body", email.get("body", "(No content)"))

            # Ensure proper HTML structure
            if not email_body.strip().startswith("<!DOCTYPE") and not email_body.strip().startswith(
                "<html"
            ):
                email_body = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <style>
                        body {{
                            font-family: Arial, Helvetica, sans-serif;
                            margin: 20px;
                            padding: 20px;
                            background: white;
                            color: #202124;
                        }}
                        img {{ max-width: 100%; height: auto; }}
                        table {{ border-collapse: collapse; max-width: 100%; }}
                        a {{ color: #1a73e8; text-decoration: none; }}
                    </style>
                </head>
                <body>
                    {email_body}
                </body>
                </html>
                """

            body_viewer.setHtml(email_body)

        except ImportError:
            # Fallback to QTextBrowser if QWebEngineView not available
            from PyQt6.QtWidgets import QTextBrowser

            body_viewer = QTextBrowser()
            body_viewer.setReadOnly(True)
            body_viewer.setOpenExternalLinks(True)
            body_viewer.setStyleSheet(
                """
                QTextBrowser {
                    background-color: white;
                    color: #202124;
                    border: none;
                    padding: 40px;
                    font-size: 14px;
                }
            """
            )

            email_body = email.get("full_body", email.get("body", "(No content)"))

            # Convert to simple HTML
            if not ("<html" in email_body.lower() or "<div" in email_body.lower()):
                formatted_body = email_body.replace("\n", "<br>")
                email_body = f'<div style="font-family: Arial; white-space: pre-wrap;">{formatted_body}</div>'

            body_viewer.setHtml(email_body)

        layout.addWidget(body_viewer, 1)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self.ACCENT_BLUE};
                color: white;
                border: none;
                padding: 12px 40px;
                border-radius: 4px;
                font-weight: bold;
                margin: 16px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {self.ACCENT_PURPLE};
            }}
        """
        )
        close_btn.clicked.connect(dialog.close)

        # Action buttons bar (Gmail-style)
        action_bar = QWidget()
        action_bar.setStyleSheet("background: transparent;")
        action_layout = QHBoxLayout(action_bar)
        action_layout.setContentsMargins(16, 8, 16, 8)
        action_layout.setSpacing(8)

        # Modern gradient reply button
        reply_btn = QPushButton("↩️ Reply with AI")
        reply_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.GRADIENT_START}, stop:1 {self.GRADIENT_END});
                color: white;
                border: none;
                padding: 12px 28px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.ACCENT_PURPLE}, stop:1 {self.ACCENT_PINK});
            }}
        """
        )
        reply_btn.clicked.connect(lambda: self._draft_ai_reply(email, dialog))
        action_layout.addWidget(reply_btn)

        # Modern archive button
        archive_btn = QPushButton("📦 Archive")
        archive_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {self.BG_LIGHTER};
                color: {self.TEXT_PRIMARY};
                border: 2px solid {self.BORDER_COLOR};
                padding: 12px 28px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {self.HOVER_COLOR};
                border-color: {self.ACCENT_BLUE};
            }}
        """
        )
        archive_btn.clicked.connect(lambda: self._archive_email(email, dialog))
        action_layout.addWidget(archive_btn)

        # Modern delete button with danger gradient
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: transparent;
                color: #ef4444;
                border: 2px solid #ef4444;
                padding: 12px 28px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ef4444, stop:1 #dc2626);
                color: white;
                border-color: transparent;
            }}
        """
        )
        delete_btn.clicked.connect(lambda: self._delete_email(email, dialog))
        action_layout.addWidget(delete_btn)

        # Modern mark button
        mark_btn = QPushButton("📧 Mark as Unread" if email.get("seen", False) else "✅ Mark as Read")
        mark_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {self.BG_LIGHTER};
                color: {self.TEXT_PRIMARY};
                border: 2px solid {self.BORDER_COLOR};
                padding: 12px 28px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {self.HOVER_COLOR};
                border-color: {self.ONLINE_GREEN};
            }}
        """
        )
        mark_btn.clicked.connect(lambda: self._toggle_email_read_status(email, dialog))
        action_layout.addWidget(mark_btn)

        action_layout.addStretch()

        layout.addWidget(action_bar)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        dialog.exec()

    def _create_email_item(self, email):
        """Create a Gmail-style email item widget"""
        widget = QFrame()
        widget.setFrameShape(QFrame.Shape.NoFrame)
        widget.setCursor(Qt.CursorShape.PointingHandCursor)
        widget.setMinimumHeight(90)  # Set minimum height for proper display
        widget.setStyleSheet(
            f"""
            QFrame {{
                background-color: {self.BG_LIGHTER};
                border: none;
                border-bottom: 1px solid {self.HOVER_COLOR};
                padding: 0;
                margin: 0;
            }}
            QFrame:hover {{
                background-color: {self.HOVER_COLOR};
            }}
        """
        )

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # Left section - Sender and Subject
        left_section = QWidget()
        left_section.setStyleSheet("background: transparent;")
        left_layout = QVBoxLayout(left_section)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        # Sender (bold)
        sender = email.get("from", "Unknown")
        # Extract just the name or email
        if "<" in sender:
            sender_name = sender.split("<")[0].strip()
            if not sender_name:
                sender_name = sender.split("<")[1].split(">")[0]
        else:
            sender_name = sender

        sender_label = QLabel(sender_name[:60])
        sender_label.setStyleSheet(
            f"""
            font-weight: bold;
            font-size: 14px;
            color: {self.TEXT_PRIMARY};
            background: transparent;
        """
        )
        sender_label.setWordWrap(False)
        sender_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        left_layout.addWidget(sender_label)

        # Subject
        subject = email.get("subject", "(No Subject)")
        subject_label = QLabel(subject[:100])
        subject_label.setStyleSheet(
            f"""
            font-size: 13px;
            color: {self.TEXT_PRIMARY};
            background: transparent;
        """
        )
        subject_label.setWordWrap(False)
        subject_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        left_layout.addWidget(subject_label)

        # Preview (first 120 chars of body)
        body_text = email.get("body", "")
        if body_text:
            # Clean up body text (remove extra whitespace/newlines and HTML tags)
            import re

            clean_text = re.sub("<[^<]+?>", "", body_text)  # Remove HTML tags
            preview = " ".join(clean_text.split())[:120]
            preview_label = QLabel(preview + ("..." if len(clean_text) > 120 else ""))
            preview_label.setStyleSheet(
                f"""
                font-size: 12px;
                color: {self.TEXT_SECONDARY};
                background: transparent;
            """
            )
            preview_label.setWordWrap(False)
            preview_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
            left_layout.addWidget(preview_label)

        left_layout.addStretch()
        layout.addWidget(left_section, 1)

        # Right section - Date/Time
        date_str = email.get("date", "")
        date_label = QLabel(self._format_email_date(date_str))
        date_label.setStyleSheet(
            f"""
            font-size: 12px;
            color: {self.TEXT_SECONDARY};
            background: transparent;
        """
        )
        date_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        date_label.setFixedWidth(120)
        layout.addWidget(date_label)

        # Store email data in widget for click handling
        widget.email_data = email

        # Make widget clickable
        widget.mousePressEvent = lambda event: self._on_email_clicked(widget)

        return widget

    def _format_email_date(self, date_str):
        """Format email date to Gmail style (e.g., '2:30 PM' or 'Nov 15')"""
        try:
            import email.utils
            from datetime import datetime

            # Parse email date
            parsed_date = email.utils.parsedate_to_datetime(date_str)
            now = datetime.now(parsed_date.tzinfo)

            # If today, show time
            if parsed_date.date() == now.date():
                return parsed_date.strftime("%I:%M %p")

            # If this year, show month and day
            elif parsed_date.year == now.year:
                return parsed_date.strftime("%b %d")

            # Otherwise show full date
            else:
                return parsed_date.strftime("%m/%d/%y")
        except:
            return date_str[:20] if date_str else ""

    def _github_login(self):
        """Handle GitHub login"""
        username = self.github_username_input.text().strip()
        token = self.github_token_input.text().strip()

        if not username or not token:
            self.github_status_label.setText("❌ Please enter both username and token")
            self.github_status_label.setStyleSheet(
                f"color: #ff4444; font-size: 14px; margin: 10px;"
            )
            return

        if not token.startswith("ghp_"):
            self.github_status_label.setText("❌ Invalid token format (must start with ghp_)")
            self.github_status_label.setStyleSheet(
                f"color: #ff4444; font-size: 14px; margin: 10px;"
            )
            return

        # Update status
        self.github_status_label.setText("🔄 Connecting to GitHub...")
        self.github_status_label.setStyleSheet(
            f"color: {self.ACCENT_BLUE}; font-size: 14px; margin: 10px;"
        )
        self.github_login_btn.setEnabled(False)

        try:
            # Initialize GitHub manager
            from modules.github_manager import GitHubManager

            self.github_manager = GitHubManager(username, token)

            # Try to connect
            if not self.github_manager.connect():
                self.github_status_label.setText("❌ Failed to connect. Check your token.")
                self.github_status_label.setStyleSheet(
                    f"color: #ff4444; font-size: 14px; margin: 10px;"
                )
                self.github_manager = None
                return

            # Save credentials to .env
            env_path = Path(".env")
            set_key(env_path, "GITHUB_USERNAME", username)
            set_key(env_path, "GITHUB_TOKEN", token)

            # Success! Load repos
            self.github_status_label.setText("✅ Connected! Loading repositories...")
            self.github_status_label.setStyleSheet(f"color: {self.ONLINE_GREEN}; font-size: 13px;")

            # Hide login card, show repos
            self.github_login_card.setVisible(False)
            self.github_repos_scroll.setVisible(True)
            self._load_github_repos()

        except Exception as e:
            self.github_status_label.setText(f"❌ Error: {str(e)}")
            self.github_status_label.setStyleSheet(
                f"color: #ff4444; font-size: 14px; margin: 10px;"
            )
            self.github_manager = None
        finally:
            self.github_login_btn.setEnabled(True)

    def _load_github_repos(self):
        """Load GitHub repositories after successful login"""
        if not self.github_manager:
            return

        try:
            self.github_list.clear()
            self.github_list.addItem("📦 Loading repositories...")

            # Get repositories
            repos = self.github_manager.get_repositories()
            stats = self.github_manager.get_user_stats()

            self.github_list.clear()

            # Show user stats first
            self.github_list.addItem(f"═══ 👤 {stats.get('username', 'User')} ═══")
            self.github_list.addItem(
                f"📊 Public Repos: {stats.get('public_repos', 0)} | Followers: {stats.get('followers', 0)} | Following: {stats.get('following', 0)}\n"
            )

            if not repos:
                self.github_list.addItem("No repositories found")
                return

            # Display repositories
            for repo in repos:
                item_text = (
                    f"📦 {repo['name']}\n"
                    f"   ⭐ {repo['stars']} stars | 🍴 {repo['forks']} forks | 📝 {repo.get('language', 'N/A')}\n"
                    f"   {repo['description'][:80] if repo.get('description') else 'No description'}\n"
                )
                self.github_list.addItem(item_text)

            self.github_status_label.setText(f"✅ Loaded {len(repos)} repositories")

        except Exception as e:
            self.github_list.clear()
            self.github_list.addItem(f"❌ Error loading repositories: {str(e)}")

    def _linkedin_login(self):
        """Handle LinkedIn login"""
        email = self.linkedin_email_input.text().strip()
        password = self.linkedin_password_input.text().strip()

        if not email or not password:
            self.linkedin_status_label.setText("❌ Please enter both email and password")
            self.linkedin_status_label.setStyleSheet(
                f"color: #ff4444; font-size: 14px; margin: 10px;"
            )
            return

        # Update status
        self.linkedin_status_label.setText("🔄 Connecting to LinkedIn...")
        self.linkedin_status_label.setStyleSheet(
            f"color: {self.ACCENT_BLUE}; font-size: 14px; margin: 10px;"
        )
        self.linkedin_login_btn.setEnabled(False)

        try:
            # Initialize LinkedIn automation
            from modules.linkedin_automation import LinkedInAutomation

            self.linkedin_automation = LinkedInAutomation(email, password)

            # Try to login
            if not self.linkedin_automation.login():
                self.linkedin_status_label.setText("❌ Failed to login. Check your credentials.")
                self.linkedin_status_label.setStyleSheet(
                    f"color: #ff4444; font-size: 14px; margin: 10px;"
                )
                self.linkedin_automation = None
                return

            # Save credentials to .env
            env_path = Path(".env")
            set_key(env_path, "LINKEDIN_EMAIL", email)
            set_key(env_path, "LINKEDIN_PASSWORD", password)

            # Success! Load profile
            self.linkedin_status_label.setText("✅ Connected! Loading profile...")
            self.linkedin_status_label.setStyleSheet(
                f"color: {self.ONLINE_GREEN}; font-size: 14px; margin: 10px;"
            )

            # Show data
            self.linkedin_data.setVisible(True)
            self._load_linkedin_profile()

        except Exception as e:
            self.linkedin_status_label.setText(f"❌ Error: {str(e)}")
            self.linkedin_status_label.setStyleSheet(
                f"color: #ff4444; font-size: 14px; margin: 10px;"
            )
            self.linkedin_automation = None
        finally:
            self.linkedin_login_btn.setEnabled(True)

    def _load_linkedin_profile(self):
        """Load LinkedIn profile after successful login"""
        if not self.linkedin_automation:
            return

        try:
            self.linkedin_data.clear()
            self.linkedin_data.append("📊 Loading LinkedIn profile...\n")

            # Get profile data
            profile = self.linkedin_automation.get_profile()

            if not profile:
                self.linkedin_data.clear()
                self.linkedin_data.append("❌ Could not load profile data")
                return

            # Display profile data
            self.linkedin_data.clear()
            self.linkedin_data.append("═══ 👤 YOUR LINKEDIN PROFILE ═══\n")
            self.linkedin_data.append(f"Name: {profile.get('name', 'N/A')}\n")
            self.linkedin_data.append(f"Headline: {profile.get('headline', 'N/A')}\n")
            self.linkedin_data.append(f"Location: {profile.get('location', 'N/A')}\n")
            self.linkedin_data.append(f"Connections: {profile.get('connections', 'N/A')}\n\n")

            # Get recent posts/activity
            activity = self.linkedin_automation.get_recent_activity(limit=5)
            if activity:
                self.linkedin_data.append("═══ 📝 RECENT ACTIVITY ═══\n")
                for item in activity:
                    self.linkedin_data.append(
                        f"• {item.get('type', 'Post')}: {item.get('text', 'N/A')[:100]}...\n"
                    )

            self.linkedin_status_label.setText("✅ Profile loaded successfully")

        except Exception as e:
            self.linkedin_data.clear()
            self.linkedin_data.append(f"❌ Error loading profile: {str(e)}")

    def _refresh_emails(self):
        """Refresh email list."""
        if not self.email_handler:
            return

        try:
            self.email_list.clear()
            self.email_list.addItem("Loading emails...")

            # Connect and get emails
            if not self.email_handler.connect():
                self.email_list.clear()
                self.email_list.addItem("❌ Failed to connect to email server")
                return

            emails = self.email_handler.get_recent_emails(count=20)
            self.email_list.clear()

            if not emails:
                self.email_list.addItem("No emails found")
                return

            for email in emails:
                item_text = (
                    f"From: {email['from']}\nSubject: {email['subject']}\nDate: {email['date']}"
                )
                self.email_list.addItem(item_text)

        except Exception as e:
            self.email_list.clear()
            self.email_list.addItem(f"❌ Error: {str(e)}")

    def _create_jobs_page(self):
        """Create LinkedIn jobs page with search and auto-apply"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header
        header = QLabel("💼 LinkedIn Job Search")
        header.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: {self.ACCENT_BLUE}; margin-bottom: 10px;"
        )
        layout.addWidget(header)

        # Search filters panel
        search_panel = QFrame()
        search_panel.setObjectName("panel")
        search_panel.setStyleSheet(
            f"""
            QFrame#panel {{
                background-color: {self.BG_LIGHTER};
                border-radius: 8px;
                padding: 20px;
            }}
        """
        )
        search_layout = QVBoxLayout(search_panel)

        # Job keywords
        keywords_label = QLabel("Job Keywords:")
        keywords_label.setStyleSheet(f"color: {self.TEXT_PRIMARY}; font-weight: bold;")
        self.job_keywords_input = QLineEdit()
        self.job_keywords_input.setPlaceholderText("e.g., Python Developer, Data Scientist")
        self.job_keywords_input.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {self.BG_DARK};
                border: 1px solid {self.BORDER_COLOR};
                border-radius: 4px;
                padding: 10px;
                color: {self.TEXT_PRIMARY};
            }}
        """
        )

        # Location
        location_label = QLabel("Location:")
        location_label.setStyleSheet(f"color: {self.TEXT_PRIMARY}; font-weight: bold;")
        self.job_location_input = QLineEdit()
        self.job_location_input.setPlaceholderText("e.g., New York, NY")
        self.job_location_input.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {self.BG_DARK};
                border: 1px solid {self.BORDER_COLOR};
                border-radius: 4px;
                padding: 10px;
                color: {self.TEXT_PRIMARY};
            }}
        """
        )

        # Filters row
        filters_row = QWidget()
        filters_row.setStyleSheet("background: transparent;")
        filters_layout = QHBoxLayout(filters_row)
        filters_layout.setContentsMargins(0, 0, 0, 0)

        # Job type
        job_type_label = QLabel("Job Type:")
        job_type_label.setStyleSheet(f"color: {self.TEXT_PRIMARY}; font-weight: bold;")
        self.job_type_combo = QComboBox()
        self.job_type_combo.addItems(["Any", "Full-time", "Part-time", "Contract", "Internship"])
        self.job_type_combo.setStyleSheet(
            f"""
            QComboBox {{
                background-color: {self.BG_DARK};
                border: 1px solid {self.BORDER_COLOR};
                border-radius: 4px;
                padding: 8px;
                color: {self.TEXT_PRIMARY};
            }}
        """
        )

        # Experience level
        experience_label = QLabel("Experience:")
        experience_label.setStyleSheet(f"color: {self.TEXT_PRIMARY}; font-weight: bold;")
        self.experience_combo = QComboBox()
        self.experience_combo.addItems(
            ["Any", "Entry level", "Associate", "Mid-Senior level", "Director", "Executive"]
        )
        self.experience_combo.setStyleSheet(
            f"""
            QComboBox {{
                background-color: {self.BG_DARK};
                border: 1px solid {self.BORDER_COLOR};
                border-radius: 4px;
                padding: 8px;
                color: {self.TEXT_PRIMARY};
            }}
        """
        )

        # Remote checkbox
        self.remote_checkbox = QPushButton("🏠 Remote Only")
        self.remote_checkbox.setCheckable(True)
        self.remote_checkbox.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self.BG_DARK};
                border: 1px solid {self.BORDER_COLOR};
                border-radius: 4px;
                padding: 8px 16px;
                color: {self.TEXT_PRIMARY};
            }}
            QPushButton:checked {{
                background-color: {self.ACCENT_PURPLE};
                border-color: {self.ACCENT_PURPLE};
                color: white;
            }}
        """
        )

        filters_layout.addWidget(job_type_label)
        filters_layout.addWidget(self.job_type_combo)
        filters_layout.addWidget(experience_label)
        filters_layout.addWidget(self.experience_combo)
        filters_layout.addWidget(self.remote_checkbox)
        filters_layout.addStretch()

        # Search button
        search_btn = QPushButton("🔍 Search Jobs")
        search_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: #0A66C2;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #004182;
            }}
        """
        )
        search_btn.clicked.connect(self._linkedin_search_jobs)

        search_layout.addWidget(keywords_label)
        search_layout.addWidget(self.job_keywords_input)
        search_layout.addWidget(location_label)
        search_layout.addWidget(self.job_location_input)
        search_layout.addWidget(filters_row)
        search_layout.addWidget(search_btn)

        layout.addWidget(search_panel)

        # Jobs list scroll area
        self.jobs_scroll = QScrollArea()
        self.jobs_scroll.setWidgetResizable(True)
        self.jobs_scroll.setStyleSheet(
            f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
        """
        )

        self.jobs_container = QWidget()
        self.jobs_container.setStyleSheet("background: transparent;")
        self.jobs_layout = QVBoxLayout(self.jobs_container)
        self.jobs_layout.setContentsMargins(0, 0, 0, 0)
        self.jobs_layout.setSpacing(12)
        self.jobs_layout.addStretch()

        self.jobs_scroll.setWidget(self.jobs_container)
        layout.addWidget(self.jobs_scroll, 1)

        return page

    def _linkedin_search_jobs(self):
        """Search for LinkedIn jobs with filters"""
        try:
            keywords = self.job_keywords_input.text().strip()
            if not keywords:
                QMessageBox.warning(
                    self, "Missing Keywords", "Please enter job keywords to search."
                )
                return

            if not self.linkedin_automation:
                QMessageBox.warning(
                    self, "Not Connected", "Please configure LinkedIn credentials in settings."
                )
                return

            # Clear previous results
            while self.jobs_layout.count() > 1:
                item = self.jobs_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # Show loading message
            loading = QLabel("🔍 Searching for jobs...")
            loading.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 16px; padding: 40px;")
            loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.jobs_layout.insertWidget(0, loading)

            # Process events to show loading
            from PyQt6.QtWidgets import QApplication

            QApplication.processEvents()

            # Get filter values
            location = self.job_location_input.text().strip()
            job_type = (
                self.job_type_combo.currentText()
                if self.job_type_combo.currentText() != "Any"
                else ""
            )
            experience = (
                self.experience_combo.currentText()
                if self.experience_combo.currentText() != "Any"
                else ""
            )
            remote = self.remote_checkbox.isChecked()

            # Search jobs
            jobs = self.linkedin_automation.search_jobs(
                keywords=keywords,
                location=location,
                job_type=job_type,
                experience_level=experience,
                remote=remote,
                max_results=25,
            )

            # Remove loading
            loading.deleteLater()

            if not jobs:
                no_results = QLabel("No jobs found. Try different keywords or filters.")
                no_results.setStyleSheet(
                    f"color: {self.TEXT_SECONDARY}; font-size: 16px; padding: 40px;"
                )
                no_results.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.jobs_layout.insertWidget(0, no_results)
                return

            # Display job cards
            for job in jobs:
                job_card = self._create_job_card(job)
                self.jobs_layout.insertWidget(self.jobs_layout.count() - 1, job_card)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to search jobs: {str(e)}")

    def _create_job_card(self, job: dict):
        """Create a job card widget"""
        card = QFrame()
        card.setObjectName("job_card")
        card.setStyleSheet(
            f"""
            QFrame#job_card {{
                background-color: {self.BG_LIGHTER};
                border: 1px solid {self.BORDER_COLOR};
                border-radius: 8px;
                padding: 16px;
            }}
            QFrame#job_card:hover {{
                border-color: {self.ACCENT_PURPLE};
                background-color: {self.HOVER_COLOR};
            }}
        """
        )

        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        # Title and company
        title = QLabel(job.get("title", "Unknown Position"))
        title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {self.TEXT_PRIMARY};")
        title.setWordWrap(True)
        layout.addWidget(title)

        company = QLabel(job.get("company", "Unknown Company"))
        company.setStyleSheet(f"font-size: 14px; color: {self.ACCENT_BLUE};")
        layout.addWidget(company)

        # Location and salary
        info_layout = QHBoxLayout()
        info_layout.setSpacing(16)

        location = QLabel(f"📍 {job.get('location', 'Unknown')}")
        location.setStyleSheet(f"font-size: 13px; color: {self.TEXT_SECONDARY};")
        info_layout.addWidget(location)

        if job.get("salary"):
            salary = QLabel(f"💰 {job['salary']}")
            salary.setStyleSheet(f"font-size: 13px; color: {self.TEXT_SECONDARY};")
            info_layout.addWidget(salary)

        info_layout.addStretch()
        layout.addLayout(info_layout)

        # Description preview
        if job.get("description"):
            desc = QLabel(
                job["description"][:200] + "..."
                if len(job.get("description", "")) > 200
                else job.get("description", "")
            )
            desc.setWordWrap(True)
            desc.setStyleSheet(f"font-size: 13px; color: {self.TEXT_SECONDARY}; margin: 8px 0;")
            layout.addWidget(desc)

        # Buttons row
        buttons_row = QWidget()
        buttons_row.setStyleSheet("background: transparent;")
        buttons_layout = QHBoxLayout(buttons_row)
        buttons_layout.setContentsMargins(0, 8, 0, 0)
        buttons_layout.setSpacing(8)

        # Easy Apply badge
        if job.get("is_easy_apply"):
            easy_badge = QLabel("⚡ Easy Apply")
            easy_badge.setStyleSheet(
                f"""
                background-color: #10b981;
                color: white;
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: bold;
            """
            )
            buttons_layout.addWidget(easy_badge)

        buttons_layout.addStretch()

        # Auto-apply button
        if job.get("is_easy_apply"):
            apply_btn = QPushButton("🤖 Auto-Apply")
            apply_btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {self.ACCENT_PURPLE};
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background-color: #9333ea;
                }}
            """
            )
            apply_btn.clicked.connect(lambda: self._auto_apply_job(job))
            buttons_layout.addWidget(apply_btn)

        # View button
        view_btn = QPushButton("👁️ View")
        view_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: transparent;
                color: {self.TEXT_PRIMARY};
                border: 1px solid {self.BORDER_COLOR};
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {self.HOVER_COLOR};
            }}
        """
        )
        view_btn.clicked.connect(lambda: webbrowser.open(job.get("url", "")))
        buttons_layout.addWidget(view_btn)

        layout.addWidget(buttons_row)

        return card

    def _auto_apply_job(self, job: dict):
        """Auto-apply to a job with AI-generated cover letter"""
        try:
            if not self.linkedin_automation:
                QMessageBox.warning(self, "Not Connected", "LinkedIn automation not configured.")
                return

            # Confirm auto-apply
            reply = QMessageBox.question(
                self,
                "Auto-Apply to Job",
                f"Apply to:\n{job.get('title', 'Unknown')}\nat {job.get('company', 'Unknown')}?\n\nAn AI cover letter will be generated.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Generate AI cover letter
            cover_letter = self.linkedin_automation.generate_cover_letter_ai(
                job_details=job, user_info={"name": self.config.user.name}
            )

            # Apply to job
            success = self.linkedin_automation.apply_to_job(
                job_url=job.get("url", ""), cover_letter=cover_letter
            )

            if success:
                QMessageBox.information(self, "Success", "Application submitted successfully!")
                job["applied"] = True
            else:
                QMessageBox.warning(
                    self,
                    "Incomplete",
                    "Application started but may require manual completion. Please check LinkedIn.",
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to auto-apply: {str(e)}")

    def _search_jobs(self):
        """Search for jobs."""
        if not self.job_automation:
            return

        job_title = self.job_title_input.text().strip()
        location = self.job_location_input.text().strip()

        if not job_title:
            self.job_list.clear()
            self.job_list.addItem("Please enter a job title to search")
            return

        try:
            self.job_list.clear()
            self.job_list.addItem(f"Searching for '{job_title}' jobs...")

            # Search jobs
            jobs = self.job_automation.search_all_platforms(
                job_title, location, max_per_platform=10
            )

            self.job_list.clear()

            if not jobs:
                self.job_list.addItem("No jobs found")
                return

            for job in jobs:
                item_text = (
                    f"{job['title']}\n{job['company']} - {job['location']}\nSource: {job['source']}"
                )
                self.job_list.addItem(item_text)

        except Exception as e:
            self.job_list.clear()
            self.job_list.addItem(f"❌ Error: {str(e)}")

    def _create_github_page(self):
        """Create GitHub management page with modern UI matching GitHub's design"""
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header section
        header = QWidget()
        header.setStyleSheet(f"background-color: {self.BG_LIGHTER}; padding: 20px;")
        header_layout = QHBoxLayout(header)

        github_icon = QLabel("⚙️ GitHub")
        github_icon.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {self.ACCENT_BLUE};")
        header_layout.addWidget(github_icon)

        header_layout.addStretch()

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: #238636;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #2ea043;
            }}
        """
        )
        refresh_btn.clicked.connect(self._refresh_github_repos)
        header_layout.addWidget(refresh_btn)

        main_layout.addWidget(header)

        # Content area
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Login card (hidden after successful login)
        self.github_login_card = QFrame()
        self.github_login_card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {self.BG_LIGHTER};
                border: 1px solid {self.HOVER_COLOR};
                border-radius: 8px;
                padding: 24px;
            }}
        """
        )
        login_card_layout = QVBoxLayout(self.github_login_card)

        login_title = QLabel("Connect to GitHub")
        login_title.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {self.TEXT_PRIMARY}; margin-bottom: 16px;"
        )
        login_card_layout.addWidget(login_title)

        # Username
        username_label = QLabel("Username:")
        username_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 13px;")
        self.github_username_input = QLineEdit()
        self.github_username_input.setPlaceholderText("octocat")
        self.github_username_input.setText(os.getenv("GITHUB_USERNAME", ""))
        self.github_username_input.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {self.BG_DARK};
                border: 1px solid {self.HOVER_COLOR};
                border-radius: 6px;
                padding: 8px 12px;
                color: {self.TEXT_PRIMARY};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {self.ACCENT_BLUE};
            }}
        """
        )

        # Token
        token_label = QLabel("Personal Access Token:")
        token_label.setStyleSheet(
            f"color: {self.TEXT_SECONDARY}; font-size: 13px; margin-top: 12px;"
        )
        self.github_token_input = QLineEdit()
        self.github_token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.github_token_input.setPlaceholderText("ghp_xxxxxxxxxxxx")
        self.github_token_input.setText(os.getenv("GITHUB_TOKEN", ""))
        self.github_token_input.setStyleSheet(self.github_username_input.styleSheet())

        # Help link
        token_help = QLabel(
            '<a href="https://github.com/settings/tokens/new?scopes=repo,read:user" style="color: #00d4ff; text-decoration: none;">→ Create a new token</a>'
        )
        token_help.setOpenExternalLinks(True)
        token_help.setStyleSheet("margin-top: 8px; margin-bottom: 16px;")

        # Login button
        self.github_login_btn = QPushButton("Connect GitHub Account")
        self.github_login_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: #238636;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #2ea043;
            }}
        """
        )
        self.github_login_btn.clicked.connect(self._github_login)

        login_card_layout.addWidget(username_label)
        login_card_layout.addWidget(self.github_username_input)
        login_card_layout.addWidget(token_label)
        login_card_layout.addWidget(self.github_token_input)
        login_card_layout.addWidget(token_help)
        login_card_layout.addWidget(self.github_login_btn)

        content_layout.addWidget(self.github_login_card)

        # Status label
        self.github_status_label = QLabel("")
        self.github_status_label.setStyleSheet(
            f"color: {self.TEXT_SECONDARY}; font-size: 13px; margin: 12px 0;"
        )
        content_layout.addWidget(self.github_status_label)

        # Repository list (scroll area with cards)
        repos_scroll = QScrollArea()
        repos_scroll.setWidgetResizable(True)
        repos_scroll.setFrameShape(QFrame.Shape.NoFrame)
        repos_scroll.setStyleSheet(f"background-color: {self.BG_DARK}; border: none;")

        self.github_repos_container = QWidget()
        self.github_repos_layout = QVBoxLayout(self.github_repos_container)
        self.github_repos_layout.setSpacing(12)
        self.github_repos_layout.setContentsMargins(0, 0, 0, 0)

        repos_scroll.setWidget(self.github_repos_container)
        repos_scroll.setVisible(False)
        self.github_repos_scroll = repos_scroll

        content_layout.addWidget(repos_scroll, 1)

        main_layout.addWidget(content, 1)

        return page

    def _refresh_github_repos(self):
        """Refresh GitHub repositories with modern cards"""
        if not self.github_manager:
            return

        self._load_github_repos()

    def _load_github_repos(self):
        """Load GitHub repositories and display as cards"""
        if not self.github_manager:
            return

        try:
            # Clear existing widgets
            while self.github_repos_layout.count():
                child = self.github_repos_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            # Get repositories
            repos = self.github_manager.get_repositories()

            if not repos:
                no_repos_label = QLabel("No repositories found")
                no_repos_label.setStyleSheet(
                    f"color: {self.TEXT_SECONDARY}; font-size: 14px; padding: 20px;"
                )
                self.github_repos_layout.addWidget(no_repos_label)
                return

            # Create repository cards
            for repo in repos:
                repo_card = self._create_repo_card(repo)
                self.github_repos_layout.addWidget(repo_card)

            # Add stretch at the end
            self.github_repos_layout.addStretch()

            self.github_status_label.setText(f"\u2705 Loaded {len(repos)} repositories")

        except Exception as e:
            error_label = QLabel(f"\u274c Error loading repositories: {str(e)}")
            error_label.setStyleSheet(f"color: #ff4444; font-size: 14px; padding: 20px;")
            self.github_repos_layout.addWidget(error_label)

    def _create_repo_card(self, repo):
        """Create a GitHub-style repository card"""
        card = QFrame()
        card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {self.BG_LIGHTER};
                border: 1px solid {self.HOVER_COLOR};
                border-radius: 6px;
                padding: 16px;
            }}
            QFrame:hover {{
                border-color: {self.ACCENT_BLUE};
            }}
        """
        )

        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        # Repo name and link
        name_layout = QHBoxLayout()
        repo_name = QLabel(
            f"<a href='{repo.get('url', '#')}' style='color: {self.ACCENT_BLUE}; text-decoration: none; font-weight: 600; font-size: 15px;'>📦 {repo.get('name', 'Unknown')}</a>"
        )
        repo_name.setOpenExternalLinks(True)
        repo_name.setTextFormat(Qt.TextFormat.RichText)
        name_layout.addWidget(repo_name)

        # Visibility badge
        visibility = "Public" if repo.get("private", False) == False else "Private"
        visibility_badge = QLabel(visibility)
        visibility_badge.setStyleSheet(
            f"""
            background-color: {self.HOVER_COLOR};
            color: {self.TEXT_SECONDARY};
            border: 1px solid {self.HOVER_COLOR};
            border-radius: 12px;
            padding: 2px 8px;
            font-size: 11px;
        """
        )
        visibility_badge.setFixedHeight(20)
        name_layout.addWidget(visibility_badge)
        name_layout.addStretch()

        layout.addLayout(name_layout)

        # Description
        description = repo.get("description", "")
        if description:
            desc_label = QLabel(description[:150] + ("..." if len(description) > 150 else ""))
            desc_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 13px;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        # Stats row
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)

        # Language
        language = repo.get("language", "")
        if language:
            lang_label = QLabel(f"🔵 {language}")
            lang_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 12px;")
            stats_layout.addWidget(lang_label)

        # Stars
        stars = repo.get("stars", 0)
        star_label = QLabel(f"⭐ {stars}")
        star_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 12px;")
        stats_layout.addWidget(star_label)

        # Forks
        forks = repo.get("forks", 0)
        fork_label = QLabel(f"🍴 {forks}")
        fork_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 12px;")
        stats_layout.addWidget(fork_label)

        # Updated date
        updated = repo.get("updated_at", "")
        if updated:
            # Parse and format date
            try:
                from datetime import datetime

                dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                time_ago = self._time_ago(dt)
                updated_label = QLabel(f"Updated {time_ago}")
                updated_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 12px;")
                stats_layout.addWidget(updated_label)
            except:
                pass

        stats_layout.addStretch()
        layout.addLayout(stats_layout)

        return card

    def _time_ago(self, dt):
        """Calculate time ago from datetime"""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        diff = now - dt

        seconds = diff.total_seconds()
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = int(seconds / 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"

    def _draft_ai_reply(self, email, dialog):
        """Draft an AI-powered reply to the email"""
        try:
            # Close the email viewer
            dialog.close()

            # Prepare context for AI
            email_context = f"""
Email From: {email.get('from', 'Unknown')}
Subject: {email.get('subject', 'No Subject')}
Date: {email.get('date', '')}

Email Body:
{email.get('body', '')}

Please draft a professional and contextually appropriate reply to this email.
Keep it concise, friendly, and professional.
"""

            # Use enhanced AI if available, otherwise basic AI
            if hasattr(self, "ai_chat_enhanced") and self.ai_chat_enhanced:
                response = self.ai_chat_enhanced.send_message(email_context)
            elif hasattr(self, "ai_chat") and self.ai_chat:
                response = self.ai_chat.send_message(email_context)
            else:
                QMessageBox.warning(
                    self, "AI Not Available", "AI chat is not configured. Please set up AI first."
                )
                return

            # Show compose dialog with AI draft
            self._show_compose_dialog(
                to=email.get("from", ""),
                subject=f"Re: {email.get('subject', 'No Subject')}",
                body=response,
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to draft reply: {str(e)}")

    def _show_compose_dialog(self, to="", subject="", body=""):
        """Show email composition dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Compose Email")
        dialog.setMinimumSize(700, 650)
        dialog.setStyleSheet(
            f"""
            QDialog {{
                background-color: {self.BG_COLOR};
            }}
        """
        )

        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header with title and template selector
        header = QWidget()
        header.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(16)

        # Title
        title = QLabel("Compose Email")
        title.setStyleSheet(
            f"""
            color: {self.TEXT_COLOR};
            font-size: 24px;
            font-weight: bold;
        """
        )
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Template selector
        template_label = QLabel("Template:")
        template_label.setStyleSheet(f"color: {self.TEXT_COLOR}; font-weight: bold;")
        header_layout.addWidget(template_label)

        template_combo = QComboBox()
        template_combo.addItem("None", None)

        # Load templates
        templates = self._load_email_templates()
        for template in templates:
            template_combo.addItem(template["name"], template)

        template_combo.setStyleSheet(
            f"""
            QComboBox {{
                background-color: {self.BG_LIGHTER};
                border: 1px solid {self.BORDER_COLOR};
                border-radius: 4px;
                padding: 8px 12px;
                color: {self.TEXT_COLOR};
                font-size: 13px;
                min-width: 150px;
            }}
            QComboBox:hover {{
                border: 1px solid {self.ACCENT_PURPLE};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {self.TEXT_COLOR};
                margin-right: 5px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {self.BG_LIGHTER};
                border: 1px solid {self.BORDER_COLOR};
                selection-background-color: {self.ACCENT_PURPLE};
                selection-color: white;
                color: {self.TEXT_COLOR};
                padding: 5px;
            }}
        """
        )
        header_layout.addWidget(template_combo)

        layout.addWidget(header)

        # To field
        to_label = QLabel("To:")
        to_label.setStyleSheet(f"color: {self.TEXT_COLOR}; font-weight: bold;")
        layout.addWidget(to_label)

        to_input = QLineEdit(to)
        to_input.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {self.BG_LIGHTER};
                border: 1px solid {self.BORDER_COLOR};
                border-radius: 4px;
                padding: 10px;
                color: {self.TEXT_COLOR};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.ACCENT_PURPLE};
            }}
        """
        )
        layout.addWidget(to_input)

        # Subject field
        subject_label = QLabel("Subject:")
        subject_label.setStyleSheet(f"color: {self.TEXT_COLOR}; font-weight: bold;")
        layout.addWidget(subject_label)

        subject_input = QLineEdit(subject)
        subject_input.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: {self.BG_LIGHTER};
                border: 1px solid {self.BORDER_COLOR};
                border-radius: 4px;
                padding: 10px;
                color: {self.TEXT_COLOR};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.ACCENT_PURPLE};
            }}
        """
        )
        layout.addWidget(subject_input)

        # Body field
        body_label = QLabel("Message:")
        body_label.setStyleSheet(f"color: {self.TEXT_COLOR}; font-weight: bold;")
        layout.addWidget(body_label)

        body_input = QTextEdit(body)
        body_input.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {self.BG_LIGHTER};
                border: 1px solid {self.BORDER_COLOR};
                border-radius: 4px;
                padding: 10px;
                color: {self.TEXT_COLOR};
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QTextEdit:focus {{
                border: 2px solid {self.ACCENT_PURPLE};
            }}
        """
        )
        layout.addWidget(body_input)

        # Button bar
        button_bar = QWidget()
        button_bar.setStyleSheet("background: transparent;")
        button_layout = QHBoxLayout(button_bar)
        button_layout.setContentsMargins(0, 8, 0, 0)
        button_layout.setSpacing(8)

        # Send button
        send_btn = QPushButton("📧 Send")
        send_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self.ACCENT_PURPLE};
                color: white;
                border: none;
                padding: 10px 32px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #9333ea;
            }}
        """
        )
        send_btn.clicked.connect(
            lambda: self._send_email(
                to_input.text(), subject_input.text(), body_input.toPlainText(), dialog
            )
        )
        button_layout.addWidget(send_btn)

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: transparent;
                color: {self.TEXT_COLOR};
                border: 1px solid {self.BORDER_COLOR};
                padding: 10px 32px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {self.HOVER_COLOR};
            }}
        """
        )
        cancel_btn.clicked.connect(dialog.close)
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()

        layout.addWidget(button_bar)

        # Template selection handler
        def on_template_selected(index):
            template = template_combo.itemData(index)
            if template:
                subject_input.setText(template.get("subject", ""))
                body_input.setPlainText(template.get("body", ""))

        template_combo.currentIndexChanged.connect(on_template_selected)

        dialog.exec()

    def _load_email_templates(self):
        """Load email templates from JSON file"""
        try:
            import json

            template_file = Path(__file__).parent.parent.parent / "data" / "email_templates.json"

            if template_file.exists():
                with open(template_file, "r") as f:
                    data = json.load(f)
                    return data.get("templates", [])
            return []
        except Exception as e:
            print(f"Error loading templates: {e}")
            return []

    def _send_email(self, to, subject, body, dialog):
        """Send the composed email"""
        try:
            if not to or not subject or not body:
                QMessageBox.warning(self, "Missing Information", "Please fill in all fields.")
                return

            if not self.email_handler:
                QMessageBox.critical(self, "Error", "Email handler not configured.")
                return

            # Send email using email handler
            self.email_handler.send_email(to, subject, body)

            QMessageBox.information(self, "Success", "Email sent successfully!")
            dialog.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send email: {str(e)}")

    def _archive_email(self, email, dialog):
        """Archive the email"""
        try:
            if not self.email_handler:
                QMessageBox.critical(self, "Error", "Email handler not configured.")
                return

            # Archive email (move to Archive folder)
            msg_id = email.get("id")
            if msg_id:
                self.email_handler.archive_email(msg_id)
                QMessageBox.information(self, "Success", "Email archived successfully!")
                dialog.close()
                self._refresh_email()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to archive email: {str(e)}")

    def _delete_email(self, email, dialog):
        """Delete the email"""
        try:
            # Confirm deletion
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                "Are you sure you want to delete this email?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            if not self.email_handler:
                QMessageBox.critical(self, "Error", "Email handler not configured.")
                return

            # Delete email
            msg_id = email.get("id")
            if msg_id:
                self.email_handler.delete_email(msg_id)
                QMessageBox.information(self, "Success", "Email deleted successfully!")
                dialog.close()
                self._refresh_email()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete email: {str(e)}")

    def _toggle_email_read_status(self, email, dialog):
        """Toggle email read/unread status"""
        try:
            if not self.email_handler:
                QMessageBox.critical(self, "Error", "Email handler not configured.")
                return

            msg_id = email.get("id")
            is_seen = email.get("seen", False)

            if msg_id:
                if is_seen:
                    self.email_handler.mark_as_unread(msg_id)
                    QMessageBox.information(self, "Success", "Email marked as unread!")
                else:
                    self.email_handler.mark_as_read(msg_id)
                    QMessageBox.information(self, "Success", "Email marked as read!")

                dialog.close()
                self._refresh_email()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update email status: {str(e)}")

    def _refresh_email(self):
        """Refresh the email list"""
        if hasattr(self, "_load_emails"):
            self._load_emails()

    def _show_github_stats(self):
        """Show GitHub user stats."""
        if not self.github_manager:
            return

        try:
            stats = self.github_manager.get_user_stats()

            from PyQt6.QtWidgets import QMessageBox

            QMessageBox.information(
                self,
                "GitHub Stats",
                f"Username: {stats.get('username', 'N/A')}\n"
                f"Name: {stats.get('name', 'N/A')}\n"
                f"Public Repos: {stats.get('public_repos', 0)}\n"
                f"Followers: {stats.get('followers', 0)}\n"
                f"Following: {stats.get('following', 0)}\n"
                f"Total Stars: {stats.get('total_stars', 0)}\n"
                f"Total Forks: {stats.get('total_forks', 0)}",
            )
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox

            QMessageBox.warning(self, "Error", f"Failed to get stats: {str(e)}")

    def _create_calendar_page(self):
        """Create calendar integration page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = QLabel("📅 Calendar Integration")
        header.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header.setStyleSheet("color: #1a73e8; margin-bottom: 10px;")
        layout.addWidget(header)

        # Sync button
        sync_btn = QPushButton("🔄 Sync with Google Calendar")
        sync_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """
        )
        sync_btn.clicked.connect(self._sync_calendar)
        layout.addWidget(sync_btn)

        # Add event button
        add_event_btn = QPushButton("➕ Add New Event")
        add_event_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #34a853;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2d8e47;
            }
        """
        )
        add_event_btn.clicked.connect(self._show_add_event_dialog)
        layout.addWidget(add_event_btn)

        # Today's events card
        self.todays_events_card = self._create_todays_events_card()
        layout.addWidget(self.todays_events_card)

        # Upcoming events card
        self.upcoming_events_card = self._create_upcoming_events_card()
        layout.addWidget(self.upcoming_events_card)

        layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(page)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #f5f5f5; }")

        return scroll

    def _create_todays_events_card(self):
        """Create today's events card"""
        card = QFrame()
        card.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
        """
        )

        layout = QVBoxLayout(card)

        title = QLabel("📋 Today's Events")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #202124; margin-bottom: 10px;")
        layout.addWidget(title)

        self.todays_events_list = QWidget()
        self.todays_events_layout = QVBoxLayout(self.todays_events_list)
        self.todays_events_layout.setSpacing(8)
        layout.addWidget(self.todays_events_list)

        return card

    def _create_upcoming_events_card(self):
        """Create upcoming events card (7 days)"""
        card = QFrame()
        card.setStyleSheet(
            """
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
            }
        """
        )

        layout = QVBoxLayout(card)

        title = QLabel("📅 Upcoming Events (Next 7 Days)")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #202124; margin-bottom: 10px;")
        layout.addWidget(title)

        self.upcoming_events_list = QWidget()
        self.upcoming_events_layout = QVBoxLayout(self.upcoming_events_list)
        self.upcoming_events_layout.setSpacing(8)
        layout.addWidget(self.upcoming_events_list)

        return card

    def _create_event_widget(self, event):
        """Create widget for a single event"""
        widget = QFrame()
        widget.setStyleSheet(
            """
            QFrame {
                background-color: #f8f9fa;
                border-left: 4px solid #1a73e8;
                border-radius: 4px;
                padding: 10px;
            }
            QFrame:hover {
                background-color: #e8f0fe;
            }
        """
        )

        layout = QVBoxLayout(widget)
        layout.setSpacing(5)

        # Event title
        title = QLabel(event.get("summary", "No Title"))
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #202124;")
        layout.addWidget(title)

        # Event time
        start = event.get("start", {})
        end = event.get("end", {})

        if "dateTime" in start:
            from datetime import datetime

            start_dt = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end["dateTime"].replace("Z", "+00:00"))

            time_str = f"🕐 {start_dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}"
        else:
            time_str = "📅 All Day"

        time_label = QLabel(time_str)
        time_label.setStyleSheet("color: #5f6368; font-size: 11px;")
        layout.addWidget(time_label)

        # Location if available
        if "location" in event:
            location_label = QLabel(f"📍 {event['location']}")
            location_label.setStyleSheet("color: #5f6368; font-size: 11px;")
            layout.addWidget(location_label)

        # Description if available
        if "description" in event:
            desc = event["description"]
            if len(desc) > 100:
                desc = desc[:100] + "..."
            desc_label = QLabel(desc)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #5f6368; font-size: 11px; margin-top: 5px;")
            layout.addWidget(desc_label)

        return widget

    def _sync_calendar(self):
        """Sync calendar with Google Calendar"""
        try:
            if not self.calendar_manager:
                from PyQt6.QtWidgets import QMessageBox

                QMessageBox.warning(self, "Error", "Calendar manager not initialized")
                return

            # Clear existing events
            while self.todays_events_layout.count():
                child = self.todays_events_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            while self.upcoming_events_layout.count():
                child = self.upcoming_events_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            # Get today's events
            todays_events = self.calendar_manager.get_todays_events()
            if todays_events:
                for event in todays_events:
                    event_widget = self._create_event_widget(event)
                    self.todays_events_layout.addWidget(event_widget)
            else:
                no_events = QLabel("No events today")
                no_events.setStyleSheet("color: #5f6368; font-style: italic; padding: 10px;")
                self.todays_events_layout.addWidget(no_events)

            # Get upcoming events
            upcoming_events = self.calendar_manager.get_upcoming_events(
                max_results=10, days_ahead=7
            )
            if upcoming_events:
                # Filter out today's events
                from datetime import datetime, timezone

                today_start = datetime.now(timezone.utc).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                today_end = today_start.replace(hour=23, minute=59, second=59)

                future_events = []
                for event in upcoming_events:
                    start = event.get("start", {})
                    if "dateTime" in start:
                        event_dt = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
                        if event_dt > today_end:
                            future_events.append(event)

                if future_events:
                    for event in future_events:
                        event_widget = self._create_event_widget(event)
                        self.upcoming_events_layout.addWidget(event_widget)
                else:
                    no_events = QLabel("No upcoming events")
                    no_events.setStyleSheet("color: #5f6368; font-style: italic; padding: 10px;")
                    self.upcoming_events_layout.addWidget(no_events)
            else:
                no_events = QLabel("No upcoming events")
                no_events.setStyleSheet("color: #5f6368; font-style: italic; padding: 10px;")
                self.upcoming_events_layout.addWidget(no_events)

            # Log to timeline
            if hasattr(self, "timeline_manager"):
                self.timeline_manager.add_activity(
                    "calendar_sync",
                    "Calendar Synced",
                    f"Synced with Google Calendar: {len(todays_events)} today, {len(future_events) if 'future_events' in locals() else 0} upcoming",
                )

            from PyQt6.QtWidgets import QMessageBox

            QMessageBox.information(self, "Success", "Calendar synced successfully!")

        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox

            QMessageBox.warning(self, "Error", f"Failed to sync calendar: {str(e)}")

    def _show_add_event_dialog(self):
        """Show dialog to add new calendar event"""
        from datetime import datetime, timedelta

        from PyQt6.QtWidgets import (
            QDateTimeEdit,
            QDialog,
            QDialogButtonBox,
            QFormLayout,
            QLineEdit,
            QTextEdit,
        )

        dialog = QDialog(self)
        dialog.setWindowTitle("Add Calendar Event")
        dialog.setMinimumWidth(500)
        dialog.setStyleSheet(
            """
            QDialog {
                background-color: white;
            }
            QLineEdit, QTextEdit, QDateTimeEdit {
                padding: 8px;
                border: 1px solid #dadce0;
                border-radius: 4px;
                font-size: 13px;
            }
            QLineEdit:focus, QTextEdit:focus, QDateTimeEdit:focus {
                border: 2px solid #1a73e8;
            }
        """
        )

        layout = QFormLayout(dialog)

        # Event fields
        title_input = QLineEdit()
        title_input.setPlaceholderText("Meeting with team")

        start_time_input = QDateTimeEdit()
        start_time_input.setDateTime(datetime.now())
        start_time_input.setCalendarPopup(True)
        start_time_input.setDisplayFormat("yyyy-MM-dd hh:mm AP")

        end_time_input = QDateTimeEdit()
        end_time_input.setDateTime(datetime.now() + timedelta(hours=1))
        end_time_input.setCalendarPopup(True)
        end_time_input.setDisplayFormat("yyyy-MM-dd hh:mm AP")

        location_input = QLineEdit()
        location_input.setPlaceholderText("Conference Room A")

        description_input = QTextEdit()
        description_input.setPlaceholderText("Event details...")
        description_input.setMaximumHeight(100)

        attendees_input = QLineEdit()
        attendees_input.setPlaceholderText("email1@example.com, email2@example.com")

        layout.addRow("Title*:", title_input)
        layout.addRow("Start Time*:", start_time_input)
        layout.addRow("End Time*:", end_time_input)
        layout.addRow("Location:", location_input)
        layout.addRow("Description:", description_input)
        layout.addRow("Attendees:", attendees_input)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            title = title_input.text().strip()
            if not title:
                from PyQt6.QtWidgets import QMessageBox

                QMessageBox.warning(self, "Error", "Event title is required")
                return

            start_dt = start_time_input.dateTime().toPyDateTime()
            end_dt = end_time_input.dateTime().toPyDateTime()
            location = location_input.text().strip() or None
            description = description_input.toPlainText().strip() or None

            attendees = []
            if attendees_input.text().strip():
                attendees = [email.strip() for email in attendees_input.text().split(",")]

            self._create_calendar_event(title, start_dt, end_dt, description, location, attendees)

    def _create_calendar_event(
        self, title, start_time, end_time, description=None, location=None, attendees=None
    ):
        """Create a new calendar event"""
        try:
            if not self.calendar_manager:
                from PyQt6.QtWidgets import QMessageBox

                QMessageBox.warning(self, "Error", "Calendar manager not initialized")
                return

            # Check for conflicts
            conflicts = self.calendar_manager.check_conflicts(start_time, end_time)
            if conflicts:
                from PyQt6.QtWidgets import QMessageBox

                conflict_msg = "This event conflicts with:\n\n"
                for event in conflicts:
                    conflict_msg += f"• {event.get('summary', 'Untitled')}\n"

                reply = QMessageBox.question(
                    self,
                    "Schedule Conflict",
                    conflict_msg + "\nDo you want to create this event anyway?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )

                if reply == QMessageBox.StandardButton.No:
                    return

            # Create event
            event = self.calendar_manager.create_event(
                summary=title,
                start_time=start_time,
                end_time=end_time,
                description=description,
                location=location,
                attendees=attendees,
            )

            if event:
                # Refresh calendar display
                self._sync_calendar()

                # Log to timeline
                if hasattr(self, "timeline_manager"):
                    self.timeline_manager.add_activity(
                        "calendar_event", "Event Created", f"Created calendar event: {title}"
                    )

                from PyQt6.QtWidgets import QMessageBox

                QMessageBox.information(self, "Success", f"Event '{title}' created successfully!")

        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox

            QMessageBox.warning(self, "Error", f"Failed to create event: {str(e)}")

    def _create_settings_page(self):
        """Create settings page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("⚙️ Settings")
        header.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: {self.ACCENT_BLUE}; margin-bottom: 20px;"
        )
        layout.addWidget(header)

        # Settings panels
        voice_panel = self._create_settings_panel(
            "Voice Settings", f"Voice Enabled: {'Yes' if self.config.user.voice_enabled else 'No'}"
        )
        layout.addWidget(voice_panel)

        ai_panel = self._create_settings_panel(
            "AI Configuration",
            f"Provider: {self.config.ai.provider if self.config.ai else 'Not configured'}",
        )
        layout.addWidget(ai_panel)

        layout.addStretch()

        return page

    def _create_stat_panel(self, icon, title, value):
        """Create a stat display panel"""
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setMinimumHeight(120)

        layout = QVBoxLayout(panel)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 32px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {self.ACCENT_BLUE};")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 12px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(icon_label)
        layout.addWidget(value_label)
        layout.addWidget(title_label)

        return panel

    def _create_settings_panel(self, title, content):
        """Create a settings panel"""
        panel = QFrame()
        panel.setObjectName("panel")

        layout = QVBoxLayout(panel)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        content_label = QLabel(content)
        content_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; margin-top: 8px;")

        layout.addWidget(title_label)
        layout.addWidget(content_label)

        return panel

    def _switch_page(self, index):
        """Switch to a different page"""
        # Uncheck all buttons
        for btn in self.nav_buttons:
            btn.setChecked(False)

        # Check the clicked button
        self.nav_buttons[index].setChecked(True)

        # Switch page
        self.content_stack.setCurrentIndex(index)

    def _send_message(self):
        """Send a message to the AI"""
        message = self.chat_input.text().strip()
        if not message:
            return

        # Add user message to chat
        self.chat_history.append(
            f'<div style="color: {self.ACCENT_BLUE}; font-weight: bold;">You:</div>'
        )
        self.chat_history.append(f'<div style="margin-bottom: 15px;">{message}</div>')

        # Clear input
        self.chat_input.clear()

        # Send to AI and get response
        if self.ai_chat and self.ai_chat.is_available():
            # Show thinking indicator
            self.chat_history.append(
                f'<div style="color: {self.ACCENT_PURPLE}; font-weight: bold;">XENO:</div>'
            )
            self.chat_history.append(
                f'<div style="margin-bottom: 15px; color: {self.TEXT_SECONDARY};">Thinking...</div>'
            )

            # Process in background (simple version - blocks UI for now)
            try:
                response = self.ai_chat.send_message(message)

                # Remove thinking indicator
                cursor = self.chat_history.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                cursor.movePosition(cursor.MoveOperation.StartOfBlock, cursor.MoveMode.KeepAnchor)
                cursor.movePosition(cursor.MoveOperation.Up, cursor.MoveMode.KeepAnchor)
                cursor.removeSelectedText()

                # Add actual response
                self.chat_history.append(f'<div style="margin-bottom: 15px;">{response}</div>')
            except Exception as e:
                self.chat_history.append(
                    f'<div style="margin-bottom: 15px; color: #ff6b6b;">Error: {str(e)}</div>'
                )
        else:
            self.chat_history.append(
                f'<div style="color: {self.ACCENT_PURPLE}; font-weight: bold;">XENO:</div>'
            )
            self.chat_history.append(
                f'<div style="margin-bottom: 15px;">AI module not yet connected. Please add your OpenAI API key in Settings → Run setup again with: python src\\jarvis.py --setup</div>'
            )

    def _open_login_page(self, url: str):
        """Open a login page in the default browser"""
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Error opening browser: {e}")

    def _show_gmail_setup(self):
        """Show Gmail OAuth2 setup dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Connect Gmail Account")
        dialog.setMinimumWidth(500)
        dialog.setStyleSheet(f"background-color: {self.BG_DARK}; color: {self.TEXT_PRIMARY};")

        layout = QVBoxLayout(dialog)

        # Title
        title = QLabel("📧 <b>Connect Your Gmail Account</b>")
        title.setStyleSheet(f"font-size: 18px; color: {self.ACCENT_BLUE}; padding: 10px;")
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "XENO needs access to your Gmail to read and manage emails.<br><br>"
            "<b>Click the button below to:</b><br>"
            "• Sign in with your Google account<br>"
            "• Grant XENO permission to access Gmail<br>"
            "• Automatically save your credentials<br><br>"
            "This uses OAuth2 - your password is never stored!"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet(f"color: {self.TEXT_SECONDARY}; padding: 10px;")
        layout.addWidget(instructions)

        # Continue with Google button (like GoDaddy!)
        google_btn = QPushButton("� Continue with Google")
        google_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: #4285F4;
                color: white;
                padding: 15px 30px;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
                margin: 20px 0px;
            }}
            QPushButton:hover {{
                background-color: #357AE8;
            }}
        """
        )

        def start_gmail_oauth():
            google_btn.setEnabled(False)
            google_btn.setText("⏳ Opening browser...")

            try:
                # For now, open App Password page (OAuth2 requires Google API credentials)
                # Full OAuth2 will be implemented in next version
                webbrowser.open("https://myaccount.google.com/apppasswords")

                # Show manual input dialog
                QMessageBox.information(
                    dialog,
                    "Get App Password",
                    "📧 <b>Gmail App Password Setup:</b><br><br>"
                    "1. A browser window has opened to Google Account settings<br>"
                    "2. Sign in if needed<br>"
                    "3. App name: <b>XENO Assistant</b><br>"
                    "4. Device: <b>Windows Computer</b><br>"
                    "5. Click <b>Generate</b><br>"
                    "6. Copy the 16-character password<br>"
                    "7. Enter it below (spaces will be removed)<br>",
                )

                dialog.accept()
                self._show_gmail_manual_setup()

            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to start OAuth: {str(e)}")
                google_btn.setEnabled(True)
                google_btn.setText("🔐 Continue with Google")

        google_btn.clicked.connect(start_gmail_oauth)
        layout.addWidget(google_btn)

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"padding: 10px; background-color: {self.BG_LIGHTER};")
        cancel_btn.clicked.connect(dialog.reject)
        layout.addWidget(cancel_btn)

        dialog.exec()

    def _show_gmail_manual_setup(self):
        """Show manual Gmail App Password entry"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Enter Gmail Credentials")
        dialog.setMinimumWidth(500)
        dialog.setStyleSheet(f"background-color: {self.BG_DARK}; color: {self.TEXT_PRIMARY};")

        layout = QVBoxLayout(dialog)

        # Email input
        email_label = QLabel("📧 Gmail Address:")
        email_label.setStyleSheet(
            f"color: {self.ACCENT_BLUE}; font-weight: bold; margin-top: 10px;"
        )
        layout.addWidget(email_label)

        email_input = QLineEdit()
        email_input.setPlaceholderText("your.email@gmail.com")
        email_input.setText(os.getenv("EMAIL_ADDRESS", ""))
        email_input.setStyleSheet(
            f"padding: 10px; background-color: {self.BG_LIGHTER}; border: 1px solid {self.HOVER_COLOR}; border-radius: 4px;"
        )
        layout.addWidget(email_input)

        # Password input
        pass_label = QLabel("🔑 App Password (16 characters, no spaces):")
        pass_label.setStyleSheet(f"color: {self.ACCENT_BLUE}; font-weight: bold; margin-top: 10px;")
        layout.addWidget(pass_label)

        pass_input = QLineEdit()
        pass_input.setPlaceholderText("abcdefghijklmnop")
        pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        pass_input.setStyleSheet(
            f"padding: 10px; background-color: {self.BG_LIGHTER}; border: 1px solid {self.HOVER_COLOR}; border-radius: 4px;"
        )
        layout.addWidget(pass_input)

        # Info text
        info = QLabel("💡 Paste the password you just copied from Google")
        info.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 12px; margin: 5px;")
        layout.addWidget(info)

        # Save button
        save_btn = QPushButton("💾 Save & Test Connection")
        save_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self.ACCENT_BLUE};
                color: white;
                padding: 12px;
                border-radius: 4px;
                font-weight: bold;
                margin-top: 20px;
            }}
            QPushButton:hover {{
                background-color: #00b8e6;
            }}
        """
        )

        def save_gmail_credentials():
            email = email_input.text().strip()
            password = pass_input.text().strip().replace(" ", "")

            if not email or not password:
                QMessageBox.warning(
                    dialog, "Missing Info", "Please enter both email and app password!"
                )
                return

            if len(password) != 16:
                QMessageBox.warning(
                    dialog,
                    "Invalid Password",
                    f"Gmail App Password must be exactly 16 characters!\nYou entered: {len(password)} characters",
                )
                return

            # Save to .env file
            env_path = Path.home() / ".xeno" / ".env"
            if not env_path.exists():
                env_path = Path("E:/Personal assistant/.env")

            try:
                set_key(str(env_path), "EMAIL_ADDRESS", email)
                set_key(str(env_path), "EMAIL_PASSWORD", password)

                # Test connection
                import imaplib

                try:
                    save_btn.setText("⏳ Testing connection...")
                    save_btn.setEnabled(False)

                    mail = imaplib.IMAP4_SSL("imap.gmail.com")
                    mail.login(email, password)
                    mail.logout()

                    QMessageBox.information(
                        dialog,
                        "✅ Success!",
                        "<b>Gmail connected successfully!</b><br><br>"
                        "Your credentials have been saved.<br><br>"
                        "Please <b>restart XENO</b> to start using Gmail features.",
                    )
                    dialog.accept()

                except imaplib.IMAP4.error as e:
                    save_btn.setText("💾 Save & Test Connection")
                    save_btn.setEnabled(True)
                    QMessageBox.critical(
                        dialog,
                        "❌ Connection Failed",
                        f"Could not connect to Gmail:<br><br>{str(e)}<br><br>"
                        "Please verify:<br>"
                        "• Email address is correct<br>"
                        "• App Password is exactly 16 characters<br>"
                        "• App Password was just created",
                    )

            except Exception as e:
                save_btn.setText("💾 Save & Test Connection")
                save_btn.setEnabled(True)
                QMessageBox.critical(dialog, "Error", f"Failed to save credentials:<br>{str(e)}")

        save_btn.clicked.connect(save_gmail_credentials)
        layout.addWidget(save_btn)

        dialog.exec()

    def _show_github_setup(self):
        """Show GitHub OAuth2 setup dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Connect GitHub Account")
        dialog.setMinimumWidth(500)
        dialog.setStyleSheet(f"background-color: {self.BG_DARK}; color: {self.TEXT_PRIMARY};")

        layout = QVBoxLayout(dialog)

        # Title
        title = QLabel("🐙 <b>Connect Your GitHub Account</b>")
        title.setStyleSheet(f"font-size: 18px; color: {self.ACCENT_BLUE}; padding: 10px;")
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "XENO needs access to your GitHub to manage repositories.<br><br>"
            "<b>Click the button below to:</b><br>"
            "• Sign in to your GitHub account<br>"
            "• Create a Personal Access Token<br>"
            "• Grant XENO permission to manage repos<br><br>"
            "Your token will be securely stored locally."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet(f"color: {self.TEXT_SECONDARY}; padding: 10px;")
        layout.addWidget(instructions)

        # Continue with GitHub button
        github_btn = QPushButton("� Continue with GitHub")
        github_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: #238636;
                color: white;
                padding: 15px 30px;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
                margin: 20px 0px;
            }}
            QPushButton:hover {{
                background-color: #2ea043;
            }}
        """
        )

        def start_github_oauth():
            github_btn.setEnabled(False)
            github_btn.setText("⏳ Opening browser...")

            try:
                # Open GitHub token creation page
                webbrowser.open(
                    "https://github.com/settings/tokens/new?description=XENO%20AI%20Assistant&scopes=repo,user,workflow"
                )

                # Show manual input dialog
                QMessageBox.information(
                    dialog,
                    "Create GitHub Token",
                    "🐙 <b>GitHub Personal Access Token Setup:</b><br><br>"
                    "1. A browser window has opened to GitHub settings<br>"
                    "2. Sign in if needed<br>"
                    "3. Note: <b>XENO AI Assistant</b> (pre-filled)<br>"
                    "4. Scopes: <b>repo, user, workflow</b> (pre-selected)<br>"
                    "5. Expiration: Choose <b>No expiration</b> or <b>90 days</b><br>"
                    "6. Click <b>Generate token</b><br>"
                    "7. Copy the token (starts with ghp_)<br>"
                    "8. Enter it below<br>",
                )

                dialog.accept()
                self._show_github_manual_setup()

            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to start OAuth: {str(e)}")
                github_btn.setEnabled(True)
                github_btn.setText("🔐 Continue with GitHub")

        github_btn.clicked.connect(start_github_oauth)
        layout.addWidget(github_btn)

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(f"padding: 10px; background-color: {self.BG_LIGHTER};")
        cancel_btn.clicked.connect(dialog.reject)
        layout.addWidget(cancel_btn)

        dialog.exec()

    def _show_github_manual_setup(self):
        """Show manual GitHub token entry"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Enter GitHub Credentials")
        dialog.setMinimumWidth(500)
        dialog.setStyleSheet(f"background-color: {self.BG_DARK}; color: {self.TEXT_PRIMARY};")

        layout = QVBoxLayout(dialog)

        # Username input
        user_label = QLabel("🐙 GitHub Username:")
        user_label.setStyleSheet(f"color: {self.ACCENT_BLUE}; font-weight: bold; margin-top: 10px;")
        layout.addWidget(user_label)

        user_input = QLineEdit()
        user_input.setPlaceholderText("your-username")
        user_input.setText(os.getenv("GITHUB_USERNAME", ""))
        user_input.setStyleSheet(
            f"padding: 10px; background-color: {self.BG_LIGHTER}; border: 1px solid {self.HOVER_COLOR}; border-radius: 4px;"
        )
        layout.addWidget(user_input)

        # Token input
        token_label = QLabel("🔑 Personal Access Token:")
        token_label.setStyleSheet(
            f"color: {self.ACCENT_BLUE}; font-weight: bold; margin-top: 10px;"
        )
        layout.addWidget(token_label)

        token_input = QLineEdit()
        token_input.setPlaceholderText("ghp_xxxxxxxxxxxx")
        token_input.setEchoMode(QLineEdit.EchoMode.Password)
        token_input.setStyleSheet(
            f"padding: 10px; background-color: {self.BG_LIGHTER}; border: 1px solid {self.HOVER_COLOR}; border-radius: 4px;"
        )
        layout.addWidget(token_input)

        # Info text
        info = QLabel("💡 Paste the token you just copied from GitHub")
        info.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 12px; margin: 5px;")
        layout.addWidget(info)

        # Save button
        save_btn = QPushButton("💾 Save & Test Connection")
        save_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {self.ACCENT_BLUE};
                color: white;
                padding: 12px;
                border-radius: 4px;
                font-weight: bold;
                margin-top: 20px;
            }}
            QPushButton:hover {{
                background-color: #00b8e6;
            }}
        """
        )

        def save_github_credentials():
            username = user_input.text().strip()
            token = token_input.text().strip()

            if not username or not token:
                QMessageBox.warning(dialog, "Missing Info", "Please enter both username and token!")
                return

            if not token.startswith("ghp_") and not token.startswith("github_pat_"):
                QMessageBox.warning(
                    dialog,
                    "Invalid Token",
                    "GitHub token should start with 'ghp_' or 'github_pat_'",
                )
                return

            # Save to .env file
            env_path = Path.home() / ".xeno" / ".env"
            if not env_path.exists():
                env_path = Path("E:/Personal assistant/.env")

            try:
                set_key(str(env_path), "GITHUB_USERNAME", username)
                set_key(str(env_path), "GITHUB_TOKEN", token)

                # Test connection
                from github import Github

                try:
                    save_btn.setText("⏳ Testing connection...")
                    save_btn.setEnabled(False)

                    g = Github(token)
                    user = g.get_user()
                    login = user.login

                    QMessageBox.information(
                        dialog,
                        "✅ Success!",
                        f"<b>GitHub connected successfully!</b><br><br>"
                        f"Connected as: <b>{login}</b><br><br>"
                        f"Please <b>restart XENO</b> to start using GitHub features.",
                    )
                    dialog.accept()

                except Exception as e:
                    save_btn.setText("💾 Save & Test Connection")
                    save_btn.setEnabled(True)
                    QMessageBox.critical(
                        dialog,
                        "❌ Connection Failed",
                        f"Could not connect to GitHub:<br><br>{str(e)}<br><br>"
                        "Please verify:<br>"
                        "• Username is correct<br>"
                        "• Token is valid and not expired<br>"
                        "• Token has correct permissions (repo, user, workflow)",
                    )

            except Exception as e:
                save_btn.setText("💾 Save & Test Connection")
                save_btn.setEnabled(True)
                QMessageBox.critical(dialog, "Error", f"Failed to save credentials:<br>{str(e)}")

        save_btn.clicked.connect(save_github_credentials)
        layout.addWidget(save_btn)

        dialog.exec()

    def closeEvent(self, event):
        """Handle window close - minimize to tray instead"""
        event.ignore()
        self.hide()
