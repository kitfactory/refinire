import pytest
from agents_sdk_models import AgentPipeline

# モック Agent と Runner を適用するフィクスチャ
@pytest.fixture(autouse=True)
def patch_agent_and_runner(monkeypatch):
    # Agent と Runner をダミーに置き換える
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
            return None
    monkeypatch.setattr("agents_sdk_models.pipeline.Agent", DummyAgent)
    monkeypatch.setattr("agents_sdk_models.pipeline.Runner", lambda: DummyRunner())

# _build_generation_prompt のテスト: 履歴なし
def test_build_generation_prompt_empty():
    pipeline = AgentPipeline(
        name="test",
        generation_instructions="",
        evaluation_instructions=None
    )
    pipeline.session_history = []
    pipeline._pipeline_history = []
    result = pipeline._build_generation_prompt("input1")
    assert result == "UserInput: input1"

# _build_generation_prompt のテスト: セッションと履歴あり
def test_build_generation_prompt_with_history_and_session():
    pipeline = AgentPipeline(
        name="test",
        generation_instructions="",
        evaluation_instructions=None,
        history_size=1,
        session_history=["S1","S2"]
    )
    pipeline._pipeline_history = [
        {"input": "i1", "output": "o1"},
        {"input": "i2", "output": "o2"}
    ]
    result = pipeline._build_generation_prompt("input3")
    expected = "S1\nS2\nUser: i2\nAI: o2\nUserInput: input3"
    assert result == expected

# _build_evaluation_prompt のテスト
def test_build_evaluation_prompt_basic():
    eval_instr = "評価指示テキスト"
    pipeline = AgentPipeline(
        name="test",
        generation_instructions="",
        evaluation_instructions=eval_instr
    )
    result = pipeline._build_evaluation_prompt("ui", "genout")
    # evaluation_instructions が先頭に含まれる
    assert result.startswith(eval_instr)
    # JSON 指示文が含まれる
    assert "上記を JSON で必ず次の形式にしてください" in result
    # ユーザー入力と生成結果のセクションが含まれる
    assert "----\nユーザー入力:\nui" in result
    assert "----\n生成結果:\ngenout" in result 