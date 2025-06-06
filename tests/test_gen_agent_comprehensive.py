"""
Comprehensive GenAgent tests migrated from pipeline_* test files
pipeline_*テストファイルから移行したGenAgentの包括的テスト

This test suite ensures GenAgent maintains all functionality from AgentPipeline.
このテストスイートは、GenAgentがAgentPipelineの全機能を維持することを確認します。
"""

import pytest
from pydantic import BaseModel
from dataclasses import dataclass
from refinire import AgentPipeline, GenAgent, Flow, EvaluationResult

class DummyAgent:
    """
    Dummy Agent class for testing
    テスト用のダミーAgentクラス
    """
    def __init__(self, name, model=None, tools=None, instructions=None, 
                 input_guardrails=None, output_guardrails=None):
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
                final_output = '{"score": 90, "comment": ["good"]}'
            return Result()

@pytest.fixture(autouse=True)
def patch_agent_and_runner(monkeypatch):
    """
    Patch Agent and Runner for testing
    テスト用のAgentとRunnerをパッチ
    """
    monkeypatch.setattr("agents_sdk_models.pipeline.Agent", DummyAgent)
    monkeypatch.setattr("agents_sdk_models.pipeline.Runner", lambda: DummyRunner())

class TestGenAgentGuardrails:
    """
    Tests for guardrail functionality
    ガードレール機能のテスト
    """

    def test_guardrails_assignment(self):
        """
        Test that guardrails are properly assigned to agents
        ガードレールがエージェントに適切に割り当てられることをテスト
        """
        input_guardrails = ['input_guard1']
        output_guardrails = ['output_guard1']

        # AgentPipeline version
        pipeline = AgentPipeline(
            name="guard_test",
            generation_instructions="Generate content",
            evaluation_instructions="Evaluate content",
            input_guardrails=input_guardrails,
            output_guardrails=output_guardrails
        )
        
        assert pipeline.gen_agent.input_guardrails == input_guardrails
        assert pipeline.eval_agent.output_guardrails == output_guardrails

        # GenAgent version
        gen_agent = GenAgent(
            name="guard_test_gen",
            generation_instructions="Generate content",
            evaluation_instructions="Evaluate content",
            input_guardrails=input_guardrails,
            output_guardrails=output_guardrails,
            store_result_key="guard_result"
        )
        
        assert gen_agent.pipeline.gen_agent.input_guardrails == input_guardrails
        assert gen_agent.pipeline.eval_agent.output_guardrails == output_guardrails

class TestGenAgentPrompts:
    """
    Tests for prompt building functionality
    プロンプト構築機能のテスト
    """

    def test_build_generation_prompt_empty(self):
        """
        Test generation prompt building with empty history
        履歴が空の場合の生成プロンプト構築をテスト
        """
        # AgentPipeline version
        pipeline = AgentPipeline(
            name="prompt_test",
            generation_instructions="",
            evaluation_instructions=None
        )
        pipeline.session_history = []
        pipeline._pipeline_history = []
        
        result = pipeline._build_generation_prompt("input1")
        assert result == "UserInput: input1"

        # GenAgent version
        gen_agent = GenAgent(
            name="prompt_test_gen",
            generation_instructions="",
            store_result_key="prompt_result"
        )
        
        gen_agent.pipeline.session_history = []
        gen_agent.pipeline._pipeline_history = []
        
        gen_result = gen_agent.pipeline._build_generation_prompt("input1")
        assert gen_result == "UserInput: input1"

    def test_build_evaluation_prompt(self):
        """
        Test evaluation prompt building
        評価プロンプト構築をテスト
        """
        eval_instructions = "評価指示テキスト"
        
        # AgentPipeline version
        pipeline = AgentPipeline(
            name="eval_prompt_test",
            generation_instructions="",
            evaluation_instructions=eval_instructions
        )
        
        result = pipeline._build_evaluation_prompt("user_input", "generated_output")
        assert result.startswith(eval_instructions)
        assert "上記を JSON で必ず次の形式にしてください" in result

        # GenAgent version
        gen_agent = GenAgent(
            name="eval_prompt_test_gen",
            generation_instructions="",
            evaluation_instructions=eval_instructions,
            store_result_key="eval_prompt_result"
        )
        
        gen_result = gen_agent.pipeline._build_evaluation_prompt("user_input", "generated_output")
        assert gen_result.startswith(eval_instructions)
        assert "上記を JSON で必ず次の形式にしてください" in gen_result

class TestGenAgentUtils:
    """
    Tests for utility functions like JSON extraction and output coercion
    JSON抽出や出力強制などのユーティリティ関数のテスト
    """

    def test_extract_json_success(self):
        """
        Test successful JSON extraction
        JSON抽出の成功をテスト
        """
        text = 'prefix {"score":10, "comment":["ok"]} suffix'
        data = AgentPipeline._extract_json(text)
        assert data == {"score": 10, "comment": ["ok"]}
        
        gen_agent = GenAgent(
            name="json_test",
            generation_instructions="Test",
            store_result_key="json_result"
        )
        
        gen_data = gen_agent.pipeline._extract_json(text)
        assert gen_data == {"score": 10, "comment": ["ok"]}

    def test_extract_json_fail(self):
        """
        Test JSON extraction failure
        JSON抽出の失敗をテスト
        """
        with pytest.raises(ValueError):
            AgentPipeline._extract_json("no json here")
        
        gen_agent = GenAgent(
            name="json_fail_test",
            generation_instructions="Test",
            store_result_key="json_fail_result"
        )
        
        with pytest.raises(ValueError):
            gen_agent.pipeline._extract_json("no json here")

    def test_coerce_output_plain(self):
        """
        Test plain text output coercion
        プレーンテキスト出力強制をテスト
        """
        # AgentPipeline version
        pipeline = AgentPipeline(
            name="coerce_test",
            generation_instructions="",
            evaluation_instructions=None
        )
        
        assert pipeline._coerce_output("abc") == "abc"

        # GenAgent version
        gen_agent = GenAgent(
            name="coerce_test_gen",
            generation_instructions="",
            store_result_key="coerce_result"
        )
        
        assert gen_agent.pipeline._coerce_output("abc") == "abc"

    def test_coerce_output_pydantic(self):
        """
        Test Pydantic model output coercion
        Pydanticモデル出力強制をテスト
        """
        class TestModel(BaseModel):
            x: int

        pipeline = AgentPipeline(
            name="pydantic_test",
            generation_instructions="",
            evaluation_instructions=None,
            output_model=TestModel
        )
        
        result = pipeline._coerce_output('{"x":123}')
        assert isinstance(result, TestModel)
        assert result.x == 123

        gen_agent = GenAgent(
            name="pydantic_test_gen",
            generation_instructions="",
            output_model=TestModel,
            store_result_key="pydantic_result"
        )
        
        gen_result = gen_agent.pipeline._coerce_output('{"x":123}')
        assert isinstance(gen_result, TestModel)
        assert gen_result.x == 123

    def test_coerce_output_dataclass(self):
        """
        Test dataclass output coercion
        データクラス出力強制をテスト
        """
        @dataclass
        class TestDataClass:
            a: int

        pipeline = AgentPipeline(
            name="dataclass_test",
            generation_instructions="",
            evaluation_instructions=None,
            output_model=TestDataClass
        )
        
        result = pipeline._coerce_output('{"a":456}')
        assert isinstance(result, TestDataClass)
        assert result.a == 456

        gen_agent = GenAgent(
            name="dataclass_test_gen",
            generation_instructions="",
            output_model=TestDataClass,
            store_result_key="dataclass_result"
        )
        
        gen_result = gen_agent.pipeline._coerce_output('{"a":456}')
        assert isinstance(gen_result, TestDataClass)
        assert gen_result.a == 456

class TestGenAgentCoverage:
    """
    Additional tests to ensure complete GenAgent coverage
    GenAgentの完全なカバレッジを確保するための追加テスト
    """

    def test_genagent_string_representation(self):
        """
        Test GenAgent string representation
        GenAgentの文字列表現をテスト
        """
        gen_agent = GenAgent(
            name="string_test",
            generation_instructions="Test instructions",
            model="test-model",
            store_result_key="string_result"
        )
        
        str_repr = str(gen_agent)
        assert "string_test" in str_repr
        assert "test-model" in str_repr

    def test_genagent_history_management(self):
        """
        Test GenAgent history management methods
        GenAgentの履歴管理メソッドをテスト
        """
        gen_agent = GenAgent(
            name="history_mgmt_test",
            generation_instructions="Test instructions",
            history_size=2,
            store_result_key="history_mgmt_result"
        )
        
        # Add some history
        gen_agent.pipeline._pipeline_history = [
            {"input": "test1", "output": "response1"},
            {"input": "test2", "output": "response2"}
        ]
        gen_agent.pipeline.session_history = ["session1", "session2"]
        
        # Test get_pipeline_history
        pipeline_history = gen_agent.get_pipeline_history()
        assert len(pipeline_history) == 2
        assert pipeline_history[0]["input"] == "test1"
        
        # Test get_session_history
        session_history = gen_agent.get_session_history()
        assert session_history == ["session1", "session2"]
        
        # Test clear_history
        gen_agent.clear_history()
        assert len(gen_agent.get_pipeline_history()) == 0
        assert len(gen_agent.get_session_history()) == 0

    def test_genagent_instructions_update(self):
        """
        Test GenAgent instruction updating
        GenAgentの指示更新をテスト
        """
        gen_agent = GenAgent(
            name="update_test",
            generation_instructions="Original generation instructions",
            evaluation_instructions="Original evaluation instructions",
            store_result_key="update_result"
        )
        
        # Update generation instructions
        new_gen_instructions = "Updated generation instructions"
        gen_agent.update_instructions(generation_instructions=new_gen_instructions)
        assert gen_agent.pipeline.generation_instructions == new_gen_instructions
        assert gen_agent.pipeline.gen_agent.instructions == new_gen_instructions
        
        # Update evaluation instructions
        new_eval_instructions = "Updated evaluation instructions"
        gen_agent.update_instructions(evaluation_instructions=new_eval_instructions)
        assert gen_agent.pipeline.evaluation_instructions == new_eval_instructions
        if gen_agent.pipeline.eval_agent:
            assert gen_agent.pipeline.eval_agent.instructions == new_eval_instructions

    def test_genagent_threshold_setting(self):
        """
        Test GenAgent threshold setting
        GenAgentの閾値設定をテスト
        """
        gen_agent = GenAgent(
            name="threshold_test",
            generation_instructions="Test instructions",
            threshold=80,
            store_result_key="threshold_result"
        )
        
        # Test valid threshold
        gen_agent.set_threshold(90)
        assert gen_agent.pipeline.threshold == 90
        
        # Test invalid threshold
        with pytest.raises(ValueError):
            gen_agent.set_threshold(150)  # Over 100
        
        with pytest.raises(ValueError):
            gen_agent.set_threshold(-10)  # Under 0

if __name__ == "__main__":
    pytest.main([__file__]) 
