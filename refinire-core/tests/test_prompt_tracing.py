"""
Tests for prompt tracing integration
プロンプトトレース統合のテスト
"""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile

from refinire.core.prompt_store import PromptStore, PromptReference


class TestPromptTracing:
    """Test prompt tracing functionality"""
    
    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    def test_prompt_reference_creation(self, temp_storage_dir):
        """Test creating PromptReference objects"""
        # Store a prompt
        PromptStore.store(
            name="test_prompt",
            content="Test instruction content",
            tag="test",
            language="en",
            storage_dir=temp_storage_dir
        )
        
        # Get with metadata
        prompt_ref = PromptStore.get(
            name="test_prompt",
            tag="test",
            language="en",
            storage_dir=temp_storage_dir
        )
        
        assert prompt_ref is not None
        assert isinstance(prompt_ref, PromptReference)
        assert prompt_ref.content == "Test instruction content"
        assert prompt_ref.name == "test_prompt"
        assert prompt_ref.tag == "test"
        assert prompt_ref.language == "en"
        assert isinstance(prompt_ref.retrieved_at, datetime)
    
    def test_prompt_reference_string_conversion(self, temp_storage_dir):
        """Test that PromptReference works as string"""
        PromptStore.store(
            name="greeting",
            content="Hello, I am an AI assistant.",
            tag="intro",
            storage_dir=temp_storage_dir
        )
        
        prompt_ref = PromptStore.get(
            name="greeting",
            tag="intro",
            storage_dir=temp_storage_dir
        )
        
        # Should work as string
        assert str(prompt_ref) == "Hello, I am an AI assistant."
        
        # Should work in f-strings
        message = f"Instruction: {prompt_ref}"
        assert message == "Instruction: Hello, I am an AI assistant."
    
    def test_prompt_reference_metadata(self, temp_storage_dir):
        """Test PromptReference metadata extraction"""
        PromptStore.store(
            name="analyzer",
            content="Analyze the given text and provide insights.",
            tag="analysis",
            language="en",
            storage_dir=temp_storage_dir
        )
        
        prompt_ref = PromptStore.get(
            name="analyzer",
            tag="analysis",
            language="en",
            storage_dir=temp_storage_dir
        )
        
        metadata = prompt_ref.get_metadata()
        
        assert metadata["prompt_name"] == "analyzer"
        assert metadata["prompt_tag"] == "analysis"
        assert metadata["prompt_language"] == "en"
        assert "retrieved_at" in metadata
        
        # Verify retrieved_at is valid ISO format
        datetime.fromisoformat(metadata["retrieved_at"])
    
    def test_prompt_reference_no_tag(self, temp_storage_dir):
        """Test PromptReference without tag"""
        PromptStore.store(
            name="simple",
            content="Simple prompt without tag",
            storage_dir=temp_storage_dir
        )
        
        prompt_ref = PromptStore.get(
            name="simple",
            storage_dir=temp_storage_dir
        )
        
        assert prompt_ref is not None
        assert prompt_ref.tag is None
        
        metadata = prompt_ref.get_metadata()
        assert "prompt_tag" not in metadata  # Should not include None tag
        assert metadata["prompt_name"] == "simple"
    
    def test_get_with_metadata_nonexistent(self, temp_storage_dir):
        """Test get for non-existent prompt"""
        result = PromptStore.get(
            name="nonexistent",
            storage_dir=temp_storage_dir
        )
        
        assert result is None
    
    def test_prompt_reference_multilingual(self, temp_storage_dir):
        """Test PromptReference with different languages"""
        # Store English prompt
        PromptStore.store(
            name="greeting",
            content="Hello, how can I help you?",
            tag="greeting",
            language="en",
            auto_translate=False,
            storage_dir=temp_storage_dir
        )
        
        # Store Japanese prompt separately
        PromptStore.store(
            name="greeting", 
            content="こんにちは、どのようにお手伝いできますか？",
            tag="greeting",
            language="ja",
            auto_translate=False,
            storage_dir=temp_storage_dir
        )
        
        # Get English version
        en_prompt = PromptStore.get(
            name="greeting",
            tag="greeting", 
            language="en",
            storage_dir=temp_storage_dir
        )
        
        # Get Japanese version
        ja_prompt = PromptStore.get(
            name="greeting",
            tag="greeting",
            language="ja", 
            storage_dir=temp_storage_dir
        )
        
        assert en_prompt.content == "Hello, how can I help you?"
        assert en_prompt.language == "en"
        assert ja_prompt.content == "こんにちは、どのようにお手伝いできますか？"
        assert ja_prompt.language == "ja"
        
        # Both should have same name and tag but different languages
        assert en_prompt.name == ja_prompt.name == "greeting"
        assert en_prompt.tag == ja_prompt.tag == "greeting"