"""
Demo: Phone Call Integration
Demonstrates Twilio phone calling capabilities
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget

from src.phone import create_call_ui
from src.core.logger import setup_logger


class PhoneDemo(QMainWindow):
    """Phone integration demo"""
    
    def __init__(self):
        super().__init__()
        
        self.logger = setup_logger("demo.phone")
        
        self.setWindowTitle("XENO Phone Call Integration Demo")
        self.setGeometry(100, 100, 900, 700)
        
        # Tab widget
        tabs = QTabWidget()
        self.setCentralWidget(tabs)
        
        # Call UI tab
        call_ui = create_call_ui()
        tabs.addTab(call_ui, "📞 Phone Calls")
        
        # Info tab
        info = self._create_info_widget()
        tabs.addTab(info, "ℹ️ Setup Info")
        
        self.logger.info("Phone demo initialized")
    
    def _create_info_widget(self):
        """Create info widget"""
        from PyQt6.QtWidgets import QTextBrowser
        
        info = QTextBrowser()
        info.setHtml("""
        <h2>📞 Phone Call Integration Setup</h2>
        
        <h3>Requirements:</h3>
        <ol>
            <li>Twilio account (free trial available at <a href="https://www.twilio.com">twilio.com</a>)</li>
            <li>Twilio phone number (provided with trial account)</li>
            <li>Twilio credentials (Account SID & Auth Token)</li>
        </ol>
        
        <h3>Environment Setup:</h3>
        <p>Add to your <code>.env</code> file:</p>
        <pre>
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
        </pre>
        
        <h3>Features:</h3>
        <ul>
            <li><b>Outbound Calls</b>: Make calls with text-to-speech messages</li>
            <li><b>AI Assistant</b>: Interactive voice assistant during calls</li>
            <li><b>Call Recording</b>: Record calls for later review</li>
            <li><b>SMS</b>: Send text messages</li>
            <li><b>Call History</b>: Track all inbound/outbound calls</li>
            <li><b>Call Statistics</b>: Analytics on call duration, status, etc.</li>
        </ul>
        
        <h3>AI Voice Commands:</h3>
        <ul>
            <li>"Check my email" - Get unread email count</li>
            <li>"What's my schedule?" - Get next calendar event</li>
            <li>"Schedule a meeting" - Add calendar event</li>
            <li>"Send an email" - Compose and send email</li>
            <li>"Check the weather" - Get current weather</li>
            <li>"Tell me a joke" - Hear an AI joke</li>
        </ul>
        
        <h3>Installation:</h3>
        <pre>pip install twilio</pre>
        
        <h3>Usage Example:</h3>
        <pre>
from src.phone import get_call_manager, get_voice_assistant

# Make a call
call_manager = get_call_manager()
call = call_manager.make_call(
    to_number="+1234567890",
    message="Hello! This is XENO calling.",
    record=True,
    ai_assistant=True
)

# Send SMS
call_manager.send_sms(
    to_number="+1234567890",
    message="Your XENO task is due tomorrow!"
)

# Get call history
history = call_manager.get_call_history(limit=10)
for call in history:
    print(f"{call.to_number}: {call.status} ({call.duration}s)")
        </pre>
        
        <h3>Security Notes:</h3>
        <ul>
            <li>Never commit Twilio credentials to git</li>
            <li>Use environment variables for sensitive data</li>
            <li>Twilio trial accounts can only call verified numbers</li>
            <li>Monitor Twilio usage to avoid unexpected charges</li>
        </ul>
        
        <p style="color: #00ff00; font-weight: bold;">
        Ready to make calls! Configure Twilio and start using the Phone tab.
        </p>
        """)
        
        return info


def main():
    """Run phone demo"""
    app = QApplication(sys.argv)
    
    # Dark theme
    app.setStyleSheet("""
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
        QLineEdit, QTextEdit {
            background: #2b2d31;
            border: 1px solid #00ffff;
            padding: 5px;
            border-radius: 3px;
        }
        QComboBox {
            background: #2b2d31;
            border: 1px solid #00ffff;
            padding: 5px;
            border-radius: 3px;
        }
        QListWidget {
            background: #2b2d31;
            border: 1px solid #00ffff;
            border-radius: 3px;
        }
        QTextBrowser {
            background: #2b2d31;
            border: 1px solid #00ffff;
            padding: 10px;
        }
    """)
    
    demo = PhoneDemo()
    demo.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
