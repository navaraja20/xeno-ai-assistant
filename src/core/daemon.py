"""
XENO Daemon - Background service manager
Coordinates all modules and handles task scheduling
"""
import asyncio
import signal
import sys
from pathlib import Path
from typing import Optional

from core.config import Config
from core.logger import setup_logger
from utils.system import enable_autostart


class XENODaemon:
    """Main daemon service for XENO"""

    def __init__(self, config: Config, ui_enabled: bool = True):
        """
        Initialize XENO daemon

        Args:
            config: Configuration instance
            ui_enabled: Whether to show UI
        """
        self.config = config
        self.ui_enabled = ui_enabled
        self.logger = setup_logger("daemon", debug=config.debug)
        self.running = False
        self.modules = {}

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def run(self) -> int:
        """
        Run the daemon

        Returns:
            Exit code
        """
        try:
            self.logger.info("XENO Daemon starting...")

            # Note: Autostart is configured separately via settings
            # Don't auto-enable on every launch to avoid duplicates

            # Initialize modules
            self._initialize_modules()

            # Start UI if enabled
            if self.ui_enabled:
                return self._run_with_ui()
            else:
                return self._run_headless()

        except Exception as e:
            self.logger.error(f"Fatal error in daemon: {e}", exc_info=True)
            return 1

    def _initialize_modules(self):
        """Initialize all enabled modules"""
        self.logger.info("Initializing modules...")

        # TODO: Initialize modules based on config
        # For now, just log which modules are enabled

        if self.config.email.enabled:
            self.logger.info("  [OK] Email module enabled")

        if self.config.jobs.enabled:
            self.logger.info("  [OK] Job application module enabled")

        if self.config.github.enabled:
            self.logger.info("  [OK] GitHub module enabled")

        if self.config.linkedin.enabled:
            self.logger.info("  [OK] LinkedIn module enabled")

        if self.config.calendar.enabled:
            self.logger.info("  [OK] Calendar module enabled")

    def _run_with_ui(self) -> int:
        """Run daemon with UI"""
        try:
            import sys
            from pathlib import Path

            # Add parent directory to path for imports
            parent_dir = Path(__file__).parent.parent.parent
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))

            from PyQt6.QtWidgets import QApplication

            from src.ui.main_window import XENOMainWindow
            from src.ui.tray import SystemTrayApp

            self.logger.info("Starting UI...")

            # Create Qt application
            app = QApplication(sys.argv)
            app.setApplicationName(self.config.app_name)
            app.setApplicationVersion(self.config.app_version)

            # CRITICAL: Prevent app from quitting when windows are closed
            # This allows XENO to run in system tray
            app.setQuitOnLastWindowClosed(False)
            self.logger.info("✓ App configured to run in background (tray mode)")

            # Create main window (hidden by default)
            try:
                self.logger.info("Creating main window...")
                self.main_window = XENOMainWindow(self)
                self.logger.info("✓ Main window created successfully")
            except Exception as e:
                self.logger.error(f"FATAL: Failed to create main window: {e}", exc_info=True)
                raise

            # Create system tray application (store as instance variable to prevent garbage collection)
            try:
                self.tray_app = SystemTrayApp(self.config, self, self.main_window)
                self.logger.info("✓ System tray icon created")
            except Exception as e:
                self.logger.error(f"✗ Failed to create system tray: {e}")
                self.tray_app = None

            # Show greeting if user is registered
            if self.config.user.name and self.tray_app:
                self.tray_app.show_greeting()

            # Show main window
            self.main_window.show()

            self.running = True
            self.logger.info("XENO is ready!")

            # CRITICAL: Re-confirm app won't quit when window closes (do this AFTER window creation)
            app.setQuitOnLastWindowClosed(False)
            self.logger.info("✓ Confirmed: App will NOT quit when window closes")

            # Run Qt event loop
            exit_code = app.exec()
            self.logger.info(f"Qt event loop exited with code: {exit_code}")
            return exit_code

        except ImportError as e:
            self.logger.error(f"UI dependencies not available: {e}")
            self.logger.info("Falling back to headless mode...")
            return self._run_headless()
        except Exception as e:
            self.logger.error(f"Error in UI mode: {e}", exc_info=True)
            return 1

    def _run_headless(self) -> int:
        """Run daemon without UI (headless mode)"""
        self.logger.info("Running in headless mode...")
        self.running = True

        try:
            # Run event loop
            asyncio.run(self._event_loop())
            return 0
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
            return 0

    async def _event_loop(self):
        """Main event loop for headless mode"""
        self.logger.info("XENO is ready! (headless)")

        while self.running:
            # TODO: Process scheduled tasks
            # TODO: Check for events
            await asyncio.sleep(1)

        self.logger.info("Event loop stopped")

    def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("Shutting down XENO...")
        self.running = False

        # TODO: Shutdown all modules
        # TODO: Save state

        self.logger.info("[OK] Shutdown complete")
