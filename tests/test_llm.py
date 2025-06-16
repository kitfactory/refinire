import pytest
from refinire.core import llm

class DummyOpenAIResponsesModel:
    def __init__(self, openai_client=None, **kwargs):
        self.openai_client = openai_client
        self.kwargs = kwargs

class DummyGeminiModel:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

class DummyClaudeModel:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

class DummyOllamaModel:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

class DummyAsyncOpenAI:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

@pytest.fixture(autouse=True)
def patch_models(monkeypatch):
    monkeypatch.setattr(llm, "OpenAIResponsesModel", DummyOpenAIResponsesModel)
    monkeypatch.setattr(llm, "GeminiModel", DummyGeminiModel)
    monkeypatch.setattr(llm, "ClaudeModel", DummyClaudeModel)
    monkeypatch.setattr(llm, "OllamaModel", DummyOllamaModel)
    monkeypatch.setattr(llm, "AsyncOpenAI", DummyAsyncOpenAI)
    monkeypatch.setattr(llm, "set_tracing_disabled", lambda x: None)


def test_get_llm_openai():
    model = llm.get_llm(model="gpt-4o", provider="openai", api_key="sk-xxx", base_url="http://api", temperature=0.5, max_tokens=100)
    assert isinstance(model, DummyOpenAIResponsesModel)
    assert model.openai_client.kwargs["api_key"] == "sk-xxx"
    assert model.openai_client.kwargs["base_url"] == "http://api"
    assert model.kwargs["model"] == "gpt-4o"
    assert model.kwargs["max_tokens"] == 100
    assert "temperature" not in model.kwargs


def test_get_llm_google():
    model = llm.get_llm(model="gemini-pro", provider="google", api_key="g-api", temperature=0.7)
    assert isinstance(model, DummyGeminiModel)
    assert model.kwargs["model"] == "gemini-pro"
    assert model.kwargs["temperature"] == 0.7
    assert model.kwargs["api_key"] == "g-api"


def test_get_llm_anthropic():
    model = llm.get_llm(model="claude-3-sonnet", provider="anthropic", api_key="a-key", temperature=0.2, thinking=True)
    assert isinstance(model, DummyClaudeModel)
    assert model.kwargs["model"] == "claude-3-sonnet"
    assert model.kwargs["temperature"] == 0.2
    assert model.kwargs["api_key"] == "a-key"
    assert model.kwargs["thinking"] is True


def test_get_llm_ollama():
    model = llm.get_llm(model="qwen3:8b", provider="ollama", base_url="http://localhost:11434", temperature=0.1)
    assert isinstance(model, DummyOllamaModel)
    assert model.kwargs["model"] == "qwen3:8b"
    assert model.kwargs["temperature"] == 0.1
    assert model.kwargs["base_url"] == "http://localhost:11434"


def test_get_llm_provider_autodetect():
    # gpt→openai, gemini→google, claude→anthropic, その他→ollama
    m1 = llm.get_llm(model="gpt-4o")
    assert isinstance(m1, DummyOpenAIResponsesModel)
    m2 = llm.get_llm(model="gemini-pro")
    assert isinstance(m2, DummyGeminiModel)
    m3 = llm.get_llm(model="claude-3-sonnet")
    assert isinstance(m3, DummyClaudeModel)
    m4 = llm.get_llm(model="qwen3:8b")
    assert isinstance(m4, DummyOllamaModel)


def test_get_llm_invalid_provider():
    with pytest.raises(ValueError):
        llm.get_llm(model="foo-bar", provider="invalid") 
