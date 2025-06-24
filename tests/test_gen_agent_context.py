"""
Tests for RefinireAgent context management integration
RefinireAgentのコンテキスト管理統合テスト
"""

import pytest
import tempfile
import os
from refinire.agents.pipeline.llm_pipeline import RefinireAgent


class TestRefinireAgentContextIntegration:
    """Test cases for RefinireAgent context management integration"""
    
    def test_agent_without_context_providers(self):
        """Test agent without context providers (backward compatibility)"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant."
        )
        
        # Should work normally without context providers
        assert hasattr(agent, 'context_providers')
        assert agent.context_providers == []
        
        # Prompt should not include context section
        prompt = agent._build_prompt("Hello")
        assert "Context:" not in prompt
        assert "Hello" in prompt
    
    def test_agent_with_conversation_provider(self):
        """Test agent with conversation history provider"""
        context_config = [
            {
                "type": "conversation_history",
                "max_items": 3
            }
        ]
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant.",
            context_providers_config=context_config
        )
        
        # Test that context providers are initialized
        assert hasattr(agent, 'context_providers')
        assert len(agent.context_providers) == 1
        assert isinstance(agent.context_providers[0], ConversationHistoryProvider)
        assert agent.context_providers[0].max_items == 3
    
    def test_agent_with_fixed_file_provider(self):
        """Test agent with fixed file provider"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("This is a test file with important information.")
            temp_file_path = f.name
        
        try:
            context_config = [
                {
                    "type": "fixed_file",
                    "file_path": temp_file_path,
                    "encoding": "utf-8"
                }
            ]
            
            agent = RefinireAgent(
                name="test_agent",
                generation_instructions="You are a helpful assistant.",
                context_providers_config=context_config
            )
            
            assert len(agent.context_providers) == 1
            assert agent.context_providers[0].__class__.__name__ == "FixedFileProvider"
            
            # Prompt should include file content
            prompt = agent._build_prompt("What's in the file?")
            assert "Context:" in prompt
            assert "This is a test file with important information." in prompt
        finally:
            os.unlink(temp_file_path)
    
    def test_agent_with_multiple_providers(self):
        """Test agent with multiple context providers"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("File content for reference.")
            temp_file_path = f.name
        
        try:
            context_config = [
                {
                    "type": "conversation_history",
                    "max_items": 2
                },
                {
                    "type": "fixed_file",
                    "file_path": temp_file_path,
                    "encoding": "utf-8"
                }
            ]
            
            agent = RefinireAgent(
                name="test_agent",
                generation_instructions="You are a helpful assistant.",
                context_providers_config=context_config
            )
            
            # Test that multiple context providers are initialized
            assert hasattr(agent, 'context_providers')
            assert len(agent.context_providers) == 2
            assert isinstance(agent.context_providers[0], ConversationHistoryProvider)
            assert isinstance(agent.context_providers[1], FixedFileProvider)
            
            # Test context chaining
            context = agent.context_providers[0].get_context("test query")
            assert context == ""  # No history yet
            
            # Test that file content is included
            file_context = agent.context_providers[1].get_context("test query")
            assert "File content for reference." in file_context
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    def test_context_provider_error_handling(self):
        """Test error handling in context providers"""
        context_config = [
            {
                "type": "fixed_file",
                "file_path": "nonexistent_file.txt",
                "encoding": "utf-8"
            }
        ]
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant.",
            context_providers_config=context_config
        )
        
        # Should not raise exception, just log warning
        prompt = agent._build_prompt("Hello")
        assert "Hello" in prompt  # Should still work
    
    def test_clear_context_method(self):
        """Test clear_context method"""
        context_config = [
            {
                "type": "conversation_history",
                "max_items": 3
            }
        ]
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant.",
            context_providers_config=context_config
        )
        
        # Add some conversation
        result = agent.run("Hello")
        assert len(agent.context_providers[0].history) > 0
        
        # Clear context only
        agent.clear_context()
        assert len(agent.context_providers[0].history) == 0
        
        # History should still be there
        assert len(agent.session_history) > 0
    
    def test_clear_history_method(self):
        """Test clear_history method with context providers"""
        context_config = [
            {
                "type": "conversation_history",
                "max_items": 3
            }
        ]
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant.",
            context_providers_config=context_config
        )
        
        # Add some conversation
        result = agent.run("Hello")
        assert len(agent.context_providers[0].history) > 0
        assert len(agent.session_history) > 0
        
        # Clear all history
        agent.clear_history()
        assert len(agent.context_providers[0].history) == 0
        assert len(agent.session_history) == 0
    
    def test_get_context_provider_schemas(self):
        """Test get_context_provider_schemas class method"""
        schemas = RefinireAgent.get_context_provider_schemas()
        
        assert "conversation_history" in schemas
        assert "fixed_file" in schemas
        
        # Check schema structure
        conversation_schema = schemas["conversation_history"]
        assert "description" in conversation_schema
        assert "parameters" in conversation_schema
        assert "example" in conversation_schema
        
        fixed_file_schema = schemas["fixed_file"]
        assert "description" in fixed_file_schema
        assert "parameters" in fixed_file_schema
        assert "example" in fixed_file_schema
    
    def test_context_provider_chaining(self):
        """Test context provider chaining functionality"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("Reference file content.")
            temp_file_path = f.name
        
        try:
            context_config = [
                {
                    "type": "fixed_file",
                    "file_path": temp_file_path,
                    "encoding": "utf-8"
                },
                {
                    "type": "conversation_history",
                    "max_items": 2
                }
            ]
            
            agent = RefinireAgent(
                name="test_agent",
                generation_instructions="You are a helpful assistant.",
                context_providers_config=context_config
            )
            
            # First provider should get empty previous_context
            # Second provider should get first provider's context as previous_context
            prompt = agent._build_prompt("Test")
            assert "Reference file content." in prompt
            
            # After interaction, conversation provider should have access to file context
            result = agent.run("Hello")
            prompt = agent._build_prompt("How are you?")
            assert "Reference file content." in prompt
            assert "User: Hello" in prompt
        finally:
            os.unlink(temp_file_path)
    
    def test_context_provider_update_on_interaction(self):
        """Test that context providers are updated after interactions"""
        context_config = [
            {
                "type": "conversation_history",
                "max_items": 3
            }
        ]
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant.",
            context_providers_config=context_config
        )
        
        # Initial state
        assert len(agent.context_providers[0].history) == 0
        
        # After interaction
        result = agent.run("Hello")
        assert len(agent.context_providers[0].history) == 1
        assert "User: Hello" in agent.context_providers[0].history[0]
        assert "Assistant:" in agent.context_providers[0].history[0]
    
    def test_context_provider_config_validation(self):
        """Test context provider configuration validation"""
        # Invalid configuration should raise error
        invalid_config = [
            {
                "type": "conversation_history",
                "max_items": "invalid"  # Should be int
            }
        ]
        
        with pytest.raises(ValueError):
            RefinireAgent(
                name="test_agent",
                generation_instructions="You are a helpful assistant.",
                context_providers_config=invalid_config
            )
    
    def test_default_conversation_history_provider(self):
        """Test that agent defaults to conversation history provider when no config is provided"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant."
        )
        
        # Should have default conversation provider
        assert len(agent.context_providers) == 1
        assert agent.context_providers[0].__class__.__name__ == "ConversationHistoryProvider"
        assert agent.context_providers[0].max_items == 10
    
    def test_agent_with_yaml_like_string_config(self):
        """Test agent with YAML-like string configuration"""
        yaml_config = """
- conversation_history
  max_items: 3
- fixed_file
  file_path: test_file.txt
  encoding: utf-8
"""
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant.",
            context_providers_config=yaml_config
        )
        
        # Should parse YAML-like string correctly
        assert len(agent.context_providers) == 2
        assert agent.context_providers[0].__class__.__name__ == "ConversationHistoryProvider"
        assert agent.context_providers[0].max_items == 3
        assert agent.context_providers[1].__class__.__name__ == "FixedFileProvider"
        assert agent.context_providers[1].file_path == "test_file.txt"
        assert agent.context_providers[1].encoding == "utf-8"
    
    def test_agent_with_simple_yaml_string_config(self):
        """Test agent with simple YAML-like string configuration"""
        yaml_config = """
- conversation_history
  max_items: 5
"""
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant.",
            context_providers_config=yaml_config
        )
        
        # Should parse simple YAML-like string correctly
        assert len(agent.context_providers) == 1
        assert agent.context_providers[0].__class__.__name__ == "ConversationHistoryProvider"
        assert agent.context_providers[0].max_items == 5
    
    def test_agent_with_empty_yaml_string_config(self):
        """Test agent with empty YAML-like string configuration"""
        yaml_config = ""
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant.",
            context_providers_config=yaml_config
        )
        
        # Should default to conversation provider when empty string
        assert len(agent.context_providers) == 1
        assert agent.context_providers[0].__class__.__name__ == "ConversationHistoryProvider"
        assert agent.context_providers[0].max_items == 10 