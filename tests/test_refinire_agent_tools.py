#!/usr/bin/env python3
"""
Test RefinireAgent tool integration with OpenAI Agents SDK.

RefinireAgentのOpenAI Agents SDKとのツール統合をテストします。
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from pydantic import BaseModel

from refinire.agents.pipeline.llm_pipeline import (
    RefinireAgent, LLMResult, EvaluationResult
)


# ============================================================================
# Test Tool Functions
# テスト用ツール関数
# ============================================================================

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


def search_web_test(query: str) -> str:
    """
    Simulate web search for testing
    テスト用のWeb検索をシミュレートする
    """
    search_results = {
        "python": "Python is a programming language",
        "AI": "Artificial Intelligence is a field of computer science",
        "machine learning": "Machine learning is a subset of AI"
    }
    return search_results.get(query.lower(), f"No results found for {query}")


# ============================================================================
# Constructor Tests
# コンストラクタテスト
# ============================================================================

class TestRefinireAgentToolConstructor:
    """Test RefinireAgent constructor with tools."""
    
    def test_constructor_with_function_tools(self):
        """Test RefinireAgent constructor with function tools."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            tools=[get_weather_test, calculate_test]
        )
        
        # Verify SDK tools were added
        assert len(agent._sdk_tools) == 2
        assert get_weather_test in agent._sdk_tools
        assert calculate_test in agent._sdk_tools
        
        # Verify tools list contains the original functions (for backward compatibility)
        assert len(agent.tools) == 2
        assert get_weather_test in agent.tools
        assert calculate_test in agent.tools
    
    def test_constructor_with_dict_tools(self):
        """Test RefinireAgent constructor with dictionary tools."""
        dict_tool = {
            "type": "function",
            "function": {
                "name": "dict_tool",
                "description": "A dictionary tool",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string"}
                    }
                }
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
        
        # Verify no SDK tools were added (dict tools are not callable)
        assert len(agent._sdk_tools) == 0
    
    def test_constructor_with_mixed_tools(self):
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
        
        # Verify SDK tools (function tools)
        assert len(agent._sdk_tools) == 2
        assert get_weather_test in agent._sdk_tools
        assert calculate_test in agent._sdk_tools
        
        # Verify tools list contains all tools (functions + dict)
        assert len(agent.tools) == 3
        assert get_weather_test in agent.tools
        assert calculate_test in agent.tools
        assert dict_tool in agent.tools
    
    def test_constructor_with_function_tool_objects(self):
        """Test RefinireAgent constructor with FunctionTool objects."""
        # Mock FunctionTool
        mock_function_tool = Mock()
        mock_function_tool.name = "test_tool"
        mock_function_tool.__name__ = "test_tool"
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            tools=[mock_function_tool]
        )
        
        # Verify FunctionTool was added to SDK tools
        assert len(agent._sdk_tools) == 1
        assert mock_function_tool in agent._sdk_tools
        
        # Verify FunctionTool was also added to tools list
        assert len(agent.tools) == 1
        assert mock_function_tool in agent.tools
    
    def test_constructor_with_no_tools(self):
        """Test RefinireAgent constructor without tools."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions"
        )
        
        # Verify no tools were added
        assert len(agent._sdk_tools) == 0
        assert len(agent.tools) == 0
    
    def test_constructor_with_empty_tools_list(self):
        """Test RefinireAgent constructor with empty tools list."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            tools=[]
        )
        
        # Verify no tools were added
        assert len(agent._sdk_tools) == 0
        assert len(agent.tools) == 0


# ============================================================================
# Run Async Tests
# run_asyncテスト
# ============================================================================

class TestRefinireAgentRunAsync:
    """Test RefinireAgent run_async method with tools."""
    
    @patch('refinire.agents.pipeline.llm_pipeline.Agent')
    @patch('refinire.agents.pipeline.llm_pipeline.Runner')
    def test_run_async_with_weather_tool(self, mock_runner, mock_agent):
        """Test run_async with weather tool integration."""
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
        assert result.attempts == 1
        
        # Verify Runner.run was called
        mock_runner.run.assert_called_once()
        call_args = mock_runner.run.call_args
        assert call_args[0][0] == agent._sdk_agent  # First argument should be the SDK agent
        assert "Tokyo" in call_args[0][1]  # Second argument should contain the prompt
    
    @patch('refinire.agents.pipeline.llm_pipeline.Agent')
    @patch('refinire.agents.pipeline.llm_pipeline.Runner')
    def test_run_async_with_calculator_tool(self, mock_runner, mock_agent):
        """Test run_async with calculator tool integration."""
        # Mock Runner.run to return a successful result
        mock_result = Mock()
        mock_result.final_output = "The result of 15 * 24 + 100 is 460"
        mock_runner.run = AsyncMock(return_value=mock_result)
        
        # Mock Agent constructor
        mock_agent_instance = Mock()
        mock_agent_instance.instructions = "Test instructions"
        mock_agent_instance.tools = []
        mock_agent.return_value = mock_agent_instance
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant with calculator tools.",
            tools=[calculate_test]
        )
        
        # Test run_async
        result = asyncio.run(agent.run_async("Calculate 15 * 24 + 100"))
        
        # Verify result
        assert result.success
        assert "460" in result.content
        assert result.metadata["sdk"] is True
        assert result.attempts == 1
        
        # Verify Runner.run was called
        mock_runner.run.assert_called_once()
    
    @patch('refinire.agents.pipeline.llm_pipeline.Agent')
    @patch('refinire.agents.pipeline.llm_pipeline.Runner')
    def test_run_async_with_multiple_tools(self, mock_runner, mock_agent):
        """Test run_async with multiple tools integration."""
        # Mock Runner.run to return a successful result
        mock_result = Mock()
        mock_result.final_output = "I can help with weather and calculations"
        mock_runner.run = AsyncMock(return_value=mock_result)
        
        # Mock Agent constructor
        mock_agent_instance = Mock()
        mock_agent_instance.instructions = "Test instructions"
        mock_agent_instance.tools = []
        mock_agent.return_value = mock_agent_instance
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant with multiple tools.",
            tools=[get_weather_test, calculate_test, search_web_test]
        )
        
        # Test run_async
        result = asyncio.run(agent.run_async("What can you help me with?"))
        
        # Verify result
        assert result.success
        assert result.metadata["sdk"] is True
        
        # Verify Runner.run was called
        mock_runner.run.assert_called_once()
        
        # Verify all tools were added to SDK agent
        assert len(agent._sdk_tools) == 3
        assert get_weather_test in agent._sdk_tools
        assert calculate_test in agent._sdk_tools
        assert search_web_test in agent._sdk_tools
    
    @patch('refinire.agents.pipeline.llm_pipeline.Agent')
    @patch('refinire.agents.pipeline.llm_pipeline.Runner')
    def test_run_async_without_tools(self, mock_runner, mock_agent):
        """Test run_async without tools."""
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
        
        # Verify no tools were added
        assert len(agent._sdk_tools) == 0
    
    @patch('refinire.agents.pipeline.llm_pipeline.Agent')
    @patch('refinire.agents.pipeline.llm_pipeline.Runner')
    def test_run_async_with_evaluation(self, mock_runner, mock_agent):
        """Test run_async with evaluation."""
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
                threshold=85.0,
                tools=[get_weather_test]
            )
            
            # Test run_async
            result = asyncio.run(agent.run_async("Test input"))
            
            # Verify result
            assert result.success
            assert result.evaluation_score == 90.0
            assert result.metadata["sdk"] is True
    
    @patch('refinire.agents.pipeline.llm_pipeline.Agent')
    @patch('refinire.agents.pipeline.llm_pipeline.Runner')
    def test_run_async_with_failed_evaluation_and_retry(self, mock_runner, mock_agent):
        """Test run_async with failed evaluation and retry."""
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
                max_retries=2,
                tools=[calculate_test]
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
    def test_run_async_with_input_validation_failure(self, mock_runner, mock_agent):
        """Test run_async with input validation failure."""
        # Mock Agent constructor
        mock_agent_instance = Mock()
        mock_agent_instance.instructions = "Test instructions"
        mock_agent_instance.tools = []
        mock_agent.return_value = mock_agent_instance
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            input_guardrails=[lambda x: len(x) > 0],  # Reject empty input
            tools=[get_weather_test]
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
    def test_run_async_with_output_validation_failure(self, mock_runner, mock_agent):
        """Test run_async with output validation failure."""
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
            output_guardrails=[lambda x: "valid" in x.lower()],  # Require "valid" in output
            tools=[calculate_test]
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
    def test_run_async_with_exception(self, mock_runner, mock_agent):
        """Test run_async with exception handling."""
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
            max_retries=1,
            tools=[get_weather_test]
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
# Tool Management Tests
# ツール管理テスト
# ============================================================================

class TestRefinireAgentToolManagement:
    """Test RefinireAgent tool management methods."""
    
    def test_add_tool_dict(self):
        """Test adding tool dictionary."""
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
    
    def test_add_tool_dict_with_handler(self):
        """Test adding tool dictionary with handler."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions"
        )
        
        def handler(x: int) -> int:
            return x * 2
        
        tool_dict = {
            "type": "function",
            "function": {
                "name": "test_tool",
                "description": "A test tool"
            }
        }
        
        agent.add_tool(tool_dict, handler=handler)
        
        # Verify tool was added
        assert len(agent.tools) == 1
        assert agent.tools[0] == tool_dict
    
    def test_remove_tool_success(self):
        """Test successful tool removal."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions"
        )
        
        tool_dict = {
            "type": "function",
            "function": {"name": "test_tool"}
        }
        
        agent.add_tool(tool_dict)
        assert len(agent.tools) == 1
        
        # Remove the tool
        success = agent.remove_tool("test_tool")
        assert success
        assert len(agent.tools) == 0
    
    def test_remove_tool_failure(self):
        """Test failed tool removal."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions"
        )
        
        # Try to remove non-existent tool
        success = agent.remove_tool("nonexistent_tool")
        assert not success
    
    def test_list_tools(self):
        """Test listing tools."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions"
        )
        
        tool1 = {
            "type": "function",
            "function": {"name": "tool1"}
        }
        tool2 = {
            "type": "function",
            "function": {"name": "tool2"}
        }
        
        agent.add_tool(tool1)
        agent.add_tool(tool2)
        
        tool_names = agent.list_tools()
        assert "tool1" in tool_names
        assert "tool2" in tool_names
        assert len(tool_names) == 2
    
    def test_list_tools_empty(self):
        """Test listing tools when no tools are present."""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions"
        )
        
        tool_names = agent.list_tools()
        assert tool_names == []


# ============================================================================
# Integration Tests
# 統合テスト
# ============================================================================

class TestRefinireAgentIntegration:
    """Integration tests for RefinireAgent with tools."""
    
    @patch('refinire.agents.pipeline.llm_pipeline.Agent')
    @patch('refinire.agents.pipeline.llm_pipeline.Runner')
    def test_full_tool_integration_workflow(self, mock_runner, mock_agent):
        """Test full tool integration workflow."""
        # Mock Runner.run to return a successful result
        mock_result = Mock()
        mock_result.final_output = "I can help with weather and calculations"
        mock_runner.run = AsyncMock(return_value=mock_result)
        
        # Mock Agent constructor
        mock_agent_instance = Mock()
        mock_agent_instance.instructions = "Test instructions"
        mock_agent_instance.tools = []
        mock_agent.return_value = mock_agent_instance
        
        # Create agent with tools
        agent = RefinireAgent(
            name="integration_agent",
            generation_instructions="You are a helpful assistant with multiple tools.",
            tools=[get_weather_test, calculate_test]
        )
        
        # Verify tools were added
        assert len(agent._sdk_tools) == 2
        assert get_weather_test in agent._sdk_tools
        assert calculate_test in agent._sdk_tools
        
        # Test run_async
        result = asyncio.run(agent.run_async("What can you help me with?"))
        
        # Verify result
        assert result.success
        assert result.metadata["sdk"] is True
        
        # Verify Runner.run was called
        mock_runner.run.assert_called_once()
        
        # Test adding more tools
        agent.add_tool({
            "type": "function",
            "function": {"name": "additional_tool"}
        })
        
        assert len(agent.tools) == 1
        
        # Test listing tools
        tool_names = agent.list_tools()
        assert "additional_tool" in tool_names
        
        # Test removing tool
        success = agent.remove_tool("additional_tool")
        assert success
        assert len(agent.tools) == 0
    
    @patch('refinire.agents.pipeline.llm_pipeline.Agent')
    @patch('refinire.agents.pipeline.llm_pipeline.Runner')
    def test_tool_integration_with_evaluation(self, mock_runner, mock_agent):
        """Test tool integration with evaluation."""
        # Mock Runner.run to return a successful result
        mock_result = Mock()
        mock_result.final_output = "The weather is sunny"
        mock_runner.run = AsyncMock(return_value=mock_result)
        
        # Mock Agent constructor
        mock_agent_instance = Mock()
        mock_agent_instance.instructions = "Test instructions"
        mock_agent_instance.tools = []
        mock_agent.return_value = mock_agent_instance
        
        # Mock evaluation to pass
        with patch.object(RefinireAgent, '_evaluate_content') as mock_evaluate:
            mock_evaluate.return_value = EvaluationResult(
                score=95.0,
                passed=True,
                feedback="Excellent response using tools"
            )
            
            agent = RefinireAgent(
                name="evaluation_agent",
                generation_instructions="Use tools when appropriate",
                evaluation_instructions="Evaluate tool usage",
                threshold=85.0,
                tools=[get_weather_test, calculate_test]
            )
            
            # Test run_async
            result = asyncio.run(agent.run_async("What's the weather like?"))
            
            # Verify result
            assert result.success
            assert result.evaluation_score == 95.0
            assert result.metadata["sdk"] is True
            
            # Verify evaluation was called
            mock_evaluate.assert_called_once()
            
            # Verify Runner.run was called
            mock_runner.run.assert_called_once() 