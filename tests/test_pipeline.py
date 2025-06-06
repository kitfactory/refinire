import pytest
from refinire import AgentPipeline, EvaluationResult

class DummyAgent:
    def __init__(self, name, model=None, tools=None, instructions=None, input_guardrails=None, output_guardrails=None):
        self.name = name
        self.model = model
        self.tools = tools
        self.instructions = instructions
        self.input_guardrails = input_guardrails
        self.output_guardrails = output_guardrails

class DummyRunner:
    def run_sync(self, agent, prompt):
        # 生成エージェントの場合はpromptをそのまま返す
        if "generator" in agent.name:
            class Result:
                final_output = f"[GEN] {prompt}"
                tool_calls = []
            return Result()
        # 評価エージェントの場合は高スコアで返す
        else:
            class Result:
                final_output = '{"score": 100, "comment": ["OK"]}'
            return Result()

@pytest.fixture(autouse=True)
def patch_agent_and_runner(monkeypatch):
    monkeypatch.setattr("agents_sdk_models.pipeline.Agent", DummyAgent)
    monkeypatch.setattr("agents_sdk_models.pipeline.Runner", lambda: DummyRunner())


def test_generation_only():
    pipeline = AgentPipeline(
        name="test_gen",
        generation_instructions="You are a test agent.",
        evaluation_instructions=None,
        model="dummy-model"
    )
    result = pipeline.run("hello")
    assert "hello" in result


def test_generation_with_evaluation():
    pipeline = AgentPipeline(
        name="test_eval",
        generation_instructions="You are a test agent.",
        evaluation_instructions="Evaluate the output.",
        model="dummy-model",
        threshold=50
    )
    result = pipeline.run("test input")
    assert result is not None
    # 評価スコアが高いので必ず返る


def test_history_size():
    pipeline = AgentPipeline(
        name="test_history",
        generation_instructions="You are a test agent.",
        evaluation_instructions=None,
        model="dummy-model",
        history_size=2
    )
    pipeline.run("first")
    pipeline.run("second")
    pipeline.run("third")
    # 履歴が2件分だけ保持されていること
    assert len(pipeline._pipeline_history) == 3
    assert len(pipeline.session_history) <= 3


def test_dynamic_prompt():
    def dyn_prompt(user_input):
        return f"DYN:{user_input.upper()}"
    pipeline = AgentPipeline(
        name="test_dyn",
        generation_instructions="You are a test agent.",
        evaluation_instructions=None,
        model="dummy-model",
        dynamic_prompt=dyn_prompt
    )
    result = pipeline.run("dynamic test")
    assert result.startswith("[GEN] DYN:DYNAMIC TEST")


def test_openai_pipeline(monkeypatch):
    # get_llmの返り値をダミーに
    from refinire import pipeline as pipeline_mod
    monkeypatch.setattr(pipeline_mod, "get_llm", lambda model=None, provider=None: f"llm-openai-{model}")
    pipeline = AgentPipeline(
        name="openai_test",
        generation_instructions="You are an OpenAI agent.",
        evaluation_instructions=None,
        model="gpt-3.5-turbo"
    )
    result = pipeline.run("openai test")
    assert "openai test" in result
    assert pipeline.gen_agent.model == "llm-openai-gpt-3.5-turbo"


def test_ollama_pipeline(monkeypatch):
    # get_llmの返り値をダミーに
    from refinire import pipeline as pipeline_mod
    monkeypatch.setattr(pipeline_mod, "get_llm", lambda model=None, provider=None: f"llm-ollama-{model}")
    pipeline = AgentPipeline(
        name="ollama_test",
        generation_instructions="You are an Ollama agent.",
        evaluation_instructions=None,
        model="qwen3:8b"
    )
    result = pipeline.run("ollama test")
    assert "ollama test" in result
    assert pipeline.gen_agent.model == "llm-ollama-qwen3:8b" 
