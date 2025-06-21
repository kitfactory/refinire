"""Test tools integration with RefinireAgent"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import Optional

try:
    from agents import function_tool
except ImportError:
    # Fallback if function_tool is not available
    def function_tool(func):
        return func

from refinire.agents.pipeline.llm_pipeline import RefinireAgent, LLMResult
from refinire.agents.flow.context import Context


@function_tool
def simple_calculator(a: int, b: int) -> int:
    """Simple calculator function for testing"""
    return a + b


@function_tool
def weather_check(city: str) -> str:
    """Mock weather check function"""
    return f"Weather in {city}: Sunny, 25°C"


class TestToolsIntegration:
    """Test tools integration with RefinireAgent"""

    def test_constructor_with_function_tools(self):
        """Test basic function tool addition via constructor"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant with tools.",
            tools=[simple_calculator, weather_check]
        )
        
        # Check if tools were added
        assert len(agent.tools) == 2
        assert len(agent._sdk_tools) == 2
        
        # Check tool names
        tool_names = agent.list_tools()
        assert "simple_calculator" in tool_names
        assert "weather_check" in tool_names

    def test_constructor_with_dict_tools(self):
        """Test dictionary tool addition via constructor"""
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
            generation_instructions="You are a helpful assistant with tools.",
            tools=[dict_tool]
        )
        
        # Check if dict tool was added
        assert len(agent.tools) == 1
        assert len(agent._sdk_tools) == 0  # Dict tools are not callable
        
        tool_names = agent.list_tools()
        assert "dict_tool" in tool_names

    def test_constructor_with_mixed_tools(self):
        """Test mixed tool types via constructor"""
        dict_tool = {
            "type": "function",
            "function": {"name": "dict_tool"}
        }
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant with tools.",
            tools=[simple_calculator, dict_tool, weather_check]
        )
        
        # Check if all tools were added
        assert len(agent.tools) == 3
        assert len(agent._sdk_tools) == 2  # Only function tools
        
        tool_names = agent.list_tools()
        assert "simple_calculator" in tool_names
        assert "dict_tool" in tool_names
        assert "weather_check" in tool_names

    def test_add_tool_dict(self):
        """Test adding dictionary tool after initialization"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant with tools."
        )
        
        dict_tool = {
            "type": "function",
            "function": {
                "name": "added_tool",
                "description": "Added tool",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string"}
                    }
                }
            }
        }
        
        agent.add_tool(dict_tool)
        
        # Check if tool was added
        assert len(agent.tools) == 1
        assert len(agent._sdk_tools) == 0
        
        tool_names = agent.list_tools()
        assert "added_tool" in tool_names

    def test_add_tool_dict_with_handler(self):
        """Test adding dictionary tool with handler"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant with tools."
        )
        
        def handler(x: int) -> int:
            return x * 2
        
        dict_tool = {
            "type": "function",
            "function": {
                "name": "handler_tool",
                "description": "Tool with handler",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer"}
                    }
                }
            }
        }
        
        agent.add_tool(dict_tool, handler)
        
        # Check if tool and handler were added
        assert len(agent.tools) == 1
        assert "handler_tool" in agent.tool_handlers
        assert agent.tool_handlers["handler_tool"] == handler

    def test_remove_tool(self):
        """Test tool removal"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant with tools.",
            tools=[simple_calculator, weather_check]
        )
        
        # Remove one tool
        removed = agent.remove_tool("simple_calculator")
        assert removed == True
        
        # Check remaining tools
        assert len(agent.tools) == 1
        tool_names = agent.list_tools()
        assert "weather_check" in tool_names
        assert "simple_calculator" not in tool_names

    def test_remove_tool_failure(self):
        """Test tool removal failure"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant with tools.",
            tools=[simple_calculator]
        )
        
        # Try to remove non-existent tool
        removed = agent.remove_tool("non_existent_tool")
        assert removed == False
        
        # Check tools are unchanged
        assert len(agent.tools) == 1
        tool_names = agent.list_tools()
        assert "simple_calculator" in tool_names

    def test_list_tools(self):
        """Test listing available tools"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant with tools.",
            tools=[simple_calculator, weather_check]
        )
        
        # List tools
        tool_list = agent.list_tools()
        assert "simple_calculator" in tool_list
        assert "weather_check" in tool_list
        assert len(tool_list) == 2

    def test_list_tools_empty(self):
        """Test listing tools when no tools are available"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant with tools."
        )
        
        # List tools
        tool_list = agent.list_tools()
        assert len(tool_list) == 0

    @pytest.mark.asyncio
    async def test_agent_with_tools_initialization(self):
        """Test agent initialization with tools"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant with tools.",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "test_tool",
                        "description": "Test tool",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "input": {"type": "string"}
                            },
                            "required": ["input"]
                        }
                    }
                }
            ]
        )
        
        # Check if tools were initialized
        assert len(agent.tools) == 1
        assert len(agent._sdk_tools) == 0  # Dict tools are not callable

    def test_function_tool_parameter_inference(self):
        """Test automatic parameter type inference for function tools"""
        @function_tool
        def test_function(name: str, age: int, active: bool = True) -> str:
            """Test function with various parameter types"""
            return f"{name} is {age} years old, active: {active}"
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant with tools.",
            tools=[test_function]
        )
        
        # Check that function tool was added
        assert len(agent._sdk_tools) == 1
        assert test_function in agent._sdk_tools
        
        # Test the function directly
        result = test_function(name="John", age=30, active=True)
        assert "John is 30 years old" in result

    @pytest.mark.asyncio
    async def test_agent_run_with_tools(self):
        """Test agent run with tools (basic functionality)"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant. Use tools when needed.",
            tools=[simple_calculator]
        )
        
        # Mock the SDK generation to avoid actual API calls
        with patch.object(agent, '_generate_content_with_sdk', return_value="I can help you with calculations using the simple_calculator tool."):
            result = agent.run("What tools do you have available?")
            
            assert result.success == True
            assert result.content is not None
            assert "simple_calculator" in str(result.content)

    def test_function_tool_wrapper_functionality(self):
        """Test that function tool wrapper functions work correctly"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant with tools.",
            tools=[simple_calculator]
        )
        
        # Test that the SDK tool was created (FunctionTool object)
        if agent._sdk_tools:
            sdk_tool = agent._sdk_tools[0]
            # FunctionTool objects are not directly callable
            # They are used by the OpenAI Agents SDK internally
            assert hasattr(sdk_tool, 'name')
            assert hasattr(sdk_tool, 'description')
            assert hasattr(sdk_tool, 'params_json_schema')
            
            # Test the original function directly
            result = simple_calculator(a=5, b=3)
            assert result == 8

    def test_tool_with_complex_parameters(self):
        """Test tool with complex parameter types"""
        @function_tool
        def complex_function(
            text: str,
            numbers: list,
            config: dict,
            optional_param: Optional[str] = None
        ) -> dict:
            """Function with complex parameter types"""
            return {
                "text": text,
                "sum": sum(numbers),
                "config_keys": list(config.keys()),
                "optional": optional_param
            }
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant with tools.",
            tools=[complex_function]
        )
        
        # Test that the SDK tool was created (FunctionTool object)
        if agent._sdk_tools:
            sdk_tool = agent._sdk_tools[0]
            # FunctionTool objects are not directly callable
            # They are used by the OpenAI Agents SDK internally
            assert hasattr(sdk_tool, 'name')
            assert hasattr(sdk_tool, 'description')
            assert hasattr(sdk_tool, 'params_json_schema')
            
            # Test the original function directly
            result = complex_function(
                text="test",
                numbers=[1, 2, 3],
                config={"key": "value"},
                optional_param="optional"
            )
            assert result["text"] == "test"
            assert result["sum"] == 6
            assert "key" in result["config_keys"] 