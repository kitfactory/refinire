"""
Simple GenAgent compatibility tests without async
非同期処理を使わない簡単なGenAgent互換性テスト

This test suite provides basic compatibility verification without complex async operations.
このテストスイートは、複雑な非同期操作なしで基本的な互換性確認を提供します。
"""

import pytest
from refinire import AgentPipeline, GenAgent

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
        if "generator" in agent.name:
            class Result:
                final_output = "generated_output"
                tool_calls = []
            return Result()
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

class TestSimpleCompatibility:
    """
    Simple compatibility tests
    シンプルな互換性テスト
    """

    def test_agentpipeline_basic_creation(self):
        """
        Test AgentPipeline basic creation and properties
        AgentPipelineの基本作成とプロパティをテスト
        """
        pipeline = AgentPipeline(
            name="test_pipeline",
            generation_instructions="Test instructions",
            evaluation_instructions=None,
            model="dummy-model"
        )
        
        assert pipeline.name == "test_pipeline"
        assert pipeline.generation_instructions == "Test instructions"
        assert pipeline.model == "dummy-model"

    def test_genagent_basic_creation(self):
        """
        Test GenAgent basic creation and properties
        GenAgentの基本作成とプロパティをテスト
        """
        gen_agent = GenAgent(
            name="test_genagent",
            generation_instructions="Test instructions",
            model="dummy-model",
            store_result_key="test_result"
        )
        
        assert gen_agent.name == "test_genagent"
        assert gen_agent.pipeline.generation_instructions == "Test instructions"
        assert gen_agent.pipeline.model == "dummy-model"
        assert gen_agent.store_result_key == "test_result"

    def test_agentpipeline_run_basic(self):
        """
        Test AgentPipeline basic run functionality
        AgentPipelineの基本実行機能をテスト
        """
        pipeline = AgentPipeline(
            name="test_run",
            generation_instructions="Test instructions",
            evaluation_instructions=None,
            model="dummy-model"
        )
        
        result = pipeline.run("test input")
        assert result == "generated_output"

    def test_backward_compatibility_imports(self):
        """
        Test that all required imports work
        必要なimportが動作することをテスト
        """
        from refinire import AgentPipeline, GenAgent, Flow
        from refinire import create_simple_gen_agent, create_evaluated_gen_agent
        
        # All imports should work without error
        # 全てのimportがエラーなしで動作するはず
        assert AgentPipeline is not None
        assert GenAgent is not None
        assert Flow is not None
        assert create_simple_gen_agent is not None
        assert create_evaluated_gen_agent is not None

    def test_deprecation_warning_issued(self):
        """
        Test that AgentPipeline issues deprecation warning
        AgentPipelineがdeprecation warningを発行することをテスト
        """
        import warnings
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            pipeline = AgentPipeline(
                name="deprecated_test",
                generation_instructions="Test",
                evaluation_instructions=None,
                model="dummy-model"
            )
            
            # Should have captured at least one deprecation warning
            # 少なくとも1つのdeprecation warningがキャプチャされるはず
            deprecation_warnings = [warning for warning in w if issubclass(warning.category, DeprecationWarning)]
            assert len(deprecation_warnings) > 0
            
            # Check warning message content
            # 警告メッセージの内容を確認
            warning_message = str(deprecation_warnings[0].message)
            assert "AgentPipeline is deprecated" in warning_message
            assert "GenAgent" in warning_message

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
