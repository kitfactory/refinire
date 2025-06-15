"""
Tests for ClarifyAgent
ClarifyAgentのテスト
"""

import pytest
import asyncio
from typing import List
from unittest.mock import patch, MagicMock
from pydantic import BaseModel

from refinire import (
    ClarifyAgent, Context, ClarificationResult, 
    create_simple_clarify_agent, create_evaluated_clarify_agent
)
from refinire.agents.clarify_agent import ClarificationQuestion


class ReportRequirementsForTest(BaseModel):
    """
    Test model for report requirements
    レポート要件テスト用モデル
    """
    event: str
    date: str  
    place: str
    topics: List[str]
    interested: str
    expression: str


class TestClarifyAgent:
    """
    Test class for ClarifyAgent
    ClarifyAgentのテストクラス
    """

    def test_clarify_agent_initialization(self):
        """
        Test ClarifyAgent initialization
        ClarifyAgentの初期化テスト
        """
        # English: Test basic initialization
        # 日本語: 基本初期化テスト
        agent = ClarifyAgent(
            name="test_clarifier",
            generation_instructions="Test instructions",
            output_data=ReportRequirementsForTest,
            clerify_max_turns=10,
            model="gpt-4o-mini"
        )
        
        assert agent.name == "test_clarifier"
        assert agent.store_result_key == "test_clarifier_result"
        assert agent.conversation_key == "test_clarifier_conversation"
        assert agent.pipeline.clerify_max_turns == 10

    def test_clarify_agent_custom_keys(self):
        """
        Test ClarifyAgent with custom storage keys
        カスタム保存キーでのClarifyAgentテスト
        """
        # English: Test with custom keys
        # 日本語: カスタムキーでのテスト
        agent = ClarifyAgent(
            name="custom_clarifier",
            generation_instructions="Test instructions",
            store_result_key="custom_result",
            conversation_key="custom_conversation"
        )
        
        assert agent.store_result_key == "custom_result"
        assert agent.conversation_key == "custom_conversation"

    @pytest.mark.asyncio
    async def test_clarify_agent_run_with_no_input(self):
        """
        Test ClarifyAgent execution with no input
        入力なしでのClarifyAgent実行テスト
        """
        # English: Create agent and context
        # 日本語: エージェントとコンテキストを作成
        agent = ClarifyAgent(
            name="no_input_clarifier",
            generation_instructions="Test instructions",
            model="gpt-4o-mini"
        )
        
        ctx = Context()
        
        # English: Run with no input
        # 日本語: 入力なしで実行
        result_ctx = await agent.run(None, ctx)
        
        # English: Verify result
        # 日本語: 結果を検証
        assert "no_input_clarifier_result" in result_ctx.shared_state
        result = result_ctx.shared_state["no_input_clarifier_result"]
        assert isinstance(result, ClarificationResult)
        assert not result.is_complete
        assert result.data is None

    @pytest.mark.asyncio
    async def test_clarify_agent_run_with_mock_pipeline(self):
        """
        Test ClarifyAgent execution with mocked pipeline
        モックパイプラインでのClarifyAgent実行テスト
        """
        # English: Create agent
        # 日本語: エージェントを作成
        agent = ClarifyAgent(
            name="mock_clarifier",
            generation_instructions="Test instructions",
            output_data=ReportRequirementsForTest,
            model="gpt-4o-mini"
        )
        
        # English: Mock pipeline methods
        # 日本語: パイプラインメソッドをモック
        mock_question = ClarificationQuestion(
            question="What event are you reporting on?",
            turn=1,
            remaining_turns=9
        )
        
        with patch.object(agent.pipeline, 'run') as mock_run, \
             patch.object(type(agent.pipeline), 'is_complete', new_callable=lambda: property(lambda self: False)), \
             patch.object(type(agent.pipeline), 'current_turn', new_callable=lambda: property(lambda self: 1)), \
             patch.object(type(agent.pipeline), 'remaining_turns', new_callable=lambda: property(lambda self: 9)), \
             patch.object(type(agent.pipeline), 'conversation_history', new_callable=lambda: property(lambda self: [])):
            
            mock_run.return_value = mock_question
            
            ctx = Context()
            result_ctx = await agent.run("I want to write a report", ctx)
            
            # English: Verify result
            # 日本語: 結果を検証
            assert "mock_clarifier_result" in result_ctx.shared_state
            result = result_ctx.shared_state["mock_clarifier_result"]
            assert isinstance(result, ClarificationResult)
            assert not result.is_complete
            assert result.data == mock_question

    @pytest.mark.asyncio
    async def test_clarify_agent_completion(self):
        """
        Test ClarifyAgent when clarification is complete
        明確化完了時のClarifyAgentテスト
        """
        # English: Create agent
        # 日本語: エージェントを作成
        agent = ClarifyAgent(
            name="complete_clarifier",
            generation_instructions="Test instructions",
            next_step="next_step",
            model="gpt-4o-mini"
        )
        
        # English: Mock completed clarification
        # 日本語: 完了した明確化をモック
        completed_data = ReportRequirementsForTest(
            event="Test Event",
            date="2024-01-01",
            place="Tokyo",
            topics=["AI", "ML"],
            interested="Innovation",
            expression="Great experience"
        )
        
        with patch.object(agent.pipeline, 'run') as mock_run, \
             patch.object(type(agent.pipeline), 'is_complete', new_callable=lambda: property(lambda self: True)), \
             patch.object(type(agent.pipeline), 'current_turn', new_callable=lambda: property(lambda self: 3)), \
             patch.object(type(agent.pipeline), 'remaining_turns', new_callable=lambda: property(lambda self: 7)), \
             patch.object(type(agent.pipeline), 'conversation_history', new_callable=lambda: property(lambda self: [])):
            
            mock_run.return_value = completed_data
            
            ctx = Context()
            result_ctx = await agent.run("Final response", ctx)
            
            # English: Verify completion
            # 日本語: 完了を検証
            assert "complete_clarifier_result" in result_ctx.shared_state
            result = result_ctx.shared_state["complete_clarifier_result"]
            assert result == completed_data
            assert result_ctx.next_label == "next_step"

    @pytest.mark.asyncio
    async def test_clarify_agent_error_handling(self):
        """
        Test ClarifyAgent error handling
        ClarifyAgentエラーハンドリングテスト
        """
        # English: Create agent
        # 日本語: エージェントを作成
        agent = ClarifyAgent(
            name="error_clarifier",
            generation_instructions="Test instructions",
            model="gpt-4o-mini"
        )
        
        # English: Mock pipeline to raise exception
        # 日本語: パイプラインが例外を発生させるようにモック
        with patch.object(agent.pipeline, 'run', side_effect=Exception("Test error")):
            ctx = Context()
            result_ctx = await agent.run("Test input", ctx)
            
            # English: Verify error handling
            # 日本語: エラーハンドリングを検証
            assert "error_clarifier_result" in result_ctx.shared_state
            result = result_ctx.shared_state["error_clarifier_result"]
            assert isinstance(result, ClarificationResult)
            assert not result.is_complete
            assert result.data is None

    def test_clarify_agent_properties(self):
        """
        Test ClarifyAgent properties
        ClarifyAgentプロパティテスト
        """
        # English: Create agent
        # 日本語: エージェントを作成
        agent = ClarifyAgent(
            name="property_clarifier",
            generation_instructions="Test instructions",
            clerify_max_turns=15,
            model="gpt-4o-mini"
        )
        
        # English: Mock pipeline properties
        # 日本語: パイプラインプロパティをモック
        with patch.object(type(agent.pipeline), 'current_turn', new_callable=lambda: property(lambda self: 5)), \
             patch.object(type(agent.pipeline), 'remaining_turns', new_callable=lambda: property(lambda self: 10)), \
             patch.object(type(agent.pipeline), 'is_complete', new_callable=lambda: property(lambda self: False)):
            
            assert agent.current_turn == 5
            assert agent.remaining_turns == 10
            assert not agent.is_clarification_complete()

    def test_clarify_agent_history_methods(self):
        """
        Test ClarifyAgent history methods
        ClarifyAgent履歴メソッドテスト
        """
        # English: Create agent
        # 日本語: エージェントを作成
        agent = ClarifyAgent(
            name="history_clarifier",
            generation_instructions="Test instructions",
            model="gpt-4o-mini"
        )
        
        # English: Mock pipeline history methods
        # 日本語: パイプライン履歴メソッドをモック
        mock_conversation = [{"user": "test", "ai": "response"}]
        mock_session = ["session1", "session2"]
        
        with patch.object(type(agent.pipeline), 'conversation_history', new_callable=lambda: property(lambda self: mock_conversation)), \
             patch.object(agent.pipeline, 'get_session_history', return_value=mock_session):
            
            assert agent.get_conversation_history() == mock_conversation
            assert agent.get_session_history() == mock_session

    def test_clarify_agent_reset(self):
        """
        Test ClarifyAgent reset functionality
        ClarifyAgentリセット機能テスト
        """
        # English: Create agent
        # 日本語: エージェントを作成
        agent = ClarifyAgent(
            name="reset_clarifier",
            generation_instructions="Test instructions",
            model="gpt-4o-mini"
        )
        
        # English: Mock pipeline reset
        # 日本語: パイプラインリセットをモック
        with patch.object(agent.pipeline, 'reset_session') as mock_reset:
            agent.reset_clarification()
            mock_reset.assert_called_once()

    def test_clarify_agent_string_representation(self):
        """
        Test ClarifyAgent string representation
        ClarifyAgent文字列表現テスト
        """
        # English: Create agent
        # 日本語: エージェントを作成
        agent = ClarifyAgent(
            name="string_clarifier",
            generation_instructions="Test instructions",
            clerify_max_turns=20,
            model="gpt-4o-mini"
        )
        
        # English: Mock pipeline properties for string representation
        # 日本語: 文字列表現用のパイプラインプロパティをモック
        with patch.object(type(agent.pipeline), 'current_turn', new_callable=lambda: property(lambda self: 3)), \
             patch.object(agent.pipeline, 'clerify_max_turns', 20):
            
            str_repr = str(agent)
            assert "ClarifyAgent" in str_repr
            assert "string_clarifier" in str_repr
            assert "3/20" in str_repr
            
            # English: Test __repr__ method
            # 日本語: __repr__メソッドをテスト
            repr_str = repr(agent)
            assert repr_str == str_repr


class TestClarifyAgentFactories:
    """
    Test class for ClarifyAgent factory functions
    ClarifyAgentファクトリ関数のテストクラス
    """

    def test_create_simple_clarify_agent(self):
        """
        Test create_simple_clarify_agent factory function
        create_simple_clarify_agentファクトリ関数テスト
        """
        # English: Create agent using factory
        # 日本語: ファクトリを使用してエージェントを作成
        agent = create_simple_clarify_agent(
            name="simple_clarifier",
            instructions="Simple test instructions",
            output_data=ReportRequirementsForTest,
            max_turns=15,
            model="gpt-4o-mini",
            next_step="next_step"
        )
        
        assert isinstance(agent, ClarifyAgent)
        assert agent.name == "simple_clarifier"
        assert agent.next_step == "next_step"
        assert agent.pipeline.clerify_max_turns == 15

    def test_create_evaluated_clarify_agent(self):
        """
        Test create_evaluated_clarify_agent factory function
        create_evaluated_clarify_agentファクトリ関数テスト
        """
        # English: Create evaluated agent using factory
        # 日本語: ファクトリを使用して評価付きエージェントを作成
        agent = create_evaluated_clarify_agent(
            name="evaluated_clarifier",
            generation_instructions="Generation instructions",
            evaluation_instructions="Evaluation instructions",
            output_data=ReportRequirementsForTest,
            max_turns=25,
            model="gpt-4o-mini",
            evaluation_model="gpt-4o",
            next_step="eval_next_step",
            threshold=90,
            retries=5
        )
        
        assert isinstance(agent, ClarifyAgent)
        assert agent.name == "evaluated_clarifier"
        assert agent.next_step == "eval_next_step"
        assert agent.pipeline.clerify_max_turns == 25
        assert agent.pipeline.threshold == 90
        assert agent.pipeline.retries == 5


class TestClarificationResult:
    """
    Test class for ClarificationResult
    ClarificationResultのテストクラス
    """

    def test_clarification_result_creation(self):
        """
        Test ClarificationResult creation
        ClarificationResult作成テスト
        """
        # English: Create completed result
        # 日本語: 完了結果を作成
        completed_result = ClarificationResult(
            is_complete=True,
            data="Clarified requirement",
            turn=5,
            remaining_turns=0
        )
        
        assert completed_result.is_complete
        assert completed_result.data == "Clarified requirement"
        assert completed_result.turn == 5
        assert completed_result.remaining_turns == 0

    def test_clarification_result_in_progress(self):
        """
        Test ClarificationResult for in-progress clarification
        進行中明確化のClarificationResultテスト
        """
        # English: Create in-progress result
        # 日本語: 進行中結果を作成
        question = ClarificationQuestion(
            question="What is the event date?",
            turn=2,
            remaining_turns=8
        )
        
        in_progress_result = ClarificationResult(
            is_complete=False,
            data=question,
            turn=2,
            remaining_turns=8
        )
        
        assert not in_progress_result.is_complete
        assert isinstance(in_progress_result.data, ClarificationQuestion)
        assert in_progress_result.turn == 2
        assert in_progress_result.remaining_turns == 8


class TestClarificationQuestion:
    """
    Test class for ClarificationQuestion
    ClarificationQuestionのテストクラス
    """

    def test_clarification_question_creation(self):
        """
        Test ClarificationQuestion creation
        ClarificationQuestion作成テスト
        """
        # English: Create clarification question
        # 日本語: 明確化質問を作成
        question = ClarificationQuestion(
            question="What is the event location?",
            turn=3,
            remaining_turns=7
        )
        
        assert question.question == "What is the event location?"
        assert question.turn == 3
        assert question.remaining_turns == 7

    def test_clarification_question_string_representation(self):
        """
        Test ClarificationQuestion string representation
        ClarificationQuestion文字列表現テスト
        """
        # English: Create question and test string representation
        # 日本語: 質問を作成して文字列表現をテスト
        question = ClarificationQuestion(
            question="イベントの場所はどこですか？",
            turn=2,
            remaining_turns=8
        )
        
        str_repr = str(question)
        assert "[ターン 2/10]" in str_repr
        assert "イベントの場所はどこですか？" in str_repr


if __name__ == "__main__":
    pytest.main([__file__])
