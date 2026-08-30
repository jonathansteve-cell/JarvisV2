"""
Jarvis V2 - AI Tests
=====================
Tests for AI conversation and response generation.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.jarvis import Jarvis
from personality.response_generator import ResponseGenerator


class TestAIConversation:
    """Test AI conversation capabilities."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.jarvis = Jarvis()
    
    def test_greeting(self):
        """Test greeting generation."""
        greeting = self.jarvis.response_gen.greeting()
        assert greeting is not None
        assert len(greeting) > 0
        assert "jarvis" in greeting.lower() or "sir" in greeting.lower()
    
    def test_offline_response(self):
        """Test offline response generation."""
        response = self.jarvis.response_gen.offline_response("what can you do")
        assert response is not None
        assert len(response) > 0
        assert "can" in response.lower() or "able" in response.lower()
    
    def test_time_response(self):
        """Test time-related responses."""
        response = self.jarvis.response_gen.offline_response("what time is it")
        assert response is not None
        assert any(word in response.lower() for word in ["time", "clock", "hour"])
    
    def test_date_response(self):
        """Test date-related responses."""
        response = self.jarvis.response_gen.offline_response("what is today's date")
        assert response is not None
        assert any(word in response.lower() for word in ["today", "date", "day"])
    
    def test_acknowledge(self):
        """Test action acknowledgment."""
        response = self.jarvis.response_gen.acknowledge("Opening Chrome")
        assert response is not None
        assert "chrome" in response.lower() or "opening" in response.lower()
    
    @patch.dict('os.environ', {'GROQ_API_KEY': ''})
    def test_no_api_key(self):
        """Test behavior without API key."""
        response = self.jarvis.response_gen.generate("hello")
        assert response.provider == "offline"
    
    def test_assistant_name(self):
        """Test assistant name retrieval."""
        name = self.jarvis.response_gen.assistant_name()
        assert name is not None
        assert isinstance(name, str)


class TestCommandProcessing:
    """Test command processing."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.jarvis = Jarvis()
    
    def test_system_status(self):
        """Test system status command."""
        result = self.jarvis.process_command("system status", speak=False)
        assert result is not None
        assert result.text is not None
    
    def test_time_command(self):
        """Test time command."""
        result = self.jarvis.process_command("what time is it", speak=False)
        assert result is not None
        assert result.text is not None
    
    def test_joke_command(self):
        """Test joke command."""
        result = self.jarvis.process_command("tell me a joke", speak=False)
        assert result is not None
        assert result.text is not None
    
    def test_unknown_command(self):
        """Test unknown command handling."""
        result = self.jarvis.process_command("xyzabc123", speak=False)
        assert result is not None
        assert result.text is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
