"""Test provider-specific model ID parsing and configuration
プロバイダー固有のモデルID解析と設定のテスト
"""

import os
from unittest.mock import patch, Mock
from refinire.core.model_parser import parse_model_id, detect_provider_from_environment, get_provider_config
from refinire.core.llm import get_llm
from agents import Model


def test_model_id_parsing():
    """Test model ID parsing with various formats
    様々な形式でのモデルID解析のテスト
    """
    print("Testing model ID parsing...")
    
    # Test cases
    test_cases = [
        ("gpt-4o-mini", (None, "gpt-4o-mini", None)),
        ("openai://gpt-4o-mini", ("openai", "gpt-4o-mini", None)),
        ("ollama://llama3#8b", ("ollama", "llama3", "8b")),
        ("azure://gpt4o-deploy#2024-10-21", ("azure", "gpt4o-deploy", "2024-10-21")),
        ("groq://mixtral-8x22b", ("groq", "mixtral-8x22b", None)),
        ("anthropic://claude-opus-4", ("anthropic", "claude-opus-4", None)),
    ]
    
    for model_id, expected in test_cases:
        result = parse_model_id(model_id)
        assert result == expected, f"Failed for {model_id}: expected {expected}, got {result}"
        print(f"✓ {model_id} -> {result}")
    
    print("✓ All model ID parsing tests passed")


def test_environment_provider_detection():
    """Test provider detection from environment variables
    環境変数からのプロバイダー検出のテスト
    """
    print("\nTesting environment provider detection...")
    
    # Test Azure detection
    with patch.dict(os.environ, {"AZURE_OPENAI_ENDPOINT": "https://myazure.openai.azure.com"}):
        provider = detect_provider_from_environment()
        assert provider == "azure"
        print("✓ Azure detection from AZURE_OPENAI_ENDPOINT")
    
    # Test Groq detection
    with patch.dict(os.environ, {"OPENAI_BASE_URL": "https://api.groq.com/v1"}):
        provider = detect_provider_from_environment()
        assert provider == "groq"
        print("✓ Groq detection from OPENAI_BASE_URL")
    
    # Test Ollama detection
    with patch.dict(os.environ, {"OPENAI_BASE_URL": "http://localhost:11434/v1"}):
        provider = detect_provider_from_environment()
        assert provider == "ollama"
        print("✓ Ollama detection from OPENAI_BASE_URL")
    
    # Test LM Studio detection
    with patch.dict(os.environ, {"OPENAI_BASE_URL": "http://localhost:1234/lmstudio/v1"}):
        provider = detect_provider_from_environment()
        assert provider == "lmstudio"
        print("✓ LM Studio detection from OPENAI_BASE_URL")
    
    # Test no detection
    with patch.dict(os.environ, {}, clear=True):
        provider = detect_provider_from_environment()
        assert provider is None
        print("✓ No provider detected when no environment variables set")


def test_provider_configuration():
    """Test provider-specific configuration
    プロバイダー固有の設定のテスト
    """
    print("\nTesting provider configuration...")
    
    # Test OpenAI configuration
    config = get_provider_config("openai", "gpt-4o-mini")
    assert config["provider"] == "openai"
    assert config["model"] == "gpt-4o-mini"
    assert config["use_chat_completions"] == False
    print("✓ OpenAI configuration (responses endpoint)")
    
    # Test OpenAI with FORCE_CHAT
    with patch.dict(os.environ, {"FORCE_CHAT": "1"}):
        config = get_provider_config("openai", "gpt-4o-mini")
        assert config["use_chat_completions"] == True
        print("✓ OpenAI configuration with FORCE_CHAT")
    
    # Test Azure configuration
    config = get_provider_config("azure", "gpt4o-deploy", "2024-10-21")
    assert config["provider"] == "azure"
    assert config["deployment_name"] == "gpt4o-deploy"
    assert config["api_version"] == "2024-10-21"
    assert config["use_chat_completions"] == True
    print("✓ Azure configuration")
    
    # Test Ollama configuration
    config = get_provider_config("ollama", "llama3", "8b")
    assert config["provider"] == "ollama"
    assert config["model"] == "llama3:8b"
    assert config["use_chat_completions"] == True
    assert "base_url" in config
    print("✓ Ollama configuration with tag")
    
    # Test Groq configuration
    config = get_provider_config("groq", "mixtral-8x22b")
    assert config["provider"] == "groq"
    assert config["model"] == "mixtral-8x22b"
    assert config["use_chat_completions"] == True
    assert config["base_url"] == "https://api.groq.com"
    print("✓ Groq configuration")


def test_get_llm_with_provider_prefix():
    """Test get_llm with provider-prefixed model IDs
    プロバイダープレフィックス付きモデルIDでのget_llmテスト
    """
    print("\nTesting get_llm with provider prefixes...")
    
    # Mock the client classes to avoid API calls
    # API呼び出しを避けるためクライアントクラスをモック
    with patch('refinire.core.llm.AsyncOpenAI') as mock_openai:
        with patch('refinire.core.llm.AsyncAzureOpenAI') as mock_azure:
            with patch('refinire.core.llm.OpenAIChatCompletionsModel') as mock_chat_model:
                with patch('refinire.core.llm.OpenAIResponsesModel') as mock_responses_model:
                    
                    # Test Groq provider prefix
                    mock_client = Mock()
                    mock_openai.return_value = mock_client
                    mock_model_instance = Mock(spec=Model)
                    mock_chat_model.return_value = mock_model_instance
                    
                    with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}):
                        model = get_llm(model="groq://mixtral-8x22b")
                        
                        # Verify OpenAI client was created with Groq base URL
                        mock_openai.assert_called_once()
                        call_args = mock_openai.call_args[1]
                        assert call_args["base_url"] == "https://api.groq.com"
                        
                        # Verify chat completions model was used
                        mock_chat_model.assert_called_once()
                        assert mock_chat_model.call_args[1]["model"] == "mixtral-8x22b"
                        
                        print("✓ Groq provider prefix creates chat completions model")
                    
                    # Reset mocks
                    mock_openai.reset_mock()
                    mock_chat_model.reset_mock()
                    
                    # Test Azure provider prefix
                    mock_azure_client = Mock()
                    mock_azure.return_value = mock_azure_client
                    
                    with patch.dict(os.environ, {
                        "AZURE_OPENAI_API_KEY": "test-key",
                        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com"
                    }):
                        model = get_llm(model="azure://gpt4o-deploy#2024-10-21")
                        
                        # Verify Azure client was created
                        mock_azure.assert_called_once()
                        call_args = mock_azure.call_args[1]
                        assert call_args["api_version"] == "2024-10-21"
                        assert call_args["azure_endpoint"] == "https://test.openai.azure.com"
                        
                        # Verify chat completions model was used with deployment name
                        assert mock_chat_model.call_args[1]["model"] == "gpt4o-deploy"
                        
                        print("✓ Azure provider prefix creates Azure client with API version")


def test_refinire_agent_with_provider_models():
    """Test RefinireAgent with provider-specific models
    プロバイダー固有モデルでのRefinireAgentテスト
    """
    print("\nTesting RefinireAgent with provider models...")
    
    from refinire.agents.pipeline.llm_pipeline import RefinireAgent
    
    # Mock get_llm to avoid API calls
    mock_model = Mock(spec=Model)
    mock_model.model = "mixtral-8x22b"
    
    with patch('refinire.agents.pipeline.llm_pipeline.get_llm') as mock_get_llm:
        mock_get_llm.return_value = mock_model
        
        # Test with Groq model
        agent = RefinireAgent(
            name="groq_agent",
            generation_instructions="You are a Groq assistant.",
            model="groq://mixtral-8x22b"
        )
        
        # Verify get_llm was called with the full model string
        mock_get_llm.assert_called_with(model="groq://mixtral-8x22b", temperature=0.7)
        assert agent.model_name == "groq://mixtral-8x22b"
        print("✓ RefinireAgent works with provider-prefixed models")


if __name__ == "__main__":
    print("Testing provider support...")
    print("=" * 60)
    
    try:
        test_model_id_parsing()
        test_environment_provider_detection()
        test_provider_configuration()
        test_get_llm_with_provider_prefix()
        test_refinire_agent_with_provider_models()
        
        print("\n" + "=" * 60)
        print("All provider support tests passed! ✓")
        print("\nProvider support implemented:")
        print("- Model ID format: <provider>://<model>[#<tag>]")
        print("- Environment-based provider detection")
        print("- Provider-specific configurations")
        print("- Automatic endpoint selection (/responses vs /chat/completions)")
        print("- Support for OpenAI, Azure, Groq, Ollama, LM Studio")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()