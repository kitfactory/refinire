"""
Tests for the Refinire CLI module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from refinire.cli import RefinireTemplateGenerator


class TestRefinireTemplateGenerator:
    """Test the RefinireTemplateGenerator class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.generator = RefinireTemplateGenerator()
    
    def test_init(self):
        """Test generator initialization"""
        assert self.generator.selected_providers == []
        assert self.generator.selected_features == []
        assert self.generator.console is not None
    
    def test_get_available_providers_with_oneenv(self):
        """Test getting providers when oneenv is available"""
        with patch('refinire.cli.oneenv') as mock_oneenv:
            mock_oneenv.has_category.return_value = True
            mock_oneenv.get_options.return_value = ["OpenAI", "Anthropic", "Google"]
            
            providers = self.generator.get_available_providers()
            
            assert len(providers) == 3
            assert ("OpenAI", "OpenAI") in providers
            assert ("Anthropic", "Anthropic") in providers
            assert ("Google", "Google") in providers
    
    def test_get_available_providers_fallback(self):
        """Test getting providers when oneenv fails"""
        with patch('refinire.cli.oneenv') as mock_oneenv:
            mock_oneenv.has_category.return_value = False
            
            providers = self.generator.get_available_providers()
            
            assert len(providers) == 7  # Fallback providers
            provider_names = [p[0] for p in providers]
            assert "OpenAI" in provider_names
            assert "Anthropic" in provider_names
            assert "Google" in provider_names
    
    def test_get_available_providers_exception(self):
        """Test getting providers when oneenv raises exception"""
        with patch('refinire.cli.oneenv') as mock_oneenv:
            mock_oneenv.has_category.side_effect = Exception("Test error")
            
            providers = self.generator.get_available_providers()
            
            assert len(providers) == 7  # Fallback providers
    
    def test_generate_template_content_with_oneenv(self):
        """Test template generation using oneenv"""
        providers = ["OpenAI", "Anthropic"]
        features = ["Agents", "Tracing"]
        
        with patch('refinire.cli.oneenv') as mock_oneenv:
            mock_oneenv.generate_template.return_value = "# Test template content"
            
            content = self.generator.generate_template_content(providers, features)
            
            assert content == "# Test template content"
            mock_oneenv.generate_template.assert_called_once()
    
    def test_generate_template_content_fallback(self):
        """Test template generation fallback"""
        providers = ["OpenAI", "Anthropic"]
        features = ["Agents", "Development"]
        
        with patch('refinire.cli.oneenv') as mock_oneenv:
            mock_oneenv.generate_template.side_effect = Exception("Test error")
            
            content = self.generator.generate_template_content(providers, features)
            
            assert "# Refinire Environment Variables" in content
            assert "OPENAI_API_KEY=" in content
            assert "ANTHROPIC_API_KEY=" in content
            assert "REFINIRE_DEFAULT_LLM_MODEL=" in content
            assert "REFINIRE_DEBUG=" in content
    
    def test_generate_fallback_template_all_providers(self):
        """Test fallback template generation with all providers"""
        providers = ["OpenAI", "Anthropic", "Google", "OpenRouter", "Groq", "Ollama", "LMStudio"]
        features = ["Agents", "Tracing", "Development"]
        
        content = self.generator._generate_fallback_template(providers, features)
        
        # Check provider variables
        assert "OPENAI_API_KEY=" in content
        assert "ANTHROPIC_API_KEY=" in content
        assert "GOOGLE_API_KEY=" in content
        assert "OPENROUTER_API_KEY=" in content
        assert "GROQ_API_KEY=" in content
        assert "OLLAMA_BASE_URL=" in content
        assert "LMSTUDIO_BASE_URL=" in content
        
        # Check feature variables
        assert "REFINIRE_DEFAULT_LLM_MODEL=" in content
        assert "REFINIRE_TRACE_OTLP_ENDPOINT=" in content
        assert "REFINIRE_DEBUG=" in content
    
    def test_save_template_success(self):
        """Test successful template saving"""
        content = "# Test template"
        filename = "test.env"
        
        with patch('pathlib.Path.exists', return_value=False), \
             patch('builtins.open', mock_open()) as mock_file:
            
            result = self.generator.save_template(content, filename)
            
            assert result is True
            mock_file.assert_called_once_with(Path(filename), 'w', encoding='utf-8')
    
    def test_save_template_file_exists_overwrite(self):
        """Test template saving when file exists and user confirms overwrite"""
        content = "# Test template"
        filename = "test.env"
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('refinire.cli.Confirm.ask', return_value=True):
            
            result = self.generator.save_template(content, filename)
            
            assert result is True
            mock_file.assert_called_once_with(Path(filename), 'w', encoding='utf-8')
    
    def test_save_template_file_exists_no_overwrite(self):
        """Test template saving when file exists and user declines overwrite"""
        content = "# Test template"
        filename = "test.env"
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('refinire.cli.Confirm.ask', return_value=False):
            
            result = self.generator.save_template(content, filename)
            
            assert result is False
    
    def test_save_template_error(self):
        """Test template saving error handling"""
        content = "# Test template"
        filename = "test.env"
        
        with patch('pathlib.Path.exists', return_value=False), \
             patch('builtins.open', side_effect=IOError("Test error")):
            
            result = self.generator.save_template(content, filename)
            
            assert result is False


def mock_open():
    """Mock open function for file operations"""
    return MagicMock()


@pytest.fixture
def mock_console():
    """Mock console for testing"""
    return Mock()


def test_main_function_exists():
    """Test that main function exists and can be imported"""
    from refinire.cli import main
    assert callable(main)


def test_cli_imports():
    """Test that CLI module can be imported with required dependencies"""
    try:
        import refinire.cli
        assert hasattr(refinire.cli, 'RefinireTemplateGenerator')
        assert hasattr(refinire.cli, 'main')
    except ImportError as e:
        # Skip test if optional dependencies not installed
        pytest.skip(f"CLI dependencies not installed: {e}")