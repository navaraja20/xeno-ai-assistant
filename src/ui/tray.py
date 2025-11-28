"""
System Tray Application for XENO
"""
from datetime import datetime
from pathlib import Path

import pyttsx3
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon


class SystemTrayApp:
    """System tray application"""

    def __init__(self, config, daemon, main_window=None):
        """
        Initialize system tray

        Args:
            config: Configuration instance
            daemon: Daemon instance
            main_window: Main window instance (optional)
        """
        self.config = config
        self.daemon = daemon
        self.main_window = main_window

        # Create system tray icon
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setToolTip("XENO - Personal AI Assistant")

        # Set icon (using a default for now, will add custom later)
        self._set_icon()

        # Create menu
        self._create_menu()

        # Show tray icon
        self.tray_icon.show()

        # Connect activation signal
        self.tray_icon.activated.connect(self._on_tray_activated)

        # Setup voice engine
        try:
            self.voice_engine = pyttsx3.init()
            self._configure_voice()
        except:
            self.voice_engine = None

    def _set_icon(self):
        """Set tray icon"""
        # For now, use a simple text-based icon
        # TODO: Create proper icon file
        from PyQt6.QtGui import QColor, QPainter, QPixmap

        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(0, 0, 0, 0))

        painter = QPainter(pixmap)
        painter.setBrush(QColor(52, 152, 219))  # Blue
        painter.drawEllipse(8, 8, 48, 48)
        painter.end()

        icon = QIcon(pixmap)
        self.tray_icon.setIcon(icon)

    def _configure_voice(self):
        """Configure voice engine for Optimus Prime-like voice"""
        if not self.voice_engine:
            return

        # Get available voices
        voices = self.voice_engine.getProperty("voices")

        # Try to find a deep male voice
        for voice in voices:
            if "male" in voice.name.lower() or "david" in voice.name.lower():
                self.voice_engine.setProperty("voice", voice.id)
                break

        # Set speech rate (slower for more dramatic effect)
        self.voice_engine.setProperty("rate", 150)  # Default is ~200

        # Set volume
        self.voice_engine.setProperty("volume", 0.9)

    def _create_menu(self):
        """Create context menu for tray icon"""
        menu = QMenu()

        # Dashboard action
        dashboard_action = QAction("📊 Open Dashboard", menu)
        dashboard_action.triggered.connect(self._open_dashboard)
        menu.addAction(dashboard_action)

        menu.addSeparator()

        # Quick actions
        email_action = QAction("📧 Check Emails", menu)
        email_action.triggered.connect(self._check_emails)
        email_action.setEnabled(self.config.email.enabled)
        menu.addAction(email_action)

        jobs_action = QAction("💼 Find Jobs", menu)
        jobs_action.triggered.connect(self._find_jobs)
        jobs_action.setEnabled(self.config.jobs.enabled)
        menu.addAction(jobs_action)

        github_action = QAction("🐙 Update GitHub", menu)
        github_action.triggered.connect(self._update_github)
        github_action.setEnabled(self.config.github.enabled)
        menu.addAction(github_action)

        menu.addSeparator()

        # Settings
        settings_action = QAction("⚙️ Settings", menu)
        settings_action.triggered.connect(self._open_settings)
        menu.addAction(settings_action)

        # About
        about_action = QAction("ℹ️ About", menu)
        about_action.triggered.connect(self._show_about)
        menu.addAction(about_action)

        menu.addSeparator()

        # Exit
        exit_action = QAction("🚪 Exit", menu)
        exit_action.triggered.connect(self._exit_application)
        menu.addAction(exit_action)

        self.tray_icon.setContextMenu(menu)

    def _on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single click - show menu
            pass
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Double click - open dashboard
            self._open_dashboard()

    def show_notification(self, message, title="XENO", duration=3000):
        """Show tray notification"""
        self.tray_icon.showMessage(
            title, message, QSystemTrayIcon.MessageIcon.Information, duration
        )

    def show_greeting(self):
        """Show greeting message"""
        name = self.config.user.name
        hour = datetime.now().hour

        # Determine greeting based on time
        if hour < 12:
            greeting = "Good morning"
        elif hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        # For display
        message = f"{greeting}, Master {name}. XENO is online and at your service."
        # For speech - pronounce XENO as "XENOo" to make it sound like a name
        speech_message = f"{greeting}, Master {name}. XENOo is online and at your service."

        # Show notification
        self.show_notification(message)

        # Speak greeting if voice enabled
        if self.config.user.voice_enabled and self.voice_engine:
            try:
                self.voice_engine.say(speech_message)
                self.voice_engine.runAndWait()
            except:
                pass

    def _open_dashboard(self):
        """Open main dashboard"""
        if self.main_window:
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
        else:
            self.tray_icon.showMessage(
                "XENO", "Dashboard not available", QSystemTrayIcon.MessageIcon.Information, 2000
            )

    def _check_emails(self):
        """Check emails"""
        # TODO: Implement email checking
        self.tray_icon.showMessage(
            "XENO", "Checking your emails...", QSystemTrayIcon.MessageIcon.Information, 2000
        )

    def _find_jobs(self):
        """Find jobs"""
        # TODO: Implement job search
        self.tray_icon.showMessage(
            "XENO",
            "Searching for job opportunities...",
            QSystemTrayIcon.MessageIcon.Information,
            2000,
        )

    def _update_github(self):
        """Update GitHub"""
        # TODO: Implement GitHub update
        self.tray_icon.showMessage(
            "XENO",
            "Checking your GitHub repositories...",
            QSystemTrayIcon.MessageIcon.Information,
            2000,
        )

    def _open_settings(self):
        """Open settings window"""
        # TODO: Implement settings window
        self.tray_icon.showMessage(
            "XENO", "Settings panel coming soon!", QSystemTrayIcon.MessageIcon.Information, 2000
        )

    def _show_about(self):
        """Show about dialog"""
        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.about(
            None,
            "About XENO",
            f"<h2>XENO</h2>"
            f"<p><b>Personal AI Assistant</b></p>"
            f"<p>Version: {self.config.app_version}</p>"
            f"<p><br>Inspired by Jarvis from Iron Man</p>"
            f"<p>Your intelligent digital companion for productivity.</p>",
        )

    def _exit_application(self):
        """Exit the application"""
        from PyQt6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            None,
            "Exit XENO",
            "Are you sure you want to exit XENO?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Speak goodbye if voice enabled - pronounce XENO as "XENOo"
            if self.config.user.voice_enabled and self.voice_engine:
                try:
                    self.voice_engine.say(
                        f"Goodbye, Master {self.config.user.name}. Until next time."
                    )
                    self.voice_engine.runAndWait()
                except:
                    pass

            self.daemon.shutdown()
            QApplication.quit()
