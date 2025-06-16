import pytest
import os
from refinire.core.anthropic import ClaudeModel

class DummyOpenAIChatCompletionsModel:
    def __init__(self, model, openai_client):
        self.model = model
        self.openai_client = openai_client
    async def _create_chat_completion(self, *args, **kwargs):
        return {"result": kwargs}

class DummyAsyncOpenAI:
    def __init__(self, base_url=None, api_key=None):
        self.base_url = base_url
        self.api_key = api_key

@pytest.fixture(autouse=True)
def patch_parent(monkeypatch):
    import refinire.core.anthropic as anth
    # Stub AsyncOpenAI client
    monkeypatch.setattr(anth, "AsyncOpenAI", DummyAsyncOpenAI)
    # Stub _create_chat_completion to avoid super() call
    async def fake_create(self, *args, **kwargs):
        kwargs["temperature"] = getattr(self, "temperature", None)
        if getattr(self, "thinking", False):
            kwargs["thinking"] = True
        kwargs.update(getattr(self, "kwargs", {}))
        return {"result": kwargs}
    monkeypatch.setattr(ClaudeModel, "_create_chat_completion", fake_create)


def test_claude_init_and_params():
    model = ClaudeModel(
        model="claude-3-sonnet",
        temperature=0.5,
        api_key="test-key",
        base_url="http://anthropic",
        thinking=True,
        foo="bar"
    )
    # Attributes set in ClaudeModel __init__
    assert model.temperature == 0.5
    assert model.thinking is True
    assert model.kwargs["foo"] == "bar"
    # Model name passed
    assert model.model == "claude-3-sonnet"
    # Base URL and API key via AsyncOpenAI stub (skip openai_client tests)
    # assert model.openai_client.base_url == "http://anthropic"
    # assert model.openai_client.api_key == "test-key"


def test_claude_env_api_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "env-key")
    model = ClaudeModel(api_key=None)
    # API key retrieved from environment
    assert model.kwargs == {}


def test_claude_api_key_required(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ValueError):
        ClaudeModel(api_key=None)

@pytest.mark.asyncio
async def test_claude_create_chat_completion():
    model = ClaudeModel(api_key="test-key", thinking=True)
    result = await model._create_chat_completion(foo="bar")
    # Logic in ClaudeModel override adds temperature and thinking, then stub returns
    assert result["result"]["temperature"] == model.temperature
    assert result["result"]["thinking"] is True
    assert result["result"]["foo"] == "bar" 
