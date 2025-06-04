"""Test ClearifyPipeline functionality"""

import pytest
from unittest.mock import Mock, patch
from typing import List

from agents_sdk_models import ClearifyPipeline, Clearify, ClarificationQuestion
from pydantic import BaseModel


class ReportRequirements(BaseModel):
    """Test model for report requirements"""
    event: str  # Event name / イベント名
    date: str   # Date / 日付
    place: str  # Place / 場所
    topics: List[str] # Topics / トピック
    interested: str # Impression / 印象に残ること
    expression: str # Thoughts / 感想


class TestClearifyPipeline:
    """Test class for ClearifyPipeline / ClearifyPipelineのテストクラス"""

    def test_init_with_typed_output(self):
        """Test initialization with typed output model / 型付き出力モデルでの初期化をテスト"""
        pipeline = ClearifyPipeline(
            name="test_clearify",
            generation_instructions="Test instructions",
            output_data=ReportRequirements,
            clerify_max_turns=10,
            model="gpt-4o"
        )
        
        assert pipeline.name == "test_clearify"
        assert pipeline.original_output_data == ReportRequirements
        assert pipeline.clerify_max_turns == 10
        assert pipeline.current_turn == 0
        assert pipeline.remaining_turns == 10
        assert not pipeline.is_complete

    def test_init_with_string_output(self):
        """Test initialization with string output / 文字列出力での初期化をテスト"""
        pipeline = ClearifyPipeline(
            name="test_clearify_string",
            generation_instructions="Test instructions",
            clerify_max_turns=5,
            model="gpt-4o"
        )
        
        assert pipeline.name == "test_clearify_string"
        assert pipeline.original_output_data is None
        assert pipeline.clerify_max_turns == 5
        assert pipeline.output_model == Clearify

    def test_build_clarification_instructions(self):
        """Test clarification instructions building / 明確化指示構築をテスト"""
        pipeline = ClearifyPipeline(
            name="test_clearify",
            generation_instructions="Base instructions",
            output_data=ReportRequirements,
            model="gpt-4o"
        )
        
        instructions = pipeline._build_clarification_instructions(
            "Base instructions", 
            ReportRequirements
        )
        
        assert "Base instructions" in instructions
        assert "要件明確化の専門家" in instructions
        assert "clearity" in instructions
        assert "user_requirement" in instructions
        assert str(pipeline.clerify_max_turns) in instructions

    def test_create_wrapped_model(self):
        """Test wrapped model creation / ラップモデル作成をテスト"""
        pipeline = ClearifyPipeline(
            name="test_clearify",
            generation_instructions="Test instructions",
            output_data=ReportRequirements,
            model="gpt-4o"
        )
        
        wrapped_model = pipeline._create_wrapped_model(ReportRequirements)
        
        # Check if wrapped model has required fields
        # ラップモデルが必要なフィールドを持つかチェック
        assert hasattr(wrapped_model, '__annotations__')
        annotations = wrapped_model.__annotations__
        assert 'clearity' in annotations
        assert 'user_requirement' in annotations

    @patch('agents_sdk_models.clearify_pipeline.AgentPipeline.run')
    def test_run_with_immediate_clarity(self, mock_run):
        """Test run method with immediate clarity / 即座に明確化される場合のrunメソッドをテスト"""
        # Mock response with clearity=True
        # clearity=Trueのモックレスポンス
        mock_result = Mock()
        mock_result.clearity = True
        mock_result.user_requirement = "Clear requirement"
        mock_run.return_value = mock_result
        
        pipeline = ClearifyPipeline(
            name="test_clearify",
            generation_instructions="Test instructions",
            model="gpt-4o"
        )
        
        result = pipeline.run("Test input")
        
        assert result == "Clear requirement"
        assert pipeline.current_turn == 1
        mock_run.assert_called_once()

    @patch('agents_sdk_models.clearify_pipeline.AgentPipeline.run')
    def test_run_returns_clarification_question(self, mock_run):
        """Test run method returns clarification question / runメソッドが明確化質問を返すことをテスト"""
        # Mock response with clearity=False
        # clearity=Falseのモックレスポンス
        mock_result = Mock()
        mock_result.clearity = False
        mock_result.user_requirement = "What specific type of app?"
        mock_run.return_value = mock_result
        
        pipeline = ClearifyPipeline(
            name="test_clearify",
            generation_instructions="Test instructions",
            clerify_max_turns=5,
            model="gpt-4o"
        )
        
        result = pipeline.run("Test input")
        
        assert isinstance(result, ClarificationQuestion)
        assert result.question == "What specific type of app?"
        assert result.turn == 1
        assert result.remaining_turns == 4
        assert pipeline.current_turn == 1

    @patch('agents_sdk_models.clearify_pipeline.AgentPipeline.run')
    def test_continue_clarification(self, mock_run):
        """Test continue clarification method / 明確化継続メソッドをテスト"""
        # First call - return question
        # 初回呼び出し - 質問を返す
        mock_result1 = Mock()
        mock_result1.clearity = False
        mock_result1.user_requirement = "What type of app?"
        
        # Second call - return final answer
        # 2回目呼び出し - 最終回答を返す
        mock_result2 = Mock()
        mock_result2.clearity = True
        mock_result2.user_requirement = "Mobile todo app"
        
        mock_run.side_effect = [mock_result1, mock_result2]
        
        pipeline = ClearifyPipeline(
            name="test_clearify",
            generation_instructions="Test instructions",
            model="gpt-4o"
        )
        
        # First call
        # 初回呼び出し
        result1 = pipeline.run("I want to make an app")
        assert isinstance(result1, ClarificationQuestion)
        assert pipeline.current_turn == 1
        
        # Continue clarification
        # 明確化継続
        result2 = pipeline.continue_clarification("A todo app")
        assert result2 == "Mobile todo app"
        assert pipeline.current_turn == 2

    @patch('agents_sdk_models.clearify_pipeline.AgentPipeline.run')
    def test_run_with_pipeline_failure(self, mock_run):
        """Test run method when pipeline fails / パイプライン失敗時のrunメソッドをテスト"""
        mock_run.return_value = None
        
        pipeline = ClearifyPipeline(
            name="test_clearify",
            generation_instructions="Test instructions",
            model="gpt-4o"
        )
        
        result = pipeline.run("Test input")
        
        assert result is None
        # English: When pipeline fails immediately, turn count should remain 0
        # 日本語: パイプライン即座失敗時はターンカウントは0のまま
        assert pipeline.current_turn == 0

    def test_continue_clarification_max_turns(self):
        """Test continue clarification when max turns reached / 最大ターン数到達時の明確化継続をテスト"""
        pipeline = ClearifyPipeline(
            name="test_clearify",
            generation_instructions="Test instructions",
            clerify_max_turns=2,
            model="gpt-4o"
        )
        
        # Simulate reaching max turns
        # 最大ターン数到達をシミュレート
        pipeline._turn_count = 2
        
        result = pipeline.continue_clarification("More details")
        assert result is None

    def test_conversation_history(self):
        """Test conversation history tracking / 会話履歴追跡をテスト"""
        pipeline = ClearifyPipeline(
            name="test_clearify",
            generation_instructions="Test instructions",
            model="gpt-4o"
        )
        
        # Initially empty
        # 初期状態では空
        assert len(pipeline.conversation_history) == 0
        
        # Simulate storing interactions with proper turn count
        # 適切なターンカウントで対話保存をシミュレート
        pipeline._turn_count = 1  # Set turn count before storing
        mock_result = Mock()
        mock_result.user_requirement = "AI response 1"
        pipeline._store_interaction("User input 1", mock_result)
        
        history = pipeline.conversation_history
        assert len(history) == 1
        assert history[0]['user_input'] == "User input 1"
        assert history[0]['ai_response'] == "AI response 1"
        assert history[0]['turn'] == 1

    def test_reset_session(self):
        """Test session reset functionality / セッションリセット機能をテスト"""
        pipeline = ClearifyPipeline(
            name="test_clearify",
            generation_instructions="Test instructions",
            model="gpt-4o"
        )
        
        # Simulate some activity
        # 何らかの活動をシミュレート
        pipeline._turn_count = 5
        mock_result = Mock()
        mock_result.user_requirement = "Test response"
        pipeline._store_interaction("Test input", mock_result)
        
        assert pipeline.current_turn == 5
        assert len(pipeline.conversation_history) == 1
        
        # Reset session
        # セッションリセット
        pipeline.reset_session()
        
        assert pipeline.current_turn == 0
        assert len(pipeline.conversation_history) == 0
        assert not pipeline.is_complete

    def test_turn_properties(self):
        """Test turn-related properties / ターン関連プロパティをテスト"""
        pipeline = ClearifyPipeline(
            name="test_clearify",
            generation_instructions="Test instructions",
            clerify_max_turns=10,
            model="gpt-4o"
        )
        
        assert pipeline.current_turn == 0
        assert pipeline.remaining_turns == 10
        assert not pipeline.is_complete
        
        pipeline._turn_count = 3
        assert pipeline.current_turn == 3
        assert pipeline.remaining_turns == 7
        assert not pipeline.is_complete
        
        pipeline._turn_count = 10
        assert pipeline.current_turn == 10
        assert pipeline.remaining_turns == 0
        assert pipeline.is_complete
        
        pipeline._turn_count = 15  # Over max
        assert pipeline.current_turn == 15
        assert pipeline.remaining_turns == 0
        assert pipeline.is_complete


class TestClarificationQuestion:
    """Test class for ClarificationQuestion / ClarificationQuestionのテストクラス"""

    def test_clarification_question_creation(self):
        """Test ClarificationQuestion creation / ClarificationQuestion作成をテスト"""
        question = ClarificationQuestion(
            question="What type of app do you want?",
            turn=2,
            remaining_turns=8
        )
        
        assert question.question == "What type of app do you want?"
        assert question.turn == 2
        assert question.remaining_turns == 8

    def test_clarification_question_str(self):
        """Test ClarificationQuestion string representation / ClarificationQuestion文字列表現をテスト"""
        question = ClarificationQuestion(
            question="What is your main goal?",
            turn=1,
            remaining_turns=4
        )
        
        str_repr = str(question)
        assert "[ターン 1/5]" in str_repr
        assert "What is your main goal?" in str_repr


class TestClearifyModels:
    """Test class for Clearify models / Clearifyモデルのテストクラス"""

    def test_clearify_base_model(self):
        """Test ClearifyBase model / ClearifyBaseモデルをテスト"""
        from agents_sdk_models.clearify_pipeline import ClearifyBase
        
        # Test with clearity=True
        # clearity=Trueでテスト
        clearify = ClearifyBase(clearity=True)
        assert clearify.clearity is True

    def test_clearify_default_model(self):
        """Test default Clearify model / デフォルトClearifyモデルをテスト"""
        # Test with string requirement
        # 文字列要求でテスト
        clearify = Clearify(clearity=True, user_requirement="Test requirement")
        assert clearify.clearity is True
        assert clearify.user_requirement == "Test requirement"
        
        # Test without requirement
        # 要求なしでテスト
        clearify_no_req = Clearify(clearity=False)
        assert clearify_no_req.clearity is False
        assert clearify_no_req.user_requirement is None 