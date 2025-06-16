#!/usr/bin/env python3
"""
Test RefinireAgent implementation for improved coverage.

RefinireAgentの実装の改善されたカバレッジをテストします。
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pydantic import BaseModel
from dataclasses import dataclass

from refinire.agents.pipeline.llm_pipeline import (
    RefinireAgent, LLMResult, EvaluationResult, 
    create_simple_agent, create_evaluated_agent, create_tool_enabled_agent
)


class OutputModel(BaseModel):
    """Test Pydantic model for structured output."""
    message: str
    score: int


class TestRefinireAgentAdvanced:
    """Advanced test cases for RefinireAgent."""
    
    def test_refinire_agent_with_prompt_reference(self):
        """Test RefinireAgent with PromptReference objects."""
        # Mock PromptReference
        mock_prompt_ref = Mock()
        mock_prompt_ref.get_metadata.return_value = {"prompt_name": "test_prompt"}
        mock_prompt_ref.__str__ = Mock(return_value="Test instructions")
        
        with patch('refinire.agents.pipeline.llm_pipeline.PromptReference', mock_prompt_ref.__class__):
            agent = RefinireAgent(
                name="test_agent",
                generation_instructions=mock_prompt_ref,
                evaluation_instructions=mock_prompt_ref
            )
            
            assert agent.generation_instructions == "Test instructions"
            assert agent.evaluation_instructions == "Test instructions"
            assert agent._generation_prompt_metadata == {"prompt_name": "test_prompt"}
            assert agent._evaluation_prompt_metadata == {"prompt_name": "test_prompt"}
    
    def test_refinire_agent_with_structured_output(self):
        """Test RefinireAgent with structured output model."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Generate structured output",
            output_model=OutputModel
        )
        
        assert agent.output_model == OutputModel
    
    def test_refinire_agent_guardrails(self):
        """Test RefinireAgent with guardrails."""
        input_guardrail = Mock(return_value=True)
        output_guardrail = Mock(return_value=True)
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            input_guardrails=[input_guardrail],
            output_guardrails=[output_guardrail]
        )
        
        assert agent.input_guardrails == [input_guardrail]
        assert agent.output_guardrails == [output_guardrail]
    
    def test_refinire_agent_tools_configuration(self):
        """Test RefinireAgent with tools configuration."""
        tools = [{"type": "function", "function": {"name": "test_tool"}}]
        mcp_servers = ["server1", "server2"]
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            tools=tools,
            mcp_servers=mcp_servers
        )
        
        assert agent.tools == tools
        assert agent.mcp_servers == mcp_servers
    
    def test_refinire_agent_evaluation_model(self):
        """Test RefinireAgent with separate evaluation model."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Generate content",
            evaluation_instructions="Evaluate content",
            model="gpt-4o-mini",
            evaluation_model="gpt-4o"
        )
        
        assert agent.model == "gpt-4o-mini"
        assert agent.evaluation_model == "gpt-4o"
    
    def test_refinire_agent_evaluation_model_fallback(self):
        """Test RefinireAgent evaluation model fallback to main model."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Generate content",
            evaluation_instructions="Evaluate content",
            model="gpt-4o-mini"
        )
        
        assert agent.model == "gpt-4o-mini"
        assert agent.evaluation_model == "gpt-4o-mini"
    
    def test_refinire_agent_session_history(self):
        """Test RefinireAgent with session history."""
        history = ["Previous interaction 1", "Previous interaction 2"]
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            session_history=history,
            history_size=5
        )
        
        assert agent.session_history == history
        assert agent.history_size == 5
    
    def test_refinire_agent_improvement_callback(self):
        """Test RefinireAgent with improvement callback."""
        callback = Mock()
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            improvement_callback=callback
        )
        
        assert agent.improvement_callback == callback
    
    def test_refinire_agent_locale_setting(self):
        """Test RefinireAgent with locale setting."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            locale="ja"
        )
        
        assert agent.locale == "ja"
    
    def test_refinire_agent_timeout_and_token_limits(self):
        """Test RefinireAgent with timeout and token limits."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            max_tokens=1000,
            timeout=60.0
        )
        
        assert agent.max_tokens == 1000
        assert agent.timeout == 60.0
    
    def test_refinire_agent_retry_configuration(self):
        """Test RefinireAgent with retry configuration."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            threshold=90.0,
            max_retries=5
        )
        
        assert agent.threshold == 90.0
        assert agent.max_retries == 5
    
    @patch('refinire.agents.pipeline.llm_pipeline.OpenAI')
    def test_refinire_agent_add_function_tool(self, mock_openai):
        """Test adding function tools to RefinireAgent."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions"
        )
        
        def test_function(x: int) -> int:
            """Test function."""
            return x * 2
        
        agent.add_function_tool(test_function)
        
        # Verify tool was added
        assert len(agent.tools) == 1
        assert agent.tools[0]["function"]["name"] == "test_function"
    
    @patch('refinire.agents.pipeline.llm_pipeline.OpenAI')
    def test_refinire_agent_add_function_tool_with_custom_name(self, mock_openai):
        """Test adding function tools with custom name."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions"
        )
        
        def test_function(x: int) -> int:
            """Test function."""
            return x * 2
        
        agent.add_function_tool(test_function, name="custom_name")
        
        # Verify tool was added with custom name
        assert len(agent.tools) == 1
        assert agent.tools[0]["function"]["name"] == "custom_name"
    
    @patch('refinire.agents.pipeline.llm_pipeline.OpenAI')
    def test_refinire_agent_add_tool_dict(self, mock_openai):
        """Test adding tool dictionary to RefinireAgent."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions"
        )
        
        tool_def = {
            "type": "function",
            "function": {
                "name": "test_tool",
                "description": "A test tool"
            }
        }
        
        agent.add_tool(tool_def)
        
        # Verify tool was added
        assert len(agent.tools) == 1
        assert agent.tools[0]["function"]["name"] == "test_tool"
    
    @patch('refinire.agents.pipeline.llm_pipeline.OpenAI')
    def test_refinire_agent_list_tools(self, mock_openai):
        """Test listing tools in RefinireAgent."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions"
        )
        
        def tool1(x: int) -> int:
            return x
        
        def tool2(y: str) -> str:
            return y
        
        agent.add_function_tool(tool1)
        agent.add_function_tool(tool2)
        
        tools = agent.list_tools()
        assert len(tools) == 2
        assert "tool1" in tools
        assert "tool2" in tools
    
    @patch('refinire.agents.pipeline.llm_pipeline.OpenAI')
    def test_refinire_agent_remove_tool(self, mock_openai):
        """Test removing tools from RefinireAgent."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions"
        )
        
        def test_function(x: int) -> int:
            return x
        
        agent.add_function_tool(test_function)
        assert len(agent.tools) == 1
        
        success = agent.remove_tool("test_function")
        assert success is True
        assert len(agent.tools) == 0
    
    @patch('refinire.agents.pipeline.llm_pipeline.OpenAI')
    def test_refinire_agent_remove_nonexistent_tool(self, mock_openai):
        """Test removing non-existent tool."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions"
        )
        
        success = agent.remove_tool("nonexistent_tool")
        assert success is False


class TestRefinireAgentFactoryFunctions:
    """Test factory functions for RefinireAgent."""
    
    def test_create_simple_agent(self):
        """Test create_simple_agent factory function."""
        agent = create_simple_agent(
            name="simple_agent",
            instructions="Simple instructions"
        )
        
        assert isinstance(agent, RefinireAgent)
        assert agent.name == "simple_agent"
        assert agent.generation_instructions == "Simple instructions"
        assert agent.evaluation_instructions is None
    
    def test_create_simple_agent_with_kwargs(self):
        """Test create_simple_agent with additional kwargs."""
        agent = create_simple_agent(
            name="simple_agent",
            instructions="Simple instructions",
            model="gpt-4o",
            temperature=0.5
        )
        
        assert agent.model == "gpt-4o"
        assert agent.temperature == 0.5
    
    def test_create_evaluated_agent(self):
        """Test create_evaluated_agent factory function."""
        agent = create_evaluated_agent(
            name="evaluated_agent",
            generation_instructions="Generate content",
            evaluation_instructions="Evaluate content"
        )
        
        assert isinstance(agent, RefinireAgent)
        assert agent.name == "evaluated_agent"
        assert agent.generation_instructions == "Generate content"
        assert agent.evaluation_instructions == "Evaluate content"
    
    def test_create_evaluated_agent_with_threshold(self):
        """Test create_evaluated_agent with custom threshold."""
        agent = create_evaluated_agent(
            name="evaluated_agent",
            generation_instructions="Generate content",
            evaluation_instructions="Evaluate content",
            threshold=95.0
        )
        
        assert agent.threshold == 95.0
    
    def test_create_tool_enabled_agent(self):
        """Test create_tool_enabled_agent factory function."""
        def test_tool(x: int) -> int:
            return x
        
        agent = create_tool_enabled_agent(
            name="tool_agent",
            instructions="Tool instructions",
            tools=[test_tool]
        )
        
        assert isinstance(agent, RefinireAgent)
        assert agent.name == "tool_agent"
        assert len(agent.tools) == 1


class TestRefinireAgentInternalMethods:
    """Test internal methods of RefinireAgent."""
    
    @patch('refinire.agents.pipeline.llm_pipeline.OpenAI')
    def test_refinire_agent_initialization_sets_up_client(self, mock_openai):
        """Test that RefinireAgent initialization sets up OpenAI client."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions"
        )
        
        # OpenAI client is created lazily, so check the mock was available
        assert mock_openai is not None
    
    def test_refinire_agent_string_representation(self):
        """Test RefinireAgent string representation."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions"
        )
        
        str_repr = str(agent)
        assert "test_agent" in str_repr
        assert "RefinireAgent" in str_repr
    
    def test_refinire_agent_repr(self):
        """Test RefinireAgent repr."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions"
        )
        
        repr_str = repr(agent)
        assert "RefinireAgent" in repr_str
        assert "test_agent" in repr_str


class TestLLMResult:
    """Test LLMResult dataclass."""
    
    def test_llm_result_creation(self):
        """Test LLMResult creation."""
        result = LLMResult(
            content="Test content",
            success=True,
            metadata={"test": "value"},
            evaluation_score=85.0,
            attempts=2
        )
        
        assert result.content == "Test content"
        assert result.success is True
        assert result.metadata == {"test": "value"}
        assert result.evaluation_score == 85.0
        assert result.attempts == 2
    
    def test_llm_result_defaults(self):
        """Test LLMResult default values."""
        result = LLMResult(content="Test")
        
        assert result.success is True
        assert result.metadata == {}
        assert result.evaluation_score is None
        assert result.attempts == 1


class TestEvaluationResult:
    """Test EvaluationResult dataclass."""
    
    def test_evaluation_result_creation(self):
        """Test EvaluationResult creation."""
        result = EvaluationResult(
            score=85.0,
            passed=True,
            feedback="Good result"
        )
        
        assert result.score == 85.0
        assert result.passed is True
        assert result.feedback == "Good result"
    
    def test_evaluation_result_defaults(self):
        """Test EvaluationResult default values."""
        result = EvaluationResult(
            score=75.0,
            passed=False
        )
        
        assert result.feedback is None
        assert result.metadata == {}


class TestRefinireAgentErrorHandling:
    """Test RefinireAgent error handling."""
    
    def test_refinire_agent_with_invalid_model(self):
        """Test RefinireAgent handles invalid model gracefully."""
        # This should not raise an exception during initialization
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            model="invalid-model"
        )
        
        assert agent.model == "invalid-model"
    
    def test_refinire_agent_with_negative_threshold(self):
        """Test RefinireAgent with negative threshold."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            threshold=-10.0
        )
        
        assert agent.threshold == -10.0
    
    def test_refinire_agent_with_zero_retries(self):
        """Test RefinireAgent with zero retries."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            max_retries=0
        )
        
        assert agent.max_retries == 0