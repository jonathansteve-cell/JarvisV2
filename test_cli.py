"""
Jarvis V2 - CLI Tests
======================
Tests for command-line interface functionality.
"""

import pytest
import sys
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from main import run_command, run_check


class TestCLICommands:
    """Test CLI command execution."""
    
    def test_run_command_time(self):
        """Test time command via CLI."""
        result = run_command("what time is it")
        assert result == 0  # Success
    
    def test_run_command_joke(self):
        """Test joke command via CLI."""
        result = run_command("tell me a joke")
        assert result == 0  # Success
    
    def test_run_command_system_status(self):
        """Test system status command via CLI."""
        result = run_command("system status")
        assert result == 0  # Success
    
    def test_run_command_unknown(self):
        """Test unknown command via CLI."""
        result = run_command("xyzabc123")
        # Unknown commands should still return 0
        assert result == 0


class TestHealthCheck:
    """Test health check functionality."""
    
    def test_health_check_verbose(self):
        """Test verbose health check."""
        result = run_check(verbose=True)
        # Health check should complete (may return non-zero if issues found)
        assert isinstance(result, int)
    
    def test_health_check_quiet(self):
        """Test quiet health check."""
        result = run_check(verbose=False)
        assert isinstance(result, int)


class TestMainModule:
    """Test main module imports and structure."""
    
    def test_import_main(self):
        """Test main module import."""
        import main
        assert hasattr(main, 'main')
        assert hasattr(main, 'run_command')
        assert hasattr(main, 'run_gui')
        assert hasattr(main, 'run_web')
    
    def test_import_jarvis(self):
        """Test Jarvis class import."""
        from core.jarvis import Jarvis
        jarvis = Jarvis()
        assert jarvis is not None
    
    def test_import_config_manager(self):
        """Test config manager import."""
        from core.config_manager import ConfigManager
        config = ConfigManager()
        assert config is not None
    
    def test_import_user_manager(self):
        """Test user manager import."""
        from core.user_manager import UserManager
        manager = UserManager()
        assert manager is not None


class TestModuleImports:
    """Test that all modules can be imported."""
    
    def test_import_research_controller(self):
        """Test research controller import."""
        from modules.research_controller import ResearchController
        controller = ResearchController()
        assert controller is not None
    
    def test_import_roblox_grind_controller(self):
        """Test Roblox grind controller import."""
        from modules.roblox_grind_controller import RobloxGrindController
        controller = RobloxGrindController()
        assert controller is not None
    
    def test_import_serious_mode_controller(self):
        """Test serious mode controller import."""
        from modules.serious_mode_controller import SeriousModeController
        controller = SeriousModeController()
        assert controller is not None
    
    def test_import_system_controller(self):
        """Test system controller import."""
        from modules.system_controller import SystemController
        controller = SystemController()
        assert controller is not None
    
    def test_import_application_manager(self):
        """Test application manager import."""
        from modules.application_manager import ApplicationManager
        manager = ApplicationManager()
        assert manager is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
