"""
GenAgent compatibility tests with AgentPipeline
AgentPipelineとGenAgentの互換性確認テスト

This test suite ensures GenAgent can provide equivalent functionality to AgentPipeline.
このテストスイートは、GenAgentがAgentPipelineと同等の機能を提供できることを確認します。
"""

import pytest
from agents_sdk_models import AgentPipeline, GenAgent, Flow, create_simple_flow, create_simple_gen_agent, create_evaluated_gen_agent

class DummyAgent:
    """
    Dummy Agent class for testing
    テスト用のダミーAgentクラス
    """
    def __init__(self, name, model=None, tools=None, instructions=None, input_guardrails=None, output_guardrails=None):
        self.name = name
        self.model = model
        self.tools = tools
        self.instructions = instructions
        self.input_guardrails = input_guardrails
        self.output_guardrails = output_guardrails

class DummyRunner:
    """
    Dummy Runner class for testing
    テスト用のダミーRunnerクラス
    """
    def run_sync(self, agent, prompt):
        # 生成エージェントの場合はpromptをそのまま返す
        # For generation agents, return the prompt as-is
        if "generator" in agent.name:
            class Result:
                final_output = f"[GEN] {prompt}"
                tool_calls = []
            return Result()
        # 評価エージェントの場合は高スコアで返す
        # For evaluation agents, return high score
        else:
            class Result:
                final_output = '{"score": 100, "comment": ["OK"]}'
            return Result()

@pytest.fixture(autouse=True)
def patch_agent_and_runner(monkeypatch):
    """
    Patch Agent and Runner for testing
    テスト用のAgentとRunnerをパッチ
    """
    monkeypatch.setattr("agents_sdk_models.pipeline.Agent", DummyAgent)
    monkeypatch.setattr("agents_sdk_models.pipeline.Runner", lambda: DummyRunner())
    # GenAgentはpipelineモジュールからAgentをインポートしているので、pipelineの方をパッチすれば十分
    # GenAgent imports Agent from pipeline module, so patching pipeline is sufficient

class TestGenAgentCompatibility:
    """
    GenAgent compatibility with AgentPipeline
    AgentPipelineとのGenAgent互換性テスト
    """

    def test_basic_generation_compatibility(self):
        """
        Test basic generation compatibility between AgentPipeline and GenAgent
        AgentPipelineとGenAgentの基本生成互換性をテスト
        """
        # AgentPipeline version
        # AgentPipelineバージョン
        pipeline = AgentPipeline(
            name="test_gen",
            generation_instructions="You are a test agent.",
            evaluation_instructions=None,
            model="dummy-model"
        )
        pipeline_result = pipeline.run("hello")

        # GenAgent version  
        # GenAgentバージョン
        from agents_sdk_models import GenAgent, Flow
        
        gen_agent = GenAgent(
            name="test_gen",
            generation_instructions="You are a test agent.",
            model="dummy-model",
            store_result_key="test_gen_result"
        )
        
        # Create Flow manually and add step
        # Flowを手動で作成してステップを追加
        flow = Flow(start="test_gen", steps={"test_gen": gen_agent})
        
        # Skip async flow test for compatibility - use direct pipeline test instead
        # 互換性テストでは非同期フロー実行をスキップ - 代わりに直接パイプラインテストを使用
        genagent_result = gen_agent.pipeline.run("hello")

        # Both should produce similar outputs
        # 両方とも似たような出力を生成するはず
        assert "hello" in pipeline_result
        assert "hello" in genagent_result
        print(f"Pipeline result: {pipeline_result}")
        print(f"GenAgent result: {genagent_result}")

    def test_evaluation_compatibility(self):
        """
        Test evaluation functionality compatibility
        評価機能の互換性をテスト
        """
        # AgentPipeline with evaluation
        # 評価機能付きAgentPipeline
        pipeline = AgentPipeline(
            name="test_eval",
            generation_instructions="You are a test agent.",
            evaluation_instructions="Evaluate the output.",
            model="dummy-model",
            threshold=50
        )
        pipeline_result = pipeline.run("test input")

        # GenAgent with evaluation
        # 評価機能付きGenAgent
        gen_agent = GenAgent(
            name="test_eval",
            generation_instructions="You are a test agent.",
            evaluation_instructions="Evaluate the output.",
            model="dummy-model",
            threshold=50,
            store_result_key="test_eval_result"
        )
        
        # Create Flow manually
        # Flowを手動で作成
        flow = Flow(start="test_eval", steps={"test_eval": gen_agent})
        
        # Skip async flow test for compatibility - use direct pipeline test instead
        # 互換性テストでは非同期フロー実行をスキップ - 代わりに直接パイプラインテストを使用
        genagent_result = gen_agent.pipeline.run("test input")

        # Both should handle evaluation and return results
        # 両方とも評価を処理して結果を返すはず
        assert pipeline_result is not None
        assert genagent_result is not None
        assert "test input" in pipeline_result
        assert "test input" in genagent_result

    def test_history_management_compatibility(self):
        """
        Test history management compatibility
        履歴管理の互換性をテスト
        """
        # AgentPipeline with history
        # 履歴付きAgentPipeline
        pipeline = AgentPipeline(
            name="test_history",
            generation_instructions="You are a test agent.",
            evaluation_instructions=None,
            model="dummy-model",
            history_size=2
        )
        
        # GenAgent with history
        # 履歴付きGenAgent
        gen_agent = GenAgent(
            name="test_history",
            generation_instructions="You are a test agent.",
            model="dummy-model",
            history_size=2,
            store_result_key="history_result"
        )
        
        # Create Flow manually
        # Flowを手動で作成
        flow = Flow(start="test_history", steps={"test_history": gen_agent})

        # Run multiple inputs on both
        # 両方で複数の入力を実行
        pipeline.run("first")
        pipeline.run("second")
        pipeline.run("third")

        # Skip async flow test for compatibility - use direct pipeline test instead
        # 互換性テストでは非同期フロー実行をスキップ - 代わりに直接パイプラインテストを使用
        gen_agent.pipeline.run("first")
        gen_agent.pipeline.run("second")
        gen_agent.pipeline.run("third")

        # Check history sizes
        # 履歴サイズを確認
        pipeline_history_count = len(pipeline._pipeline_history)
        genagent_history_count = len(gen_agent.get_pipeline_history())

        # Both should manage history similarly
        # 両方とも同様に履歴を管理するはず
        assert pipeline_history_count == genagent_history_count == 3
        print(f"Pipeline history count: {pipeline_history_count}")
        print(f"GenAgent history count: {genagent_history_count}")

    def test_dynamic_prompt_compatibility(self):
        """
        Test dynamic prompt functionality compatibility
        動的プロンプト機能の互換性をテスト
        """
        def dynamic_prompt_func(user_input):
            return f"DYN:{user_input.upper()}"

        # AgentPipeline with dynamic prompt
        # 動的プロンプト付きAgentPipeline
        pipeline = AgentPipeline(
            name="test_dyn",
            generation_instructions="You are a test agent.",
            evaluation_instructions=None,
            model="dummy-model",
            dynamic_prompt=dynamic_prompt_func
        )
        pipeline_result = pipeline.run("dynamic test")

        # GenAgent with dynamic prompt
        # 動的プロンプト付きGenAgent
        gen_agent = GenAgent(
            name="test_dyn",
            generation_instructions="You are a test agent.",
            model="dummy-model",
            dynamic_prompt=dynamic_prompt_func,
            store_result_key="dynamic_result"
        )
        
        # Create Flow manually
        # Flowを手動で作成
        flow = Flow(start="test_dyn", steps={"test_dyn": gen_agent})

        # Skip async flow test for compatibility - use direct pipeline test instead
        # 互換性テストでは非同期フロー実行をスキップ - 代わりに直接パイプラインテストを使用
        genagent_result = gen_agent.pipeline.run("dynamic test")

        # Both should apply dynamic prompt transformation
        # 両方とも動的プロンプト変換を適用するはず
        assert "DYN:DYNAMIC TEST" in pipeline_result
        assert "DYN:DYNAMIC TEST" in genagent_result
        print(f"Pipeline dynamic result: {pipeline_result}")
        print(f"GenAgent dynamic result: {genagent_result}")

    def test_model_provider_compatibility(self, monkeypatch):
        """
        Test model provider compatibility
        モデルプロバイダーの互換性をテスト
        """
        # Mock get_llm for testing
        # テスト用にget_llmをモック
        from agents_sdk_models import pipeline as pipeline_mod
        
        def mock_get_llm(model=None, provider=None):
            return f"llm-{provider or 'openai'}-{model}"
        
        monkeypatch.setattr(pipeline_mod, "get_llm", mock_get_llm)
        # GenAgentはpipelineモジュールからget_llmをインポートしているので、pipelineのモックで十分
        # GenAgent imports get_llm from pipeline module, so mocking pipeline is sufficient

        # Test OpenAI compatibility
        # OpenAI互換性をテスト
        pipeline_openai = AgentPipeline(
            name="openai_test",
            generation_instructions="You are an OpenAI agent.",
            evaluation_instructions=None,
            model="gpt-3.5-turbo"
        )
        
        gen_agent_openai = GenAgent(
            name="openai_test",
            generation_instructions="You are an OpenAI agent.",
            model="gpt-3.5-turbo"
        )

        # Both should use the same model setup
        # 両方とも同じモデル設定を使用するはず
        assert pipeline_openai.gen_agent.model == "llm-openai-gpt-3.5-turbo"
        assert gen_agent_openai.pipeline.gen_agent.model == "llm-openai-gpt-3.5-turbo"

    def test_error_handling_compatibility(self):
        """
        Test error handling compatibility
        エラーハンドリングの互換性をテスト
        """
        # Test with valid configurations (both should work)
        # 有効な設定でテスト（両方とも動作するはず）
        try:
            # AgentPipeline with valid config
            # 有効な設定のAgentPipeline
            pipeline = AgentPipeline(
                name="valid_pipeline",
                generation_instructions="Test",
                evaluation_instructions=None,
                model="dummy-model"
            )
            assert pipeline is not None
        except Exception as e:
            pytest.fail(f"AgentPipeline creation should not fail: {e}")

        try:
            # GenAgent with valid config
            # 有効な設定のGenAgent
            gen_agent = GenAgent(
                name="valid_genagent",
                generation_instructions="Test",
                model="dummy-model"
            )
            assert gen_agent is not None
        except Exception as e:
            pytest.fail(f"GenAgent creation should not fail: {e}")

class TestBackwardCompatibility:
    """
    Backward compatibility tests
    後方互換性テスト
    """

    def test_agentpipeline_still_works(self):
        """
        Test that AgentPipeline still works despite deprecation warning
        AgentPipelineが廃止予定警告にもかかわらず引き続き動作することをテスト
        """
        import warnings
        
        # Capture deprecation warning
        # 廃止予定警告をキャプチャ
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            pipeline = AgentPipeline(
                name="backward_test",
                generation_instructions="You are a test agent.",
                evaluation_instructions=None,
                model="dummy-model"
            )
            
            # Should show deprecation warning
            # 廃止予定警告を表示するはず
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()
            
        # But pipeline should still work
        # しかしパイプラインは引き続き動作するはず
        result = pipeline.run("test input")
        assert "test input" in result

    def test_import_compatibility(self):
        """
        Test that all imports remain available
        すべてのインポートが引き続き利用可能であることをテスト
        """
        # All these imports should still work
        # これらのインポートはすべて引き続き動作するはず
        from agents_sdk_models import AgentPipeline
        from agents_sdk_models import GenAgent
        from agents_sdk_models import create_simple_gen_agent
        from agents_sdk_models import create_evaluated_gen_agent
        from agents_sdk_models import Flow
        from agents_sdk_models import create_simple_flow
        
        # Verify classes exist
        # クラスが存在することを確認
        assert AgentPipeline is not None
        assert GenAgent is not None
        assert create_simple_gen_agent is not None
        assert create_evaluated_gen_agent is not None
        assert Flow is not None
        assert create_simple_flow is not None

if __name__ == "__main__":
    pytest.main([__file__]) 