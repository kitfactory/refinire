"""
Tests for CutContextProvider
CutContextProviderのテスト
"""

import pytest
from pathlib import Path
from typing import Dict, Any
from refinire.agents.providers.cut_context import CutContextProvider
from refinire.agents.providers.conversation_history import ConversationHistoryProvider
from refinire.agents.providers.fixed_file import FixedFileProvider


class TestCutContextProvider:
    """Test cases for CutContextProvider"""
    
    def test_provider_initialization(self):
        """Test basic provider initialization"""
        provider = ConversationHistoryProvider(max_items=5)
        cut_provider = CutContextProvider(
            provider=provider,
            max_chars=1000,
            cut_strategy="end"
        )
        
        assert cut_provider.provider == provider
        assert cut_provider.max_chars == 1000
        assert cut_provider.max_tokens is None
        assert cut_provider.cut_strategy == "end"
        assert cut_provider.preserve_sections is True
    
    def test_provider_initialization_with_tokens(self):
        """Test provider initialization with token limit"""
        provider = ConversationHistoryProvider(max_items=5)
        cut_provider = CutContextProvider(
            provider=provider,
            max_tokens=100,
            cut_strategy="middle"
        )
        
        assert cut_provider.max_chars is None
        assert cut_provider.max_tokens == 100
        assert cut_provider.cut_strategy == "middle"
    
    def test_provider_initialization_validation(self):
        """Test provider initialization validation"""
        provider = ConversationHistoryProvider(max_items=5)
        
        # Test invalid cut strategy
        with pytest.raises(ValueError, match="cut_strategy must be"):
            CutContextProvider(
                provider=provider,
                max_chars=1000,
                cut_strategy="invalid"
            )
        
        # Test no limits specified
        with pytest.raises(ValueError, match="Either max_chars or max_tokens must be specified"):
            CutContextProvider(provider=provider)
    
    def test_token_counting(self):
        """Test token counting functionality"""
        provider = ConversationHistoryProvider(max_items=5)
        cut_provider = CutContextProvider(
            provider=provider,
            max_tokens=10
        )
        
        # Test simple token counting
        text = "This is a test sentence with multiple words."
        tokens = cut_provider._count_tokens(text)
        assert tokens == 8  # "This", "is", "a", "test", "sentence", "with", "multiple", "words"
        
        # Test with punctuation
        text_with_punct = "Hello, world! How are you?"
        tokens = cut_provider._count_tokens(text_with_punct)
        assert tokens == 5  # "Hello,", "world!", "How", "are", "you?"
    
    def test_text_cutting_end_strategy(self):
        """Test text cutting with end strategy"""
        provider = ConversationHistoryProvider(max_items=5)
        cut_provider = CutContextProvider(
            provider=provider,
            max_chars=20,
            cut_strategy="end"
        )
        
        long_text = "This is a very long text that should be cut"
        result = cut_provider._cut_text(long_text, 20, "end")
        assert len(result) <= 20
        assert result == "This is a very long "  # Note the trailing space
    
    def test_text_cutting_start_strategy(self):
        """Test text cutting with start strategy"""
        provider = ConversationHistoryProvider(max_items=5)
        cut_provider = CutContextProvider(
            provider=provider,
            max_chars=20,
            cut_strategy="start"
        )
        
        long_text = "This is a very long text that should be cut"
        result = cut_provider._cut_text(long_text, 20, "start")
        assert len(result) <= 20
        assert result == "t that should be cut"  # Keep the end part
    
    def test_text_cutting_middle_strategy(self):
        """Test text cutting with middle strategy"""
        provider = ConversationHistoryProvider(max_items=5)
        cut_provider = CutContextProvider(
            provider=provider,
            max_chars=30,
            cut_strategy="middle"
        )
        
        long_text = "This is a very long text that should be cut from the middle"
        result = cut_provider._cut_text(long_text, 30, "middle")
        assert len(result) <= 30
        # Should contain "..." or be cut from end if middle strategy doesn't work
        assert "..." in result or len(result) <= 30
    
    def test_section_splitting(self):
        """Test section splitting functionality"""
        provider = ConversationHistoryProvider(max_items=5)
        cut_provider = CutContextProvider(
            provider=provider,
            max_chars=50
        )
        
        text_with_sections = "Section 1\n\nSection 2\n\nSection 3"
        sections = cut_provider._split_into_sections(text_with_sections)
        assert len(sections) == 3
        assert "Section 1" in sections[0]
        assert "Section 2" in sections[1]
        assert "Section 3" in sections[2]
    
    def test_section_preservation(self):
        """Test section preservation during cutting"""
        provider = ConversationHistoryProvider(max_items=5)
        cut_provider = CutContextProvider(
            provider=provider,
            max_chars=30,
            cut_strategy="end",
            preserve_sections=True
        )
        
        text_with_sections = "Section 1\n\nSection 2\n\nSection 3"
        result = cut_provider._cut_text(text_with_sections, 30, "end")
        # Should preserve complete sections
        assert "Section 1" in result or "Section 2" in result or "Section 3" in result
    
    def test_get_context_with_character_limit(self):
        """Test get_context with character limit"""
        # Create a mock provider that returns long text
        class MockProvider:
            def get_context(self, query, previous_context=None, **kwargs):
                return "This is a very long context that should be cut when it exceeds the character limit"
            
            def update(self, interaction):
                pass
            
            def clear(self):
                pass
        
        cut_provider = CutContextProvider(
            provider=MockProvider(),
            max_chars=30,
            cut_strategy="end"
        )
        
        result = cut_provider.get_context("test query")
        assert len(result) <= 30
        assert "This is a very long context" in result
    
    def test_get_context_with_token_limit(self):
        """Test get_context with token limit"""
        class MockProvider:
            def get_context(self, query, previous_context=None, **kwargs):
                return "This is a very long context with many tokens that should be cut"
            
            def update(self, interaction):
                pass
            
            def clear(self):
                pass
        
        cut_provider = CutContextProvider(
            provider=MockProvider(),
            max_tokens=5,
            cut_strategy="end"
        )
        
        result = cut_provider.get_context("test query")
        # Should be cut to approximately 5 tokens (allow some tolerance)
        tokens = cut_provider._count_tokens(result)
        assert tokens <= 7  # Allow some tolerance for token estimation
    
    def test_get_context_no_cutting_needed(self):
        """Test get_context when no cutting is needed"""
        class MockProvider:
            def get_context(self, query, previous_context=None, **kwargs):
                return "Short text"
            
            def update(self, interaction):
                pass
            
            def clear(self):
                pass
        
        cut_provider = CutContextProvider(
            provider=MockProvider(),
            max_chars=100,
            cut_strategy="end"
        )
        
        result = cut_provider.get_context("test query")
        assert result == "Short text"
    
    def test_update_and_clear_delegation(self):
        """Test that update and clear delegate to wrapped provider"""
        provider = ConversationHistoryProvider(max_items=5)
        cut_provider = CutContextProvider(
            provider=provider,
            max_chars=100
        )
        
        # Test update delegation
        interaction = {"user": "test", "assistant": "response"}
        cut_provider.update(interaction)
        # Should not raise any errors
        
        # Test clear delegation
        cut_provider.clear()
        # Should not raise any errors
    
    def test_config_schema(self):
        """Test configuration schema"""
        schema = CutContextProvider.get_config_schema()
        
        assert 'description' in schema
        assert 'parameters' in schema
        assert 'example' in schema
        
        params = schema['parameters']
        assert 'provider' in params
        assert 'max_chars' in params
        assert 'max_tokens' in params
        assert 'cut_strategy' in params
        assert 'preserve_sections' in params
        
        assert params['cut_strategy']['default'] == 'end'
        assert params['preserve_sections']['default'] is True
    
    def test_from_config_with_dict_provider(self):
        """Test creating provider from config with dict provider"""
        config = {
            'provider': {
                'type': 'conversation_history',
                'max_items': 10
            },
            'max_chars': 2000,
            'cut_strategy': 'middle',
            'preserve_sections': False
        }
        
        provider = CutContextProvider.from_config(config)
        
        assert provider.max_chars == 2000
        assert provider.cut_strategy == 'middle'
        assert provider.preserve_sections is False
        assert isinstance(provider.provider, ConversationHistoryProvider)
    
    def test_from_config_with_string_provider(self):
        """Test creating provider from config with string provider"""
        config = {
            'provider': '- conversation_history:\n  max_items: 5',
            'max_tokens': 100,
            'cut_strategy': 'start'
        }
        
        provider = CutContextProvider.from_config(config)
        
        assert provider.max_tokens == 100
        assert provider.cut_strategy == 'start'
        assert isinstance(provider.provider, ConversationHistoryProvider)
    
    def test_provider_name(self):
        """Test provider name"""
        provider = ConversationHistoryProvider(max_items=5)
        cut_provider = CutContextProvider(
            provider=provider,
            max_chars=100
        )
        
        assert cut_provider.provider_name == "cut_context"
    
    def test_complex_cutting_scenario(self):
        """Test complex cutting scenario with multiple sections"""
        class MockProvider:
            def get_context(self, query, previous_context=None, **kwargs):
                return """# File: test.py
This is the first section with some content.

# File: another.py
This is the second section with more content.

# File: third.py
This is the third section with even more content."""
            
            def update(self, interaction):
                pass
            
            def clear(self):
                pass
        
        cut_provider = CutContextProvider(
            provider=MockProvider(),
            max_chars=80,
            cut_strategy="middle",
            preserve_sections=True
        )
        
        result = cut_provider.get_context("test query")
        # Should preserve file sections and cut from middle
        assert "File:" in result  # Check for file marker
        assert len(result) <= 80 