import pytest
import asyncio
from unittest.mock import MagicMock, patch
from refinire import GenAgent, Context, create_simple_gen_agent, create_evaluated_gen_agent


# モック LLMPipeline を適用するフィクスチャ
@pytest.fixture(autouse=True)
def patch_llm_pipeline(monkeypatch):
    # LLMPipeline をダミーに置き換える
    class DummyLLMResult:
        def __init__(self, text, score=85.0):
            self.final_output = text
            self.evaluation_score = score
            self.raw_content = text
            self.structured_output = None
            self.evaluation_result = None
    
    class DummyLLMPipeline:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
        
        async def run_async(self, prompt, **kwargs):
            return DummyLLMResult(f"Generated response for: {prompt[:50]}...")
        
        def run(self, prompt, **kwargs):
            return DummyLLMResult(f"Generated response for: {prompt[:50]}...")
    
    monkeypatch.setattr("refinire.agents.pipeline.llm_pipeline.RefinireAgent", DummyLLMPipeline)


class TestGenAgent:
    """
    Test cases for GenAgent class
    GenAgentクラスのテストケース
    """

    def test_gen_agent_initialization(self):
        """
        Test GenAgent initialization
        GenAgentの初期化をテスト
        """
        gen_agent = GenAgent(
            name="test_gen_agent",
            generation_instructions="Generate helpful responses",
            evaluation_instructions="Evaluate response quality",
            model="gpt-4o-mini",
            next_step="next_step",
            threshold=85,
            max_retries=2
        )
        
        assert gen_agent.name == "test_gen_agent"
        assert gen_agent.next_step == "next_step"
        assert gen_agent.store_result_key == "test_gen_agent_result"
        assert gen_agent.llm_pipeline.generation_instructions == "Generate helpful responses"
        assert gen_agent.llm_pipeline.evaluation_instructions == "Evaluate response quality"
        assert gen_agent.llm_pipeline.threshold == 85
        assert gen_agent.llm_pipeline.max_retries == 2

    def test_gen_agent_custom_store_key(self):
        """
        Test GenAgent with custom store result key
        カスタム結果保存キーでのGenAgentをテスト
        """
        gen_agent = GenAgent(
            name="test_agent",
            generation_instructions="Test instructions",
            store_result_key="custom_result"
        )
        
        assert gen_agent.store_result_key == "custom_result"

    @pytest.mark.asyncio
    async def test_gen_agent_run_with_input(self):
        """
        Test GenAgent run method with user input
        ユーザー入力でのGenAgent実行メソッドをテスト
        """
        gen_agent = GenAgent(
            name="test_gen_agent",
            generation_instructions="Generate helpful responses",
            next_step="next_step"
        )
        
        ctx = Context()
        user_input = "Hello, how are you?"
        
        # モックパイプラインの結果を設定
        mock_result = type('LLMResult', (), {'content': "I'm doing well, thank you!", 'success': True})()
        with patch.object(gen_agent.llm_pipeline, 'run', return_value=mock_result) as mock_run:
            result_ctx = await gen_agent.run(user_input, ctx)
            
            # パイプラインが正しい入力で呼ばれたことを確認
            mock_run.assert_called_once_with(user_input)
            
            # コンテキストが正しく更新されたことを確認
            assert result_ctx.current_step == "test_gen_agent"
            assert result_ctx.next_label == "next_step"
            assert result_ctx.shared_state["test_gen_agent_result"] == "I'm doing well, thank you!"
            assert result_ctx.prev_outputs["test_gen_agent"] == "I'm doing well, thank you!"
            
            # メッセージが追加されたことを確認
            assert len(result_ctx.messages) > 0
            assert any("Pipeline executed successfully" in msg.content for msg in result_ctx.messages)

    @pytest.mark.asyncio
    async def test_gen_agent_run_without_input(self):
        """
        Test GenAgent run method without user input
        ユーザー入力なしでのGenAgent実行メソッドをテスト
        """
        gen_agent = GenAgent(
            name="test_gen_agent",
            generation_instructions="Generate helpful responses"
        )
        
        ctx = Context()
        # ユーザー入力なし
        
        result_ctx = await gen_agent.run(None, ctx)
        
        # 入力がない場合のメッセージが追加されたことを確認
        assert any("No input available" in msg.content for msg in result_ctx.messages)
        assert result_ctx.shared_state["test_gen_agent_result"] is None

    @pytest.mark.asyncio
    async def test_gen_agent_run_with_context_input(self):
        """
        Test GenAgent run method using context's last user input
        コンテキストの最後のユーザー入力を使用するGenAgent実行メソッドをテスト
        """
        gen_agent = GenAgent(
            name="test_gen_agent",
            generation_instructions="Generate helpful responses"
        )
        
        ctx = Context()
        ctx.add_user_message("Previous user input")
        
        mock_result = type('LLMResult', (), {'content': "Response", 'success': True})()
        with patch.object(gen_agent.llm_pipeline, 'run', return_value=mock_result) as mock_run:
            await gen_agent.run(None, ctx)
            
            # コンテキストの最後のユーザー入力が使用されたことを確認
            mock_run.assert_called_once_with("Previous user input")

    @pytest.mark.asyncio
    async def test_gen_agent_run_pipeline_failure(self):
        """
        Test GenAgent run method when pipeline returns None
        パイプラインがNoneを返す場合のGenAgent実行メソッドをテスト
        """
        gen_agent = GenAgent(
            name="test_gen_agent",
            generation_instructions="Generate helpful responses"
        )
        
        ctx = Context()
        user_input = "Test input"
        
        mock_result = type('LLMResult', (), {'content': None, 'success': False})()
        with patch.object(gen_agent.llm_pipeline, 'run', return_value=mock_result) as mock_run:
            result_ctx = await gen_agent.run(user_input, ctx)
            
            # 失敗メッセージが追加されたことを確認
            assert any("Pipeline execution failed" in msg.content for msg in result_ctx.messages)
            assert result_ctx.shared_state["test_gen_agent_result"] is None

    @pytest.mark.asyncio
    async def test_gen_agent_run_exception_handling(self):
        """
        Test GenAgent run method exception handling
        GenAgent実行メソッドの例外処理をテスト
        """
        gen_agent = GenAgent(
            name="test_gen_agent",
            generation_instructions="Generate helpful responses"
        )
        
        ctx = Context()
        user_input = "Test input"
        
        with patch.object(gen_agent.llm_pipeline, 'run', side_effect=Exception("Test error")):
            result_ctx = await gen_agent.run(user_input, ctx)
            
            # エラーメッセージが追加されたことを確認
            assert any("execution error" in msg.content for msg in result_ctx.messages)
            assert result_ctx.shared_state["test_gen_agent_result"] is None

    def test_gen_agent_get_pipeline_history(self):
        """
        Test getting pipeline history
        パイプライン履歴の取得をテスト
        """
        gen_agent = GenAgent(
            name="test_gen_agent",
            generation_instructions="Generate helpful responses"
        )
        
        # 履歴を追加
        with patch.object(gen_agent.llm_pipeline, 'get_history', return_value=[{"input": "test", "output": "response"}]):
            history = gen_agent.get_pipeline_history()
            assert len(history) == 1
            assert history[0]["input"] == "test"
            assert history[0]["output"] == "response"

    def test_gen_agent_get_session_history(self):
        """
        Test getting session history
        セッション履歴の取得をテスト
        """
        gen_agent = GenAgent(
            name="test_gen_agent",
            generation_instructions="Generate helpful responses",
            session_history=["Message 1", "Message 2"]
        )
        
        history = gen_agent.get_session_history()
        assert history == ["Message 1", "Message 2"]

    def test_gen_agent_update_instructions(self):
        """
        Test updating pipeline instructions
        パイプライン指示の更新をテスト
        """
        gen_agent = GenAgent(
            name="test_gen_agent",
            generation_instructions="Original generation instructions",
            evaluation_instructions="Original evaluation instructions"
        )
        
        # 指示を更新
        gen_agent.update_instructions(
            generation_instructions="New generation instructions",
            evaluation_instructions="New evaluation instructions"
        )
        
        assert gen_agent.llm_pipeline.generation_instructions == "New generation instructions"
        assert gen_agent.llm_pipeline.evaluation_instructions == "New evaluation instructions"

    def test_gen_agent_clear_history(self):
        """
        Test clearing history
        履歴のクリアをテスト
        """
        gen_agent = GenAgent(
            name="test_gen_agent",
            generation_instructions="Generate helpful responses",
            session_history=["Message 1"]
        )
        
        # 履歴をクリア機能をモック
        with patch.object(gen_agent.llm_pipeline, 'clear_history') as mock_clear:
            gen_agent.clear_history()
            mock_clear.assert_called_once()

    def test_gen_agent_set_threshold(self):
        """
        Test setting evaluation threshold
        評価閾値の設定をテスト
        """
        gen_agent = GenAgent(
            name="test_gen_agent",
            generation_instructions="Generate helpful responses",
            threshold=85
        )
        
        # 閾値を更新
        gen_agent.set_threshold(90)
        assert gen_agent.llm_pipeline.threshold == 90

    def test_gen_agent_str_representation(self):
        """
        Test string representation
        文字列表現をテスト
        """
        gen_agent = GenAgent(
            name="test_gen_agent",
            generation_instructions="Generate helpful responses",
            model="gpt-4o-mini"
        )
        
        str_repr = str(gen_agent)
        assert "GenAgent(test_gen_agent" in str_repr
        assert "model=gpt-4o-mini" in str_repr


class TestGenAgentUtilities:
    """
    Test cases for GenAgent utility functions
    GenAgentユーティリティ関数のテストケース
    """

    def test_create_simple_gen_agent(self):
        """
        Test create_simple_gen_agent utility function
        create_simple_gen_agentユーティリティ関数をテスト
        """
        gen_agent = create_simple_gen_agent(
            name="simple_agent",
            instructions="Simple instructions",
            model="gpt-4o-mini",
            next_step="next",
            threshold=80,
            retries=2
        )
        
        assert gen_agent.name == "simple_agent"
        assert gen_agent.next_step == "next"
        assert gen_agent.llm_pipeline.generation_instructions == "Simple instructions"
        assert gen_agent.llm_pipeline.evaluation_instructions is None
        assert gen_agent.llm_pipeline.model == "gpt-4o-mini"
        assert gen_agent.llm_pipeline.threshold == 80
        assert gen_agent.llm_pipeline.max_retries == 2

    def test_create_evaluated_gen_agent(self):
        """
        Test create_evaluated_gen_agent utility function
        create_evaluated_gen_agentユーティリティ関数をテスト
        """
        gen_agent = create_evaluated_gen_agent(
            name="eval_agent",
            generation_instructions="Generate content",
            evaluation_instructions="Evaluate content",
            model="gpt-4o",
            evaluation_model="gpt-4o-mini",
            next_step="next",
            threshold=90,
            retries=1
        )
        
        assert gen_agent.name == "eval_agent"
        assert gen_agent.next_step == "next"
        assert gen_agent.llm_pipeline.generation_instructions == "Generate content"
        assert gen_agent.llm_pipeline.evaluation_instructions == "Evaluate content"
        assert gen_agent.llm_pipeline.model == "gpt-4o"
        assert gen_agent.llm_pipeline.evaluation_model == "gpt-4o-mini"
        assert gen_agent.llm_pipeline.threshold == 90
        assert gen_agent.llm_pipeline.max_retries == 1
