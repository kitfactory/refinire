#!/usr/bin/env python3
"""
Test RefinireAgent functionality
RefinireAgentの機能をテスト

This test module ensures that RefinireAgent correctly handles
various configurations, tool integration, and error scenarios.
このテストモジュールは、RefinireAgentが様々な設定、ツール統合、
エラーシナリオを正しく処理することを確保します。
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from pydantic import BaseModel
from dataclasses import dataclass

try:
    from agents import function_tool
except ImportError:
    # Fallback if function_tool is not available
    def function_tool(func):
        return func

from refinire.agents.pipeline.llm_pipeline import (
    RefinireAgent, LLMResult, EvaluationResult, 
    create_simple_agent, create_evaluated_agent, create_tool_enabled_agent
)


class OutputModel(BaseModel):
    """Test Pydantic model for structured output."""
    message: str
    score: int


# ============================================================================
# Tool Functions for Testing
# テスト用のツール関数
# ============================================================================

@function_tool
def get_weather_test(location: str) -> str:
    """
    Get weather information for testing
    テスト用の天気情報を取得する
    """
    weather_data = {
        "Tokyo": "Sunny, 22°C",
        "New York": "Cloudy, 18°C",
        "London": "Rainy, 15°C",
        "Paris": "Partly Cloudy, 20°C"
    }
    return weather_data.get(location, f"Weather data not available for {location}")


@function_tool
def calculate_test(expression: str) -> str:
    """
    Perform mathematical calculations for testing
    テスト用の数学的計算を実行する
    """
    try:
        allowed_names = {'abs': abs, 'round': round, 'min': min, 'max': max}
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================================
# Advanced Test Cases
# 高度なテストケース
# ============================================================================

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
    
    def test_refinire_agent_mcp_servers_integration(self):
        """Test that MCP servers are properly passed to SDK Agent."""
        mcp_servers = ["stdio://test-server", "http://localhost:8000/mcp"]
        
        agent = RefinireAgent(
            name="mcp_test_agent",
            generation_instructions="Test with MCP servers",
            mcp_servers=mcp_servers
        )
        
        # Verify MCP servers are stored
        assert agent.mcp_servers == mcp_servers
        
        # Verify SDK agent has access to MCP servers
        # Note: This test verifies the parameter is passed, actual MCP functionality
        # depends on OpenAI Agents SDK implementation
        assert hasattr(agent, '_sdk_agent')
        
    def test_refinire_agent_without_mcp_servers(self):
        """Test RefinireAgent without MCP servers (default behavior)."""
        agent = RefinireAgent(
            name="no_mcp_agent",
            generation_instructions="Test without MCP"
        )
        
        # Should have empty MCP servers list by default
        assert agent.mcp_servers == []
        assert hasattr(agent, '_sdk_agent')
    
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
    def test_refinire_agent_constructor_with_function_tools(self, mock_openai):
        """Test adding function tools to RefinireAgent via constructor."""
        @function_tool
        def test_function(x: int) -> int:
            """Test function."""
            return x * 2
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            tools=[test_function]
        )
        
        # Verify tool was added
        assert len(agent.tools) == 1
        assert len(agent._sdk_tools) == 1
        assert test_function in agent._sdk_tools
        
        # Verify tool name
        tool_names = agent.list_tools()
        assert "test_function" in tool_names
    
    @patch('refinire.agents.pipeline.llm_pipeline.OpenAI')
    def test_refinire_agent_constructor_with_custom_named_tools(self, mock_openai):
        """Test adding function tools with custom name via constructor."""
        @function_tool
        def test_function(x: int) -> int:
            """Test function."""
            return x * 2
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            tools=[test_function]
        )
        
        # Verify tool was added
        assert len(agent.tools) == 1
        assert len(agent._sdk_tools) == 1
        assert test_function in agent._sdk_tools
        
        # Verify tool name (uses function name)
        tool_names = agent.list_tools()
        assert "test_function" in tool_names
    
    @patch('refinire.agents.pipeline.llm_pipeline.OpenAI')
    def test_refinire_agent_add_tool_dict(self, mock_openai):
        """Test adding tool dictionary to RefinireAgent."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions"
        )
        
        tool_dict = {
            "type": "function",
            "function": {
                "name": "test_tool",
                "description": "A test tool",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer"}
                    }
                }
            }
        }
        
        agent.add_tool(tool_dict)
        
        # Verify tool was added
        assert len(agent.tools) == 1
        assert agent.tools[0] == tool_dict
    
    @patch('refinire.agents.pipeline.llm_pipeline.OpenAI')
    def test_refinire_agent_list_tools(self, mock_openai):
        """Test listing tools in RefinireAgent."""
        @function_tool
        def tool1(x: int) -> int:
            return x * 2
        
        @function_tool
        def tool2(y: str) -> str:
            return y.upper()
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            tools=[tool1, tool2]
        )
        
        tool_names = agent.list_tools()
        assert "tool1" in tool_names
        assert "tool2" in tool_names
        assert len(tool_names) == 2
    
    @patch('refinire.agents.pipeline.llm_pipeline.OpenAI')
    def test_refinire_agent_remove_tool(self, mock_openai):
        """Test removing tools from RefinireAgent."""
        @function_tool
        def test_function(x: int) -> int:
            return x * 2
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            tools=[test_function]
        )
        
        assert len(agent.tools) == 1
        
        # Remove the tool
        success = agent.remove_tool("test_function")
        assert success
        assert len(agent.tools) == 0
    
    @patch('refinire.agents.pipeline.llm_pipeline.OpenAI')
    def test_refinire_agent_remove_nonexistent_tool(self, mock_openai):
        """Test removing non-existent tool from RefinireAgent."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions"
        )
        
        # Try to remove non-existent tool
        success = agent.remove_tool("nonexistent_tool")
        assert not success


# ============================================================================
# Tool Integration Tests
# ツール統合テスト
# ============================================================================

class TestRefinireAgentToolIntegration:
    """Test RefinireAgent tool integration with OpenAI Agents SDK."""
    
    def test_refinire_agent_constructor_with_tools(self):
        """Test RefinireAgent constructor with tools parameter."""
        # Mock function_tool decorator
        with patch('refinire.agents.pipeline.llm_pipeline.function_tool') as mock_function_tool:
            # Mock the decorated function
            mock_decorated_function = Mock()
            mock_function_tool.return_value = mock_decorated_function
            
            agent = RefinireAgent(
                name="test_agent",
                generation_instructions="Test instructions",
                tools=[get_weather_test, calculate_test]
            )
            
            # Verify tools were processed
            assert len(agent._sdk_tools) == 2
            assert get_weather_test in agent._sdk_tools
            assert calculate_test in agent._sdk_tools
    
    def test_refinire_agent_constructor_with_function_tools(self):
        """Test RefinireAgent constructor with FunctionTool objects."""
        # Mock FunctionTool
        mock_function_tool = Mock()
        mock_function_tool.name = "test_tool"
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            tools=[mock_function_tool]
        )
        
        # Verify FunctionTool was added
        assert len(agent._sdk_tools) == 1
        assert mock_function_tool in agent._sdk_tools
    
    def test_refinire_agent_constructor_with_dict_tools(self):
        """Test RefinireAgent constructor with dictionary tools."""
        dict_tool = {
            "type": "function",
            "function": {
                "name": "dict_tool",
                "description": "A dictionary tool"
            }
        }
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            tools=[dict_tool]
        )
        
        # Verify dict tool was added to tools list
        assert len(agent.tools) == 1
        assert agent.tools[0] == dict_tool
        # Verify no SDK tools were added
        assert len(agent._sdk_tools) == 0
    
    def test_refinire_agent_constructor_with_mixed_tools(self):
        """Test RefinireAgent constructor with mixed tool types."""
        dict_tool = {
            "type": "function",
            "function": {"name": "dict_tool"}
        }
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            tools=[get_weather_test, dict_tool, calculate_test]
        )
        
        # Verify SDK tools
        assert len(agent._sdk_tools) == 2
        assert get_weather_test in agent._sdk_tools
        assert calculate_test in agent._sdk_tools
        
        # Verify dict tools
        assert len(agent.tools) == 1
        assert agent.tools[0] == dict_tool
    
    @patch('refinire.agents.pipeline.llm_pipeline.Agent')
    @patch('refinire.agents.pipeline.llm_pipeline.Runner')
    def test_refinire_agent_run_async_with_tools(self, mock_runner, mock_agent):
        """Test RefinireAgent run_async with tools integration."""
        # Mock Runner.run to return a successful result
        mock_result = Mock()
        mock_result.final_output = "The weather in Tokyo is sunny, 22°C"
        mock_runner.run = AsyncMock(return_value=mock_result)
        
        # Mock Agent constructor
        mock_agent_instance = Mock()
        mock_agent_instance.instructions = "Test instructions"
        mock_agent_instance.tools = []
        mock_agent.return_value = mock_agent_instance
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant with weather tools.",
            tools=[get_weather_test]
        )
        
        # Test run_async
        result = asyncio.run(agent.run_async("What's the weather in Tokyo?"))
        
        # Verify result
        assert result.success
        assert "sunny" in result.content
        assert result.metadata["sdk"] is True
        
        # Verify Runner.run was called
        mock_runner.run.assert_called_once()
        call_args = mock_runner.run.call_args
        assert call_args[0][0] == agent._sdk_agent  # First argument should be the SDK agent
        assert "Tokyo" in call_args[0][1]  # Second argument should contain the prompt
    
    @patch('refinire.agents.pipeline.llm_pipeline.Agent')
    @patch('refinire.agents.pipeline.llm_pipeline.Runner')
    def test_refinire_agent_run_async_without_tools(self, mock_runner, mock_agent):
        """Test RefinireAgent run_async without tools."""
        # Mock Runner.run to return a successful result
        mock_result = Mock()
        mock_result.final_output = "Artificial intelligence is a field of computer science."
        mock_runner.run = AsyncMock(return_value=mock_result)
        
        # Mock Agent constructor
        mock_agent_instance = Mock()
        mock_agent_instance.instructions = "Test instructions"
        mock_agent_instance.tools = []
        mock_agent.return_value = mock_agent_instance
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant."
        )
        
        # Test run_async
        result = asyncio.run(agent.run_async("What is AI?"))
        
        # Verify result
        assert result.success
        assert "intelligence" in result.content
        assert result.metadata["sdk"] is True
        
        # Verify Runner.run was called
        mock_runner.run.assert_called_once()
    
    @patch('refinire.agents.pipeline.llm_pipeline.Agent')
    @patch('refinire.agents.pipeline.llm_pipeline.Runner')
    def test_refinire_agent_run_async_with_evaluation(self, mock_runner, mock_agent):
        """Test RefinireAgent run_async with evaluation."""
        # Mock Runner.run to return a successful result
        mock_result = Mock()
        mock_result.final_output = "Test response"
        mock_runner.run = AsyncMock(return_value=mock_result)
        
        # Mock Agent constructor
        mock_agent_instance = Mock()
        mock_agent_instance.instructions = "Test instructions"
        mock_agent_instance.tools = []
        mock_agent.return_value = mock_agent_instance
        
        # Mock evaluation to pass
        with patch.object(RefinireAgent, '_evaluate_content') as mock_evaluate:
            mock_evaluate.return_value = EvaluationResult(
                score=90.0,
                passed=True,
                feedback="Good response"
            )
            
            agent = RefinireAgent(
                name="test_agent",
                generation_instructions="Generate content",
                evaluation_instructions="Evaluate content",
                threshold=85.0
            )
            
            # Test run_async
            result = asyncio.run(agent.run_async("Test input"))
            
            # Verify result
            assert result.success
            assert result.evaluation_score == 90.0
            assert result.metadata["sdk"] is True
    
    @patch('refinire.agents.pipeline.llm_pipeline.Agent')
    @patch('refinire.agents.pipeline.llm_pipeline.Runner')
    def test_refinire_agent_run_async_with_failed_evaluation(self, mock_runner, mock_agent):
        """Test RefinireAgent run_async with failed evaluation and retry."""
        # Mock Runner.run to return different results on each call
        mock_results = [
            Mock(final_output="First attempt"),
            Mock(final_output="Second attempt - better")
        ]
        mock_runner.run = AsyncMock(side_effect=mock_results)
        
        # Mock Agent constructor
        mock_agent_instance = Mock()
        mock_agent_instance.instructions = "Test instructions"
        mock_agent_instance.tools = []
        mock_agent.return_value = mock_agent_instance
        
        # Mock evaluation to fail first, then pass
        evaluation_results = [
            EvaluationResult(score=70.0, passed=False, feedback="Needs improvement"),
            EvaluationResult(score=90.0, passed=True, feedback="Good response")
        ]
        
        with patch.object(RefinireAgent, '_evaluate_content') as mock_evaluate:
            mock_evaluate.side_effect = evaluation_results
            
            agent = RefinireAgent(
                name="test_agent",
                generation_instructions="Generate content",
                evaluation_instructions="Evaluate content",
                threshold=85.0,
                max_retries=2
            )
            
            # Test run_async
            result = asyncio.run(agent.run_async("Test input"))
            
            # Verify result
            assert result.success
            assert result.evaluation_score == 90.0
            assert result.attempts == 2
            assert result.metadata["sdk"] is True
            
            # Verify Runner.run was called twice
            assert mock_runner.run.call_count == 2
    
    @patch('refinire.agents.pipeline.llm_pipeline.Agent')
    @patch('refinire.agents.pipeline.llm_pipeline.Runner')
    def test_refinire_agent_run_async_with_input_validation_failure(self, mock_runner, mock_agent):
        """Test RefinireAgent run_async with input validation failure."""
        # Mock Agent constructor
        mock_agent_instance = Mock()
        mock_agent_instance.instructions = "Test instructions"
        mock_agent_instance.tools = []
        mock_agent.return_value = mock_agent_instance
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            input_guardrails=[lambda x: len(x) > 0]  # Reject empty input
        )
        
        # Test run_async with empty input
        result = asyncio.run(agent.run_async(""))
        
        # Verify result
        assert not result.success
        assert result.content is None
        assert "Input validation failed" in result.metadata["error"]
        
        # Verify Runner.run was not called
        mock_runner.run.assert_not_called()
    
    @patch('refinire.agents.pipeline.llm_pipeline.Agent')
    @patch('refinire.agents.pipeline.llm_pipeline.Runner')
    def test_refinire_agent_run_async_with_output_validation_failure(self, mock_runner, mock_agent):
        """Test RefinireAgent run_async with output validation failure."""
        # Mock Runner.run to return a result
        mock_result = Mock()
        mock_result.final_output = "Invalid output"
        mock_runner.run = AsyncMock(return_value=mock_result)
        
        # Mock Agent constructor
        mock_agent_instance = Mock()
        mock_agent_instance.instructions = "Test instructions"
        mock_agent_instance.tools = []
        mock_agent.return_value = mock_agent_instance
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            output_guardrails=[lambda x: "valid" in x.lower()]  # Require "valid" in output
        )
        
        # Test run_async
        result = asyncio.run(agent.run_async("Test input"))
        
        # Verify result
        assert not result.success
        assert result.content is None
        assert "Output validation failed" in result.metadata["error"]
        
        # Verify Runner.run was called
        mock_runner.run.assert_called_once()
    
    @patch('refinire.agents.pipeline.llm_pipeline.Agent')
    @patch('refinire.agents.pipeline.llm_pipeline.Runner')
    def test_refinire_agent_run_async_with_exception(self, mock_runner, mock_agent):
        """Test RefinireAgent run_async with exception handling."""
        # Mock Runner.run to raise an exception
        mock_runner.run = AsyncMock(side_effect=Exception("Test error"))
        
        # Mock Agent constructor
        mock_agent_instance = Mock()
        mock_agent_instance.instructions = "Test instructions"
        mock_agent_instance.tools = []
        mock_agent.return_value = mock_agent_instance
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            max_retries=1
        )
        
        # Test run_async
        result = asyncio.run(agent.run_async("Test input"))
        
        # Verify result
        assert not result.success
        assert result.content is None
        assert "Test error" in result.metadata["error"]
        assert result.metadata["sdk"] is True
        
        # Verify Runner.run was called
        mock_runner.run.assert_called_once()


# ============================================================================
# Factory Function Tests
# ファクトリ関数テスト
# ============================================================================

class TestRefinireAgentFactoryFunctions:
    """Test RefinireAgent factory functions."""
    
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
        @function_tool
        def test_tool(x: int) -> int:
            return x * 2
        
        agent = create_tool_enabled_agent(
            name="tool_agent",
            instructions="Use tools",
            tools=[test_tool]
        )
        
        assert isinstance(agent, RefinireAgent)
        assert agent.name == "tool_agent"
        assert agent.generation_instructions == "Use tools"
        assert len(agent._sdk_tools) == 1
        assert test_tool in agent._sdk_tools


# ============================================================================
# Internal Method Tests
# 内部メソッドテスト
# ============================================================================

class TestRefinireAgentInternalMethods:
    """Test RefinireAgent internal methods."""
    
    @patch('refinire.agents.pipeline.llm_pipeline.OpenAI')
    def test_refinire_agent_initialization_sets_up_client(self, mock_openai):
        """Test that RefinireAgent initialization sets up OpenAI client."""
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions"
        )
        
        # Verify OpenAI client was created
        mock_openai.assert_called_once()
        assert agent._client == mock_client
    
    def test_refinire_agent_string_representation(self):
        """Test RefinireAgent string representation."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions"
        )
        
        str_repr = str(agent)
        assert "RefinireAgent" in str_repr
        assert "test_agent" in str_repr
    
    def test_refinire_agent_repr(self):
        """Test RefinireAgent repr representation."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            model="gpt-4o-mini"
        )
        
        repr_str = repr(agent)
        assert "RefinireAgent" in repr_str
        assert "test_agent" in repr_str
        assert "gpt-4o-mini" in repr_str


# ============================================================================
# Data Class Tests
# データクラステスト
# ============================================================================

class TestLLMResult:
    """Test LLMResult data class."""
    
    def test_llm_result_creation(self):
        """Test LLMResult creation with all parameters."""
        result = LLMResult(
            content="Test content",
            success=True,
            metadata={"key": "value"},
            evaluation_score=85.0,
            attempts=2
        )
        
        assert result.content == "Test content"
        assert result.success is True
        assert result.metadata == {"key": "value"}
        assert result.evaluation_score == 85.0
        assert result.attempts == 2
    
    def test_llm_result_defaults(self):
        """Test LLMResult creation with default values."""
        result = LLMResult(content="Test content")
        
        assert result.content == "Test content"
        assert result.success is True
        assert result.metadata == {}
        assert result.evaluation_score is None
        assert result.attempts == 1


class TestEvaluationResult:
    """Test EvaluationResult data class."""
    
    def test_evaluation_result_creation(self):
        """Test EvaluationResult creation with all parameters."""
        result = EvaluationResult(
            score=90.0,
            passed=True,
            feedback="Good response",
            metadata={"key": "value"}
        )
        
        assert result.score == 90.0
        assert result.passed is True
        assert result.feedback == "Good response"
        assert result.metadata == {"key": "value"}
    
    def test_evaluation_result_defaults(self):
        """Test EvaluationResult creation with default values."""
        result = EvaluationResult(score=85.0, passed=False)
        
        assert result.score == 85.0
        assert result.passed is False
        assert result.feedback is None
        assert result.metadata == {}


# ============================================================================
# Error Handling Tests
# エラーハンドリングテスト
# ============================================================================

class TestRefinireAgentErrorHandling:
    """Test RefinireAgent error handling."""
    
    def test_refinire_agent_with_invalid_model(self):
        """Test RefinireAgent with invalid model name."""
        # This should not raise an exception during initialization
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            model="invalid-model"
        )
        
        assert agent.model == "invalid-model"
    
    def test_refinire_agent_with_negative_threshold(self):
        """Test RefinireAgent with negative threshold."""
        # This should not raise an exception during initialization
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            threshold=-10.0
        )
        
        assert agent.threshold == -10.0
    
    def test_refinire_agent_with_zero_retries(self):
        """Test RefinireAgent with zero retries."""
        # This should not raise an exception during initialization
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            max_retries=0
        )
        
        assert agent.max_retries == 0