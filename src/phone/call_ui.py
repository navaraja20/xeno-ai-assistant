"""
Phone Call UI
PyQt6 interface for managing phone calls
"""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.core.logger import setup_logger
from src.phone.call_manager import CallStatus, get_call_manager
from src.phone.voice_assistant import get_voice_assistant


class CallUI(QWidget):
    """Phone call management UI"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.logger = setup_logger("phone.ui")
        self.call_manager = get_call_manager()
        self.voice_assistant = get_voice_assistant()
        
        self.init_ui()
        
        # Refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_call_list)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("📞 Phone Call Integration")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ffff;")
        layout.addWidget(title)
        
        # Configuration status
        if self.call_manager.is_configured():
            status = QLabel(f"✅ Connected: {self.call_manager.phone_number}")
            status.setStyleSheet("color: #00ff00;")
        else:
            status = QLabel("⚠️ Not Configured - Set Twilio credentials in .env")
            status.setStyleSheet("color: #ff9900;")
        layout.addWidget(status)
        
        # Make call section
        make_call_group = self._create_make_call_section()
        layout.addWidget(make_call_group)
        
        # Call history section
        history_group = self._create_history_section()
        layout.addWidget(history_group)
        
        # Statistics
        stats_group = self._create_stats_section()
        layout.addWidget(stats_group)
    
    def _create_make_call_section(self) -> QGroupBox:
        """Create make call section"""
        group = QGroupBox("Make Call")
        layout = QVBoxLayout(group)
        
        # Phone number input
        phone_layout = QHBoxLayout()
        phone_layout.addWidget(QLabel("Phone Number:"))
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("+1234567890")
        phone_layout.addWidget(self.phone_input)
        layout.addLayout(phone_layout)
        
        # Message input
        layout.addWidget(QLabel("Message (optional):"))
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Enter message to speak...")
        self.message_input.setMaximumHeight(100)
        layout.addWidget(self.message_input)
        
        # Options
        options_layout = QHBoxLayout()
        
        self.record_checkbox = QComboBox()
        self.record_checkbox.addItems(["Don't Record", "Record Call"])
        options_layout.addWidget(self.record_checkbox)
        
        self.ai_checkbox = QComboBox()
        self.ai_checkbox.addItems(["Simple Message", "AI Assistant"])
        options_layout.addWidget(self.ai_checkbox)
        
        layout.addLayout(options_layout)
        
        # Call button
        call_btn = QPushButton("📞 Make Call")
        call_btn.clicked.connect(self.make_call)
        call_btn.setStyleSheet("""
            QPushButton {
                background: #28A745;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        layout.addWidget(call_btn)
        
        # SMS section
        sms_layout = QHBoxLayout()
        sms_btn = QPushButton("💬 Send SMS Instead")
        sms_btn.clicked.connect(self.send_sms)
        sms_btn.setStyleSheet("""
            QPushButton {
                background: #007ACC;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
        """)
        sms_layout.addWidget(sms_btn)
        layout.addLayout(sms_layout)
        
        return group
    
    def _create_history_section(self) -> QGroupBox:
        """Create call history section"""
        group = QGroupBox("Call History")
        layout = QVBoxLayout(group)
        
        # Filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        
        self.direction_filter = QComboBox()
        self.direction_filter.addItems(["All", "Inbound", "Outbound"])
        self.direction_filter.currentTextChanged.connect(self.refresh_call_list)
        filter_layout.addWidget(self.direction_filter)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Completed", "Failed", "In Progress"])
        self.status_filter.currentTextChanged.connect(self.refresh_call_list)
        filter_layout.addWidget(self.status_filter)
        
        layout.addLayout(filter_layout)
        
        # Call list
        self.call_list = QListWidget()
        self.call_list.itemDoubleClicked.connect(self.show_call_details)
        layout.addWidget(self.call_list)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_call_list)
        layout.addWidget(refresh_btn)
        
        # Initial populate
        self.refresh_call_list()
        
        return group
    
    def _create_stats_section(self) -> QGroupBox:
        """Create statistics section"""
        group = QGroupBox("Statistics")
        layout = QVBoxLayout(group)
        
        self.stats_label = QLabel("Loading statistics...")
        layout.addWidget(self.stats_label)
        
        self.update_statistics()
        
        return group
    
    def make_call(self):
        """Make a phone call"""
        phone = self.phone_input.text().strip()
        message = self.message_input.toPlainText().strip()
        
        if not phone:
            self.logger.warning("Phone number required")
            return
        
        record = self.record_checkbox.currentIndex() == 1
        ai_assistant = self.ai_checkbox.currentIndex() == 1
        
        if ai_assistant:
            # Use AI assistant
            self.voice_assistant.make_ai_call(
                to_number=phone,
                initial_message=message or "Hello! This is XENO calling.",
                enable_conversation=True,
            )
        else:
            # Simple call
            self.call_manager.make_call(
                to_number=phone,
                message=message or None,
                record=record,
                ai_assistant=False,
            )
        
        self.logger.info(f"Call initiated to {phone}")
        
        # Clear inputs
        self.phone_input.clear()
        self.message_input.clear()
        
        # Refresh history
        QTimer.singleShot(2000, self.refresh_call_list)
    
    def send_sms(self):
        """Send SMS message"""
        phone = self.phone_input.text().strip()
        message = self.message_input.toPlainText().strip()
        
        if not phone or not message:
            self.logger.warning("Phone number and message required for SMS")
            return
        
        success = self.call_manager.send_sms(phone, message)
        
        if success:
            self.logger.info(f"SMS sent to {phone}")
            self.phone_input.clear()
            self.message_input.clear()
    
    def refresh_call_list(self):
        """Refresh call history list"""
        self.call_list.clear()
        
        # Get filters
        direction = self.direction_filter.currentText().lower()
        if direction == "all":
            direction = None
        
        status = self.status_filter.currentText().lower().replace(" ", "-")
        if status == "all":
            status = None
        
        # Get calls
        calls = self.call_manager.get_call_history(
            limit=50,
            direction=direction,
            status=status,
        )
        
        # Populate list
        for call in reversed(calls):
            # Format call info
            direction_icon = "📞" if call.direction == "outbound" else "📱"
            status_color = {
                CallStatus.COMPLETED: "#00ff00",
                CallStatus.FAILED: "#ff0000",
                CallStatus.IN_PROGRESS: "#ffaa00",
            }.get(call.status, "#ffffff")
            
            duration_str = f"{call.duration}s" if call.duration else "N/A"
            
            item_text = (
                f"{direction_icon} {call.to_number} | "
                f"Status: {call.status} | "
                f"Duration: {duration_str}"
            )
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, call)
            item.setForeground(QColor(status_color))
            self.call_list.addItem(item)
        
        self.update_statistics()
    
    def show_call_details(self, item: QListWidgetItem):
        """Show detailed call information"""
        call = item.data(Qt.ItemDataRole.UserRole)
        
        details = (
            f"Call SID: {call.call_sid}\n"
            f"From: {call.from_number}\n"
            f"To: {call.to_number}\n"
            f"Direction: {call.direction}\n"
            f"Status: {call.status}\n"
            f"Duration: {call.duration}s\n"
            f"Started: {call.started_at}\n"
        )
        
        if call.recording_url:
            details += f"Recording: {call.recording_url}\n"
        
        if call.notes:
            details += f"Notes: {', '.join(call.notes)}\n"
        
        self.logger.info(f"Call details:\n{details}")
    
    def update_statistics(self):
        """Update call statistics"""
        stats = self.call_manager.get_call_statistics()
        
        stats_text = (
            f"Total Calls: {stats['total_calls']} | "
            f"Inbound: {stats['inbound_calls']} | "
            f"Outbound: {stats['outbound_calls']} | "
            f"Avg Duration: {stats['average_duration']:.1f}s"
        )
        
        self.stats_label.setText(stats_text)


def create_call_ui(parent=None) -> CallUI:
    """Create call UI widget"""
    return CallUI(parent)
