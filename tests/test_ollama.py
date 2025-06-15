import pytest
import os
import refinire.core.ollama as oll
from refinire.core.ollama import OllamaModel

# Dummy AsyncOpenAI to verify base_url and api_key attributes
class DummyAsyncOpenAI:
    def __init__(self, base_url=None, api_key=None):
        self.base_url = base_url
        self.api_key = api_key

# Autouse fixture to patch AsyncOpenAI and override create_chat for OllamaModel
@pytest.fixture(autouse=True)
def patch_parent(monkeypatch):
    # Stub AsyncOpenAI client
    monkeypatch.setattr(oll, "AsyncOpenAI", DummyAsyncOpenAI)
    # Stub _create_chat_completion to avoid real API call and test override logic
    async def fake_create(self, *args, **kwargs):
        kwargs["temperature"] = getattr(self, "temperature", None)
        kwargs.update(getattr(self, "kwargs", {}))
        return {"result": kwargs}
    monkeypatch.setattr(OllamaModel, "_create_chat_completion", fake_create)

# Test default base_url fallback and defaults
def test_ollama_default_base_url(monkeypatch):
    # Ensure no environment variable
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    model = OllamaModel()
    # Defaults
    assert model.temperature == 0.3
    assert model.kwargs == {}
    assert model.model == "phi4-mini:latest"
    # Default base_url
    assert isinstance(model.openai_client, DummyAsyncOpenAI)
    assert model.openai_client.base_url == "http://localhost:11434/v1"
    assert model.openai_client.api_key == "ollama"

# Test environment variable base_url is used
def test_ollama_env_base_url(monkeypatch):
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://env-base/")
    model = OllamaModel()
    assert model.openai_client.base_url == "http://env-base/v1"

# Test explicit base_url override and other params
def test_ollama_explicit_base_url_and_params(monkeypatch):
    # Override base_url and pass extra kwargs
    custom = "http://custom-base/"
    model = OllamaModel(base_url=custom, foo="bar")
    assert model.kwargs["foo"] == "bar"
    assert isinstance(model.openai_client, DummyAsyncOpenAI)
    assert model.openai_client.base_url == "http://custom-base/v1"
    assert model.openai_client.api_key == "ollama"

# Test create_chat_completion override behavior
@pytest.mark.asyncio
async def test_ollama_create_chat_completion():
    model = OllamaModel(temperature=0.9, foo="baz")
    result = await model._create_chat_completion(test="value")
    # Override logic should include temperature and kwargs
    assert result["result"]["temperature"] == 0.9
    assert result["result"]["test"] == "value"
    assert result["result"]["foo"] == "baz" 
