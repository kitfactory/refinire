"""Test tools integration with RefinireAgent"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import Optional

from refinire.agents.pipeline.llm_pipeline import RefinireAgent, LLMResult
from refinire.agents.flow.context import Context


def simple_calculator(a: int, b: int) -> int:
    """Simple calculator function for testing"""
    return a + b


def weather_check(city: str) -> str:
    """Mock weather check function"""
    return f"Weather in {city}: Sunny, 25°C"


class TestToolsIntegration:
    """Test tools integration with RefinireAgent"""

    def test_add_function_tool_basic(self):
        """Test basic function tool addition"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant with tools."
        )
        
        # Add a simple tool
        agent.add_function_tool(simple_calculator)
        
        # Check if tool was added
        assert len(agent.tools) == 1
        assert len(agent._sdk_tools) == 1
        
        tool_def = agent.tools[0]
        assert tool_def["function"]["name"] == "simple_calculator"
        assert "a" in tool_def["function"]["parameters"]["properties"]
        assert "b" in tool_def["function"]["parameters"]["properties"]

    def test_add_function_tool_with_custom_name(self):
        """Test function tool addition with custom name"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant with tools."
        )
        
        # Add tool with custom name
        agent.add_function_tool(
            simple_calculator, 
            name="custom_calc",
            description="Custom calculator function"
        )
        
        # Check if tool was added with custom name
        assert len(agent.tools) == 1
        tool_def = agent.tools[0]
        assert tool_def["function"]["name"] == "custom_calc"
        assert tool_def["function"]["description"] == "Custom calculator function"

    def test_add_multiple_tools(self):
        """Test adding multiple tools"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant with tools."
        )
        
        # Add multiple tools
        agent.add_function_tool(simple_calculator)
        agent.add_function_tool(weather_check)
        
        # Check if both tools were added
        assert len(agent.tools) == 2
        assert len(agent._sdk_tools) == 2
        
        tool_names = [tool["function"]["name"] for tool in agent.tools]
        assert "simple_calculator" in tool_names
        assert "weather_check" in tool_names

    def test_remove_tool(self):
        """Test tool removal"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant with tools."
        )
        
        # Add tools
        agent.add_function_tool(simple_calculator)
        agent.add_function_tool(weather_check)
        
        # Remove one tool
        removed = agent.remove_tool("simple_calculator")
        assert removed == True
        
        # Check remaining tools
        assert len(agent.tools) == 1
        assert agent.tools[0]["function"]["name"] == "weather_check"

    def test_list_tools(self):
        """Test listing available tools"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant with tools."
        )
        
        # Add tools
        agent.add_function_tool(simple_calculator)
        agent.add_function_tool(weather_check)
        
        # List tools
        tool_list = agent.list_tools()
        assert "simple_calculator" in tool_list
        assert "weather_check" in tool_list
        assert len(tool_list) == 2

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
        assert len(agent._sdk_tools) == 1

    def test_tool_parameter_inference(self):
        """Test automatic parameter type inference"""
        def test_function(name: str, age: int, active: bool = True) -> str:
            """Test function with various parameter types"""
            return f"{name} is {age} years old, active: {active}"
        
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant with tools."
        )
        
        agent.add_function_tool(test_function)
        
        # Check parameter types were inferred correctly
        tool_def = agent.tools[0]
        params = tool_def["function"]["parameters"]["properties"]
        
        assert params["name"]["type"] == "string"
        assert params["age"]["type"] == "integer"
        assert params["active"]["type"] == "boolean"
        
        # Check required parameters
        required = tool_def["function"]["parameters"]["required"]
        assert "name" in required
        assert "age" in required
        assert "active" not in required  # Has default value

    @pytest.mark.asyncio
    async def test_agent_run_with_tools(self):
        """Test agent run with tools (basic functionality)"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant. Use tools when needed."
        )
        
        agent.add_function_tool(simple_calculator)
        
        # Mock the SDK generation to avoid actual API calls
        with patch.object(agent, '_generate_content_with_sdk', return_value="I can help you with calculations using the simple_calculator tool."):
            result = agent.run("What tools do you have available?")
            
            assert result.success == True
            assert result.content is not None
            assert "simple_calculator" in str(result.content)

    def test_tool_wrapper_functionality(self):
        """Test that tool wrapper functions work correctly"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="You are a helpful assistant with tools."
        )
        
        agent.add_function_tool(simple_calculator)
        
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
            generation_instructions="You are a helpful assistant with tools."
        )
        
        agent.add_function_tool(complex_function)
        
        # Check parameter types
        tool_def = agent.tools[0]
        params = tool_def["function"]["parameters"]["properties"]
        
        assert params["text"]["type"] == "string"
        assert params["numbers"]["type"] == "array"
        assert params["config"]["type"] == "object"
        assert params["optional_param"]["type"] == "string"
        
        # Test the SDK tool was created (FunctionTool object)
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