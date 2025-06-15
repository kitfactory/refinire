import pytest
import os
import refinire.core.anthropic as anth
from refinire.core.anthropic import ClaudeModel

# Dummy AsyncOpenAI to verify base_url and api_key attributes
class DummyAsyncOpenAI:
    def __init__(self, base_url=None, api_key=None):
        self.base_url = base_url
        self.api_key = api_key

# Autouse fixture to patch AsyncOpenAI in Anthropic module
@pytest.fixture(autouse=True)
def patch_async(monkeypatch):
    monkeypatch.setattr(anth, "AsyncOpenAI", DummyAsyncOpenAI)

# Test default model name, temperature, thinking flag, and base_url fallback when base_url=None
def test_default_model_and_temperature_and_base_url(monkeypatch):
    # Ensure environment variable is set for API key fallback
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "env-test")

    model = ClaudeModel(api_key=None, base_url=None)
    # Default model name from signature
    assert model.model == "claude-3-5-sonnet-latest"
    # Default temperature
    assert model.temperature == 0.3
    # Default thinking flag
    assert model.thinking is False
    # openai_client should be our dummy with default base_url
    assert isinstance(model.openai_client, DummyAsyncOpenAI)
    assert model.openai_client.base_url == "https://api.anthropic.com/v1/"
    assert model.openai_client.api_key == "env-test"

# Test explicit base_url override is honored
def test_base_url_explicit(monkeypatch):
    # Ensure environment variable is set for API key fallback
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "env-test2")

    custom_url = "https://custom/"
    model = ClaudeModel(api_key=None, base_url=custom_url)
    assert isinstance(model.openai_client, DummyAsyncOpenAI)
    assert model.openai_client.base_url == custom_url
    assert model.openai_client.api_key == "env-test2" 
