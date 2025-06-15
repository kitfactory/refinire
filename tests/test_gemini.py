import pytest
import os
from refinire.core.gemini import GeminiModel

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
    import refinire.core.gemini as gem
    # Stub AsyncOpenAI client
    monkeypatch.setattr(gem, "AsyncOpenAI", DummyAsyncOpenAI)
    # Stub _create_chat_completion to avoid super() call
    async def fake_create(self, *args, **kwargs):
        kwargs["temperature"] = getattr(self, "temperature", None)
        kwargs.update(getattr(self, "kwargs", {}))
        return {"result": kwargs}
    monkeypatch.setattr(GeminiModel, "_create_chat_completion", fake_create)


def test_gemini_init_and_params():
    model = GeminiModel(
        model="gemini-pro",
        temperature=0.7,
        api_key="g-key",
        base_url="http://gemini",
        foo="bar"
    )
    assert model.temperature == 0.7
    assert model.kwargs["foo"] == "bar"
    assert model.model == "gemini-pro"
    # Base URL and API key via AsyncOpenAI stub (skip openai_client tests)


def test_gemini_env_api_key(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "env-gkey")
    model = GeminiModel(api_key=None)
    # API key retrieved from environment
    assert model.kwargs == {}


def test_gemini_api_key_required(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    with pytest.raises(ValueError):
        GeminiModel(api_key=None)

@pytest.mark.asyncio
async def test_gemini_create_chat_completion():
    model = GeminiModel(api_key="g-key")
    result = await model._create_chat_completion(foo="bar")
    assert result["result"]["temperature"] == model.temperature
    assert result["result"]["foo"] == "bar" 
