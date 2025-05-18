import pytest
from agents_sdk_models import AgentPipeline, EvaluationResult

# モック Agent と Runner を適用するフィクスチャ
@pytest.fixture(autouse=True)
def patch_agent_and_runner(monkeypatch):
    # Dummy Agent returning only name and ignoring guardrails
    class DummyAgent:
        def __init__(self, name, model=None, tools=None, instructions=None,
                     input_guardrails=None, output_guardrails=None):
            self.name = name
    # Dummy Runner to simulate generation and low-score evaluation
    class DummyRunner:
        def run_sync(self, agent, prompt):
            if "generator" in agent.name:
                class Result:
                    final_output = "generated_output"
                    tool_calls = []
                return Result()
            else:
                class Result:
                    final_output = '{"score": 10, "comment": ["needs improvement"]}'
                return Result()
    monkeypatch.setattr("agents_sdk_models.pipeline.Agent", DummyAgent)
    monkeypatch.setattr("agents_sdk_models.pipeline.Runner", lambda: DummyRunner())

# improvements_callback が呼び出されることをテスト
def test_improvements_callback_invoked():
    calls = {}
    def improvement_callback(parsed_output, eval_result):
        calls['parsed'] = parsed_output
        calls['eval'] = eval_result

    pipeline = AgentPipeline(
        name="imp_test",
        generation_instructions="gen",
        evaluation_instructions="eval",
        threshold=50,
        retries=1,
        improvement_callback=improvement_callback
    )
    result = pipeline.run("input")
    assert result is None
    assert calls.get('parsed') == "generated_output"
    assert isinstance(calls.get('eval'), EvaluationResult)
    assert calls['eval'].score == 10
    assert calls['eval'].comment == ["needs improvement"] 