"""
XENO - Personal AI Assistant
Main entry point for the application
"""
import sys
import os
import warnings
import argparse
from pathlib import Path

# Suppress non-critical warnings for cleaner startup
warnings.filterwarnings("ignore", category=FutureWarning, module="google.api_core")
warnings.filterwarnings("ignore", message=".*packages_distributions.*")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from core.daemon import XENODaemon
from core.config import Config
from core.logger import setup_logger
from ui.setup_wizard import SetupWizard
from utils.system import is_first_run, create_directories


def main():
    """Main entry point for XENO"""
    parser = argparse.ArgumentParser(description="XENO - Personal AI Assistant")
    parser.add_argument("--setup", action="store_true", help="Run setup wizard")
    parser.add_argument("--no-ui", action="store_true", help="Run without UI (daemon only)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--config", type=str, help="Path to config file")
    
    args = parser.parse_args()
    
    # Setup directories
    create_directories()
    
    # Setup logging
    logger = setup_logger(debug=args.debug)
    logger.info("Starting XENO...")
    
    # Load configuration
    config = Config(config_path=args.config)
    
    # Check if first run or setup requested
    if is_first_run() or args.setup:
        logger.info("First run detected or setup requested")
        if not args.no_ui:
            # Run setup wizard
            from PyQt6.QtWidgets import QApplication
            app = QApplication(sys.argv)
            wizard = SetupWizard()
            
            if wizard.exec():
                logger.info("Setup completed successfully")
                # Save config from wizard
                config.save(wizard.get_config())
            else:
                logger.warning("Setup cancelled by user")
                return 1
        else:
            logger.error("Cannot run setup in no-ui mode")
            return 1
    
    # Start the daemon
    try:
        daemon = XENODaemon(config=config, ui_enabled=not args.no_ui)
        return daemon.run()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
