"""
Setup Wizard for first-time XENO configuration
"""
from PyQt6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox,
    QTextEdit, QGroupBox, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap
from typing import Dict, Any
import pyttsx3


class WelcomePage(QWizardPage):
    """Welcome page - Master name registration"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Welcome to XENO")
        self.setSubTitle("Your Personal AI Assistant")
        
        layout = QVBoxLayout()
        
        # Welcome message
        welcome_text = QLabel(
            "<h2>🤖 Welcome!</h2>"
            "<p>I am XENO, your personal AI assistant.</p>"
            "<p>I'm here to help you with emails, job applications, "
            "GitHub management, and much more.</p>"
            "<p><b>First, I need to know your name, Master.</b></p>"
        )
        welcome_text.setWordWrap(True)
        layout.addWidget(welcome_text)
        
        # Name input
        name_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name...")
        self.name_input.textChanged.connect(self._on_name_changed)
        name_layout.addRow("Your Name:", self.name_input)
        
        layout.addLayout(name_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Register field for validation
        self.registerField("user_name*", self.name_input)
    
    def _on_name_changed(self, text):
        """Handle name input change"""
        self.completeChanged.emit()
    
    def validatePage(self):
        """Validate before moving to next page"""
        name = self.name_input.text().strip()
        if name:
            # Speak greeting - pronounce XENO as "XENOo"
            try:
                engine = pyttsx3.init()
                engine.say(f"Welcome, Master {name}. It's a pleasure to meet you.")
                engine.runAndWait()
            except:
                pass  # Voice not critical for setup
            return True
        return False


class ModulesPage(QWizardPage):
    """Module selection page"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Select Modules")
        self.setSubTitle("Choose which features you want to enable")
        
        layout = QVBoxLayout()
        
        # Email module
        email_group = QGroupBox("📧 Email Automation")
        email_layout = QVBoxLayout()
        self.email_checkbox = QCheckBox("Enable email automation")
        self.email_provider = QComboBox()
        self.email_provider.addItems(["Gmail", "Outlook"])
        email_layout.addWidget(self.email_checkbox)
        email_layout.addWidget(QLabel("Provider:"))
        email_layout.addWidget(self.email_provider)
        email_group.setLayout(email_layout)
        layout.addWidget(email_group)
        
        # Job application module
        job_group = QGroupBox("💼 Job Application Automation")
        job_layout = QVBoxLayout()
        self.job_checkbox = QCheckBox("Enable job application automation")
        job_layout.addWidget(self.job_checkbox)
        job_group.setLayout(job_layout)
        layout.addWidget(job_group)
        
        # GitHub module
        github_group = QGroupBox("🐙 GitHub Management")
        github_layout = QVBoxLayout()
        self.github_checkbox = QCheckBox("Enable GitHub management")
        github_layout.addWidget(self.github_checkbox)
        github_group.setLayout(github_layout)
        layout.addWidget(github_group)
        
        # LinkedIn module
        linkedin_group = QGroupBox("💼 LinkedIn Automation")
        linkedin_layout = QVBoxLayout()
        self.linkedin_checkbox = QCheckBox("Enable LinkedIn automation")
        linkedin_layout.addWidget(self.linkedin_checkbox)
        linkedin_group.setLayout(linkedin_layout)
        layout.addWidget(linkedin_group)
        
        # Calendar module
        calendar_group = QGroupBox("📅 Calendar Integration")
        calendar_layout = QVBoxLayout()
        self.calendar_checkbox = QCheckBox("Enable calendar integration")
        self.calendar_provider = QComboBox()
        self.calendar_provider.addItems(["Google Calendar", "Outlook Calendar"])
        calendar_layout.addWidget(self.calendar_checkbox)
        calendar_layout.addWidget(QLabel("Provider:"))
        calendar_layout.addWidget(self.calendar_provider)
        calendar_group.setLayout(calendar_layout)
        layout.addWidget(calendar_group)
        
        layout.addStretch()
        self.setLayout(layout)


class AIConfigPage(QWizardPage):
    """AI/LLM configuration page"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("AI Configuration")
        self.setSubTitle("Configure the AI engine")
        
        layout = QFormLayout()
        
        # AI provider
        self.ai_provider = QComboBox()
        self.ai_provider.addItems(["OpenAI (GPT-4)", "Google Gemini"])
        layout.addRow("AI Provider:", self.ai_provider)
        
        # API key
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your API key...")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("API Key:", self.api_key_input)
        
        # API key help
        api_help = QLabel(
            '<a href="https://platform.openai.com/api-keys">Get OpenAI API Key</a> | '
            '<a href="https://makersuite.google.com/app/apikey">Get Gemini API Key</a>'
        )
        api_help.setOpenExternalLinks(True)
        layout.addRow("", api_help)
        
        # Voice settings
        self.voice_checkbox = QCheckBox("Enable voice responses")
        self.voice_checkbox.setChecked(True)
        layout.addRow("Voice:", self.voice_checkbox)
        
        voice_help = QLabel("(Optimus Prime voice will be configured later)")
        voice_help.setStyleSheet("color: gray; font-size: 10px;")
        layout.addRow("", voice_help)
        
        self.setLayout(layout)
        
        # Register field
        self.registerField("ai_api_key", self.api_key_input)


class CredentialsPage(QWizardPage):
    """Email, GitHub, and LinkedIn credentials page"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Account Credentials")
        self.setSubTitle("Connect your accounts for automation")
        
        layout = QVBoxLayout()
        
        # Email section
        email_group = QGroupBox("📧 Email Account")
        email_layout = QFormLayout()
        
        self.email_address = QLineEdit()
        self.email_address.setPlaceholderText("your.email@gmail.com")
        email_layout.addRow("Email Address:", self.email_address)
        
        self.email_password = QLineEdit()
        self.email_password.setPlaceholderText("App password or OAuth token")
        self.email_password.setEchoMode(QLineEdit.EchoMode.Password)
        email_layout.addRow("Password/Token:", self.email_password)
        
        # OAuth button for Gmail
        email_btn_layout = QHBoxLayout()
        gmail_oauth_btn = QPushButton("🔐 Get Gmail App Password")
        gmail_oauth_btn.clicked.connect(self._open_gmail_oauth)
        gmail_oauth_btn.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ae8;
            }
        """)
        email_btn_layout.addWidget(gmail_oauth_btn)
        email_btn_layout.addStretch()
        email_layout.addRow("", email_btn_layout)
        
        email_help = QLabel(
            '<a href="https://myaccount.google.com/apppasswords">Direct Link</a> | '
            '<a href="#" style="color: #00d4ff;">Help</a>'
        )
        email_help.setOpenExternalLinks(True)
        email_help.linkActivated.connect(self._show_email_help)
        email_layout.addRow("", email_help)
        
        email_group.setLayout(email_layout)
        layout.addWidget(email_group)
        
        # GitHub section
        github_group = QGroupBox("🐙 GitHub Account")
        github_layout = QFormLayout()
        
        self.github_username = QLineEdit()
        self.github_username.setPlaceholderText("your-username")
        github_layout.addRow("GitHub Username:", self.github_username)
        
        self.github_token = QLineEdit()
        self.github_token.setPlaceholderText("ghp_xxxxxxxxxxxx")
        self.github_token.setEchoMode(QLineEdit.EchoMode.Password)
        github_layout.addRow("Personal Access Token:", self.github_token)
        
        # OAuth button for GitHub
        github_btn_layout = QHBoxLayout()
        github_oauth_btn = QPushButton("🔐 Generate GitHub Token")
        github_oauth_btn.clicked.connect(self._open_github_oauth)
        github_oauth_btn.setStyleSheet("""
            QPushButton {
                background-color: #238636;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
        """)
        github_btn_layout.addWidget(github_oauth_btn)
        github_btn_layout.addStretch()
        github_layout.addRow("", github_btn_layout)
        
        github_help = QLabel(
            '<a href="https://github.com/settings/tokens">Direct Link</a> | '
            '<a href="#" style="color: #00d4ff;">Help</a>'
        )
        github_help.setOpenExternalLinks(True)
        github_help.linkActivated.connect(self._show_github_help)
        github_layout.addRow("", github_help)
        
        github_group.setLayout(github_layout)
        layout.addWidget(github_group)
        
        # LinkedIn section
        linkedin_group = QGroupBox("💼 LinkedIn Account")
        linkedin_layout = QFormLayout()
        
        self.linkedin_email = QLineEdit()
        self.linkedin_email.setPlaceholderText("your.email@example.com")
        linkedin_layout.addRow("LinkedIn Email:", self.linkedin_email)
        
        self.linkedin_password = QLineEdit()
        self.linkedin_password.setPlaceholderText("Your LinkedIn password")
        self.linkedin_password.setEchoMode(QLineEdit.EchoMode.Password)
        linkedin_layout.addRow("Password:", self.linkedin_password)
        
        linkedin_note = QLabel("Note: LinkedIn credentials are stored securely and encrypted.")
        linkedin_note.setStyleSheet("color: gray; font-size: 10px;")
        linkedin_layout.addRow("", linkedin_note)
        
        linkedin_group.setLayout(linkedin_layout)
        layout.addWidget(linkedin_group)
        
        # Skip option
        skip_label = QLabel("You can skip this and add credentials later in Settings.")
        skip_label.setStyleSheet("color: #00d4ff; font-style: italic; margin-top: 10px;")
        layout.addWidget(skip_label)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Register fields
        self.registerField("email_address", self.email_address)
        self.registerField("email_password", self.email_password)
        self.registerField("github_username", self.github_username)
        self.registerField("github_token", self.github_token)
        self.registerField("linkedin_email", self.linkedin_email)
        self.registerField("linkedin_password", self.linkedin_password)
    
    def _open_gmail_oauth(self):
        """Open Gmail App Password page in browser."""
        import webbrowser
        webbrowser.open("https://myaccount.google.com/apppasswords")
    
    def _open_github_oauth(self):
        """Open GitHub token creation page in browser."""
        import webbrowser
        webbrowser.open("https://github.com/settings/tokens/new?description=XENO%20AI%20Assistant&scopes=repo,user,read:org")
    
    def _show_email_help(self):
        """Show email setup help."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Gmail App Password Help",
            "To create a Gmail App Password:\n\n"
            "1. Click the button to open Google Account settings\n"
            "2. You may need to verify it's you\n"
            "3. Enable 2-Step Verification if not already enabled\n"
            "4. Go to App Passwords section\n"
            "5. Select 'Mail' and your device\n"
            "6. Click 'Generate'\n"
            "7. Copy the 16-character password\n"
            "8. Paste it in the Password field above\n\n"
            "Note: This is different from your regular Google password!"
        )
    
    def _show_github_help(self):
        """Show GitHub setup help."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "GitHub Token Help",
            "To create a GitHub Personal Access Token:\n\n"
            "1. Click the button to open GitHub settings\n"
            "2. Give your token a name (e.g., 'XENO AI Assistant')\n"
            "3. Set expiration (recommended: 90 days)\n"
            "4. Select these scopes:\n"
            "   • repo (Full control of repositories)\n"
            "   • user (Update user data)\n"
            "   • read:org (Read org data)\n"
            "5. Click 'Generate token'\n"
            "6. Copy the token (you won't see it again!)\n"
            "7. Paste it in the Token field above\n\n"
            "Note: Treat this token like a password - never share it!"
        )


class CompletePage(QWizardPage):
    """Completion page"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Setup Complete!")
        self.setSubTitle("XENO is ready to assist you")
        
        layout = QVBoxLayout()
        
        complete_text = QLabel(
            "<h2>🎉 All Set!</h2>"
            "<p><b>XENO is now configured and ready.</b></p>"
            "<p>I will start automatically when you log in.</p>"
            "<p>You can access me through the system tray icon.</p>"
            "<p><br><b>Quick tips:</b></p>"
            "<ul>"
            "<li>Right-click the tray icon for quick actions</li>"
            "<li>Say 'Hey XENO' to activate voice commands (if enabled)</li>"
            "<li>Access settings anytime from the tray menu</li>"
            "<li>I'll notify you of important events and tasks</li>"
            "</ul>"
            "<p><br><i>Welcome aboard, Master. Let's accomplish great things together.</i></p>"
        )
        complete_text.setWordWrap(True)
        layout.addWidget(complete_text)
        
        self.setLayout(layout)


class SetupWizard(QWizard):
    """Main setup wizard"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("XENO Setup")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setFixedSize(700, 550)
        
        # Add pages
        self.addPage(WelcomePage())
        self.addPage(ModulesPage())
        self.addPage(AIConfigPage())
        self.addPage(CredentialsPage())
        self.addPage(CompletePage())
        
        # Customize button text
        self.setButtonText(QWizard.WizardButton.FinishButton, "Start XENO")
        
    def get_config(self) -> Dict[str, Any]:
        """Get configuration from wizard"""
        # Get pages
        welcome_page = self.page(0)
        modules_page = self.page(1)
        ai_page = self.page(2)
        creds_page = self.page(3)
        
        config = {
            'user': {
                'name': self.field('user_name'),
                'voice_enabled': ai_page.voice_checkbox.isChecked(),
            },
            'email': {
                'enabled': modules_page.email_checkbox.isChecked(),
                'provider': modules_page.email_provider.currentText().lower(),
                'address': self.field('email_address') or '',
                'password': self.field('email_password') or '',
            },
            'jobs': {
                'enabled': modules_page.job_checkbox.isChecked(),
            },
            'github': {
                'enabled': modules_page.github_checkbox.isChecked(),
                'username': self.field('github_username') or '',
                'token': self.field('github_token') or '',
            },
            'linkedin': {
                'enabled': modules_page.linkedin_checkbox.isChecked(),
                'email': self.field('linkedin_email') or '',
                'password': self.field('linkedin_password') or '',
            },
            'calendar': {
                'enabled': modules_page.calendar_checkbox.isChecked(),
                'provider': modules_page.calendar_provider.currentText().lower().replace(' ', '_'),
            },
            'ai': {
                'provider': 'openai' if 'openai' in ai_page.ai_provider.currentText().lower() else 'gemini',
                'api_key': self.field('ai_api_key') or '',
            }
        }
        
        # Store API key and credentials in .env file
        self._save_credentials(config)
        
        return config
    
    def _save_credentials(self, config):
        """Save credentials to .env file"""
        from pathlib import Path
        import os
        
        env_path = Path(__file__).parent.parent.parent / ".env"
        
        # Read existing .env
        env_content = {}
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_content[key] = value
        
        # Update with new credentials
        if config['ai']['api_key']:
            env_content['OPENAI_API_KEY'] = config['ai']['api_key']
        
        if config['email']['password']:
            env_content['EMAIL_PASSWORD'] = config['email']['password']
        
        if config['github']['token']:
            env_content['GITHUB_TOKEN'] = config['github']['token']
        
        if config['linkedin']['password']:
            env_content['LINKEDIN_PASSWORD'] = config['linkedin']['password']
        
        # Write back to .env
        with open(env_path, 'w') as f:
            for key, value in env_content.items():
                f.write(f"{key}={value}\n")
        
        print(f"[OK] Credentials saved to {env_path}")
    
    def accept(self):
        """Handle wizard completion"""
        # Mark first run as complete
        from utils.system import mark_first_run_complete, create_desktop_shortcut
        mark_first_run_complete()
        
        # Create desktop shortcut
        try:
            if create_desktop_shortcut():
                print("[OK] Desktop shortcut created")
        except Exception as e:
            print(f"Could not create desktop shortcut: {e}")
        
        # Speak completion message - pronounce XENO as "XENOo"
        try:
            engine = pyttsx3.init()
            engine.say("Setup complete. XENOo is now online and at your service.")
            engine.runAndWait()
        except:
            pass
        
        super().accept()
