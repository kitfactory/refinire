"""
Test Context Provider Interface
コンテキストプロバイダーインターフェースのテスト

This module tests the ContextProvider abstract base class and its functionality.
このモジュールはContextProvider抽象基底クラスとその機能をテストします。
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from refinire.agents.context_provider import ContextProvider


class MockContextProvider(ContextProvider):
    """
    Mock implementation of ContextProvider for testing
    テスト用のContextProviderのモック実装
    """
    
    provider_name: str = "mock"
    
    def __init__(self, test_data: str = ""):
        self.test_data = test_data
        self.context_calls = []
        self.update_calls = []
        self.clear_calls = 0
    
    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """Get configuration schema for mock provider"""
        return {
            "description": "Mock context provider for testing",
            "parameters": {
                "test_data": {
                    "type": "str",
                    "default": "",
                    "description": "Test data to return"
                }
            },
            "example": "mock:\n  test_data: 'test content'"
        }
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'MockContextProvider':
        """Create mock provider from configuration"""
        return cls(**config)
    
    def get_context(self, query: str, previous_context: str = None, **kwargs) -> str:
        """Get mock context"""
        self.context_calls.append({
            "query": query,
            "previous_context": previous_context,
            "kwargs": kwargs
        })
        return self.test_data
    
    def update(self, interaction: Dict[str, Any]) -> None:
        """Update mock provider"""
        self.update_calls.append(interaction)
    
    def clear(self) -> None:
        """Clear mock provider"""
        self.clear_calls += 1


class TestContextProvider:
    """Test cases for ContextProvider interface"""
    
    def test_provider_name_class_variable(self):
        """Test that provider_name is properly defined as class variable"""
        # Test base class
        assert ContextProvider.provider_name == "base"
        
        # Test concrete implementation
        assert MockContextProvider.provider_name == "mock"
    
    def test_get_config_schema_base_class(self):
        """Test get_config_schema method on base class"""
        schema = ContextProvider.get_config_schema()
        
        assert isinstance(schema, dict)
        assert "description" in schema
        assert "parameters" in schema
        assert "example" in schema
        assert schema["description"] == "Base context provider"
        assert schema["parameters"] == {}
        assert schema["example"] == "base: {}"
    
    def test_get_config_schema_concrete_class(self):
        """Test get_config_schema method on concrete implementation"""
        schema = MockContextProvider.get_config_schema()
        
        assert isinstance(schema, dict)
        assert "description" in schema
        assert "parameters" in schema
        assert "example" in schema
        assert schema["description"] == "Mock context provider for testing"
        assert "test_data" in schema["parameters"]
        assert schema["parameters"]["test_data"]["type"] == "str"
    
    def test_from_config_base_class(self):
        """Test from_config method on base class"""
        # Base class should raise NotImplementedError since it's abstract
        with pytest.raises(TypeError):
            ContextProvider.from_config({})
    
    def test_from_config_concrete_class(self):
        """Test from_config method on concrete implementation"""
        config = {"test_data": "test content"}
        provider = MockContextProvider.from_config(config)
        
        assert isinstance(provider, MockContextProvider)
        assert provider.test_data == "test content"
    
    def test_from_config_empty_config(self):
        """Test from_config method with empty configuration"""
        provider = MockContextProvider.from_config({})
        
        assert isinstance(provider, MockContextProvider)
        assert provider.test_data == ""
    
    def test_get_context_method_signature(self):
        """Test get_context method signature and basic functionality"""
        provider = MockContextProvider("test context")
        
        # Test basic call
        result = provider.get_context("test query")
        assert result == "test context"
        assert len(provider.context_calls) == 1
        assert provider.context_calls[0]["query"] == "test query"
        assert provider.context_calls[0]["previous_context"] is None
        
        # Test with previous context
        result = provider.get_context("test query", "previous context")
        assert result == "test context"
        assert len(provider.context_calls) == 2
        assert provider.context_calls[1]["previous_context"] == "previous context"
        
        # Test with additional kwargs
        result = provider.get_context("test query", extra_param="value")
        assert result == "test context"
        assert len(provider.context_calls) == 3
        assert provider.context_calls[2]["kwargs"]["extra_param"] == "value"
    
    def test_update_method(self):
        """Test update method functionality"""
        provider = MockContextProvider()
        interaction = {"user_input": "test", "result": "response"}
        
        provider.update(interaction)
        
        assert len(provider.update_calls) == 1
        assert provider.update_calls[0] == interaction
    
    def test_clear_method(self):
        """Test clear method functionality"""
        provider = MockContextProvider()
        
        assert provider.clear_calls == 0
        
        provider.clear()
        assert provider.clear_calls == 1
        
        provider.clear()
        assert provider.clear_calls == 2
    
    def test_abstract_methods_raise_error(self):
        """Test that abstract methods raise NotImplementedError when not implemented"""
        # Create a class that doesn't implement abstract methods
        class IncompleteProvider(ContextProvider):
            pass
        
        # Instantiating should raise TypeError
        with pytest.raises(TypeError):
            IncompleteProvider()
    
    def test_provider_lifecycle(self):
        """Test complete provider lifecycle"""
        provider = MockContextProvider("initial context")
        
        # Initial state
        assert provider.test_data == "initial context"
        assert len(provider.context_calls) == 0
        assert len(provider.update_calls) == 0
        assert provider.clear_calls == 0
        
        # Get context
        context = provider.get_context("test query")
        assert context == "initial context"
        assert len(provider.context_calls) == 1
        
        # Update with interaction
        interaction = {"user_input": "hello", "result": "hi"}
        provider.update(interaction)
        assert len(provider.update_calls) == 1
        assert provider.update_calls[0] == interaction
        
        # Clear
        provider.clear()
        assert provider.clear_calls == 1
        
        # Verify state after clear
        assert len(provider.context_calls) == 1  # Should not be affected by clear
        assert len(provider.update_calls) == 1   # Should not be affected by clear
    
    def test_multiple_providers_independence(self):
        """Test that multiple provider instances are independent"""
        provider1 = MockContextProvider("context1")
        provider2 = MockContextProvider("context2")
        
        # Test independence of context calls
        provider1.get_context("query1")
        provider2.get_context("query2")
        
        assert len(provider1.context_calls) == 1
        assert len(provider2.context_calls) == 1
        assert provider1.context_calls[0]["query"] == "query1"
        assert provider2.context_calls[0]["query"] == "query2"
        
        # Test independence of update calls
        interaction1 = {"data": "1"}
        interaction2 = {"data": "2"}
        
        provider1.update(interaction1)
        provider2.update(interaction2)
        
        assert len(provider1.update_calls) == 1
        assert len(provider2.update_calls) == 1
        assert provider1.update_calls[0] == interaction1
        assert provider2.update_calls[0] == interaction2
        
        # Test independence of clear calls
        provider1.clear()
        assert provider1.clear_calls == 1
        assert provider2.clear_calls == 0 