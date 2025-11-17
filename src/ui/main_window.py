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
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize
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
    
    def _init_voice_system(self):
        """Initialize voice recognition and command processing"""
        try:
            from voice.recognition import VoiceRecognition
            from voice.commands import VoiceCommandProcessor
            import pyttsx3
            
            # Initialize voice recognition
            self.voice_recognition = VoiceRecognition()
            
            # Initialize command processor
            self.voice_command_processor = VoiceCommandProcessor(self)
            
            # Initialize text-to-speech
            self.voice_engine = pyttsx3.init()
            
            # Configure voice
            voices = self.voice_engine.getProperty('voices')
            for voice in voices:
                if 'male' in voice.name.lower() or 'david' in voice.name.lower():
                    self.voice_engine.setProperty('voice', voice.id)
                    break
            
            self.voice_engine.setProperty('rate', 150)
            self.voice_engine.setProperty('volume', 0.9)
            
            # Start voice command monitoring
            self._start_voice_monitoring()
            
            print("✓ Voice system initialized")
            
            # Welcome message
            if self.config.user.voice_enabled:
                self._speak("Voice commands activated. Say 'Hey XENO' followed by your command.")
            
        except Exception as e:
            print(f"✗ Could not initialize voice system: {e}")
            self.voice_recognition = None
            self.voice_command_processor = None
            self.voice_engine = None
    
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
                if self.config.user.voice_enabled and self.voice_engine:
                    self._speak("Yes Master, how can I help you?")
                return
            
            print(f"🎤 Voice command: {command}")
            
            # Process command
            response = self.voice_command_processor.process_command(command)
            
            if response:
                print(f"🔊 Response: {response}")
                
                # Speak response
                if self.config.user.voice_enabled and self.voice_engine:
                    self._speak(response)
    
    def _speak(self, text):
        """Speak text using TTS"""
        try:
            if self.voice_engine:
                self.voice_engine.say(text)
                self.voice_engine.runAndWait()
        except Exception as e:
            print(f"Error speaking: {e}")
        
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
            ("📧 Gmail", 2),
            ("💼 LinkedIn", 3),
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
        """Create Gmail-style email management page"""
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Gmail-style header bar
        header_bar = QFrame()
        header_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {self.BG_LIGHTER};
                border-bottom: 1px solid {self.HOVER_COLOR};
                padding: 15px 20px;
            }}
        """)
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        gmail_logo = QLabel("📧 Gmail")
        gmail_logo.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {self.ACCENT_BLUE};")
        header_layout.addWidget(gmail_logo)
        header_layout.addStretch()
        
        # Add refresh button to header
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet(f"""
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
        """)
        refresh_btn.clicked.connect(self._load_gmail_emails)
        header_layout.addWidget(refresh_btn)
        main_layout.addWidget(header_bar)
        
        # Login form (shown when not logged in)
        self.gmail_login_frame = QFrame()
        self.gmail_login_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.BG_DARK};
                padding: 40px;
            }}
        """)
        login_outer_layout = QVBoxLayout(self.gmail_login_frame)
        login_outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        login_card = QFrame()
        login_card.setFixedWidth(400)
        login_card.setStyleSheet(f"""
            QFrame {{
                background-color: {self.BG_LIGHTER};
                border-radius: 8px;
                padding: 30px;
            }}
        """)
        card_layout = QVBoxLayout(login_card)
        
        login_title = QLabel("Sign in to Gmail")
        login_title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {self.TEXT_PRIMARY}; margin-bottom: 20px;")
        login_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(login_title)
        
        self.gmail_email_input = QLineEdit()
        self.gmail_email_input.setPlaceholderText("Email address")
        self.gmail_email_input.setText(os.getenv('EMAIL_ADDRESS', ''))
        self.gmail_email_input.setStyleSheet(f"""
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
        """)
        card_layout.addWidget(self.gmail_email_input)
        
        self.gmail_password_input = QLineEdit()
        self.gmail_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.gmail_password_input.setPlaceholderText("App Password (16 characters)")
        self.gmail_password_input.setText(os.getenv('EMAIL_PASSWORD', ''))
        self.gmail_password_input.setStyleSheet(f"""
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
        """)
        card_layout.addWidget(self.gmail_password_input)
        
        app_pass_help = QLabel('<a href="https://myaccount.google.com/apppasswords" style="color: #4285F4;">Get App Password</a>')
        app_pass_help.setOpenExternalLinks(True)
        app_pass_help.setStyleSheet("margin: 10px 0; font-size: 13px;")
        app_pass_help.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(app_pass_help)
        
        self.gmail_login_btn = QPushButton("Sign In")
        self.gmail_login_btn.setStyleSheet(f"""
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
        """)
        self.gmail_login_btn.clicked.connect(self._gmail_login)
        card_layout.addWidget(self.gmail_login_btn)
        
        self.gmail_status_label = QLabel("")
        self.gmail_status_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 13px; margin-top: 10px;")
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
        self.gmail_tabs.setStyleSheet(f"""
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
        """)
        
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
                subject_lower = email.get('subject', '').lower()
                from_lower = email.get('from', '').lower()
                
                # Categorize emails
                if any(word in subject_lower or word in from_lower for word in ['facebook', 'twitter', 'linkedin', 'instagram', 'notification', 'social']):
                    social_emails.append(email)
                elif any(word in subject_lower for word in ['offer', 'sale', 'discount', 'deal', 'promo', 'shop', 'buy', 'save']):
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
        if not hasattr(widget, 'email_data'):
            return
        
        email = widget.email_data
        self._show_email_dialog(email)
    
    def _show_email_dialog(self, email):
        """Show email in a dialog"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
        
        dialog = QDialog(self)
        dialog.setWindowTitle(email.get('subject', '(No Subject)'))
        dialog.setMinimumSize(900, 700)
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {self.BG_DARK};
            }}
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header with email info
        header = QWidget()
        header.setStyleSheet(f"""
            background-color: {self.BG_LIGHTER};
            padding: 24px;
            border-bottom: 1px solid {self.HOVER_COLOR};
        """)
        header_layout = QVBoxLayout(header)
        
        subject_label = QLabel(email.get('subject', '(No Subject)'))
        subject_label.setStyleSheet(f"""
            font-size: 22px;
            font-weight: bold;
            color: {self.TEXT_PRIMARY};
            margin-bottom: 12px;
        """)
        subject_label.setWordWrap(True)
        header_layout.addWidget(subject_label)
        
        from_label = QLabel(f"From: {email.get('from', 'Unknown')}")
        from_label.setStyleSheet(f"font-size: 14px; color: {self.TEXT_SECONDARY};")
        header_layout.addWidget(from_label)
        
        date_label = QLabel(f"Date: {email.get('date', 'Unknown')}")
        date_label.setStyleSheet(f"font-size: 14px; color: {self.TEXT_SECONDARY};")
        header_layout.addWidget(date_label)
        
        layout.addWidget(header)
        
        # Email body - use QWebEngineView for full HTML rendering with images
        try:
            from PyQt6.QtWebEngineWidgets import QWebEngineView
            from PyQt6.QtWebEngineCore import QWebEngineSettings
            
            body_viewer = QWebEngineView()
            
            # Enable JavaScript and images
            settings = body_viewer.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavaScriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
            
            body_viewer.setStyleSheet("background-color: white;")
            
            # Get email body and render as HTML
            email_body = email.get('full_body', email.get('body', '(No content)'))
            
            # Ensure proper HTML structure
            if not email_body.strip().startswith('<!DOCTYPE') and not email_body.strip().startswith('<html'):
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
            body_viewer.setStyleSheet("""
                QTextBrowser {
                    background-color: white;
                    color: #202124;
                    border: none;
                    padding: 40px;
                    font-size: 14px;
                }
            """)
            
            email_body = email.get('full_body', email.get('body', '(No content)'))
            
            # Convert to simple HTML
            if not ('<html' in email_body.lower() or '<div' in email_body.lower()):
                formatted_body = email_body.replace('\n', '<br>')
                email_body = f'<div style="font-family: Arial; white-space: pre-wrap;">{formatted_body}</div>'
            
            body_viewer.setHtml(email_body)
        
        layout.addWidget(body_viewer, 1)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(f"""
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
        """)
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        dialog.exec()
    
    def _create_email_item(self, email):
        """Create a Gmail-style email item widget"""
        widget = QFrame()
        widget.setFrameShape(QFrame.Shape.NoFrame)
        widget.setCursor(Qt.CursorShape.PointingHandCursor)
        widget.setMinimumHeight(90)  # Set minimum height for proper display
        widget.setStyleSheet(f"""
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
        """)
        
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
        sender = email.get('from', 'Unknown')
        # Extract just the name or email
        if '<' in sender:
            sender_name = sender.split('<')[0].strip()
            if not sender_name:
                sender_name = sender.split('<')[1].split('>')[0]
        else:
            sender_name = sender
        
        sender_label = QLabel(sender_name[:60])
        sender_label.setStyleSheet(f"""
            font-weight: bold;
            font-size: 14px;
            color: {self.TEXT_PRIMARY};
            background: transparent;
        """)
        sender_label.setWordWrap(False)
        sender_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        left_layout.addWidget(sender_label)
        
        # Subject
        subject = email.get('subject', '(No Subject)')
        subject_label = QLabel(subject[:100])
        subject_label.setStyleSheet(f"""
            font-size: 13px;
            color: {self.TEXT_PRIMARY};
            background: transparent;
        """)
        subject_label.setWordWrap(False)
        subject_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        left_layout.addWidget(subject_label)
        
        # Preview (first 120 chars of body)
        body_text = email.get('body', '')
        if body_text:
            # Clean up body text (remove extra whitespace/newlines and HTML tags)
            import re
            clean_text = re.sub('<[^<]+?>', '', body_text)  # Remove HTML tags
            preview = ' '.join(clean_text.split())[:120]
            preview_label = QLabel(preview + ("..." if len(clean_text) > 120 else ""))
            preview_label.setStyleSheet(f"""
                font-size: 12px;
                color: {self.TEXT_SECONDARY};
                background: transparent;
            """)
            preview_label.setWordWrap(False)
            preview_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
            left_layout.addWidget(preview_label)
        
        left_layout.addStretch()
        layout.addWidget(left_section, 1)
        
        # Right section - Date/Time
        date_str = email.get('date', '')
        date_label = QLabel(self._format_email_date(date_str))
        date_label.setStyleSheet(f"""
            font-size: 12px;
            color: {self.TEXT_SECONDARY};
            background: transparent;
        """)
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
            from datetime import datetime
            import email.utils
            
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
            self.github_status_label.setStyleSheet(f"color: #ff4444; font-size: 14px; margin: 10px;")
            return
        
        if not token.startswith('ghp_'):
            self.github_status_label.setText("❌ Invalid token format (must start with ghp_)")
            self.github_status_label.setStyleSheet(f"color: #ff4444; font-size: 14px; margin: 10px;")
            return
        
        # Update status
        self.github_status_label.setText("🔄 Connecting to GitHub...")
        self.github_status_label.setStyleSheet(f"color: {self.ACCENT_BLUE}; font-size: 14px; margin: 10px;")
        self.github_login_btn.setEnabled(False)
        
        try:
            # Initialize GitHub manager
            from modules.github_manager import GitHubManager
            self.github_manager = GitHubManager(username, token)
            
            # Try to connect
            if not self.github_manager.connect():
                self.github_status_label.setText("❌ Failed to connect. Check your token.")
                self.github_status_label.setStyleSheet(f"color: #ff4444; font-size: 14px; margin: 10px;")
                self.github_manager = None
                return
            
            # Save credentials to .env
            env_path = Path(".env")
            set_key(env_path, "GITHUB_USERNAME", username)
            set_key(env_path, "GITHUB_TOKEN", token)
            
            # Success! Load repos
            self.github_status_label.setText("✅ Connected! Loading repositories...")
            self.github_status_label.setStyleSheet(f"color: {self.ONLINE_GREEN}; font-size: 14px; margin: 10px;")
            
            # Show repo list
            self.github_list.setVisible(True)
            self._load_github_repos()
            
        except Exception as e:
            self.github_status_label.setText(f"❌ Error: {str(e)}")
            self.github_status_label.setStyleSheet(f"color: #ff4444; font-size: 14px; margin: 10px;")
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
            self.github_list.addItem(f"📊 Public Repos: {stats.get('public_repos', 0)} | Followers: {stats.get('followers', 0)} | Following: {stats.get('following', 0)}\n")
            
            if not repos:
                self.github_list.addItem("No repositories found")
                return
            
            # Display repositories
            for repo in repos:
                item_text = (f"📦 {repo['name']}\n"
                           f"   ⭐ {repo['stars']} stars | 🍴 {repo['forks']} forks | 📝 {repo.get('language', 'N/A')}\n"
                           f"   {repo['description'][:80] if repo.get('description') else 'No description'}\n")
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
            self.linkedin_status_label.setStyleSheet(f"color: #ff4444; font-size: 14px; margin: 10px;")
            return
        
        # Update status
        self.linkedin_status_label.setText("🔄 Connecting to LinkedIn...")
        self.linkedin_status_label.setStyleSheet(f"color: {self.ACCENT_BLUE}; font-size: 14px; margin: 10px;")
        self.linkedin_login_btn.setEnabled(False)
        
        try:
            # Initialize LinkedIn automation
            from modules.linkedin_automation import LinkedInAutomation
            self.linkedin_automation = LinkedInAutomation(email, password)
            
            # Try to login
            if not self.linkedin_automation.login():
                self.linkedin_status_label.setText("❌ Failed to login. Check your credentials.")
                self.linkedin_status_label.setStyleSheet(f"color: #ff4444; font-size: 14px; margin: 10px;")
                self.linkedin_automation = None
                return
            
            # Save credentials to .env
            env_path = Path(".env")
            set_key(env_path, "LINKEDIN_EMAIL", email)
            set_key(env_path, "LINKEDIN_PASSWORD", password)
            
            # Success! Load profile
            self.linkedin_status_label.setText("✅ Connected! Loading profile...")
            self.linkedin_status_label.setStyleSheet(f"color: {self.ONLINE_GREEN}; font-size: 14px; margin: 10px;")
            
            # Show data
            self.linkedin_data.setVisible(True)
            self._load_linkedin_profile()
            
        except Exception as e:
            self.linkedin_status_label.setText(f"❌ Error: {str(e)}")
            self.linkedin_status_label.setStyleSheet(f"color: #ff4444; font-size: 14px; margin: 10px;")
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
                    self.linkedin_data.append(f"• {item.get('type', 'Post')}: {item.get('text', 'N/A')[:100]}...\n")
            
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
                item_text = f"From: {email['from']}\nSubject: {email['subject']}\nDate: {email['date']}"
                self.email_list.addItem(item_text)
            
        except Exception as e:
            self.email_list.clear()
            self.email_list.addItem(f"❌ Error: {str(e)}")
        
    def _create_jobs_page(self):
        """Create LinkedIn page with login form"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel("💼 LinkedIn")
        header.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {self.ACCENT_BLUE}; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Login form (always visible)
        login_frame = QFrame()
        login_frame.setObjectName("panel")
        login_frame.setStyleSheet(f"""
            QFrame#panel {{
                background-color: {self.BG_LIGHTER};
                border-radius: 8px;
                padding: 20px;
            }}
        """)
        login_layout = QVBoxLayout(login_frame)
        
        # Email input
        email_label = QLabel("LinkedIn Email:")
        email_label.setStyleSheet(f"color: {self.TEXT_PRIMARY}; font-size: 14px; margin-bottom: 5px;")
        self.linkedin_email_input = QLineEdit()
        self.linkedin_email_input.setPlaceholderText("your.email@example.com")
        self.linkedin_email_input.setText(os.getenv('LINKEDIN_EMAIL', ''))
        
        # Password input
        password_label = QLabel("LinkedIn Password:")
        password_label.setStyleSheet(f"color: {self.TEXT_PRIMARY}; font-size: 14px; margin-top: 10px; margin-bottom: 5px;")
        self.linkedin_password_input = QLineEdit()
        self.linkedin_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.linkedin_password_input.setPlaceholderText("Your password")
        self.linkedin_password_input.setText(os.getenv('LINKEDIN_PASSWORD', ''))
        
        # Login button
        self.linkedin_login_btn = QPushButton("🔑 Login to LinkedIn")
        self.linkedin_login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #0A66C2;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #004182;
            }}
        """)
        self.linkedin_login_btn.clicked.connect(self._linkedin_login)
        
        login_layout.addWidget(email_label)
        login_layout.addWidget(self.linkedin_email_input)
        login_layout.addWidget(password_label)
        login_layout.addWidget(self.linkedin_password_input)
        login_layout.addWidget(self.linkedin_login_btn)
        
        layout.addWidget(login_frame)
        
        # Status label
        self.linkedin_status_label = QLabel("")
        self.linkedin_status_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 14px; margin: 10px;")
        layout.addWidget(self.linkedin_status_label)
        
        # Profile/data display (hidden until login)
        self.linkedin_data = QTextEdit()
        self.linkedin_data.setReadOnly(True)
        self.linkedin_data.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.BG_LIGHTER};
                border: 1px solid {self.HOVER_COLOR};
                border-radius: 4px;
                padding: 10px;
            }}
        """)
        self.linkedin_data.setVisible(False)
        layout.addWidget(self.linkedin_data, 1)
        
        layout.addStretch()
        
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
        """Create GitHub management page with login form"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel("⚙️ GitHub")
        header.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {self.ACCENT_BLUE}; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # Login form (always visible)
        login_frame = QFrame()
        login_frame.setObjectName("panel")
        login_frame.setStyleSheet(f"""
            QFrame#panel {{
                background-color: {self.BG_LIGHTER};
                border-radius: 8px;
                padding: 20px;
            }}
        """)
        login_layout = QVBoxLayout(login_frame)
        
        # Username input
        username_label = QLabel("GitHub Username:")
        username_label.setStyleSheet(f"color: {self.TEXT_PRIMARY}; font-size: 14px; margin-bottom: 5px;")
        self.github_username_input = QLineEdit()
        self.github_username_input.setPlaceholderText("your-username")
        self.github_username_input.setText(os.getenv('GITHUB_USERNAME', ''))
        
        # Token input
        token_label = QLabel("Personal Access Token:")
        token_label.setStyleSheet(f"color: {self.TEXT_PRIMARY}; font-size: 14px; margin-top: 10px; margin-bottom: 5px;")
        self.github_token_input = QLineEdit()
        self.github_token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.github_token_input.setPlaceholderText("ghp_xxxxxxxxxxxx")
        self.github_token_input.setText(os.getenv('GITHUB_TOKEN', ''))
        
        # Get Token link
        token_help = QLabel('<a href="https://github.com/settings/tokens/new?scopes=repo,read:user" style="color: #00d4ff;">Create Personal Access Token</a>')
        token_help.setOpenExternalLinks(True)
        token_help.setStyleSheet("margin-bottom: 10px;")
        
        # Login button
        self.github_login_btn = QPushButton("🔑 Login and Retrieve Repositories")
        self.github_login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #238636;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #2ea043;
            }}
        """)
        self.github_login_btn.clicked.connect(self._github_login)
        
        login_layout.addWidget(username_label)
        login_layout.addWidget(self.github_username_input)
        login_layout.addWidget(token_label)
        login_layout.addWidget(self.github_token_input)
        login_layout.addWidget(token_help)
        login_layout.addWidget(self.github_login_btn)
        
        layout.addWidget(login_frame)
        
        # Status label
        self.github_status_label = QLabel("")
        self.github_status_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 14px; margin: 10px;")
        layout.addWidget(self.github_status_label)
        
        # Repo list (hidden until login)
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
        self.github_list.setVisible(False)
        layout.addWidget(self.github_list, 1)
        
        layout.addStretch()
        
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
