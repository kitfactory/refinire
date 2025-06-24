"""
Tests for ContextProviderFactory
ContextProviderFactoryのテスト
"""

import pytest
from unittest.mock import patch, MagicMock
from refinire.agents.context_provider_factory import ContextProviderFactory
from refinire.agents.providers.conversation_history import ConversationHistoryProvider
from refinire.agents.providers.fixed_file import FixedFileProvider


class TestContextProviderFactory:
    """Test cases for ContextProviderFactory"""
    
    def test_create_conversation_provider(self):
        """Test creating conversation history provider"""
        config = {
            "type": "conversation_history",
            "max_items": 10
        }
        
        provider = ContextProviderFactory.create_provider(config)
        
        assert isinstance(provider, ConversationHistoryProvider)
        assert provider.max_items == 10
    
    def test_create_fixed_file_provider(self):
        """Test creating fixed file provider"""
        config = {
            "type": "fixed_file",
            "file_path": "test.txt",
            "encoding": "utf-8",
            "check_updates": True
        }
        
        provider = ContextProviderFactory.create_provider(config)
        
        assert isinstance(provider, FixedFileProvider)
        assert provider.file_path == "test.txt"
        assert provider.encoding == "utf-8"
        assert provider.check_updates is True
    
    def test_create_provider_without_type(self):
        """Test creating provider without type specification"""
        config = {
            "max_items": 10
        }
        
        with pytest.raises(ValueError, match="Provider type is required"):
            ContextProviderFactory.create_provider(config)
    
    def test_create_provider_unknown_type(self):
        """Test creating provider with unknown type"""
        config = {
            "type": "unknown_provider"
        }
        
        with pytest.raises(ValueError, match="Unknown provider type"):
            ContextProviderFactory.create_provider(config)
    
    def test_create_provider_with_empty_config(self):
        """Test creating provider with empty configuration"""
        config = {}
        
        with pytest.raises(ValueError, match="Provider type is required"):
            ContextProviderFactory.create_provider(config)
    
    def test_create_provider_with_none_config(self):
        """Test creating provider with None configuration"""
        with pytest.raises(ValueError, match="Configuration is required"):
            ContextProviderFactory.create_provider(None)
    
    def test_create_multiple_providers(self):
        """Test creating multiple providers"""
        configs = [
            {
                "type": "conversation_history",
                "max_items": 5
            },
            {
                "type": "fixed_file",
                "file_path": "test.txt"
            }
        ]
        
        providers = ContextProviderFactory.create_providers(configs)
        
        assert len(providers) == 2
        assert isinstance(providers[0], ConversationHistoryProvider)
        assert isinstance(providers[1], FixedFileProvider)
    
    def test_create_providers_with_empty_list(self):
        """Test creating providers with empty list"""
        providers = ContextProviderFactory.create_providers([])
        assert providers == []
    
    def test_create_providers_with_none_list(self):
        """Test creating providers with None list"""
        with pytest.raises(ValueError, match="Configuration list is required"):
            ContextProviderFactory.create_providers(None)
    
    def test_create_providers_with_invalid_config(self):
        """Test creating providers with invalid configuration in list"""
        configs = [
            {
                "type": "conversation_history",
                "max_items": 5
            },
            {
                "type": "unknown_provider"
            }
        ]
        
        with pytest.raises(ValueError, match="Unknown provider type"):
            ContextProviderFactory.create_providers(configs)
    
    def test_get_available_provider_types(self):
        """Test getting available provider types"""
        types = ContextProviderFactory.get_available_provider_types()
        
        assert "conversation_history" in types
        assert "fixed_file" in types
        assert len(types) >= 2
    
    def test_get_provider_schema(self):
        """Test getting provider schema"""
        schema = ContextProviderFactory.get_provider_schema("conversation_history")
        
        assert "description" in schema
        assert "parameters" in schema
        assert "example" in schema
        assert "max_items" in schema["parameters"]
    
    def test_get_provider_schema_unknown_type(self):
        """Test getting schema for unknown provider type"""
        with pytest.raises(ValueError, match="Unknown provider type"):
            ContextProviderFactory.get_provider_schema("unknown_provider")
    
    def test_get_all_provider_schemas(self):
        """Test getting all provider schemas"""
        schemas = ContextProviderFactory.get_all_provider_schemas()
        
        assert "conversation_history" in schemas
        assert "fixed_file" in schemas
        assert len(schemas) >= 2
        
        # Check that each schema has required fields
        for provider_type, schema in schemas.items():
            assert "description" in schema
            assert "parameters" in schema
            assert "example" in schema
    
    def test_validate_config_valid(self):
        """Test validating valid configuration"""
        config = {
            "type": "conversation_history",
            "max_items": 10
        }
        
        # Should not raise any exception
        ContextProviderFactory.validate_config(config)
    
    def test_validate_config_invalid(self):
        """Test validating invalid configuration"""
        config = {
            "type": "conversation_history",
            "max_items": "invalid"  # Should be int
        }
        
        with pytest.raises(ValueError):
            ContextProviderFactory.validate_config(config)
    
    def test_validate_config_missing_required(self):
        """Test validating configuration with missing required parameters"""
        config = {
            "type": "fixed_file"
            # Missing required file_path
        }
        
        with pytest.raises(ValueError):
            ContextProviderFactory.validate_config(config)
    
    def test_create_provider_with_validation(self):
        """Test creating provider with validation enabled"""
        config = {
            "type": "conversation_history",
            "max_items": 5
        }
        
        provider = ContextProviderFactory.create_provider(config, validate=True)
        
        assert isinstance(provider, ConversationHistoryProvider)
        assert provider.max_items == 5
    
    def test_create_provider_with_validation_failure(self):
        """Test creating provider with validation failure"""
        config = {
            "type": "conversation_history",
            "max_items": "invalid"  # Should be int
        }
        
        with pytest.raises(ValueError):
            ContextProviderFactory.create_provider(config, validate=True)
    
    def test_create_providers_with_validation(self):
        """Test creating multiple providers with validation"""
        configs = [
            {
                "type": "conversation_history",
                "max_items": 3
            },
            {
                "type": "fixed_file",
                "file_path": "config.txt"
            }
        ]
        
        providers = ContextProviderFactory.create_providers(configs, validate=True)
        
        assert len(providers) == 2
        assert isinstance(providers[0], ConversationHistoryProvider)
        assert isinstance(providers[1], FixedFileProvider)
    
    def test_create_providers_with_validation_failure(self):
        """Test creating multiple providers with validation failure"""
        configs = [
            {
                "type": "conversation_history",
                "max_items": 3
            },
            {
                "type": "fixed_file"
                # Missing required file_path
            }
        ]
        
        with pytest.raises(ValueError):
            ContextProviderFactory.create_providers(configs, validate=True) 