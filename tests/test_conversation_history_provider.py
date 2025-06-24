"""
Test Conversation History Provider
会話履歴プロバイダーのテスト

This module tests the ConversationHistoryProvider class and its functionality.
このモジュールはConversationHistoryProviderクラスとその機能をテストします。
"""

import pytest
from typing import Dict, Any

from refinire.agents.providers.conversation_history import ConversationHistoryProvider


class TestConversationHistoryProvider:
    """Test cases for ConversationHistoryProvider"""
    
    def test_provider_name(self):
        """Test that provider_name is correctly set"""
        assert ConversationHistoryProvider.provider_name == "conversation"
    
    def test_initialization_default_values(self):
        """Test initialization with default values"""
        provider = ConversationHistoryProvider()
        
        assert provider.history == []
        assert provider.max_items == 10
    
    def test_initialization_with_custom_values(self):
        """Test initialization with custom values"""
        initial_history = ["User: hello\nAssistant: hi"]
        provider = ConversationHistoryProvider(history=initial_history, max_items=5)
        
        assert provider.history == initial_history
        assert provider.max_items == 5
    
    def test_get_config_schema(self):
        """Test get_config_schema method"""
        schema = ConversationHistoryProvider.get_config_schema()
        
        assert isinstance(schema, dict)
        assert "description" in schema
        assert "parameters" in schema
        assert "example" in schema
        assert schema["description"] == "Provides conversation history context"
        assert "max_items" in schema["parameters"]
        assert schema["parameters"]["max_items"]["type"] == "int"
        assert schema["parameters"]["max_items"]["default"] == 10
    
    def test_from_config_empty(self):
        """Test from_config method with empty configuration"""
        provider = ConversationHistoryProvider.from_config({})
        
        assert isinstance(provider, ConversationHistoryProvider)
        assert provider.history == []
        assert provider.max_items == 10
    
    def test_from_config_with_max_items(self):
        """Test from_config method with max_items configuration"""
        config = {"max_items": 5}
        provider = ConversationHistoryProvider.from_config(config)
        
        assert isinstance(provider, ConversationHistoryProvider)
        assert provider.max_items == 5
    
    def test_get_context_empty_history(self):
        """Test get_context with empty history"""
        provider = ConversationHistoryProvider()
        
        context = provider.get_context("test query")
        assert context == ""
    
    def test_get_context_with_history(self):
        """Test get_context with existing history"""
        history = [
            "User: hello\nAssistant: hi",
            "User: how are you?\nAssistant: I'm fine, thank you!"
        ]
        provider = ConversationHistoryProvider(history=history)
        
        context = provider.get_context("test query")
        expected = "User: hello\nAssistant: hi\nUser: how are you?\nAssistant: I'm fine, thank you!"
        assert context == expected
    
    def test_get_context_respects_max_items(self):
        """Test that get_context respects max_items limit"""
        history = [
            "User: msg1\nAssistant: resp1",
            "User: msg2\nAssistant: resp2",
            "User: msg3\nAssistant: resp3",
            "User: msg4\nAssistant: resp4",
            "User: msg5\nAssistant: resp5"
        ]
        provider = ConversationHistoryProvider(history=history, max_items=3)
        
        context = provider.get_context("test query")
        # Should only include the last 3 items
        expected = "User: msg3\nAssistant: resp3\nUser: msg4\nAssistant: resp4\nUser: msg5\nAssistant: resp5"
        assert context == expected
    
    def test_update_with_valid_interaction(self):
        """Test update method with valid interaction data"""
        provider = ConversationHistoryProvider()
        
        interaction = {
            "user_input": "Hello",
            "result": "Hi there!"
        }
        
        provider.update(interaction)
        
        assert len(provider.history) == 1
        assert provider.history[0] == "User: Hello\nAssistant: Hi there!"
    
    def test_update_with_missing_fields(self):
        """Test update method with missing fields in interaction"""
        provider = ConversationHistoryProvider()
        
        # Missing user_input
        interaction1 = {"result": "Hi there!"}
        provider.update(interaction1)
        assert len(provider.history) == 0
        
        # Missing result
        interaction2 = {"user_input": "Hello"}
        provider.update(interaction2)
        assert len(provider.history) == 0
        
        # Empty strings
        interaction3 = {"user_input": "", "result": "Hi there!"}
        provider.update(interaction3)
        assert len(provider.history) == 0
    
    def test_update_respects_max_items(self):
        """Test that update respects max_items limit"""
        provider = ConversationHistoryProvider(max_items=2)
        
        # Add 3 interactions
        interactions = [
            {"user_input": "msg1", "result": "resp1"},
            {"user_input": "msg2", "result": "resp2"},
            {"user_input": "msg3", "result": "resp3"}
        ]
        
        for interaction in interactions:
            provider.update(interaction)
        
        # Should only keep the last 2
        assert len(provider.history) == 2
        assert provider.history[0] == "User: msg2\nAssistant: resp2"
        assert provider.history[1] == "User: msg3\nAssistant: resp3"
    
    def test_clear(self):
        """Test clear method"""
        history = ["User: hello\nAssistant: hi"]
        provider = ConversationHistoryProvider(history=history)
        
        assert len(provider.history) == 1
        
        provider.clear()
        
        assert len(provider.history) == 0
    
    def test_add_conversation_direct(self):
        """Test add_conversation method"""
        provider = ConversationHistoryProvider()
        
        provider.add_conversation("Hello", "Hi there!")
        
        assert len(provider.history) == 1
        assert provider.history[0] == "User: Hello\nAssistant: Hi there!"
    
    def test_add_conversation_respects_max_items(self):
        """Test that add_conversation respects max_items limit"""
        provider = ConversationHistoryProvider(max_items=2)
        
        provider.add_conversation("msg1", "resp1")
        provider.add_conversation("msg2", "resp2")
        provider.add_conversation("msg3", "resp3")
        
        assert len(provider.history) == 2
        assert provider.history[0] == "User: msg2\nAssistant: resp2"
        assert provider.history[1] == "User: msg3\nAssistant: resp3"
    
    def test_get_history_count(self):
        """Test get_history_count method"""
        provider = ConversationHistoryProvider()
        
        assert provider.get_history_count() == 0
        
        provider.add_conversation("Hello", "Hi")
        assert provider.get_history_count() == 1
        
        provider.add_conversation("How are you?", "Fine")
        assert provider.get_history_count() == 2
    
    def test_is_empty(self):
        """Test is_empty method"""
        provider = ConversationHistoryProvider()
        
        assert provider.is_empty() is True
        
        provider.add_conversation("Hello", "Hi")
        assert provider.is_empty() is False
        
        provider.clear()
        assert provider.is_empty() is True
    
    def test_get_context_with_previous_context(self):
        """Test get_context with previous_context parameter (should be ignored)"""
        history = ["User: hello\nAssistant: hi"]
        provider = ConversationHistoryProvider(history=history)
        
        # previous_context should be ignored by this provider
        context = provider.get_context("test query", previous_context="some previous context")
        expected = "User: hello\nAssistant: hi"
        assert context == expected
    
    def test_get_context_with_kwargs(self):
        """Test get_context with additional kwargs (should be ignored)"""
        history = ["User: hello\nAssistant: hi"]
        provider = ConversationHistoryProvider(history=history)
        
        # Additional kwargs should be ignored by this provider
        context = provider.get_context("test query", extra_param="value")
        expected = "User: hello\nAssistant: hi"
        assert context == expected
    
    def test_provider_lifecycle(self):
        """Test complete provider lifecycle"""
        provider = ConversationHistoryProvider(max_items=3)
        
        # Initial state
        assert provider.is_empty() is True
        assert provider.get_history_count() == 0
        assert provider.get_context("query") == ""
        
        # Add conversations
        provider.add_conversation("Hello", "Hi")
        provider.add_conversation("How are you?", "Fine")
        
        assert provider.is_empty() is False
        assert provider.get_history_count() == 2
        
        context = provider.get_context("query")
        expected = "User: Hello\nAssistant: Hi\nUser: How are you?\nAssistant: Fine"
        assert context == expected
        
        # Update with interaction
        interaction = {"user_input": "Goodbye", "result": "See you!"}
        provider.update(interaction)
        
        assert provider.get_history_count() == 3
        
        # Clear
        provider.clear()
        
        assert provider.is_empty() is True
        assert provider.get_history_count() == 0
        assert provider.get_context("query") == ""
    
    def test_edge_case_max_items_zero(self):
        """Test edge case with max_items set to zero"""
        provider = ConversationHistoryProvider(max_items=0)
        
        provider.add_conversation("Hello", "Hi")
        
        assert len(provider.history) == 0
        assert provider.get_context("query") == ""
    
    def test_edge_case_max_items_one(self):
        """Test edge case with max_items set to one"""
        provider = ConversationHistoryProvider(max_items=1)
        
        provider.add_conversation("Hello", "Hi")
        provider.add_conversation("How are you?", "Fine")
        
        assert len(provider.history) == 1
        assert provider.history[0] == "User: How are you?\nAssistant: Fine"
    
    def test_multiple_providers_independence(self):
        """Test that multiple provider instances are independent"""
        provider1 = ConversationHistoryProvider(max_items=2)
        provider2 = ConversationHistoryProvider(max_items=3)
        
        # Add conversations to both providers
        provider1.add_conversation("Hello", "Hi")
        provider2.add_conversation("Goodbye", "See you")
        
        assert provider1.get_history_count() == 1
        assert provider2.get_history_count() == 1
        
        assert "Hello" in provider1.get_context("query")
        assert "Goodbye" in provider2.get_context("query")
        assert "Hello" not in provider2.get_context("query")
        assert "Goodbye" not in provider1.get_context("query") 