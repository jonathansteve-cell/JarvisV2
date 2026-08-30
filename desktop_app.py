"""
Jarvis V2 - Desktop Application Entry Point
=============================================
Main entry point for the packaged desktop application.

This file is used by PyInstaller to create the executable.
It handles:
- First-run setup wizard
- User login
- Main application launch
"""

from __future__ import annotations

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/jarvis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_base_path() -> Path:
    """Get the base path for the application."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return Path(sys.executable).parent
    else:
        # Running as script
        return Path(__file__).parent


def setup_environment():
    """Setup the application environment."""
    base_path = get_base_path()
    
    # Change to base directory
    os.chdir(base_path)
    
    # Add to path
    sys.path.insert(0, str(base_path))
    
    # Create necessary directories
    directories = ['data', 'logs', 'screenshots', 'documents', 'research']
    for directory in directories:
        (base_path / directory).mkdir(exist_ok=True)
    
    # Load environment variables
    env_file = base_path / '.env'
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    logger.info(f"Environment setup complete. Base path: {base_path}")


def check_first_run() -> bool:
    """Check if this is the first run."""
    from core.user_manager import get_user_manager
    user_manager = get_user_manager()
    return user_manager.is_first_run()


def run_setup_wizard():
    """Run the first-run setup wizard."""
    from gui.setup_wizard_gui import SetupWizardGUI
    
    logger.info("Running first-run setup wizard")
    wizard = SetupWizardGUI()
    wizard.run()


def check_login() -> bool:
    """Check if user is logged in."""
    from core.user_manager import get_user_manager
    user_manager = get_user_manager()
    
    if user_manager.is_logged_in():
        return True
    
    # Show login dialog
    from gui.login_dialog import show_login_dialog
    return show_login_dialog()


def run_main_application():
    """Run the main Jarvis application."""
    from gui.main_window import JarvisMainWindow
    
    logger.info("Starting Jarvis V2 main application")
    app = JarvisMainWindow()
    app.run()


def main():
    """Main entry point."""
    try:
        # Setup environment
        setup_environment()
        
        # Check if first run
        if check_first_run():
            logger.info("First run detected, launching setup wizard")
            run_setup_wizard()
        
        # Check login
        if not check_login():
            logger.info("Login cancelled or failed")
            return 1
        
        # Run main application
        run_main_application()
        
        return 0
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
