"""
Main XENO Dashboard Window - Discord-inspired Gaming UI
"""
import sys
import webbrowser
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTextEdit, QLineEdit, QScrollArea,
    QFrame, QStackedWidget, QListWidget, QListWidgetItem, QDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon
from datetime import datetime
from dotenv import load_dotenv, set_key


class XenoMainWindow(QMainWindow):
    """Discord-style dark gaming UI for XENO"""
    
    # Gaming color scheme (Discord-inspired)
    BG_DARK = "#1e1e1e"          # Main background
    BG_DARKER = "#141414"        # Sidebar background
    BG_LIGHTER = "#2b2b2b"       # Panel background
    ACCENT_BLUE = "#00d4ff"      # XENO cyan accent
    ACCENT_PURPLE = "#7c3aed"    # Secondary accent
    TEXT_PRIMARY = "#ffffff"     # Main text
    TEXT_SECONDARY = "#a0a0a0"   # Muted text
    HOVER_COLOR = "#323232"      # Hover state
    ONLINE_GREEN = "#3ba55c"     # Online status
    
    def __init__(self, daemon):
        super().__init__()
        self.daemon = daemon
        self.config = daemon.config
        
        # Initialize AI chat
        try:
            from modules.ai_chat import get_ai_chat
            self.ai_chat = get_ai_chat(self.config)
        except Exception as e:
            print(f"Could not initialize AI chat: {e}")
            self.ai_chat = None
        
        # Initialize automation modules
        self._init_automation_modules()
        
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
                    self.config.email.address,
                    self.config.email.password
                )
                print("✓ Email handler initialized")
        except Exception as e:
            print(f"✗ Could not initialize email handler: {e}")
        
        try:
            # GitHub Manager
            if self.config.github and self.config.github.username and self.config.github.token:
                from modules.github_manager import GitHubManager
                self.github_manager = GitHubManager(
                    self.config.github.username,
                    self.config.github.token
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
            if self.config.linkedin and self.config.linkedin.email and self.config.linkedin.password:
                from modules.linkedin_automation import LinkedInAutomation
                self.linkedin_automation = LinkedInAutomation(
                    self.config.linkedin.email,
                    self.config.linkedin.password
                )
                print("✓ LinkedIn automation initialized")
        except Exception as e:
            print(f"✗ Could not initialize LinkedIn automation: {e}")
        
        try:
            # Calendar Sync
            from modules.calendar_sync import CalendarSync
            self.calendar_sync = CalendarSync()
            print("✓ Calendar sync initialized")
        except Exception as e:
            print(f"✗ Could not initialize calendar sync: {e}")
        
    def _apply_theme(self):
        """Apply Discord-style dark gaming theme"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.BG_DARK};
                color: {self.TEXT_PRIMARY};
            }}
            
            QLabel {{
                color: {self.TEXT_PRIMARY};
                background: transparent;
            }}
            
            QPushButton {{
                background-color: {self.BG_LIGHTER};
                color: {self.TEXT_PRIMARY};
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {self.HOVER_COLOR};
            }}
            
            QPushButton:pressed {{
                background-color: {self.ACCENT_BLUE};
            }}
            
            QPushButton#sidebar_button {{
                text-align: left;
                padding: 12px 20px;
                border-radius: 8px;
                margin: 2px 8px;
            }}
            
            QPushButton#sidebar_button:hover {{
                background-color: {self.HOVER_COLOR};
            }}
            
            QPushButton#sidebar_button:checked {{
                background-color: {self.ACCENT_BLUE};
                color: #000000;
            }}
            
            QLineEdit {{
                background-color: {self.BG_LIGHTER};
                color: {self.TEXT_PRIMARY};
                border: 2px solid {self.BG_LIGHTER};
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }}
            
            QLineEdit:focus {{
                border: 2px solid {self.ACCENT_BLUE};
            }}
            
            QTextEdit {{
                background-color: {self.BG_LIGHTER};
                color: {self.TEXT_PRIMARY};
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }}
            
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            
            QScrollBar:vertical {{
                background-color: {self.BG_DARKER};
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {self.ACCENT_BLUE};
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {self.ACCENT_PURPLE};
            }}
            
            QListWidget {{
                background-color: {self.BG_LIGHTER};
                color: {self.TEXT_PRIMARY};
                border: none;
                border-radius: 8px;
                padding: 8px;
            }}
            
            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
            }}
            
            QListWidget::item:hover {{
                background-color: {self.HOVER_COLOR};
            }}
            
            QListWidget::item:selected {{
                background-color: {self.ACCENT_BLUE};
                color: #000000;
            }}
            
            QFrame#panel {{
                background-color: {self.BG_LIGHTER};
                border-radius: 8px;
                padding: 16px;
            }}
        """)
        
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
        self.settings_page = self._create_settings_page()
        
        self.content_stack.addWidget(self.chat_page)
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.email_page)
        self.content_stack.addWidget(self.jobs_page)
        self.content_stack.addWidget(self.github_page)
        self.content_stack.addWidget(self.settings_page)
        
        main_layout.addWidget(self.content_stack, 1)
        
    def _create_sidebar(self):
        """Create Discord-style sidebar"""
        sidebar = QFrame()
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {self.BG_DARKER};
                border-right: 1px solid #000000;
            }}
        """)
        sidebar.setFixedWidth(250)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(8)
        
        # XENO logo/header
        header = QLabel("XENO")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {self.ACCENT_BLUE};
            padding: 20px;
            letter-spacing: 4px;
        """)
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
            ("📧 Email", 2),
            ("💼 Jobs", 3),
            ("⚙️ GitHub", 4),
            ("⚙️ Settings", 5),
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
        user_frame.setStyleSheet(f"""
            background-color: {self.BG_LIGHTER};
            border-radius: 8px;
            padding: 12px;
            margin: 0 8px;
        """)
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
        header.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {self.ACCENT_BLUE}; margin-bottom: 10px;")
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
        send_btn.setStyleSheet(f"""
            background-color: {self.ACCENT_BLUE};
            color: #000000;
            font-weight: bold;
            padding: 10px 30px;
        """)
        send_btn.clicked.connect(self._send_message)
        
        input_layout.addWidget(self.chat_input, 1)
        input_layout.addWidget(send_btn)
        
        layout.addLayout(input_layout)
        
        return page
        
    def _create_dashboard_page(self):
        """Create dashboard overview"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel("Dashboard")
        header.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {self.ACCENT_BLUE}; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Stats panels - Load real stats
        stats_layout = QHBoxLayout()
        
        # Get real stats
        email_count = self._get_email_count()
        jobs_count = self._get_jobs_count()
        github_repos = self._get_github_repo_count()
        
        stats = [
            ("Unread Emails", str(email_count), "📧"),
            ("Saved Jobs", str(jobs_count), "💼"),
            ("GitHub Repos", str(github_repos), "⚙️"),
            ("AI Chat Active", "✓" if self.ai_chat else "✗", "🤖"),
        ]
        
        for title, value, icon in stats:
            panel = self._create_stat_panel(icon, title, value)
            stats_layout.addWidget(panel)
        
        layout.addLayout(stats_layout)
        
        # Recent activity
        activity_label = QLabel("Recent Activity")
        activity_label.setStyleSheet(f"font-size: 18px; font-weight: bold; margin-top: 20px; margin-bottom: 10px;")
        layout.addWidget(activity_label)
        
        activity_list = QListWidget()
        activity_list.addItem("✓ XENO started successfully")
        user_name = self.config.user.name if self.config.user.name else "User"
        activity_list.addItem(f"✓ Configuration loaded for {user_name}")
        
        # Add module status
        if self.email_handler:
            activity_list.addItem("✓ Email module: Connected")
        if self.github_manager:
            activity_list.addItem("✓ GitHub module: Connected")
        if self.job_automation:
            activity_list.addItem("✓ Job automation: Ready")
        if self.ai_chat:
            activity_list.addItem("✓ AI Chat: Ready")
        
        activity_list.addItem("✓ All systems online")
        layout.addWidget(activity_list, 1)
        
        return page
    
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
        try:
            from core.database import get_session
            from models.database import JobApplication
            session = get_session()
            count = session.query(JobApplication).count()
            session.close()
            return count
        except:
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
        """Create email management page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel("📧 Email Management")
        header.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {self.ACCENT_BLUE}; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Action buttons (always show)
        btn_layout = QHBoxLayout()
        
        # Gmail Setup Button (opens credential dialog)
        gmail_setup_btn = QPushButton("⚙️ Setup Gmail Credentials")
        gmail_setup_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.ACCENT_BLUE};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #00b8e6;
            }}
        """)
        gmail_setup_btn.clicked.connect(self._show_gmail_setup)
        btn_layout.addWidget(gmail_setup_btn)
        
        # Gmail Login Button (opens Gmail in browser)
        gmail_login_btn = QPushButton("🌐 Open Gmail")
        gmail_login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #4285F4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #357AE8;
            }}
        """)
        gmail_login_btn.clicked.connect(lambda: self._open_login_page("https://mail.google.com"))
        btn_layout.addWidget(gmail_login_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        if not self.email_handler:
            info = QLabel("⚠️ <b>Email not configured.</b><br><br>"
                         "Click <b>'⚙️ Setup Gmail Credentials'</b> button above to:<br>"
                         "• Enter your Gmail address<br>"
                         "• Get and enter your App Password<br>"
                         "• Test connection automatically<br><br>"
                         "Then restart XENO to see your emails!")
            info.setWordWrap(True)
            info.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 14px; margin: 20px;")
            layout.addWidget(info)
            layout.addStretch()
            return page
        
        # Refresh button
        refresh_btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Refresh Emails")
        refresh_btn.clicked.connect(self._refresh_emails)
        refresh_btn_layout.addWidget(refresh_btn)
        refresh_btn_layout.addStretch()
        layout.addLayout(refresh_btn_layout)
        
        # Email list
        self.email_list = QListWidget()
        self.email_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {self.BG_LIGHTER};
                border: 1px solid {self.HOVER_COLOR};
                border-radius: 4px;
                padding: 10px;
            }}
            QListWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {self.HOVER_COLOR};
            }}
            QListWidget::item:hover {{
                background-color: {self.HOVER_COLOR};
            }}
        """)
        layout.addWidget(self.email_list, 1)
        
        # Auto-load emails
        QTimer.singleShot(500, self._refresh_emails)
        
        return page
    
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
                item_text = f"From: {email['from']}\nSubject: {email['subject']}\nDate: {email['date']}"
                self.email_list.addItem(item_text)
            
        except Exception as e:
            self.email_list.clear()
            self.email_list.addItem(f"❌ Error: {str(e)}")
        
    def _create_jobs_page(self):
        """Create job applications page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel("💼 Job Applications")
        header.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {self.ACCENT_BLUE}; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # LinkedIn Login Button (always show)
        linkedin_layout = QHBoxLayout()
        
        linkedin_login_btn = QPushButton("🌐 Login to LinkedIn")
        linkedin_login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #0A66C2;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #004182;
            }}
        """)
        linkedin_login_btn.clicked.connect(lambda: self._open_login_page("https://www.linkedin.com"))
        linkedin_layout.addWidget(linkedin_login_btn)
        
        indeed_btn = QPushButton("🌐 Visit Indeed")
        indeed_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #2164F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1850C9;
            }}
        """)
        indeed_btn.clicked.connect(lambda: self._open_login_page("https://www.indeed.com"))
        linkedin_layout.addWidget(indeed_btn)
        
        linkedin_layout.addStretch()
        layout.addLayout(linkedin_layout)
        
        if not self.job_automation:
            info = QLabel("⚠️ Job automation not available.\n\nYou can still use the login buttons above to search manually.")
            info.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 14px; margin: 20px;")
            layout.addWidget(info)
            layout.addStretch()
            return page
        
        # Search controls
        search_layout = QHBoxLayout()
        self.job_title_input = QLineEdit()
        self.job_title_input.setPlaceholderText("Job title (e.g., Python Developer)")
        search_layout.addWidget(self.job_title_input)
        
        self.job_location_input = QLineEdit()
        self.job_location_input.setPlaceholderText("Location (optional)")
        search_layout.addWidget(self.job_location_input)
        
        search_btn = QPushButton("🔍 Search Jobs")
        search_btn.clicked.connect(self._search_jobs)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # Job list
        self.job_list = QListWidget()
        self.job_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {self.BG_LIGHTER};
                border: 1px solid {self.HOVER_COLOR};
                border-radius: 4px;
                padding: 10px;
            }}
            QListWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {self.HOVER_COLOR};
            }}
            QListWidget::item:hover {{
                background-color: {self.HOVER_COLOR};
            }}
        """)
        layout.addWidget(self.job_list, 1)
        
        return page
    
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
            jobs = self.job_automation.search_all_platforms(job_title, location, max_per_platform=10)
            
            self.job_list.clear()
            
            if not jobs:
                self.job_list.addItem("No jobs found")
                return
            
            for job in jobs:
                item_text = f"{job['title']}\n{job['company']} - {job['location']}\nSource: {job['source']}"
                self.job_list.addItem(item_text)
            
        except Exception as e:
            self.job_list.clear()
            self.job_list.addItem(f"❌ Error: {str(e)}")
        
    def _create_github_page(self):
        """Create GitHub management page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel("⚙️ GitHub Management")
        header.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {self.ACCENT_BLUE}; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # GitHub Login Buttons (always show)
        login_layout = QHBoxLayout()
        
        # GitHub Setup Button (opens credential dialog)
        github_setup_btn = QPushButton("⚙️ Setup GitHub Credentials")
        github_setup_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.ACCENT_BLUE};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #00b8e6;
            }}
        """)
        github_setup_btn.clicked.connect(self._show_github_setup)
        login_layout.addWidget(github_setup_btn)
        
        # GitHub Login Button (opens GitHub in browser)
        github_login_btn = QPushButton("🌐 Open GitHub")
        github_login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #238636;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2ea043;
            }}
        """)
        github_login_btn.clicked.connect(lambda: self._open_login_page("https://github.com"))
        login_layout.addWidget(github_login_btn)
        
        login_layout.addStretch()
        layout.addLayout(login_layout)
        
        if not self.github_manager:
            info = QLabel("⚠️ <b>GitHub not configured.</b><br><br>"
                         "Click <b>'⚙️ Setup GitHub Credentials'</b> button above to:<br>"
                         "• Enter your GitHub username<br>"
                         "• Get and enter your Personal Access Token<br>"
                         "• Test connection automatically<br><br>"
                         "Then restart XENO to manage your repositories!")
            info.setWordWrap(True)
            info.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 14px; margin: 20px;")
            layout.addWidget(info)
            layout.addStretch()
            return page
        
        # Action buttons
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Refresh Repositories")
        refresh_btn.clicked.connect(self._refresh_github_repos)
        btn_layout.addWidget(refresh_btn)
        
        stats_btn = QPushButton("📊 View Stats")
        stats_btn.clicked.connect(self._show_github_stats)
        btn_layout.addWidget(stats_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Repo list
        self.github_list = QListWidget()
        self.github_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {self.BG_LIGHTER};
                border: 1px solid {self.HOVER_COLOR};
                border-radius: 4px;
                padding: 10px;
            }}
            QListWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {self.HOVER_COLOR};
            }}
            QListWidget::item:hover {{
                background-color: {self.HOVER_COLOR};
            }}
        """)
        layout.addWidget(self.github_list, 1)
        
        # Auto-load repos
        QTimer.singleShot(500, self._refresh_github_repos)
        
        return page
    
    def _refresh_github_repos(self):
        """Refresh GitHub repositories."""
        if not self.github_manager:
            return
        
        try:
            self.github_list.clear()
            self.github_list.addItem("Loading repositories...")
            
            # Connect and get repos
            if not self.github_manager.connect():
                self.github_list.clear()
                self.github_list.addItem("❌ Failed to connect to GitHub")
                return
            
            repos = self.github_manager.get_repositories()
            self.github_list.clear()
            
            if not repos:
                self.github_list.addItem("No repositories found")
                return
            
            for repo in repos:
                item_text = (f"{repo['name']}\n"
                           f"⭐ {repo['stars']} | 🍴 {repo['forks']} | {repo['language']}\n"
                           f"{repo['description'][:100] if repo['description'] else 'No description'}")
                self.github_list.addItem(item_text)
            
        except Exception as e:
            self.github_list.clear()
            self.github_list.addItem(f"❌ Error: {str(e)}")
    
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
                f"Total Forks: {stats.get('total_forks', 0)}"
            )
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", f"Failed to get stats: {str(e)}")
        
    def _create_settings_page(self):
        """Create settings page"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel("⚙️ Settings")
        header.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {self.ACCENT_BLUE}; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Settings panels
        voice_panel = self._create_settings_panel(
            "Voice Settings",
            f"Voice Enabled: {'Yes' if self.config.user.voice_enabled else 'No'}"
        )
        layout.addWidget(voice_panel)
        
        ai_panel = self._create_settings_panel(
            "AI Configuration",
            f"Provider: {self.config.ai.provider if self.config.ai else 'Not configured'}"
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
        self.chat_history.append(f'<div style="color: {self.ACCENT_BLUE}; font-weight: bold;">You:</div>')
        self.chat_history.append(f'<div style="margin-bottom: 15px;">{message}</div>')
        
        # Clear input
        self.chat_input.clear()
        
        # Send to AI and get response
        if self.ai_chat and self.ai_chat.is_available():
            # Show thinking indicator
            self.chat_history.append(f'<div style="color: {self.ACCENT_PURPLE}; font-weight: bold;">XENO:</div>')
            self.chat_history.append(f'<div style="margin-bottom: 15px; color: {self.TEXT_SECONDARY};">Thinking...</div>')
            
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
                self.chat_history.append(f'<div style="margin-bottom: 15px; color: #ff6b6b;">Error: {str(e)}</div>')
        else:
            self.chat_history.append(f'<div style="color: {self.ACCENT_PURPLE}; font-weight: bold;">XENO:</div>')
            self.chat_history.append(f'<div style="margin-bottom: 15px;">AI module not yet connected. Please add your OpenAI API key in Settings → Run setup again with: python src\\jarvis.py --setup</div>')
    
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
        google_btn.setStyleSheet(f"""
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
        """)
        
        def start_gmail_oauth():
            google_btn.setEnabled(False)
            google_btn.setText("⏳ Opening browser...")
            
            try:
                # For now, open App Password page (OAuth2 requires Google API credentials)
                # Full OAuth2 will be implemented in next version
                webbrowser.open("https://myaccount.google.com/apppasswords")
                
                # Show manual input dialog
                QMessageBox.information(dialog, "Get App Password",
                    "📧 <b>Gmail App Password Setup:</b><br><br>"
                    "1. A browser window has opened to Google Account settings<br>"
                    "2. Sign in if needed<br>"
                    "3. App name: <b>XENO Assistant</b><br>"
                    "4. Device: <b>Windows Computer</b><br>"
                    "5. Click <b>Generate</b><br>"
                    "6. Copy the 16-character password<br>"
                    "7. Enter it below (spaces will be removed)<br>")
                
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
        email_label.setStyleSheet(f"color: {self.ACCENT_BLUE}; font-weight: bold; margin-top: 10px;")
        layout.addWidget(email_label)
        
        email_input = QLineEdit()
        email_input.setPlaceholderText("your.email@gmail.com")
        email_input.setText(os.getenv('EMAIL_ADDRESS', ''))
        email_input.setStyleSheet(f"padding: 10px; background-color: {self.BG_LIGHTER}; border: 1px solid {self.HOVER_COLOR}; border-radius: 4px;")
        layout.addWidget(email_input)
        
        # Password input
        pass_label = QLabel("🔑 App Password (16 characters, no spaces):")
        pass_label.setStyleSheet(f"color: {self.ACCENT_BLUE}; font-weight: bold; margin-top: 10px;")
        layout.addWidget(pass_label)
        
        pass_input = QLineEdit()
        pass_input.setPlaceholderText("abcdefghijklmnop")
        pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        pass_input.setStyleSheet(f"padding: 10px; background-color: {self.BG_LIGHTER}; border: 1px solid {self.HOVER_COLOR}; border-radius: 4px;")
        layout.addWidget(pass_input)
        
        # Info text
        info = QLabel("💡 Paste the password you just copied from Google")
        info.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 12px; margin: 5px;")
        layout.addWidget(info)
        
        # Save button
        save_btn = QPushButton("💾 Save & Test Connection")
        save_btn.setStyleSheet(f"""
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
        """)
        
        def save_gmail_credentials():
            email = email_input.text().strip()
            password = pass_input.text().strip().replace(' ', '')
            
            if not email or not password:
                QMessageBox.warning(dialog, "Missing Info", "Please enter both email and app password!")
                return
            
            if len(password) != 16:
                QMessageBox.warning(dialog, "Invalid Password", 
                    f"Gmail App Password must be exactly 16 characters!\nYou entered: {len(password)} characters")
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
                    
                    mail = imaplib.IMAP4_SSL('imap.gmail.com')
                    mail.login(email, password)
                    mail.logout()
                    
                    QMessageBox.information(dialog, "✅ Success!", 
                        "<b>Gmail connected successfully!</b><br><br>"
                        "Your credentials have been saved.<br><br>"
                        "Please <b>restart XENO</b> to start using Gmail features.")
                    dialog.accept()
                    
                except imaplib.IMAP4.error as e:
                    save_btn.setText("💾 Save & Test Connection")
                    save_btn.setEnabled(True)
                    QMessageBox.critical(dialog, "❌ Connection Failed", 
                        f"Could not connect to Gmail:<br><br>{str(e)}<br><br>"
                        "Please verify:<br>"
                        "• Email address is correct<br>"
                        "• App Password is exactly 16 characters<br>"
                        "• App Password was just created")
                    
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
        github_btn.setStyleSheet(f"""
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
        """)
        
        def start_github_oauth():
            github_btn.setEnabled(False)
            github_btn.setText("⏳ Opening browser...")
            
            try:
                # Open GitHub token creation page
                webbrowser.open("https://github.com/settings/tokens/new?description=XENO%20AI%20Assistant&scopes=repo,user,workflow")
                
                # Show manual input dialog
                QMessageBox.information(dialog, "Create GitHub Token",
                    "🐙 <b>GitHub Personal Access Token Setup:</b><br><br>"
                    "1. A browser window has opened to GitHub settings<br>"
                    "2. Sign in if needed<br>"
                    "3. Note: <b>XENO AI Assistant</b> (pre-filled)<br>"
                    "4. Scopes: <b>repo, user, workflow</b> (pre-selected)<br>"
                    "5. Expiration: Choose <b>No expiration</b> or <b>90 days</b><br>"
                    "6. Click <b>Generate token</b><br>"
                    "7. Copy the token (starts with ghp_)<br>"
                    "8. Enter it below<br>")
                
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
        user_input.setText(os.getenv('GITHUB_USERNAME', ''))
        user_input.setStyleSheet(f"padding: 10px; background-color: {self.BG_LIGHTER}; border: 1px solid {self.HOVER_COLOR}; border-radius: 4px;")
        layout.addWidget(user_input)
        
        # Token input
        token_label = QLabel("🔑 Personal Access Token:")
        token_label.setStyleSheet(f"color: {self.ACCENT_BLUE}; font-weight: bold; margin-top: 10px;")
        layout.addWidget(token_label)
        
        token_input = QLineEdit()
        token_input.setPlaceholderText("ghp_xxxxxxxxxxxx")
        token_input.setEchoMode(QLineEdit.EchoMode.Password)
        token_input.setStyleSheet(f"padding: 10px; background-color: {self.BG_LIGHTER}; border: 1px solid {self.HOVER_COLOR}; border-radius: 4px;")
        layout.addWidget(token_input)
        
        # Info text
        info = QLabel("💡 Paste the token you just copied from GitHub")
        info.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 12px; margin: 5px;")
        layout.addWidget(info)
        
        # Save button
        save_btn = QPushButton("💾 Save & Test Connection")
        save_btn.setStyleSheet(f"""
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
        """)
        
        def save_github_credentials():
            username = user_input.text().strip()
            token = token_input.text().strip()
            
            if not username or not token:
                QMessageBox.warning(dialog, "Missing Info", "Please enter both username and token!")
                return
            
            if not token.startswith('ghp_') and not token.startswith('github_pat_'):
                QMessageBox.warning(dialog, "Invalid Token", 
                    "GitHub token should start with 'ghp_' or 'github_pat_'")
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
                    
                    QMessageBox.information(dialog, "✅ Success!", 
                        f"<b>GitHub connected successfully!</b><br><br>"
                        f"Connected as: <b>{login}</b><br><br>"
                        f"Please <b>restart XENO</b> to start using GitHub features.")
                    dialog.accept()
                    
                except Exception as e:
                    save_btn.setText("💾 Save & Test Connection")
                    save_btn.setEnabled(True)
                    QMessageBox.critical(dialog, "❌ Connection Failed", 
                        f"Could not connect to GitHub:<br><br>{str(e)}<br><br>"
                        "Please verify:<br>"
                        "• Username is correct<br>"
                        "• Token is valid and not expired<br>"
                        "• Token has correct permissions (repo, user, workflow)")
                    
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
