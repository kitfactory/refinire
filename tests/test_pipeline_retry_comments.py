import pytest
from refinire import AgentPipeline, EvaluationResult

# Fixture to patch Agent and Runner
@pytest.fixture(autouse=True)
def patch_agent_and_runner(monkeypatch):
    # Dummy Agent that stores name
    class DummyAgent:
        def __init__(self, name, model=None, tools=None, instructions=None,
                     input_guardrails=None, output_guardrails=None):
            self.name = name
    # Dummy Runner with generation prompt capture
    class DummyRunner:
        def __init__(self):
            self.generation_prompts = []
        def run_sync(self, agent, prompt):
            if "generator" in agent.name:
                # capture generation prompt
                self.generation_prompts.append(prompt)
                class Result:
                    final_output = "generated"
                    tool_calls = []
                return Result()
            else:
                # first evaluation returns low score, second returns high score
                class Result:
                    # Simulate evaluation JSON with importance levels
                    final_output = '{"score": 10, "comment": [' \
                                   '{"content":"crit","importance":"serious"},' \
                                   '{"content":"note","importance":"minor"}' \
                                   ']}'
                return Result()
    # Patch Agent and Runner
    monkeypatch.setattr("agents_sdk_models.pipeline.Agent", DummyAgent)
    monkeypatch.setattr("agents_sdk_models.pipeline.Runner", lambda: DummyRunner())

# Test retry includes only specified importance comments
def test_retry_includes_filtered_comments():
    # Set retries=1 to get one retry
    pipeline = AgentPipeline(
        name="retry", 
        generation_instructions="gen", 
        evaluation_instructions="eval",
        threshold=50, retries=1,
        retry_comment_importance=["serious"]
    )
    # Run pipeline: first attempt generation_prompts[0], then retry generation_prompts[1]
    result = pipeline.run("input")
    # Access DummyRunner instance
    runner = pipeline._runner
    # Should have exactly 2 generation prompts
    assert len(runner.generation_prompts) == 2
    # First prompt should not contain comment lines
    assert "(serious)" not in runner.generation_prompts[0]
    # Second prompt should include only the serious comment
    assert "(serious) crit" in runner.generation_prompts[1]
    # 'minor' comment should not appear
    assert "(minor) note" not in runner.generation_prompts[1] 
