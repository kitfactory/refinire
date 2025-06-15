import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from refinire import get_available_models, get_available_models_async


class TestGetAvailableModels:
    """
    Test class for get_available_models functionality.
    
    English:
    Test class for get_available_models functionality.
    
    日本語:
    get_available_models 機能のテストクラス。
    """

    @pytest.mark.asyncio
    async def test_get_available_models_openai(self):
        """
        Test getting available OpenAI models.
        
        English:
        Test getting available OpenAI models.
        
        日本語:
        利用可能な OpenAI モデルの取得をテストします。
        """
        result = await get_available_models_async(["openai"])
        
        assert "openai" in result
        assert isinstance(result["openai"], list)
        assert len(result["openai"]) > 0
        assert "gpt-4o-mini" in result["openai"]
        assert "gpt-4o" in result["openai"]
        assert "gpt-4.1" in result["openai"]
        assert "o3" in result["openai"]
        assert "o4-mini" in result["openai"]

    @pytest.mark.asyncio
    async def test_get_available_models_google(self):
        """
        Test getting available Google models.
        
        English:
        Test getting available Google models.
        
        日本語:
        利用可能な Google モデルの取得をテストします。
        """
        result = await get_available_models_async(["google"])
        
        assert "google" in result
        assert isinstance(result["google"], list)
        assert len(result["google"]) > 0
        assert "gemini-2.5-pro" in result["google"]
        assert "gemini-2.5-flash" in result["google"]

    @pytest.mark.asyncio
    async def test_get_available_models_anthropic(self):
        """
        Test getting available Anthropic models.
        
        English:
        Test getting available Anthropic models.
        
        日本語:
        利用可能な Anthropic モデルの取得をテストします。
        """
        result = await get_available_models_async(["anthropic"])
        
        assert "anthropic" in result
        assert isinstance(result["anthropic"], list)
        assert len(result["anthropic"]) > 0
        assert "claude-opus-4" in result["anthropic"]
        assert "claude-sonnet-4" in result["anthropic"]

    @pytest.mark.asyncio
    async def test_get_available_models_multiple_providers(self):
        """
        Test getting available models for multiple providers.
        
        English:
        Test getting available models for multiple providers.
        
        日本語:
        複数のプロバイダーの利用可能なモデルの取得をテストします。
        """
        result = await get_available_models_async(["openai", "google", "anthropic"])
        
        assert "openai" in result
        assert "google" in result
        assert "anthropic" in result
        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_get_available_models_ollama_success(self):
        """
        Test getting available Ollama models with successful API response.
        
        English:
        Test getting available Ollama models with successful API response.
        
        日本語:
        成功した API レスポンスでの利用可能な Ollama モデルの取得をテストします。
        """
        mock_response_data = {
            "models": [
                {"name": "llama2:7b"},
                {"name": "codellama:13b"},
                {"name": "mistral:7b"}
            ]
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            # Create a mock response object
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            
            # Create a mock client instance
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            
            # Set up the context manager
            mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await get_available_models_async(["ollama"])
            
            assert "ollama" in result
            assert isinstance(result["ollama"], list)
            assert "llama2:7b" in result["ollama"]
            assert "codellama:13b" in result["ollama"]
            assert "mistral:7b" in result["ollama"]

    @pytest.mark.asyncio
    async def test_get_available_models_ollama_connection_error(self):
        """
        Test Ollama models with connection error.
        
        English:
        Test Ollama models with connection error.
        
        日本語:
        接続エラーでの Ollama モデルをテストします。
        """
        with patch('httpx.AsyncClient') as mock_client_class:
            # Create a mock client instance that raises an exception
            mock_client_instance = AsyncMock()
            mock_client_instance.get.side_effect = Exception("Connection failed")
            
            # Set up the context manager
            mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await get_available_models_async(["ollama"])
            
            assert "ollama" in result
            assert result["ollama"] == []

    @pytest.mark.asyncio
    async def test_get_available_models_ollama_custom_base_url(self):
        """
        Test Ollama models with custom base URL.
        
        English:
        Test Ollama models with custom base URL.
        
        日本語:
        カスタムベース URL での Ollama モデルをテストします。
        """
        custom_url = "http://custom-ollama:11434"
        mock_response_data = {"models": [{"name": "custom-model:7b"}]}
        
        with patch('httpx.AsyncClient') as mock_client_class:
            # Create a mock response object
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            
            # Create a mock client instance
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            
            # Set up the context manager
            mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await get_available_models_async(["ollama"], ollama_base_url=custom_url)
            
            # Verify the correct URL was called
            mock_client_instance.get.assert_called_with(f"{custom_url}/api/tags")
            assert "ollama" in result
            assert "custom-model:7b" in result["ollama"]

    @pytest.mark.asyncio
    async def test_get_available_models_invalid_provider(self):
        """
        Test with invalid provider.
        
        English:
        Test with invalid provider.
        
        日本語:
        無効なプロバイダーでのテストします。
        """
        with pytest.raises(ValueError, match="Unsupported provider"):
            await get_available_models_async(["invalid_provider"])

    def test_get_available_models_sync(self):
        """
        Test synchronous function.
        
        English:
        Test synchronous function.
        
        日本語:
        同期関数をテストします。
        """
        result = get_available_models(["openai"])
        
        assert "openai" in result
        assert isinstance(result["openai"], list)
        assert len(result["openai"]) > 0
        assert "gpt-4o-mini" in result["openai"]
        assert "gpt-4.1" in result["openai"]

    @pytest.mark.asyncio
    async def test_get_available_models_ollama_environment_variable(self):
        """
        Test Ollama with environment variable for base URL.
        
        English:
        Test Ollama with environment variable for base URL.
        
        日本語:
        ベース URL の環境変数での Ollama をテストします。
        """
        env_url = "http://env-ollama:11434"
        mock_response_data = {"models": [{"name": "env-model:7b"}]}
        
        with patch('httpx.AsyncClient') as mock_client_class, \
             patch.dict('os.environ', {'OLLAMA_BASE_URL': env_url}):
            
            # Create a mock response object
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            
            # Create a mock client instance
            mock_client_instance = AsyncMock()
            mock_client_instance.get = AsyncMock(return_value=mock_response)
            
            # Set up the context manager
            mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
            mock_client_class.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await get_available_models_async(["ollama"])
            
            # Verify the environment variable URL was used
            mock_client_instance.get.assert_called_with(f"{env_url}/api/tags")
            assert "ollama" in result
            assert "env-model:7b" in result["ollama"] 
