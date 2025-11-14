"""
XENO Daemon - Background service manager
Coordinates all modules and handles task scheduling
"""
import asyncio
import signal
import sys
from typing import Optional
from pathlib import Path

from core.config import Config
from core.logger import setup_logger
from utils.system import enable_autostart


class XenoDaemon:
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
            
            # Enable autostart if not already enabled
            if self.config.get('user.name'):
                self.logger.info("Enabling autostart...")
                enable_autostart()
            
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
            from PyQt6.QtWidgets import QApplication
            from ui.tray import SystemTrayApp
            from ui.main_window import XenoMainWindow
            
            self.logger.info("Starting UI...")
            
            # Create Qt application
            app = QApplication(sys.argv)
            app.setApplicationName(self.config.app_name)
            app.setApplicationVersion(self.config.app_version)
            
            # Prevent app from quitting when windows are closed
            app.setQuitOnLastWindowClosed(False)
            
            # Create main window (hidden by default)
            self.main_window = XenoMainWindow(self)
            
            # Create system tray application
            tray_app = SystemTrayApp(self.config, self, self.main_window)
            
            # Show greeting if user is registered
            if self.config.user.name:
                tray_app.show_greeting()
            
            # Show main window
            self.main_window.show()
            
            self.running = True
            self.logger.info("XENO is ready!")
            
            # Run Qt event loop
            return app.exec()
            
        except ImportError as e:
            self.logger.error(f"UI dependencies not available: {e}")
            self.logger.info("Falling back to headless mode...")
            return self._run_headless()
    
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
