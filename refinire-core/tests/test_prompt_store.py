"""
Tests for PromptStore class
PromptStoreクラスのテスト
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import json
import os
from unittest.mock import patch, AsyncMock

from refinire.core.prompt_store import PromptStore, StoredPrompt, detect_system_language


class TestPromptStore:
    """Test PromptStore functionality"""
    
    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def mock_llm_response(self, monkeypatch):
        """Mock LLM responses for translation"""
        mock_agent = AsyncMock()
        mock_response = AsyncMock()
        mock_response.messages = [AsyncMock(text="Translated content")]
        mock_agent.run.return_value = mock_response
        
        mock_llm = AsyncMock()
        mock_llm.agent = mock_agent
        
        def mock_get_llm(*args, **kwargs):
            return mock_llm
        
        monkeypatch.setattr("refinire.core.prompt_store.get_llm", mock_get_llm)
        return mock_agent
    
    def test_detect_system_language_japanese(self):
        """Test Japanese language detection"""
        with patch.dict(os.environ, {"LANG": "ja_JP.UTF-8"}):
            assert detect_system_language() == "ja"
        
        with patch.dict(os.environ, {"LC_ALL": "ja_JP.UTF-8"}, clear=True):
            assert detect_system_language() == "ja"
    
    def test_detect_system_language_english(self):
        """Test English language detection (default)"""
        with patch.dict(os.environ, {"LANG": "en_US.UTF-8"}):
            assert detect_system_language() == "en"
        
        with patch.dict(os.environ, {}, clear=True):
            # Should default to English
            lang = detect_system_language()
            assert lang in ["en", "ja"]  # Depends on system locale
    
    def test_store_prompt_basic(self, mock_llm_response, temp_storage_dir):
        """Test basic prompt storage"""
        prompt = PromptStore.store(
            name="greeting",
            content="Hello, how can I help you?",
            tag="basic",
            language="en",
            storage_dir=temp_storage_dir
        )
        
        assert prompt.name == "greeting"
        assert prompt.content["en"] == "Hello, how can I help you?"
        assert prompt.tag == "basic"
        
        # Should have auto-translated to Japanese
        assert "ja" in prompt.content
        assert mock_llm_response.run.called
    
    def test_store_prompt_no_translation(self, temp_storage_dir):
        """Test storing without auto-translation"""
        prompt = PromptStore.store(
            name="test",
            content="Test content",
            language="en",
            auto_translate=False,
            storage_dir=temp_storage_dir
        )
        
        assert "en" in prompt.content
        assert "ja" not in prompt.content
    
    def test_get_prompt(self, temp_storage_dir):
        """Test prompt retrieval"""
        # Store a prompt directly
        PromptStore.store("test", "English", language="en", auto_translate=False, storage_dir=temp_storage_dir)
        PromptStore.store("test", "日本語", language="ja", auto_translate=False, storage_dir=temp_storage_dir)
        
        # Get in specific language
        en_prompt = PromptStore.get("test", language="en", storage_dir=temp_storage_dir)
        ja_prompt = PromptStore.get("test", language="ja", storage_dir=temp_storage_dir)
        assert str(en_prompt) == "English"
        assert str(ja_prompt) == "日本語"
        
        # Store a prompt with tag
        PromptStore.store("test", "Tagged", tag="special", language="en", auto_translate=False, storage_dir=temp_storage_dir)
        PromptStore.store("test", "タグ付き", tag="special", language="ja", auto_translate=False, storage_dir=temp_storage_dir)
        tagged_prompt = PromptStore.get("test", tag="special", language="en", storage_dir=temp_storage_dir)
        assert str(tagged_prompt) == "Tagged"
        
        # Get with system language detection
        with patch("refinire.core.prompt_store.detect_system_language", return_value="ja"):
            # Now there are multiple prompts with name "test", so get without tag should return None
            assert PromptStore.get("test", storage_dir=temp_storage_dir) is None
            # But with tag it works
            tagged_ja = PromptStore.get("test", tag="special", storage_dir=temp_storage_dir)
            assert str(tagged_ja) == "タグ付き"
    
    def test_get_nonexistent_prompt(self, temp_storage_dir):
        """Test getting non-existent prompt"""
        assert PromptStore.get("nonexistent", storage_dir=temp_storage_dir) is None
    
    def test_list_prompts(self, temp_storage_dir):
        """Test listing prompts"""
        # Add test prompts
        PromptStore.store("prompt1", "1", tag="tag1", auto_translate=False, storage_dir=temp_storage_dir)
        PromptStore.store("prompt2", "2", tag="tag2", auto_translate=False, storage_dir=temp_storage_dir)
        PromptStore.store("prompt3", "3", tag="tag1", auto_translate=False, storage_dir=temp_storage_dir)
        
        # List all
        all_prompts = PromptStore.list_prompts(storage_dir=temp_storage_dir)
        assert len(all_prompts) == 3
        
        # Filter by name
        prompt1_list = PromptStore.list_prompts(name="prompt1", storage_dir=temp_storage_dir)
        assert len(prompt1_list) == 1
        assert prompt1_list[0].name == "prompt1"
        
        # Add another prompt with same name but different tag
        PromptStore.store("prompt1", "4", tag="tag3", auto_translate=False, storage_dir=temp_storage_dir)
        
        prompt1_list = PromptStore.list_prompts(name="prompt1", storage_dir=temp_storage_dir)
        assert len(prompt1_list) == 2
        assert all(p.name == "prompt1" for p in prompt1_list)
    
    def test_delete_prompt(self, temp_storage_dir):
        """Test prompt deletion"""
        PromptStore.store("test", "Test1", tag="tag1", auto_translate=False, storage_dir=temp_storage_dir)
        PromptStore.store("test", "Test2", tag="tag2", auto_translate=False, storage_dir=temp_storage_dir)
        PromptStore.store("other", "Other", auto_translate=False, storage_dir=temp_storage_dir)
        
        # Delete by name and tag
        assert PromptStore.delete("test", tag="tag1", storage_dir=temp_storage_dir) == 1
        assert len(PromptStore.list_prompts(storage_dir=temp_storage_dir)) == 2
        
        # Delete all with name
        assert PromptStore.delete("test", storage_dir=temp_storage_dir) == 1  # Only one "test" left
        assert len(PromptStore.list_prompts(storage_dir=temp_storage_dir)) == 1
        
        # Delete non-existent
        assert PromptStore.delete("nonexistent", storage_dir=temp_storage_dir) == 0
    
    def test_database_persistence(self, temp_storage_dir):
        """Test saving and loading from SQLite database"""
        # Save prompts
        PromptStore.store("persistent", "English", tag="test", language="en", auto_translate=False, storage_dir=temp_storage_dir)
        PromptStore.store("persistent", "日本語", tag="test", language="ja", auto_translate=False, storage_dir=temp_storage_dir)
        
        # Load using class methods
        loaded_prompt = PromptStore.get_prompt("persistent", tag="test", storage_dir=temp_storage_dir)
        
        assert loaded_prompt is not None
        assert loaded_prompt.name == "persistent"
        assert loaded_prompt.content == {"en": "English", "ja": "日本語"}
        assert loaded_prompt.tag == "test"
    
    def test_update_existing_prompt(self, mock_llm_response, temp_storage_dir):
        """Test updating an existing prompt"""
        # Initial store
        PromptStore.store(
            name="test",
            content="Original",
            tag="original",
            language="en",
            storage_dir=temp_storage_dir
        )
        
        # Update
        updated = PromptStore.store(
            name="test",
            content="Updated",
            tag="updated",
            language="en",
            storage_dir=temp_storage_dir
        )
        
        assert updated.content["en"] == "Updated"
        assert updated.tag == "updated"
        assert updated.updated_at > updated.created_at
    
    def test_translation_prompt_format(self, monkeypatch, temp_storage_dir):
        """Test that translation prompts are formatted correctly"""
        translation_prompts = []
        
        def mock_run(prompt):
            translation_prompts.append(prompt)
            mock_response = AsyncMock()
            mock_response.messages = [AsyncMock(text="翻訳されたコンテンツ")]
            return mock_response
        
        mock_agent = AsyncMock()
        mock_agent.run = mock_run
        
        mock_llm = AsyncMock()
        mock_llm.agent = mock_agent
        
        monkeypatch.setattr("refinire.core.prompt_store.get_llm", lambda: mock_llm)
        
        PromptStore.store(
            name="test",
            content="Test prompt with {variable}",
            language="en",
            storage_dir=temp_storage_dir
        )
        
        # Check translation prompt was formatted correctly
        assert len(translation_prompts) == 1
        assert "English prompt:" in translation_prompts[0]
        assert "Test prompt with {variable}" in translation_prompts[0]
        assert "Japanese translation:" in translation_prompts[0]