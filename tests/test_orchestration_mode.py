"""Test cases for RefinireAgent orchestration mode functionality.

オーケストレーション・モードのテストケース。
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.refinire.agents.pipeline.llm_pipeline import RefinireAgent, LLMResult
from src.refinire.agents.flow.context import Context


class TestOrchestrationMode:
    """Test orchestration mode functionality / オーケストレーション・モード機能のテスト"""
    
    def test_orchestration_mode_parameter(self):
        """Test orchestration_mode parameter initialization / orchestration_modeパラメータの初期化テスト"""
        # Test default value (False)
        # デフォルト値（False）のテスト
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions"
        )
        assert agent.orchestration_mode is False
        
        # Test explicit True
        # 明示的にTrueのテスト
        agent_orchestration = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            orchestration_mode=True
        )
        assert agent_orchestration.orchestration_mode is True
    
    def test_orchestration_template_preparation(self):
        """Test orchestration template preparation / オーケストレーション・テンプレート準備のテスト"""
        # Test English template
        # 英語テンプレートのテスト
        agent_en = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            orchestration_mode=True,
            locale="en"
        )
        assert hasattr(agent_en, '_orchestration_template')
        assert "JSON structure" in agent_en._orchestration_template
        assert "status" in agent_en._orchestration_template
        assert "reasoning" in agent_en._orchestration_template
        assert "next_hint" in agent_en._orchestration_template
        
        # Test Japanese template
        # 日本語テンプレートのテスト
        agent_ja = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            orchestration_mode=True,
            locale="ja"
        )
        assert hasattr(agent_ja, '_orchestration_template')
        assert "JSON構造で必ず回答" in agent_ja._orchestration_template
    
    def test_has_orchestration_instruction(self):
        """Test _has_orchestration_instruction method / _has_orchestration_instructionメソッドのテスト"""
        # Test English locale
        agent_en = RefinireAgent(
            name="test_agent_en",
            generation_instructions="Test instructions",
            orchestration_mode=True,
            locale="en"
        )
        
        # Test with English orchestration indicators
        instruction_with_json = "You must respond in the following JSON"
        assert agent_en._has_orchestration_instruction(instruction_with_json) is True
        
        instruction_with_deviate = "Do not deviate from this format"
        assert agent_en._has_orchestration_instruction(instruction_with_deviate) is True
        
        # Test Japanese locale
        agent_ja = RefinireAgent(
            name="test_agent_ja",
            generation_instructions="Test instructions",
            orchestration_mode=True,
            locale="ja"
        )
        
        # Test with Japanese orchestration indicators
        instruction_with_json_ja = "以下のJSON構造で"
        assert agent_ja._has_orchestration_instruction(instruction_with_json_ja) is True
        
        instruction_with_deviate_ja = "この形式から逸脱しない"
        assert agent_ja._has_orchestration_instruction(instruction_with_deviate_ja) is True
        
        # Test without orchestration indicators
        regular_instruction = "Please provide a helpful response"
        assert agent_en._has_orchestration_instruction(regular_instruction) is False
        assert agent_ja._has_orchestration_instruction(regular_instruction) is False
        
        # Test empty/None instructions
        assert agent_en._has_orchestration_instruction("") is False
        assert agent_en._has_orchestration_instruction(None) is False
    
    def test_parse_orchestration_result_valid_json(self):
        """Test _parse_orchestration_result with valid JSON / 有効なJSONでの_parse_orchestration_resultテスト"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            orchestration_mode=True
        )
        
        # Test valid orchestration JSON
        # 有効なオーケストレーションJSONのテスト
        valid_json = {
            "status": "completed",
            "result": "Task completed successfully",
            "reasoning": "Analysis shows positive outcome",
            "next_hint": {
                "task": "report_generation",
                "confidence": 0.8,
                "rationale": "Next logical step"
            }
        }
        
        result = agent._parse_orchestration_result(valid_json)
        assert result["status"] == "completed"
        assert result["result"] == "Task completed successfully"
        assert result["reasoning"] == "Analysis shows positive outcome"
        assert result["next_hint"]["task"] == "report_generation"
        assert result["next_hint"]["confidence"] == 0.8
    
    def test_parse_orchestration_result_json_string(self):
        """Test _parse_orchestration_result with JSON string / JSON文字列での_parse_orchestration_resultテスト"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            orchestration_mode=True
        )
        
        # Test JSON string
        # JSON文字列のテスト
        json_string = json.dumps({
            "status": "failed",
            "result": None,
            "reasoning": "Insufficient data provided"
        })
        
        result = agent._parse_orchestration_result(json_string)
        assert result["status"] == "failed"
        assert result["result"] is None
        assert result["reasoning"] == "Insufficient data provided"
    
    def test_parse_orchestration_result_markdown_json(self):
        """Test _parse_orchestration_result with markdown JSON / MarkdownJSONでの_parse_orchestration_resultテスト"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            orchestration_mode=True
        )
        
        # Test JSON in markdown codeblock
        # Markdownコードブロック内のJSONのテスト
        markdown_json = '''```json
{
  "status": "completed",
  "result": "Analysis complete",
  "reasoning": "All data processed"
}
```'''
        
        result = agent._parse_orchestration_result(markdown_json)
        assert result["status"] == "completed"
        assert result["result"] == "Analysis complete"
        assert result["reasoning"] == "All data processed"
    
    def test_parse_orchestration_result_missing_fields(self):
        """Test _parse_orchestration_result with missing required fields / 必須フィールド欠落での_parse_orchestration_resultテスト"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            orchestration_mode=True
        )
        
        # Test missing status field
        # statusフィールド欠落のテスト
        invalid_json = {
            "result": "Some result",
            "reasoning": "Some reasoning"
        }
        
        with pytest.raises(Exception) as exc_info:
            agent._parse_orchestration_result(invalid_json)
        assert "Missing required field: status" in str(exc_info.value)
    
    def test_parse_orchestration_result_invalid_status(self):
        """Test _parse_orchestration_result with invalid status value / 無効なstatus値での_parse_orchestration_resultテスト"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            orchestration_mode=True
        )
        
        # Test invalid status value
        # 無効なstatus値のテスト
        invalid_json = {
            "status": "in_progress",  # Should be "completed" or "failed"
            "result": "Some result",
            "reasoning": "Some reasoning"
        }
        
        with pytest.raises(Exception) as exc_info:
            agent._parse_orchestration_result(invalid_json)
        assert "Invalid status value" in str(exc_info.value)
    
    def test_parse_orchestration_result_next_hint_defaults(self):
        """Test _parse_orchestration_result next_hint default values / next_hintデフォルト値での_parse_orchestration_resultテスト"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            orchestration_mode=True
        )
        
        # Test next_hint with minimal data
        # 最小データでのnext_hintのテスト
        json_with_minimal_hint = {
            "status": "completed",
            "result": "Task done",
            "reasoning": "All good",
            "next_hint": {
                "task": "review"
            }
        }
        
        result = agent._parse_orchestration_result(json_with_minimal_hint)
        assert result["next_hint"]["confidence"] == 0.5  # Default value
        assert result["next_hint"]["rationale"] == ""    # Default value
    
    def test_parse_orchestration_result_invalid_json(self):
        """Test _parse_orchestration_result with invalid JSON / 無効なJSONでの_parse_orchestration_resultテスト"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            orchestration_mode=True
        )
        
        # Test malformed JSON string
        # 不正なJSON文字列のテスト
        malformed_json = '{"status": "completed", "result": "missing quote}'
        
        with pytest.raises(Exception) as exc_info:
            agent._parse_orchestration_result(malformed_json)
        assert "Invalid JSON format" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_run_orchestration_mode_success(self):
        """Test run method in orchestration mode with successful execution / 成功実行でのオーケストレーション・モードrun方法テスト"""
        with patch('src.refinire.agents.pipeline.llm_pipeline.Runner') as mock_runner:
            # Mock successful LLM response with orchestration JSON
            # オーケストレーションJSONでの成功LLM応答をモック
            mock_result = MagicMock()
            mock_result.final_output = json.dumps({
                "status": "completed",
                "result": "Task completed successfully",
                "reasoning": "All requirements met",
                "next_hint": {
                    "task": "validation",
                    "confidence": 0.9,
                    "rationale": "Ready for validation"
                }
            })
            mock_runner.run = AsyncMock(return_value=mock_result)
            
            agent = RefinireAgent(
                name="test_agent",
                generation_instructions="Test instructions",
                orchestration_mode=True
            )
            
            result = agent.run("Test input")
            
            # In orchestration mode, should return dict not Context
            # オーケストレーション・モードでは、Contextではなく辞書を返す必要がある
            assert isinstance(result, dict)
            assert result["status"] == "completed"
            assert result["result"] == "Task completed successfully"
            assert result["reasoning"] == "All requirements met"
            assert result["next_hint"]["task"] == "validation"
    
    @pytest.mark.asyncio
    async def test_run_orchestration_mode_json_parse_error(self):
        """Test run method in orchestration mode with JSON parse error / JSON解析エラーでのオーケストレーション・モードrun方法テスト"""
        with patch('src.refinire.agents.pipeline.llm_pipeline.Runner') as mock_runner:
            # Mock LLM response with invalid JSON
            # 無効なJSONでのLLM応答をモック
            mock_result = MagicMock()
            mock_result.final_output = "Invalid JSON response from LLM"
            mock_runner.run = AsyncMock(return_value=mock_result)
            
            agent = RefinireAgent(
                name="test_agent",
                generation_instructions="Test instructions",
                orchestration_mode=True
            )
            
            result = agent.run("Test input")
            
            # Should return error in orchestration format
            # オーケストレーション形式でエラーを返す必要がある
            assert isinstance(result, dict)
            assert result["status"] == "failed"
            assert result["result"] is None
            assert "Execution error" in result["reasoning"]
    
    def test_run_normal_mode_returns_context(self):
        """Test run method in normal mode returns Context / 通常モードでのrun方法がContextを返すテスト"""
        with patch('src.refinire.agents.pipeline.llm_pipeline.Runner') as mock_runner:
            # Mock successful LLM response
            # 成功LLM応答をモック
            mock_result = MagicMock()
            mock_result.final_output = "Normal response"
            mock_runner.run = AsyncMock(return_value=mock_result)
            
            agent = RefinireAgent(
                name="test_agent",
                generation_instructions="Test instructions",
                orchestration_mode=False  # Normal mode
            )
            
            result = agent.run("Test input")
            
            # In normal mode, should return Context
            # 通常モードでは、Contextを返す必要がある
            assert isinstance(result, Context)
            assert result.result == "Normal response"
    
    def test_orchestration_mode_factory_functions(self):
        """Test that factory functions work with orchestration_mode / ファクトリ関数がorchestration_modeで動作することをテスト"""
        from src.refinire.agents.pipeline.llm_pipeline import create_simple_agent, create_evaluated_agent
        
        # Test simple agent with orchestration mode
        # オーケストレーション・モードでのシンプルエージェントのテスト
        agent = create_simple_agent(
            name="orchestration_agent",
            instructions="Test instructions",
            orchestration_mode=True
        )
        assert agent.orchestration_mode is True
        
        # Test evaluated agent with orchestration mode
        # オーケストレーション・モードでの評価エージェントのテスト
        evaluated_agent = create_evaluated_agent(
            name="evaluated_orchestration_agent",
            generation_instructions="Test instructions",
            evaluation_instructions="Evaluate response",
            orchestration_mode=True
        )
        assert evaluated_agent.orchestration_mode is True
    
    def test_orchestration_mode_with_output_model(self):
        """Test orchestration mode with output_model / output_modelでのオーケストレーション・モードテスト"""
        from pydantic import BaseModel
        
        class TestOutput(BaseModel):
            task_id: str
            description: str
            priority: int
        
        # Test orchestration mode with output_model
        # output_modelでのオーケストレーション・モードテスト
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            orchestration_mode=True,
            output_model=TestOutput
        )
        
        # Test that orchestration result parsing applies output_model to result field
        # オーケストレーション結果解析がresultフィールドにoutput_modelを適用することをテスト
        orchestration_json = {
            "status": "completed",
            "result": '{"task_id": "123", "description": "Test task", "priority": 1}',
            "reasoning": "Task analysis complete",
            "next_hint": {
                "task": "validation",
                "confidence": 0.9
            }
        }
        
        result = agent._parse_orchestration_result(orchestration_json)
        assert result["status"] == "completed"
        assert isinstance(result["result"], str)  # Still string at this point
        
        # Simulate the output_model parsing that would happen in _run_standalone
        # _run_standaloneで発生するoutput_model解析をシミュレート
        if agent.output_model and result.get("result") is not None:
            try:
                result["result"] = agent._parse_structured_output(result["result"])
            except Exception:
                pass
        
        # After parsing, result should be typed object
        # 解析後、resultは型付きオブジェクトである必要がある
        assert isinstance(result["result"], TestOutput)
        assert result["result"].task_id == "123"
        assert result["result"].description == "Test task"
        assert result["result"].priority == 1
    
    def test_normal_mode_with_output_model(self):
        """Test normal mode with output_model / output_modelでの通常モードテスト"""
        from pydantic import BaseModel
        
        class TestOutput(BaseModel):
            message: str
            code: int
        
        # Test normal mode with output_model
        # output_modelでの通常モードテスト
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            orchestration_mode=False,
            output_model=TestOutput
        )
        
        # Test structured output parsing
        # 構造化出力解析のテスト
        json_content = '{"message": "Hello World", "code": 200}'
        result = agent._parse_structured_output(json_content)
        
        assert isinstance(result, TestOutput)
        assert result.message == "Hello World"
        assert result.code == 200
    
    def test_orchestration_result_without_output_model(self):
        """Test orchestration result without output_model (string result) / output_modelなし（文字列結果）でのオーケストレーション結果テスト"""
        agent = RefinireAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            orchestration_mode=True
            # No output_model specified
        )
        
        orchestration_json = {
            "status": "completed",
            "result": "Simple string result",
            "reasoning": "Task completed successfully",
            "next_hint": {
                "task": "review",
                "confidence": 0.8
            }
        }
        
        result = agent._parse_orchestration_result(orchestration_json)
        assert result["status"] == "completed"
        assert result["result"] == "Simple string result"
        assert isinstance(result["result"], str)


if __name__ == "__main__":
    pytest.main([__file__])