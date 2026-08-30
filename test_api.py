"""
Jarvis V2 - API Tests
======================
Tests for API integrations and validation.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.api_manager import APIManager, APIProvider
from core.api_validator import APIValidator, ValidationStatus
from core.secure_env import SecureEnvManager


class TestAPIManager:
    """Test API manager functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.manager = APIManager()
    
    def test_get_configured_providers(self):
        """Test getting configured providers."""
        providers = self.manager.get_configured_providers()
        assert isinstance(providers, list)
    
    def test_has_credentials(self):
        """Test credential checking."""
        result = self.manager.has_credentials(APIProvider.GROQ)
        assert isinstance(result, bool)
    
    def test_get_provider_info(self):
        """Test provider info retrieval."""
        info = self.manager.get_provider_info(APIProvider.GROQ)
        assert "provider" in info
        assert "configured" in info
    
    def test_export_config(self):
        """Test config export."""
        config = self.manager.export_config()
        assert isinstance(config, dict)
        assert "groq" in config


class TestAPIValidator:
    """Test API validation."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.validator = APIValidator()
    
    def test_validate_invalid_key(self):
        """Test validation with invalid key."""
        result = self.validator.validate_groq("invalid_key")
        assert result.status == ValidationStatus.INVALID
    
    def test_validate_placeholder_key(self):
        """Test validation with placeholder key."""
        result = self.validator.validate_groq("your_groq_api_key_here")
        assert result.status == ValidationStatus.INVALID
    
    def test_health_metrics(self):
        """Test health metrics tracking."""
        # Perform a validation to generate metrics
        self.validator.validate_groq("test_key")
        
        metrics = self.validator.get_health_metrics("groq")
        assert metrics is not None
        assert metrics.total_requests > 0


class TestSecureEnv:
    """Test secure environment management."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.env_manager = SecureEnvManager()
    
    def test_load_env(self):
        """Test environment loading."""
        env_vars = self.env_manager.load()
        assert isinstance(env_vars, dict)
    
    def test_get_set_variable(self):
        """Test getting and setting variables."""
        # Set a test variable
        self.env_manager.set("TEST_VAR", "test_value", save=False)
        
        # Get it back
        value = self.env_manager.get("TEST_VAR")
        assert value == "test_value"
    
    def test_validate_variable(self):
        """Test variable validation."""
        # Valid Groq key format
        is_valid, msg = self.env_manager.validate("GROQ_API_KEY", "gsk_test123456789")
        assert is_valid is True
        
        # Invalid format
        is_valid, msg = self.env_manager.validate("GROQ_API_KEY", "invalid")
        assert is_valid is False
    
    def test_masked_values(self):
        """Test masked value retrieval."""
        masked = self.env_manager.get_masked_values()
        assert isinstance(masked, dict)
    
    def test_status_report(self):
        """Test status report generation."""
        report = self.env_manager.get_status_report()
        assert isinstance(report, str)
        assert len(report) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
