import pytest
from agents_sdk_models import AgentPipeline

# Test routing_func is applied to parsed output
def test_routing_func(monkeypatch):
    # Dummy result without tool_calls
    class DummyResult:
        final_output = "out"
        tool_calls = []
    class DummyRunner:
        def run_sync(self, agent, prompt):
            return DummyResult()
    # Stub Agent and Runner
    monkeypatch.setattr("agents_sdk_models.pipeline.Agent", lambda *args, **kwargs: None)
    monkeypatch.setattr("agents_sdk_models.pipeline.Runner", lambda: DummyRunner())
    # Create pipeline with routing_func
    pipeline = AgentPipeline(
        name="rout",
        generation_instructions="",
        evaluation_instructions=None,
        model=None,
        routing_func=lambda x: f"R:{x}"
    )
    result = pipeline.run("input")
    assert result == "R:out"

# Test generation_tools path: use tool call output
def test_generation_tools(monkeypatch):
    class DummyToolCall:
        def call(self):
            return "TOOL"
    class DummyResult:
        final_output = "ignored"
        tool_calls = [DummyToolCall()]
    class DummyRunner:
        def run_sync(self, agent, prompt):
            return DummyResult()
    monkeypatch.setattr("agents_sdk_models.pipeline.Agent", lambda *args, **kwargs: None)
    monkeypatch.setattr("agents_sdk_models.pipeline.Runner", lambda: DummyRunner())
    # Stub a dummy tool for generation_tools
    def dummy_tool(): pass
    pipeline = AgentPipeline(
        name="tool",
        generation_instructions="",
        evaluation_instructions=None,
        model=None,
        generation_tools=[dummy_tool]
    )
    result = pipeline.run("input")
    assert result == "TOOL"

# Test simple run without evaluation and without routing/tools
def test_run_simple(monkeypatch):
    class DummyResult:
        final_output = "hello"
        tool_calls = []
    class DummyRunner:
        def run_sync(self, agent, prompt):
            return DummyResult()
    monkeypatch.setattr("agents_sdk_models.pipeline.Agent", lambda *args, **kwargs: None)
    monkeypatch.setattr("agents_sdk_models.pipeline.Runner", lambda: DummyRunner())
    pipeline = AgentPipeline(
        name="simple",
        generation_instructions="",
        evaluation_instructions=None,
        model=None
    )
    assert pipeline.run("xyz") == "hello" 