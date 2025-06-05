"""
Tests for ClearifyAgent
ClearifyAgentのテスト
"""

import pytest
import asyncio
from typing import List
from unittest.mock import patch, MagicMock
from pydantic import BaseModel

from agents_sdk_models import (
    ClearifyAgent, Context, ClarificationResult, 
    create_simple_clearify_agent, create_evaluated_clearify_agent
)
from agents_sdk_models.clearify_agent import ClarificationQuestion


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


class TestClearifyAgent:
    """
    Test class for ClearifyAgent
    ClearifyAgentのテストクラス
    """

    def test_clearify_agent_initialization(self):
        """
        Test ClearifyAgent initialization
        ClearifyAgentの初期化テスト
        """
        # English: Test basic initialization
        # 日本語: 基本初期化テスト
        agent = ClearifyAgent(
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

    def test_clearify_agent_custom_keys(self):
        """
        Test ClearifyAgent with custom storage keys
        カスタム保存キーでのClearifyAgentテスト
        """
        # English: Test with custom keys
        # 日本語: カスタムキーでのテスト
        agent = ClearifyAgent(
            name="custom_clarifier",
            generation_instructions="Test instructions",
            store_result_key="custom_result",
            conversation_key="custom_conversation"
        )
        
        assert agent.store_result_key == "custom_result"
        assert agent.conversation_key == "custom_conversation"

    @pytest.mark.asyncio
    async def test_clearify_agent_run_with_no_input(self):
        """
        Test ClearifyAgent execution with no input
        入力なしでのClearifyAgent実行テスト
        """
        # English: Create agent and context
        # 日本語: エージェントとコンテキストを作成
        agent = ClearifyAgent(
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
    async def test_clearify_agent_run_with_mock_pipeline(self):
        """
        Test ClearifyAgent execution with mocked pipeline
        モックパイプラインでのClearifyAgent実行テスト
        """
        # English: Create agent
        # 日本語: エージェントを作成
        agent = ClearifyAgent(
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
    async def test_clearify_agent_completion(self):
        """
        Test ClearifyAgent when clarification is complete
        明確化完了時のClearifyAgentテスト
        """
        # English: Create agent
        # 日本語: エージェントを作成
        agent = ClearifyAgent(
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
    async def test_clearify_agent_error_handling(self):
        """
        Test ClearifyAgent error handling
        ClearifyAgentエラーハンドリングテスト
        """
        # English: Create agent
        # 日本語: エージェントを作成
        agent = ClearifyAgent(
            name="error_clarifier",
            generation_instructions="Test instructions",
            model="gpt-4o-mini"
        )
        
        # English: Mock pipeline to raise exception
        # 日本語: 例外を発生させるためにパイプラインをモック
        with patch.object(agent.pipeline, 'run') as mock_run:
            mock_run.side_effect = Exception("Test error")
            
            ctx = Context()
            result_ctx = await agent.run("Test input", ctx)
            
            # English: Verify error handling
            # 日本語: エラーハンドリングを検証
            assert "error_clarifier_result" in result_ctx.shared_state
            result = result_ctx.shared_state["error_clarifier_result"]
            assert isinstance(result, ClarificationResult)
            assert not result.is_complete
            assert result.data is None

    def test_clearify_agent_properties(self):
        """
        Test ClearifyAgent properties
        ClearifyAgentプロパティテスト
        """
        # English: Create agent
        # 日本語: エージェントを作成
        agent = ClearifyAgent(
            name="prop_clarifier",
            generation_instructions="Test instructions",
            clerify_max_turns=15
        )
        
        # English: Mock pipeline properties
        # 日本語: パイプラインプロパティをモック
        with patch.object(type(agent.pipeline), 'current_turn', new_callable=lambda: property(lambda self: 5)), \
             patch.object(type(agent.pipeline), 'remaining_turns', new_callable=lambda: property(lambda self: 10)), \
             patch.object(type(agent.pipeline), 'is_complete', new_callable=lambda: property(lambda self: False)):
            
            assert agent.current_turn == 5
            assert agent.remaining_turns == 10
            assert not agent.is_clarification_complete()

    def test_clearify_agent_history_methods(self):
        """
        Test ClearifyAgent history methods
        ClearifyAgent履歴メソッドテスト
        """
        # English: Create agent
        # 日本語: エージェントを作成
        agent = ClearifyAgent(
            name="history_clarifier",
            generation_instructions="Test instructions"
        )
        
        # English: Mock history data
        # 日本語: 履歴データをモック
        mock_conversation = [{"user_input": "test", "ai_response": "response"}]
        mock_session = ["session1", "session2"]
        
        with patch.object(type(agent.pipeline), 'conversation_history', new_callable=lambda: property(lambda self: mock_conversation)), \
             patch.object(agent.pipeline, 'get_session_history', return_value=mock_session):
            
            assert agent.get_conversation_history() == mock_conversation
            assert agent.get_session_history() == mock_session

    def test_clearify_agent_reset(self):
        """
        Test ClearifyAgent reset functionality
        ClearifyAgentリセット機能テスト
        """
        # English: Create agent
        # 日本語: エージェントを作成
        agent = ClearifyAgent(
            name="reset_clarifier",
            generation_instructions="Test instructions"
        )
        
        # English: Mock reset method
        # 日本語: リセットメソッドをモック
        with patch.object(agent.pipeline, 'reset_session') as mock_reset:
            agent.reset_clarification()
            mock_reset.assert_called_once()

    def test_clearify_agent_string_representation(self):
        """
        Test ClearifyAgent string representation
        ClearifyAgent文字列表現テスト
        """
        # English: Create agent
        # 日本語: エージェントを作成
        agent = ClearifyAgent(
            name="string_clarifier",
            generation_instructions="Test instructions",
            clerify_max_turns=20
        )
        
        # English: Mock properties for string representation
        # 日本語: 文字列表現用プロパティをモック
        with patch.object(type(agent.pipeline), 'current_turn', new_callable=lambda: property(lambda self: 3)), \
             patch.object(agent.pipeline, 'clerify_max_turns', 20):
            
            expected = "ClearifyAgent(name=string_clarifier, turns=3/20)"
            assert str(agent) == expected
            assert repr(agent) == expected


class TestClearifyAgentFactories:
    """
    Test class for ClearifyAgent factory functions
    ClearifyAgentファクトリ関数のテストクラス
    """

    def test_create_simple_clearify_agent(self):
        """
        Test create_simple_clearify_agent factory function
        create_simple_clearify_agentファクトリ関数テスト
        """
        # English: Create simple agent
        # 日本語: シンプルエージェントを作成
        agent = create_simple_clearify_agent(
            name="simple_test",
            instructions="Simple instructions",
            output_data=ReportRequirementsForTest,
            max_turns=25,
            model="gpt-4o",
            next_step="next"
        )
        
        assert isinstance(agent, ClearifyAgent)
        assert agent.name == "simple_test"
        assert agent.pipeline.clerify_max_turns == 25
        assert agent.next_step == "next"

    def test_create_evaluated_clearify_agent(self):
        """
        Test create_evaluated_clearify_agent factory function
        create_evaluated_clearify_agentファクトリ関数テスト
        """
        # English: Create evaluated agent
        # 日本語: 評価付きエージェントを作成
        agent = create_evaluated_clearify_agent(
            name="evaluated_test",
            generation_instructions="Generation instructions",
            evaluation_instructions="Evaluation instructions",
            output_data=ReportRequirementsForTest,
            max_turns=30,
            model="gpt-4o",
            evaluation_model="gpt-4o-mini",
            next_step="next",
            threshold=90,
            retries=5
        )
        
        assert isinstance(agent, ClearifyAgent)
        assert agent.name == "evaluated_test"
        assert agent.pipeline.clerify_max_turns == 30
        assert agent.pipeline.threshold == 90
        assert agent.pipeline.retries == 5
        assert agent.next_step == "next"


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
        # English: Create result with completion
        # 日本語: 完了状態で結果を作成
        complete_result = ClarificationResult(
            is_complete=True,
            data="Completed data",
            turn=5,
            remaining_turns=0
        )
        
        assert complete_result.is_complete
        assert complete_result.data == "Completed data"
        assert complete_result.turn == 5
        assert complete_result.remaining_turns == 0

    def test_clarification_result_in_progress(self):
        """
        Test ClarificationResult for in-progress clarification
        進行中明確化用ClarificationResultテスト
        """
        # English: Create result for in-progress clarification
        # 日本語: 進行中明確化用結果を作成
        progress_result = ClarificationResult(
            is_complete=False,
            data=ClarificationQuestion("What is your goal?", 2, 8),
            turn=2,
            remaining_turns=8
        )
        
        assert not progress_result.is_complete
        assert isinstance(progress_result.data, ClarificationQuestion)
        assert progress_result.turn == 2
        assert progress_result.remaining_turns == 8


if __name__ == "__main__":
    pytest.main([__file__])