"""
Test RefinireAgent tool functionality
RefinireAgentのtool機能をテスト

This test module ensures that RefinireAgent correctly handles tools,
function calling, and automatic tool execution.
このテストモジュールは、RefinireAgentがtools、関数呼び出し、
自動tool実行を正しく処理することを確保します。
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from refinire import RefinireAgent, LLMResult, create_tool_enabled_agent
from refinire.agents.pipeline.llm_pipeline import create_calculator_agent, create_web_search_agent


class TestRefinireAgentTools:
    """Test RefinireAgent tool integration / RefinireAgentのtool統合をテスト"""
    
    def test_add_function_tool(self):
        """Test adding Python function as tool / Python関数をtoolとして追加するテスト"""
        pipeline = RefinireAgent(
            name="test_pipeline",
            generation_instructions="Test instructions",
            model="gpt-4o-mini",
            tools=[]
        )
        
        def test_function(param1: str, param2: int = 10) -> str:
            """Test function for tool integration"""
            return f"Result: {param1}, {param2}"
        
        # Add function as tool
        # 関数をtoolとして追加
        pipeline.add_function_tool(test_function)
        
        # Verify tool was added
        # toolが追加されたことを確認
        assert len(pipeline.tools) == 1
        tool = pipeline.tools[0]
        assert tool["type"] == "function"
        assert tool["function"]["name"] == "test_function"
        assert tool["function"]["description"] == "Test function for tool integration"
        assert "callable" in tool
        
        # Verify parameters
        # パラメータを確認
        params = tool["function"]["parameters"]
        assert params["type"] == "object"
        assert "param1" in params["properties"]
        assert "param2" in params["properties"]
        assert "param1" in params["required"]
        assert "param2" not in params["required"]  # Has default value
    
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
        assert pipeline.tools[0]["callable"] == custom_handler
    
    def test_list_tools(self):
        """Test listing available tools / 利用可能なtoolのリストをテスト"""
        pipeline = RefinireAgent(
            name="test_pipeline",
            generation_instructions="Test instructions",
            model="gpt-4o-mini",
            tools=[]
        )
        
        def tool1():
            pass
            
        def tool2():
            pass
        
        pipeline.add_function_tool(tool1, "custom_tool1")
        pipeline.add_function_tool(tool2, "custom_tool2")
        
        tools = pipeline.list_tools()
        assert "custom_tool1" in tools
        assert "custom_tool2" in tools
        assert len(tools) == 2
    
    def test_remove_tool(self):
        """Test removing tools / toolの削除をテスト"""
        pipeline = RefinireAgent(
            name="test_pipeline",
            generation_instructions="Test instructions",
            model="gpt-4o-mini",
            tools=[]
        )
        
        def test_tool():
            pass
        
        pipeline.add_function_tool(test_tool)
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
    
    @patch('refinire.agents.pipeline.llm_pipeline.OpenAI')
    def test_tool_execution_in_pipeline(self, mock_openai):
        """Test tool execution within pipeline / パイプライン内でのtool実行をテスト"""
        # Mock OpenAI client
        # OpenAIクライアントをモック
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        # Mock tool call response
        # tool呼び出しレスポンスをモック
        mock_tool_call = Mock()
        mock_tool_call.id = "test_tool_call_id"
        mock_tool_call.function.name = "get_weather"
        mock_tool_call.function.arguments = '{"city": "Tokyo"}'
        mock_tool_call.type = "function"
        
        # Mock first response (with tool call)
        # 最初のレスポンス（tool呼び出し付き）をモック
        mock_first_response = Mock()
        mock_first_response.choices = [Mock()]
        mock_first_response.choices[0].message.content = None
        mock_first_response.choices[0].message.tool_calls = [mock_tool_call]
        
        # Mock second response (final answer)
        # 2番目のレスポンス（最終回答）をモック
        mock_final_response = Mock()
        mock_final_response.choices = [Mock()]
        mock_final_response.choices[0].message.content = "The weather in Tokyo is sunny, 22°C"
        mock_final_response.choices[0].message.tool_calls = None
        
        # Set up client response sequence
        # クライアントレスポンスシーケンスを設定
        mock_client.chat.completions.create.side_effect = [
            mock_first_response,
            mock_final_response
        ]
        
        # Create pipeline with tool
        # toolありのパイプラインを作成
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
        
        # Verify OpenAI was called correctly
        # OpenAIが正しく呼び出されたことを確認
        assert mock_client.chat.completions.create.call_count == 2
    
    def test_create_tool_enabled_pipeline(self):
        """Test tool-enabled pipeline creation / tool対応パイプライン作成をテスト"""
        def get_time() -> str:
            return "12:00 PM"
        
        def calculate(expr: str) -> float:
            return 42.0
        
        pipeline = create_tool_enabled_agent(
            name="multi_tool",
            instructions="Assistant with tools",
            tools=[get_time, calculate],
            model="gpt-4o-mini"
        )
        
        assert len(pipeline.tools) == 2
        tool_names = pipeline.list_tools()
        assert "get_time" in tool_names
        assert "calculate" in tool_names
    
    def test_create_calculator_agent(self):
        """Test calculator pipeline creation / 計算機パイプライン作成をテスト"""
        pipeline = create_calculator_agent(
            name="math_assistant",
            model="gpt-4o-mini"
        )
        
        assert len(pipeline.tools) == 1
        assert "calculate" in pipeline.list_tools()
        
        # Test the calculator function
        # 計算機関数をテスト
        calc_tool = pipeline.tools[0]
        calc_func = calc_tool["callable"]
        
        # Test valid expression
        # 有効な式をテスト
        result = calc_func("2 + 3")
        assert result == 5.0
        
        # Test invalid expression
        # 無効な式をテスト
        result = calc_func("invalid_expression")
        assert isinstance(result, str)
        assert "Error" in result
    
    def test_create_web_search_agent(self):
        """Test web search pipeline creation / Web検索パイプライン作成をテスト"""
        pipeline = create_web_search_agent(
            name="search_assistant",
            model="gpt-4o-mini"
        )
        
        assert len(pipeline.tools) == 1
        assert "web_search" in pipeline.list_tools()
        
        # Test the search function (placeholder)
        # 検索関数をテスト（プレースホルダー）
        search_tool = pipeline.tools[0]
        search_func = search_tool["callable"]
        
        result = search_func("test query")
        assert isinstance(result, str)
        assert "test query" in result
        assert "placeholder" in result.lower()
    
    def test_tool_execution_error_handling(self):
        """Test error handling in tool execution / tool実行でのエラーハンドリングをテスト"""
        pipeline = RefinireAgent(
            name="test_pipeline",
            generation_instructions="Test instructions",
            model="gpt-4o-mini",
            tools=[]
        )
        
        def failing_tool():
            raise ValueError("Tool execution failed")
        
        pipeline.add_function_tool(failing_tool)
        
        # Create mock tool call
        # モックtool呼び出しを作成
        mock_tool_call = Mock()
        mock_tool_call.id = "test_id"
        mock_tool_call.function.name = "failing_tool"
        mock_tool_call.function.arguments = "{}"
        
        # Test error handling
        # エラーハンドリングをテスト
        try:
            result = pipeline._execute_tool(mock_tool_call)
            # Should not reach here
            assert False, "Expected exception was not raised"
        except ValueError:
            # Expected behavior
            pass
    
    def test_tool_not_found_error(self):
        """Test error when tool is not found / toolが見つからない場合のエラーをテスト"""
        pipeline = RefinireAgent(
            name="test_pipeline",
            generation_instructions="Test instructions",
            model="gpt-4o-mini",
            tools=[]
        )
        
        # Create mock tool call for non-existent tool
        # 存在しないtool用のモックtool呼び出しを作成
        mock_tool_call = Mock()
        mock_tool_call.id = "test_id"
        mock_tool_call.function.name = "non_existent_tool"
        mock_tool_call.function.arguments = "{}"
        
        with pytest.raises(ValueError, match="Tool not found"):
            pipeline._execute_tool(mock_tool_call)


class TestRefinireAgentToolIntegration:
    """Integration tests for RefinireAgent tools / RefinireAgentのtools統合テスト"""
    
    @patch('refinire.agents.pipeline.llm_pipeline.OpenAI')
    def test_multiple_tool_calls(self, mock_openai):
        """Test handling multiple tool calls in sequence / 複数tool呼び出しの連続処理をテスト"""
        # This would test the full tool calling loop
        # 完全なtool呼び出しループをテストする
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        # Setup complex tool call scenario
        # 複雑なtool呼び出しシナリオを設定
        # ... (detailed mock setup would go here)
        
        # For now, just verify the structure exists
        # 現在は、構造が存在することのみ確認
        pipeline = create_tool_enabled_agent(
            name="test",
            instructions="Test",
            tools=[],
            model="gpt-4o-mini"
        )
        
        assert hasattr(pipeline, '_generate_content')
        assert hasattr(pipeline, '_execute_tool') 
