"""
Test Fixed File Provider
固定ファイルプロバイダーのテスト

This module tests the FixedFileProvider class and its functionality.
このモジュールはFixedFileProviderクラスとその機能をテストします。
"""

import pytest
import tempfile
import os
import time
from typing import Dict, Any

from refinire.agents.providers.fixed_file import FixedFileProvider


class TestFixedFileProvider:
    """Test cases for FixedFileProvider"""
    
    def test_provider_name(self):
        """Test that provider_name is correctly set"""
        assert FixedFileProvider.provider_name == "fixed_file"
    
    def test_initialization_default_values(self):
        """Test initialization with default values"""
        provider = FixedFileProvider("test.txt")
        
        assert provider.file_path == "test.txt"
        assert provider.encoding == "utf-8"
        assert provider.check_updates is True
        assert provider._cached_content is None
        assert provider._last_modified is None
    
    def test_initialization_with_custom_values(self):
        """Test initialization with custom values"""
        provider = FixedFileProvider(
            file_path="test.txt",
            encoding="shift_jis",
            check_updates=False
        )
        
        assert provider.file_path == "test.txt"
        assert provider.encoding == "shift_jis"
        assert provider.check_updates is False
    
    def test_get_config_schema(self):
        """Test get_config_schema method"""
        schema = FixedFileProvider.get_config_schema()
        
        assert isinstance(schema, dict)
        assert "description" in schema
        assert "parameters" in schema
        assert "example" in schema
        assert schema["description"] == "Provides fixed file content as context"
        assert "file_path" in schema["parameters"]
        assert "encoding" in schema["parameters"]
        assert "check_updates" in schema["parameters"]
        assert schema["parameters"]["file_path"]["required"] is True
        assert schema["parameters"]["encoding"]["default"] == "utf-8"
        assert schema["parameters"]["check_updates"]["default"] is True
    
    def test_from_config_empty(self):
        """Test from_config method with empty configuration (should fail)"""
        with pytest.raises(TypeError):
            FixedFileProvider.from_config({})
    
    def test_from_config_with_file_path(self):
        """Test from_config method with file_path"""
        config = {"file_path": "test.txt"}
        provider = FixedFileProvider.from_config(config)
        
        assert isinstance(provider, FixedFileProvider)
        assert provider.file_path == "test.txt"
        assert provider.encoding == "utf-8"
        assert provider.check_updates is True
    
    def test_from_config_with_all_parameters(self):
        """Test from_config method with all parameters"""
        config = {
            "file_path": "test.txt",
            "encoding": "shift_jis",
            "check_updates": False
        }
        provider = FixedFileProvider.from_config(config)
        
        assert isinstance(provider, FixedFileProvider)
        assert provider.file_path == "test.txt"
        assert provider.encoding == "shift_jis"
        assert provider.check_updates is False
    
    def test_get_context_nonexistent_file(self):
        """Test get_context with non-existent file"""
        provider = FixedFileProvider("nonexistent.txt")
        
        context = provider.get_context("test query")
        assert context == ""
    
    def test_get_context_existing_file(self):
        """Test get_context with existing file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("This is test content")
            temp_file_path = f.name
        
        try:
            provider = FixedFileProvider(temp_file_path)
            
            context = provider.get_context("test query")
            assert context == "This is test content"
        finally:
            os.unlink(temp_file_path)
    
    def test_get_context_caching(self):
        """Test that get_context caches file content"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("This is test content")
            temp_file_path = f.name
        
        try:
            provider = FixedFileProvider(temp_file_path)
            
            # First call should read from file
            context1 = provider.get_context("test query")
            assert context1 == "This is test content"
            assert provider._cached_content == "This is test content"
            
            # Second call should use cache
            context2 = provider.get_context("test query")
            assert context2 == "This is test content"
            assert provider._cached_content == "This is test content"
        finally:
            os.unlink(temp_file_path)
    
    def test_get_context_file_update_detection(self):
        """Test file update detection"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("Original content")
            temp_file_path = f.name
        
        try:
            provider = FixedFileProvider(temp_file_path, check_updates=True)
            
            # First read
            context1 = provider.get_context("test query")
            assert context1 == "Original content"
            
            # Update file
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                f.write("Updated content")
            
            # Small delay to ensure file modification time changes
            time.sleep(0.1)
            
            # Second read should detect update and re-read
            context2 = provider.get_context("test query")
            assert context2 == "Updated content"
        finally:
            os.unlink(temp_file_path)
    
    def test_get_context_no_update_checking(self):
        """Test get_context without update checking"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("Original content")
            temp_file_path = f.name
        
        try:
            provider = FixedFileProvider(temp_file_path, check_updates=False)
            
            # First read
            context1 = provider.get_context("test query")
            assert context1 == "Original content"
            
            # Update file
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                f.write("Updated content")
            
            # Second read should use cache (no update checking)
            context2 = provider.get_context("test query")
            assert context2 == "Original content"  # Should still be cached
        finally:
            os.unlink(temp_file_path)
    
    def test_get_context_encoding_error(self):
        """Test get_context with encoding error"""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            # Write bytes that are not valid UTF-8
            f.write(b'\xff\xfe\x00\x00')
            temp_file_path = f.name
        
        try:
            provider = FixedFileProvider(temp_file_path, encoding='utf-8')
            
            # Should return empty string on encoding error
            context = provider.get_context("test query")
            assert context == ""
        finally:
            os.unlink(temp_file_path)
    
    def test_get_context_with_previous_context(self):
        """Test get_context with previous_context parameter (should be ignored)"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("File content")
            temp_file_path = f.name
        
        try:
            provider = FixedFileProvider(temp_file_path)
            
            # previous_context should be ignored by this provider
            context = provider.get_context("test query", previous_context="some previous context")
            assert context == "File content"
        finally:
            os.unlink(temp_file_path)
    
    def test_get_context_with_kwargs(self):
        """Test get_context with additional kwargs (should be ignored)"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("File content")
            temp_file_path = f.name
        
        try:
            provider = FixedFileProvider(temp_file_path)
            
            # Additional kwargs should be ignored by this provider
            context = provider.get_context("test query", extra_param="value")
            assert context == "File content"
        finally:
            os.unlink(temp_file_path)
    
    def test_update_method(self):
        """Test update method (should be no-op)"""
        provider = FixedFileProvider("test.txt")
        
        # Update should not change anything
        interaction = {"user_input": "test", "result": "response"}
        provider.update(interaction)
        
        # No state should be changed
        assert provider._cached_content is None
        assert provider._last_modified is None
    
    def test_clear(self):
        """Test clear method"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("Test content")
            temp_file_path = f.name
        
        try:
            provider = FixedFileProvider(temp_file_path)
            
            # Read file to populate cache
            provider.get_context("test query")
            assert provider._cached_content is not None
            assert provider._last_modified is not None
            
            # Clear cache
            provider.clear()
            
            assert provider._cached_content is None
            assert provider._last_modified is None
        finally:
            os.unlink(temp_file_path)
    
    def test_file_exists(self):
        """Test file_exists method"""
        provider = FixedFileProvider("nonexistent.txt")
        assert provider.file_exists() is False
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("test")
            temp_file_path = f.name
        
        try:
            provider = FixedFileProvider(temp_file_path)
            assert provider.file_exists() is True
        finally:
            os.unlink(temp_file_path)
    
    def test_get_file_size(self):
        """Test get_file_size method"""
        provider = FixedFileProvider("nonexistent.txt")
        assert provider.get_file_size() is None
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("test content")
            temp_file_path = f.name
        
        try:
            provider = FixedFileProvider(temp_file_path)
            size = provider.get_file_size()
            assert size is not None
            assert size > 0
        finally:
            os.unlink(temp_file_path)
    
    def test_get_file_info(self):
        """Test get_file_info method"""
        provider = FixedFileProvider("nonexistent.txt")
        info = provider.get_file_info()
        
        assert info["exists"] is False
        assert info["path"] == "nonexistent.txt"
        assert info["encoding"] == "utf-8"
        assert info["check_updates"] is True
        assert "size" not in info
        assert "last_modified" not in info
        assert "cached" not in info
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("test content")
            temp_file_path = f.name
        
        try:
            provider = FixedFileProvider(temp_file_path)
            
            # Read file to populate cache
            provider.get_context("test query")
            
            info = provider.get_file_info()
            assert info["exists"] is True
            assert info["path"] == temp_file_path
            assert info["encoding"] == "utf-8"
            assert info["check_updates"] is True
            assert "size" in info
            assert "last_modified" in info
            assert info["cached"] is True
        finally:
            os.unlink(temp_file_path)
    
    def test_force_refresh(self):
        """Test force_refresh method"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("Original content")
            temp_file_path = f.name
        
        try:
            provider = FixedFileProvider(temp_file_path)
            
            # Read file to populate cache
            provider.get_context("test query")
            assert provider._cached_content is not None
            
            # Force refresh
            provider.force_refresh()
            assert provider._cached_content is None
            assert provider._last_modified is None
        finally:
            os.unlink(temp_file_path)
    
    def test_set_file_path(self):
        """Test set_file_path method"""
        # Create a temporary file to populate cache
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("Original content")
            original_file_path = f.name
        
        try:
            provider = FixedFileProvider(original_file_path)
            
            # Read original file to populate cache
            provider.get_context("test query")
            assert provider._cached_content is not None
            
            # Create new file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
                f.write("New file content")
                temp_file_path = f.name
            
            try:
                # Change file path
                provider.set_file_path(temp_file_path)
                assert provider.file_path == temp_file_path
                assert provider._cached_content is None  # Cache should be cleared
                
                # Read new file
                context = provider.get_context("test query")
                assert context == "New file content"
            finally:
                os.unlink(temp_file_path)
        finally:
            os.unlink(original_file_path)
    
    def test_set_encoding(self):
        """Test set_encoding method"""
        # Create a temporary file to populate cache
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("Test content")
            temp_file_path = f.name
        
        try:
            provider = FixedFileProvider(temp_file_path, encoding="utf-8")
            
            # Read file to populate cache
            provider.get_context("test query")
            assert provider._cached_content is not None
            
            # Change encoding
            provider.set_encoding("shift_jis")
            assert provider.encoding == "shift_jis"
            assert provider._cached_content is None  # Cache should be cleared
        finally:
            os.unlink(temp_file_path)
    
    def test_provider_lifecycle(self):
        """Test complete provider lifecycle"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("Test content")
            temp_file_path = f.name
        
        try:
            provider = FixedFileProvider(temp_file_path)
            
            # Initial state
            assert provider.file_exists() is True
            assert provider._cached_content is None
            
            # Get context
            context = provider.get_context("test query")
            assert context == "Test content"
            assert provider._cached_content == "Test content"
            
            # Update (should be no-op)
            interaction = {"user_input": "test", "result": "response"}
            provider.update(interaction)
            
            # Clear
            provider.clear()
            assert provider._cached_content is None
            assert provider._last_modified is None
        finally:
            os.unlink(temp_file_path) 