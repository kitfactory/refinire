import pytest
from agents_sdk_models import AgentPipeline

@pytest.fixture(autouse=True)
def patch_agent_and_runner(monkeypatch):
    # Dummy Agent to capture guardrails
    class DummyAgent:
        def __init__(self, name, model=None, tools=None, instructions=None,
                     input_guardrails=None, output_guardrails=None):
            self.name = name
            self.input_guardrails = input_guardrails
            self.output_guardrails = output_guardrails
    class DummyRunner:
        def run_sync(self, agent, prompt):
            return None
    monkeypatch.setattr("agents_sdk_models.pipeline.Agent", DummyAgent)
    monkeypatch.setattr("agents_sdk_models.pipeline.Runner", lambda: DummyRunner())

# Guardrails の設定が AgentPipeline に正しく渡されることをテスト
def test_guardrails_assignment():
    ig = ['guard1']
    og = ['guard2']
    pipeline = AgentPipeline(
        name="guard_test",
        generation_instructions="gen",
        evaluation_instructions="eval",
        input_guardrails=ig,
        output_guardrails=og
    )
    # generation agent に input_guardrails が設定されている
    assert pipeline.gen_agent.input_guardrails == ig
    # evaluation agent に output_guardrails が設定されている
    assert pipeline.eval_agent.output_guardrails == og 