#!/usr/bin/env python3
"""
Test PromptStore implementation.

PromptStoreの実装をテストします。
"""

import pytest
import tempfile
import os
from unittest.mock import patch, Mock
from pathlib import Path
from datetime import datetime

from refinire.core.prompt_store import (
    PromptStore, PromptReference, StoredPrompt,
    get_default_storage_dir, detect_system_language,
    SUPPORTED_LANGUAGES, LanguageCode
)


class TestPromptReference:
    """Test cases for PromptReference class."""
    
    def test_prompt_reference_creation(self):
        """Test PromptReference creation."""
        prompt = PromptReference(
            content="Hello, world!",
            name="greeting",
            tag="test",
            language="en"
        )
        
        assert prompt.content == "Hello, world!"
        assert prompt.name == "greeting"
        assert prompt.tag == "test"
        assert prompt.language == "en"
        assert isinstance(prompt.retrieved_at, datetime)
    
    def test_prompt_reference_str(self):
        """Test PromptReference string representation."""
        prompt = PromptReference(
            content="Test content",
            name="test"
        )
        
        assert str(prompt) == "Test content"
    
    def test_prompt_reference_metadata(self):
        """Test PromptReference metadata generation."""
        prompt = PromptReference(
            content="Test",
            name="test_prompt",
            tag="example",
            language="ja"
        )
        
        metadata = prompt.get_metadata()
        
        assert metadata["prompt_name"] == "test_prompt"
        assert metadata["prompt_language"] == "ja"
        assert metadata["prompt_tag"] == "example"
        assert "retrieved_at" in metadata
    
    def test_prompt_reference_metadata_without_tag(self):
        """Test PromptReference metadata without tag."""
        prompt = PromptReference(
            content="Test",
            name="test_prompt"
        )
        
        metadata = prompt.get_metadata()
        
        assert metadata["prompt_name"] == "test_prompt"
        assert metadata["prompt_language"] == "en"
        assert "prompt_tag" not in metadata
        assert "retrieved_at" in metadata


class TestStoredPrompt:
    """Test cases for StoredPrompt class."""
    
    def test_stored_prompt_creation(self):
        """Test StoredPrompt creation."""
        prompt = StoredPrompt(
            name="test_prompt",
            content={"en": "Hello", "ja": "こんにちは"},
            tag="greeting"
        )
        
        assert prompt.name == "test_prompt"
        assert prompt.content["en"] == "Hello"
        assert prompt.content["ja"] == "こんにちは"
        assert prompt.tag == "greeting"
        assert isinstance(prompt.created_at, datetime)


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_get_default_storage_dir_with_env(self):
        """Test get_default_storage_dir with environment variable."""
        with patch.dict(os.environ, {"REFINIRE_DIR": "/test/path"}):
            result = get_default_storage_dir()
            assert result == Path("/test/path")
    
    def test_get_default_storage_dir_without_env(self):
        """Test get_default_storage_dir without environment variable."""
        with patch.dict(os.environ, {}, clear=True):
            result = get_default_storage_dir()
            assert result == Path.home() / ".refinire"
    
    def test_detect_system_language_japanese_lang(self):
        """Test detect_system_language with Japanese LANG."""
        with patch.dict(os.environ, {"LANG": "ja_JP.UTF-8"}):
            result = detect_system_language()
            assert result == "ja"
    
    def test_detect_system_language_japanese_lc_all(self):
        """Test detect_system_language with Japanese LC_ALL."""
        with patch.dict(os.environ, {"LC_ALL": "ja_JP.UTF-8"}):
            result = detect_system_language()
            assert result == "ja"
    
    def test_detect_system_language_english_default(self):
        """Test detect_system_language defaults to English."""
        with patch.dict(os.environ, {"LANG": "en_US.UTF-8"}):
            result = detect_system_language()
            assert result == "en"
    
    def test_detect_system_language_fallback(self):
        """Test detect_system_language with system locale fallback."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('locale.getdefaultlocale', return_value=('ja_JP', 'UTF-8')):
                result = detect_system_language()
                assert result == "ja"
    
    def test_detect_system_language_fallback_english(self):
        """Test detect_system_language fallback to English."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('locale.getdefaultlocale', return_value=(None, None)):
                result = detect_system_language()
                assert result == "en"


class TestPromptStore:
    """Test cases for PromptStore class."""
    
    def test_prompt_store_initialization(self):
        """Test PromptStore initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir)
            store = PromptStore(storage_dir=storage_dir)
            
            assert store.storage_dir == storage_dir
            assert store.db_path == storage_dir / "prompts.db"
            assert store.db_path.exists()
    
    def test_prompt_store_singleton_behavior(self):
        """Test PromptStore singleton behavior."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir)
            
            # Clear singleton
            PromptStore._instance = None
            PromptStore._storage_dir = None
            
            instance1 = PromptStore._get_instance(storage_dir)
            instance2 = PromptStore._get_instance(storage_dir)
            
            assert instance1 is instance2
    
    def test_prompt_store_set_storage_dir(self):
        """Test setting storage directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir)
            
            # Clear singleton
            PromptStore._instance = None
            PromptStore._storage_dir = None
            
            PromptStore.set_storage_dir(storage_dir)
            assert PromptStore._storage_dir == storage_dir
    
    def test_prompt_store_database_creation(self):
        """Test database table creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir)
            store = PromptStore(storage_dir=storage_dir)
            
            # Verify table exists
            import sqlite3
            conn = sqlite3.connect(store.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='prompts'")
            result = cursor.fetchone()
            assert result is not None
            conn.close()
    
    def test_prompt_store_store_and_get(self):
        """Test storing and retrieving prompts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir)
            
            # Clear singleton
            PromptStore._instance = None
            PromptStore._storage_dir = None
            
            # Store a prompt
            stored_prompt = PromptStore.store(
                name="greeting",
                content="Hello world",
                tag="test",
                language="en",
                auto_translate=False,
                storage_dir=storage_dir
            )
            
            assert stored_prompt.name == "greeting"
            
            # Retrieve the prompt
            result = PromptStore.get("greeting", tag="test", storage_dir=storage_dir)
            
            assert result is not None
            assert result.name == "greeting"
            assert result.content == "Hello world"
            assert result.language == "en"
            assert result.tag == "test"
    
    def test_prompt_store_get_japanese(self):
        """Test retrieving Japanese prompts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir)
            
            # Clear singleton
            PromptStore._instance = None
            PromptStore._storage_dir = None
            
            # Store a Japanese prompt
            PromptStore.store(
                name="greeting",
                content="こんにちは世界",
                language="ja",
                auto_translate=False,
                storage_dir=storage_dir
            )
            
            # Retrieve with Japanese language preference
            result = PromptStore.get("greeting", language="ja", storage_dir=storage_dir)
            
            assert result is not None
            assert result.content == "こんにちは世界"
            assert result.language == "ja"
    
    def test_prompt_store_get_nonexistent(self):
        """Test retrieving non-existent prompt."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir)
            
            # Clear singleton
            PromptStore._instance = None
            PromptStore._storage_dir = None
            
            result = PromptStore.get("nonexistent", storage_dir=storage_dir)
            assert result is None
    
    def test_prompt_store_list_prompts(self):
        """Test listing prompts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir)
            
            # Clear singleton
            PromptStore._instance = None
            PromptStore._storage_dir = None
            
            # Store multiple prompts
            PromptStore.store("prompt1", "Content 1", tag="tag1", auto_translate=False, storage_dir=storage_dir)
            PromptStore.store("prompt2", "Content 2", tag="tag2", auto_translate=False, storage_dir=storage_dir)
            PromptStore.store("prompt3", "Content 3", auto_translate=False, storage_dir=storage_dir)
            
            # List all prompts
            prompts = PromptStore.list_prompts(storage_dir=storage_dir)
            
            assert len(prompts) >= 3
            names = [p.name for p in prompts]
            assert "prompt1" in names
            assert "prompt2" in names
            assert "prompt3" in names
    
    def test_prompt_store_delete(self):
        """Test deleting prompts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir)
            
            # Clear singleton
            PromptStore._instance = None
            PromptStore._storage_dir = None
            
            # Store and then delete a prompt
            PromptStore.store("test_prompt", "Test content", auto_translate=False, storage_dir=storage_dir)
            assert PromptStore.get("test_prompt", storage_dir=storage_dir) is not None
            
            result = PromptStore.delete("test_prompt", storage_dir=storage_dir)
            assert result >= 1  # Number of deleted rows
            assert PromptStore.get("test_prompt", storage_dir=storage_dir) is None
    
    def test_prompt_store_delete_nonexistent(self):
        """Test deleting non-existent prompt."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir)
            
            # Clear singleton
            PromptStore._instance = None
            PromptStore._storage_dir = None
            
            result = PromptStore.delete("nonexistent", storage_dir=storage_dir)
            assert result == 0  # No rows deleted
    
    def test_prompt_store_update(self):
        """Test updating existing prompts."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir)
            
            # Clear singleton
            PromptStore._instance = None
            PromptStore._storage_dir = None
            
            # Store initial prompt
            PromptStore.store("test_prompt", "Original content", tag="test", auto_translate=False, storage_dir=storage_dir)
            
            # Update prompt (same name and tag should update)
            PromptStore.store("test_prompt", "Updated content", tag="test", auto_translate=False, storage_dir=storage_dir)
            
            # Verify update
            result = PromptStore.get("test_prompt", tag="test", storage_dir=storage_dir)
            assert result.content == "Updated content"
            assert result.tag == "test"
    
    def test_prompt_store_get_prompt_method(self):
        """Test get_prompt method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_dir = Path(temp_dir)
            
            # Clear singleton
            PromptStore._instance = None
            PromptStore._storage_dir = None
            
            # Store a prompt
            PromptStore.store("test", "Test content", tag="example", auto_translate=False, storage_dir=storage_dir)
            
            # Get prompt using get_prompt method
            result = PromptStore.get_prompt("test", tag="example", storage_dir=storage_dir)
            
            assert result is not None
            assert result.name == "test"
            assert result.get_content("en") == "Test content"


class TestStoredPromptMethods:
    """Test StoredPrompt methods."""
    
    def test_stored_prompt_get_content(self):
        """Test StoredPrompt get_content method."""
        prompt = StoredPrompt(
            name="test",
            content={"en": "Hello", "ja": "こんにちは"}
        )
        
        assert prompt.get_content("en") == "Hello"
        assert prompt.get_content("ja") == "こんにちは"
        assert prompt.get_content() == "Hello"  # Default should be detected language
    
    def test_stored_prompt_get_content_fallback(self):
        """Test StoredPrompt get_content fallback behavior."""
        prompt = StoredPrompt(
            name="test",
            content={"en": "Hello"}  # Only English content
        )
        
        # Should fallback to available language when requested language not available
        assert prompt.get_content("ja") == "Hello"
    
    def test_stored_prompt_to_dict(self):
        """Test StoredPrompt to_dict method."""
        prompt = StoredPrompt(
            name="test",
            content={"en": "Hello"},
            tag="example"
        )
        
        data = prompt.to_dict()
        
        assert data["name"] == "test"
        assert data["content"] == {"en": "Hello"}
        assert data["tag"] == "example"
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_stored_prompt_from_dict(self):
        """Test StoredPrompt from_dict method."""
        data = {
            "name": "test",
            "content": {"en": "Hello"},
            "tag": "example",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        prompt = StoredPrompt.from_dict(data)
        
        assert prompt.name == "test"
        assert prompt.content == {"en": "Hello"}
        assert prompt.tag == "example"
    
    def test_stored_prompt_from_dict_backward_compatibility(self):
        """Test StoredPrompt from_dict with old tags format."""
        data = {
            "name": "test",
            "content": {"en": "Hello"},
            "tags": ["example", "old"],  # Old format with multiple tags
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        prompt = StoredPrompt.from_dict(data)
        
        assert prompt.name == "test"
        assert prompt.tag == "example"  # Should take first tag
    
    def test_supported_languages_constant(self):
        """Test SUPPORTED_LANGUAGES constant."""
        assert "en" in SUPPORTED_LANGUAGES
        assert "ja" in SUPPORTED_LANGUAGES
        assert len(SUPPORTED_LANGUAGES) == 2