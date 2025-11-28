"""
Voice UI for XENO - PyQt6 Interface
Visual interface for voice interactions with waveform visualization
"""

from typing import Optional

import numpy as np
from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSlider,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.voice.advanced_voice_engine import Emotion, Language


class WaveformVisualizer(QWidget):
    """Real-time audio waveform visualizer"""

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(100)
        self.waveform_data = np.zeros(100)
        self.is_active = False
        self.color = QColor("#5865F2")

    def update_waveform(self, audio_data: np.ndarray):
        """Update waveform with new audio data"""
        if len(audio_data) > 0:
            # Downsample to 100 points for display
            step = max(1, len(audio_data) // 100)
            self.waveform_data = audio_data[::step][:100]
            self.update()

    def set_active(self, active: bool):
        """Set visualization active state"""
        self.is_active = active
        self.color = QColor("#5865F2") if active else QColor("#40444b")
        self.update()

    def paintEvent(self, event):
        """Paint waveform"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        painter.fillRect(self.rect(), QColor("#2b2d31"))

        # Draw waveform
        width = self.width()
        height = self.height()
        center_y = height // 2

        pen = QPen(self.color, 2)
        painter.setPen(pen)

        if len(self.waveform_data) > 0:
            x_step = width / len(self.waveform_data)

            for i in range(len(self.waveform_data) - 1):
                x1 = int(i * x_step)
                x2 = int((i + 1) * x_step)

                # Normalize amplitude
                y1 = center_y - int(self.waveform_data[i] * center_y * 0.8)
                y2 = center_y - int(self.waveform_data[i + 1] * center_y * 0.8)

                painter.drawLine(x1, y1, x2, y2)

        # Draw center line
        pen.setColor(QColor("#40444b"))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLine(0, center_y, width, center_y)


class VoiceThread(QThread):
    """Background thread for voice processing"""

    audio_received = pyqtSignal(np.ndarray)
    text_recognized = pyqtSignal(str, str)  # text, language
    error_occurred = pyqtSignal(str)

    def __init__(self, voice_engine):
        super().__init__()
        self.voice_engine = voice_engine
        self.is_running = False

    def run(self):
        """Run voice processing loop"""
        import speech_recognition as sr

        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        self.is_running = True

        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)

        while self.is_running:
            try:
                with microphone as source:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

                # Emit audio data
                audio_np = np.frombuffer(audio.get_raw_data(), dtype=np.int16)
                audio_np = audio_np.astype(float) / 32768.0  # Normalize
                self.audio_received.emit(audio_np)

                # Process with voice engine
                import asyncio

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                result = loop.run_until_complete(self.voice_engine.process_audio(audio))

                if result.get("success") and result.get("text"):
                    self.text_recognized.emit(
                        result["text"],
                        result["language"].value
                        if hasattr(result["language"], "value")
                        else "en-US",
                    )

            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                self.error_occurred.emit(str(e))

    def stop(self):
        """Stop voice processing"""
        self.is_running = False


class VoiceUI(QWidget):
    """Main voice interface"""

    def __init__(self, voice_engine):
        super().__init__()
        self.voice_engine = voice_engine
        self.voice_thread: Optional[VoiceThread] = None
        self.is_listening = False

        self.init_ui()

    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("XENO Voice Control")
        self.setMinimumSize(600, 700)

        # Apply dark theme
        self.setStyleSheet(
            """
            QWidget {
                background-color: #2b2d31;
                color: #ffffff;
                font-family: 'Segoe UI', Arial;
                font-size: 11pt;
            }
            QGroupBox {
                background-color: #313338;
                border: 1px solid #40444b;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #5865F2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4752C4;
            }
            QPushButton:pressed {
                background-color: #3C45A5;
            }
            QPushButton:disabled {
                background-color: #40444b;
                color: #72767d;
            }
            QComboBox, QSlider {
                background-color: #313338;
                border: 1px solid #40444b;
                border-radius: 4px;
                padding: 5px;
            }
            QTextEdit {
                background-color: #1e1f22;
                border: 1px solid #40444b;
                border-radius: 6px;
                padding: 10px;
            }
            QLabel {
                color: #b5bac1;
            }
            QProgressBar {
                border: 1px solid #40444b;
                border-radius: 4px;
                text-align: center;
                background-color: #1e1f22;
            }
            QProgressBar::chunk {
                background-color: #5865F2;
                border-radius: 3px;
            }
        """
        )

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("🎤 XENO Voice Control")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #5865F2; padding: 10px;")
        layout.addWidget(title)

        # Waveform visualizer
        waveform_group = QGroupBox("Audio Input")
        waveform_layout = QVBoxLayout()
        self.waveform = WaveformVisualizer()
        waveform_layout.addWidget(self.waveform)
        waveform_group.setLayout(waveform_layout)
        layout.addWidget(waveform_group)

        # Control buttons
        controls_layout = QHBoxLayout()

        self.listen_btn = QPushButton("🎙️ Start Listening")
        self.listen_btn.clicked.connect(self.toggle_listening)
        self.listen_btn.setMinimumHeight(50)
        controls_layout.addWidget(self.listen_btn)

        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.clicked.connect(self.stop_listening)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumHeight(50)
        controls_layout.addWidget(self.stop_btn)

        layout.addLayout(controls_layout)

        # Settings group
        settings_group = QGroupBox("Voice Settings")
        settings_layout = QVBoxLayout()

        # Language selection
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:"))
        self.language_combo = QComboBox()
        for lang in Language:
            self.language_combo.addItem(lang.name.replace("_", " ").title(), lang)
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        lang_layout.addWidget(self.language_combo)
        settings_layout.addLayout(lang_layout)

        # Sensitivity
        sens_layout = QHBoxLayout()
        sens_layout.addWidget(QLabel("Sensitivity:"))
        self.sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.sensitivity_slider.setMinimum(1)
        self.sensitivity_slider.setMaximum(10)
        self.sensitivity_slider.setValue(7)
        self.sensitivity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.sensitivity_slider.setTickInterval(1)
        sens_layout.addWidget(self.sensitivity_slider)
        self.sensitivity_label = QLabel("0.7")
        sens_layout.addWidget(self.sensitivity_label)
        self.sensitivity_slider.valueChanged.connect(
            lambda v: self.sensitivity_label.setText(f"{v/10:.1f}")
        )
        settings_layout.addLayout(sens_layout)

        # Wake word
        wake_layout = QHBoxLayout()
        wake_layout.addWidget(QLabel("Wake Word:"))
        self.wake_word_combo = QComboBox()
        self.wake_word_combo.addItems(["XENO", "Hey XENO", "OK XENO", "Computer"])
        wake_layout.addWidget(self.wake_word_combo)
        settings_layout.addLayout(wake_layout)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Status indicators
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()

        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("font-weight: bold; color: #23a559;")
        status_layout.addWidget(self.status_label)

        self.confidence_bar = QProgressBar()
        self.confidence_bar.setMaximum(100)
        self.confidence_bar.setValue(0)
        status_layout.addWidget(self.confidence_bar)

        self.emotion_label = QLabel("Emotion: Neutral")
        status_layout.addWidget(self.emotion_label)

        self.speaker_label = QLabel("Speaker: Unknown")
        status_layout.addWidget(self.speaker_label)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Transcript
        transcript_group = QGroupBox("Conversation")
        transcript_layout = QVBoxLayout()

        self.transcript = QTextEdit()
        self.transcript.setReadOnly(True)
        self.transcript.setMinimumHeight(200)
        transcript_layout.addWidget(self.transcript)

        clear_btn = QPushButton("Clear Transcript")
        clear_btn.clicked.connect(self.transcript.clear)
        transcript_layout.addWidget(clear_btn)

        transcript_group.setLayout(transcript_layout)
        layout.addWidget(transcript_group)

        self.setLayout(layout)

    def toggle_listening(self):
        """Toggle voice listening"""
        if self.is_listening:
            self.stop_listening()
        else:
            self.start_listening()

    def start_listening(self):
        """Start voice listening"""
        self.is_listening = True
        self.listen_btn.setText("🎙️ Listening...")
        self.listen_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.waveform.set_active(True)

        self.status_label.setText("Status: Listening")
        self.status_label.setStyleSheet("font-weight: bold; color: #5865F2;")

        # Start voice thread
        self.voice_thread = VoiceThread(self.voice_engine)
        self.voice_thread.audio_received.connect(self.on_audio_received)
        self.voice_thread.text_recognized.connect(self.on_text_recognized)
        self.voice_thread.error_occurred.connect(self.on_error)
        self.voice_thread.start()

        self.add_to_transcript("[System] Listening started...")

    def stop_listening(self):
        """Stop voice listening"""
        self.is_listening = False
        self.listen_btn.setText("🎙️ Start Listening")
        self.listen_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.waveform.set_active(False)

        self.status_label.setText("Status: Stopped")
        self.status_label.setStyleSheet("font-weight: bold; color: #f23f43;")

        # Stop voice thread
        if self.voice_thread:
            self.voice_thread.stop()
            self.voice_thread.wait()
            self.voice_thread = None

        self.add_to_transcript("[System] Listening stopped.")

    def on_audio_received(self, audio_data: np.ndarray):
        """Handle audio data received"""
        self.waveform.update_waveform(audio_data)

    def on_text_recognized(self, text: str, language: str):
        """Handle text recognition"""
        self.add_to_transcript(f"[You ({language})]: {text}")

        # Update confidence (placeholder)
        self.confidence_bar.setValue(90)

        # Simulate response
        self.add_to_transcript(f"[XENO]: I heard you say: {text}")

    def on_error(self, error: str):
        """Handle error"""
        self.add_to_transcript(f"[Error]: {error}")
        self.status_label.setText(f"Status: Error - {error}")
        self.status_label.setStyleSheet("font-weight: bold; color: #f23f43;")

    def on_language_changed(self, index: int):
        """Handle language change"""
        language = self.language_combo.itemData(index)
        self.voice_engine.set_language(language)
        self.add_to_transcript(f"[System] Language changed to: {language.name}")

    def add_to_transcript(self, text: str):
        """Add text to transcript"""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        self.transcript.append(f"[{timestamp}] {text}")

        # Auto-scroll to bottom
        cursor = self.transcript.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.transcript.setTextCursor(cursor)
