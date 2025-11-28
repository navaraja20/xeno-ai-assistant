"""
AI Chat UI
Interactive chat interface for XENO AI Agent
"""

import sys
from typing import Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.ai.ai_agent import ModelProvider, get_ai_agent
from src.core.logger import setup_logger


class ChatWorker(QThread):
    """Background worker for chat"""

    response = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, message: str, provider: ModelProvider, system_prompt: Optional[str] = None):
        super().__init__()
        self.message = message
        self.provider = provider
        self.system_prompt = system_prompt
        self.agent = get_ai_agent()

    def run(self):
        try:
            response = self.agent.chat(
                self.message, provider=self.provider, system_prompt=self.system_prompt
            )
            self.response.emit(response)
        except Exception as e:
            self.error.emit(str(e))


class AIChatWidget(QWidget):
    """AI Chat interface"""

    def __init__(self):
        super().__init__()
        self.logger = setup_logger("ai.chat_ui")
        self.agent = get_ai_agent()
        self.chat_worker: Optional[ChatWorker] = None

        self.init_ui()
        self.update_status()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("🤖 XENO AI Agent")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Status
        status_group = QGroupBox("📊 Status")
        status_layout = QVBoxLayout()

        self.status_label = QLabel()
        status_layout.addWidget(self.status_label)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Provider selection
        provider_group = QGroupBox("🎛️ AI Provider")
        provider_layout = QHBoxLayout()

        self.provider_group = QButtonGroup()

        self.auto_radio = QRadioButton("Auto (Smart)")
        self.auto_radio.setChecked(True)
        self.local_radio = QRadioButton("Local (Ollama)")
        self.gemini_radio = QRadioButton("Cloud (Gemini)")

        self.provider_group.addButton(self.auto_radio, 0)
        self.provider_group.addButton(self.local_radio, 1)
        self.provider_group.addButton(self.gemini_radio, 2)

        provider_layout.addWidget(self.auto_radio)
        provider_layout.addWidget(self.local_radio)
        provider_layout.addWidget(self.gemini_radio)

        provider_group.setLayout(provider_layout)
        layout.addWidget(provider_group)

        # Model selection (for local)
        model_group = QGroupBox("🧠 Local Model")
        model_layout = QHBoxLayout()

        self.model_combo = QComboBox()
        self.refresh_models()
        model_layout.addWidget(self.model_combo)

        refresh_models_btn = QPushButton("🔄 Refresh")
        refresh_models_btn.clicked.connect(self.refresh_models)
        model_layout.addWidget(refresh_models_btn)

        model_group.setLayout(model_layout)
        layout.addWidget(model_group)

        # Chat history
        chat_group = QGroupBox("💬 Conversation")
        chat_layout = QVBoxLayout()

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(400)
        chat_layout.addWidget(self.chat_display)

        chat_group.setLayout(chat_layout)
        layout.addWidget(chat_group)

        # Input area
        input_layout = QHBoxLayout()

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Ask me anything...")
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)

        send_btn = QPushButton("📤 Send")
        send_btn.clicked.connect(self.send_message)
        send_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        input_layout.addWidget(send_btn)

        layout.addLayout(input_layout)

        # Quick actions
        actions_layout = QHBoxLayout()

        clear_btn = QPushButton("🗑️ Clear Chat")
        clear_btn.clicked.connect(self.clear_chat)
        actions_layout.addWidget(clear_btn)

        code_btn = QPushButton("💻 Generate Code")
        code_btn.clicked.connect(self.show_code_prompt)
        actions_layout.addWidget(code_btn)

        analyze_btn = QPushButton("📝 Analyze Text")
        analyze_btn.clicked.connect(self.show_analyze_prompt)
        actions_layout.addWidget(analyze_btn)

        actions_layout.addStretch()

        layout.addLayout(actions_layout)

        self.setLayout(layout)

    def update_status(self):
        """Update status display"""
        status = self.agent.get_status()

        status_text = f"""**Ollama (Local):** {'✅ Available' if status['ollama_available'] else '❌ Not Available'}
**Models Installed:** {len(status['ollama_models'])}
**Current Model:** {status['current_local_model']}

**Gemini (Cloud):** {'✅ Available' if status['gemini_available'] else '❌ Not Configured'}

**Conversation:** {status['conversation_length']} exchanges
"""

        self.status_label.setText(status_text)

    def refresh_models(self):
        """Refresh available Ollama models"""
        models = self.agent.list_local_models()

        self.model_combo.clear()

        if models:
            self.model_combo.addItems(models)
            # Select current model
            current = self.agent.current_local_model
            idx = self.model_combo.findText(current)
            if idx >= 0:
                self.model_combo.setCurrentIndex(idx)
        else:
            self.model_combo.addItem("No models installed")

        self.model_combo.currentTextChanged.connect(self.change_model)

    def change_model(self, model: str):
        """Change active model"""
        if model and model != "No models installed":
            self.agent.set_local_model(model)
            self.update_status()

    def get_selected_provider(self) -> ModelProvider:
        """Get selected provider"""
        if self.auto_radio.isChecked():
            return ModelProvider.AUTO
        elif self.local_radio.isChecked():
            return ModelProvider.LOCAL
        elif self.gemini_radio.isChecked():
            return ModelProvider.GEMINI
        return ModelProvider.AUTO

    def send_message(self):
        """Send chat message"""
        message = self.message_input.text().strip()
        if not message:
            return

        # Display user message
        self.append_message("You", message, "#2196F3")

        # Clear input
        self.message_input.clear()

        # Get provider
        provider = self.get_selected_provider()

        # Show thinking
        self.append_message("XENO", "Thinking...", "#9E9E9E")

        # Start worker
        self.chat_worker = ChatWorker(message, provider)
        self.chat_worker.response.connect(self.show_response)
        self.chat_worker.error.connect(self.show_error)
        self.chat_worker.start()

    def show_response(self, response: str):
        """Show AI response"""
        # Remove "thinking" message
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()

        # Add actual response
        self.append_message("XENO", response, "#4CAF50")

        self.update_status()

    def show_error(self, error: str):
        """Show error"""
        self.append_message("Error", error, "#F44336")

    def append_message(self, sender: str, message: str, color: str):
        """Append message to chat"""
        self.chat_display.append(
            f'<span style="color: {color}; font-weight: bold;">{sender}:</span>'
        )
        self.chat_display.append(message)
        self.chat_display.append("")

        # Scroll to bottom
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)

    def clear_chat(self):
        """Clear chat history"""
        self.chat_display.clear()
        self.agent.clear_history()
        self.update_status()

    def show_code_prompt(self):
        """Show code generation prompt"""
        self.message_input.setText("Generate Python code to ")
        self.message_input.setFocus()
        cursor_pos = len(self.message_input.text())
        self.message_input.setCursorPosition(cursor_pos)

    def show_analyze_prompt(self):
        """Show text analysis prompt"""
        self.message_input.setText("Analyze this text: ")
        self.message_input.setFocus()
        cursor_pos = len(self.message_input.text())
        self.message_input.setCursorPosition(cursor_pos)


def main():
    """Run chat UI"""
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("XENO AI Chat")
    window.setGeometry(100, 100, 800, 900)

    widget = AIChatWidget()
    window.setCentralWidget(widget)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
