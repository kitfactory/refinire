"""
Test RefinireAgent tool functionality
RefinireAgentのtool機能をテスト

This test module ensures that RefinireAgent correctly handles tools,
function calling, and automatic tool execution.
このテストモジュールは、RefinireAgentがtools、関数呼び出し、
自動tool実行を正しく処理することを確保します。
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock

try:
    from agents import function_tool
except ImportError:
    # Fallback if function_tool is not available
    def function_tool(func):
        return func

from refinire import RefinireAgent, LLMResult, create_tool_enabled_agent
from refinire.agents.pipeline.llm_pipeline import create_calculator_agent, create_web_search_agent


class TestRefinireAgentTools:
    """Test RefinireAgent tool integration / RefinireAgentのtool統合をテスト"""
    
    def test_constructor_with_function_tools(self):
        """Test adding Python function as tool via constructor / コンストラクタでPython関数をtoolとして追加するテスト"""
        @function_tool
        def test_function(param1: str, param2: int = 10) -> str:
            """Test function for tool integration"""
            return f"Result: {param1}, {param2}"
        
        pipeline = RefinireAgent(
            name="test_pipeline",
            generation_instructions="Test instructions",
            model="gpt-4o-mini",
            tools=[test_function]
        )
        
        # Verify tool was added
        # toolが追加されたことを確認
        assert len(pipeline.tools) == 1
        assert len(pipeline._sdk_tools) == 1
        assert test_function in pipeline._sdk_tools
        
        # Verify tool names
        # tool名を確認
        tool_names = pipeline.list_tools()
        assert "test_function" in tool_names
    
    def test_add_tool_with_handler(self):
        """Test adding tool with custom handler / カスタムハンドラー付きtoolの追加をテスト"""
        pipeline = RefinireAgent(
            name="test_pipeline",
            generation_instructions="Test instructions",
            model="gpt-4o-mini",
            tools=[]
        )
        
        def custom_handler(query: str) -> str:
            return f"Handled: {query}"
        
        tool_definition = {
            "type": "function",
            "function": {
                "name": "custom_tool",
                "description": "Custom tool for testing",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"}
                    },
                    "required": ["query"]
                }
            }
        }
        
        pipeline.add_tool(tool_definition, custom_handler)
        
        assert len(pipeline.tools) == 1
        assert "custom_tool" in pipeline.tool_handlers
        assert pipeline.tool_handlers["custom_tool"] == custom_handler
    
    def test_list_tools(self):
        """Test listing available tools / 利用可能なtoolのリストをテスト"""
        @function_tool
        def tool1():
            pass
            
        @function_tool
        def tool2():
            pass
        
        pipeline = RefinireAgent(
            name="test_pipeline",
            generation_instructions="Test instructions",
            model="gpt-4o-mini",
            tools=[tool1, tool2]
        )
        
        tools = pipeline.list_tools()
        assert "tool1" in tools
        assert "tool2" in tools
        assert len(tools) == 2
    
    def test_remove_tool(self):
        """Test removing tools / toolの削除をテスト"""
        @function_tool
        def test_tool():
            pass
        
        pipeline = RefinireAgent(
            name="test_pipeline",
            generation_instructions="Test instructions",
            model="gpt-4o-mini",
            tools=[test_tool]
        )
        
        assert len(pipeline.tools) == 1
        
        # Remove tool
        # toolを削除
        removed = pipeline.remove_tool("test_tool")
        assert removed is True
        assert len(pipeline.tools) == 0
        
        # Try to remove non-existent tool
        # 存在しないtoolの削除を試行
        removed = pipeline.remove_tool("non_existent")
        assert removed is False
    
    @patch('refinire.agents.pipeline.llm_pipeline.Agent')
    @patch('refinire.agents.pipeline.llm_pipeline.Runner')
    def test_tool_execution_in_pipeline(self, mock_runner, mock_agent):
        """Test tool execution within pipeline / パイプライン内でのtool実行をテスト"""
        # Mock Runner.run to return a successful result
        mock_result = Mock()
        mock_result.final_output = "The weather in Tokyo is sunny, 22°C"
        mock_result.output = "The weather in Tokyo is sunny, 22°C"
        mock_runner.run = AsyncMock(return_value=mock_result)
        
        # Mock Agent constructor
        mock_agent_instance = Mock()
        mock_agent_instance.instructions = "You can get weather information."
        mock_agent_instance.tools = [Mock()]  # Add a mock tool
        mock_agent.return_value = mock_agent_instance
        
        # Create pipeline with tool
        # toolありのパイプラインを作成
        @function_tool
        def get_weather(city: str) -> str:
            """Get weather for a city"""
            return f"Weather in {city}: Sunny, 22°C"
        
        pipeline = create_tool_enabled_agent(
            name="weather_assistant",
            instructions="You can get weather information.",
            tools=[get_weather],
            model="gpt-4o-mini"
        )
        
        # Run pipeline
        # パイプラインを実行
        result = pipeline.run("What's the weather in Tokyo?")
        
        # Verify result
        # 結果を確認
        assert result.success is True
        assert "Tokyo" in result.content
        assert "sunny" in result.content.lower()
        
        # Verify Runner.run was called
        mock_runner.run.assert_called_once()
        call_args = mock_runner.run.call_args
        assert call_args[0][0] == pipeline._sdk_agent  # First argument should be the SDK agent
        assert "Tokyo" in call_args[0][1]  # Second argument should contain the prompt
    
    def test_create_tool_enabled_pipeline(self):
        """Test create_tool_enabled_agent factory function / create_tool_enabled_agentファクトリ関数をテスト"""
        @function_tool
        def get_time() -> str:
            """Get current time"""
            return "Current time: 12:00 PM"
        
        @function_tool
        def calculate(expr: str) -> float:
            """Calculate mathematical expression"""
            return eval(expr)
        
        # Create agent with multiple tools
        # 複数のtoolでエージェントを作成
        agent = create_tool_enabled_agent(
            name="test_agent",
            instructions="You have access to time and calculation tools.",
            tools=[get_time, calculate],
            model="gpt-4o-mini"
        )
        
        # Verify tools were added
        # toolが追加されたことを確認
        assert len(agent.tools) == 2
        assert len(agent._sdk_tools) == 2
        assert get_time in agent._sdk_tools
        assert calculate in agent._sdk_tools
        
        # Verify tool names
        # tool名を確認
        tool_names = agent.list_tools()
        assert "get_time" in tool_names
        assert "calculate" in tool_names
    
    def test_create_calculator_agent(self):
        """Test create_calculator_agent factory function / create_calculator_agentファクトリ関数をテスト"""
        agent = create_calculator_agent(
            name="calc_agent",
            instructions="You are a calculator assistant.",
            model="gpt-4o-mini"
        )
        
        # Verify calculator tool was added
        # 計算機toolが追加されたことを確認
        assert len(agent.tools) == 1
        assert len(agent._sdk_tools) == 1
        
        # Verify tool names
        # tool名を確認
        tool_names = agent.list_tools()
        assert "calculate" in tool_names
    
    def test_create_web_search_agent(self):
        """Test create_web_search_agent factory function / create_web_search_agentファクトリ関数をテスト"""
        agent = create_web_search_agent(
            name="search_agent",
            instructions="You can search the web for information.",
            model="gpt-4o-mini"
        )
        
        # Verify web search tool was added
        # Web検索toolが追加されたことを確認
        assert len(agent.tools) == 1
        assert len(agent._sdk_tools) == 1
        
        # Verify tool names
        # tool名を確認
        tool_names = agent.list_tools()
        assert "web_search" in tool_names
    
    def test_tool_execution_error_handling(self):
        """Test error handling when tool execution fails / tool実行失敗時のエラーハンドリングをテスト"""
        @function_tool
        def failing_tool():
            """Tool that always fails"""
            raise Exception("Tool execution failed")
        
        pipeline = RefinireAgent(
            name="test_pipeline",
            generation_instructions="Test instructions",
            model="gpt-4o-mini",
            tools=[failing_tool]
        )
        
        # Verify tool was added despite potential failure
        # 失敗の可能性があってもtoolが追加されたことを確認
        assert len(pipeline.tools) == 1
        assert len(pipeline._sdk_tools) == 1
        assert failing_tool in pipeline._sdk_tools
    
    def test_tool_not_found_error(self):
        """Test error handling when tool is not found / toolが見つからない場合のエラーハンドリングをテスト"""
        pipeline = RefinireAgent(
            name="test_pipeline",
            generation_instructions="Test instructions",
            model="gpt-4o-mini",
            tools=[]
        )
        
        # Try to remove non-existent tool
        # 存在しないtoolの削除を試行
        removed = pipeline.remove_tool("non_existent_tool")
        assert removed is False
        
        # Verify tools list is unchanged
        # toolリストが変更されていないことを確認
        assert len(pipeline.tools) == 0
        assert len(pipeline._sdk_tools) == 0


class TestRefinireAgentToolIntegration:
    """Test RefinireAgent tool integration scenarios / RefinireAgentのtool統合シナリオをテスト"""
    
    @patch('refinire.agents.pipeline.llm_pipeline.Agent')
    @patch('refinire.agents.pipeline.llm_pipeline.Runner')
    def test_multiple_tool_calls(self, mock_runner, mock_agent):
        """Test multiple tool calls in sequence / 複数のtool呼び出しのシーケンスをテスト"""
        # Mock Runner.run to return a successful result
        mock_result = Mock()
        mock_result.final_output = "Weather in Tokyo is sunny. 15 + 25 = 40"
        mock_result.output = "Weather in Tokyo is sunny. 15 + 25 = 40"
        mock_runner.run = AsyncMock(return_value=mock_result)
        
        # Mock Agent constructor
        mock_agent_instance = Mock()
        mock_agent_instance.instructions = "You have weather and calculation tools."
        mock_agent_instance.tools = [Mock(), Mock()]  # Add mock tools
        mock_agent.return_value = mock_agent_instance
        
        # Create pipeline with multiple tools
        # 複数のtoolでパイプラインを作成
        @function_tool
        def get_weather(city: str) -> str:
            return f"Weather in {city}: Sunny, 22°C"
        
        @function_tool
        def calculate(expression: str) -> str:
            return f"Result: {eval(expression)}"
        
        pipeline = RefinireAgent(
            name="multi_tool_agent",
            generation_instructions="You have weather and calculation tools.",
            model="gpt-4o-mini",
            tools=[get_weather, calculate]
        )
        
        # Run pipeline
        # パイプラインを実行
        result = pipeline.run("What's the weather in Tokyo and what's 15 + 25?")
        
        # Verify result
        # 結果を確認
        assert result.success is True
        assert "Tokyo" in result.content
        assert "40" in result.content
        
        # Verify Runner.run was called
        mock_runner.run.assert_called_once()
        call_args = mock_runner.run.call_args
        assert call_args[0][0] == pipeline._sdk_agent  # First argument should be the SDK agent
        assert "Tokyo" in call_args[0][1]  # Second argument should contain the prompt 