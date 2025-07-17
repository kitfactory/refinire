from typing import Literal, Optional, Any, List
from agents import Model, OpenAIChatCompletionsModel, set_tracing_disabled
# English: Import OpenAI client
# 日本語: OpenAI クライアントをインポート
from openai import AsyncOpenAI, AsyncAzureOpenAI
from agents import OpenAIResponsesModel
# English: Import HTTP client for API requests
# 日本語: API リクエスト用の HTTP クライアントをインポート
import httpx
import asyncio
import os

from .anthropic import ClaudeModel
from .gemini import GeminiModel
from .ollama import OllamaModel
from .model_parser import parse_model_id, detect_provider_from_environment, get_provider_config

# Define the provider type hint
ProviderType = Literal["openai", "google", "anthropic", "ollama", "azure", "groq", "lmstudio", "openrouter"]


def get_llm(
    model: Optional[str] = None,
    provider: Optional[ProviderType] = None,
    temperature: float = 0.3,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    thinking: bool = False,
    **kwargs: Any,
) -> Model:
    """
    Factory function to get an instance of a language model based on the provider.

    English:
    Factory function to get an instance of a language model based on the provider.

    日本語:
    プロバイダーに基づいて言語モデルのインスタンスを取得するファクトリ関数。

    Args:
        provider (ProviderType): The LLM provider ("openai", "google", "anthropic", "ollama"). Defaults to "openai".
            LLM プロバイダー ("openai", "google", "anthropic", "ollama")。デフォルトは "openai"。
        model (Optional[str]): The specific model name for the provider. If None, uses the default for the provider.
            プロバイダー固有のモデル名。None の場合、プロバイダーのデフォルトを使用します。
        temperature (float): Sampling temperature. Defaults to 0.3.
            サンプリング温度。デフォルトは 0.3。
        api_key (Optional[str]): API key for the provider, if required.
            プロバイダーの API キー (必要な場合)。
        base_url (Optional[str]): Base URL for the provider's API, if needed (e.g., for self-hosted Ollama or OpenAI-compatible APIs).
            プロバイダー API のベース URL (必要な場合、例: セルフホストの Ollama や OpenAI 互換 API)。
        thinking (bool): Enable thinking mode for Claude models. Defaults to False.
            Claude モデルの思考モードを有効にするか。デフォルトは False。
        tracing (bool): Whether to enable tracing for the Agents SDK. Defaults to False.
            Agents SDK のトレーシングを有効化するか。デフォルトは False。
        **kwargs (Any): Additional keyword arguments to pass to the model constructor.
            モデルのコンストラクタに渡す追加のキーワード引数。

    Returns:
        Model: An instance of the appropriate language model class.
               適切な言語モデルクラスのインスタンス。

    Raises:
        ValueError: If an unsupported provider is specified.
                    サポートされていないプロバイダーが指定された場合。
    """
    # English: Configure OpenAI Agents SDK tracing
    # 日本語: OpenAI Agents SDK のトレーシングを設定する
    # set_tracing_disabled(not tracing)


    if model is None:
        model = os.environ.get("REFINIRE_DEFAULT_LLM_MODEL", "gpt-4o-mini")

    # Parse model ID to extract provider, model name, and tag
    # モデルIDを解析してプロバイダー、モデル名、タグを抽出
    parsed_provider, model_name, model_tag = parse_model_id(model)
    
    # Determine provider if not explicitly specified
    # 明示的に指定されていない場合はプロバイダーを決定
    if provider is None:
        if parsed_provider:
            provider = parsed_provider
        else:
            # Try environment detection first
            # まず環境検出を試す
            env_provider = detect_provider_from_environment()
            if env_provider:
                provider = env_provider
            else:
                # Fallback to model name detection
                # モデル名検出にフォールバック
                def get_provider_candidate(model: str) -> ProviderType:
                    if "gpt" in model:
                        return "openai"
                    if "o3" in model or "o4" in model:
                        return "openai"
                    elif "gemini" in model:
                        return "google"
                    elif "claude" in model:
                        return "anthropic"
                    else:
                        return "ollama"
                provider = get_provider_candidate(model_name)
    
    # Get provider-specific configuration
    # プロバイダー固有の設定を取得
    provider_config = get_provider_config(provider, model_name, model_tag)

    # Handle provider-specific model creation
    # プロバイダー固有のモデル作成を処理
    if provider == "openai" or provider in ["groq", "lmstudio", "openrouter"]:
        # Use OpenAI-compatible API
        # OpenAI互換APIを使用
        openai_kwargs = kwargs.copy()
        client_args = {}
        model_args = {}

        # Set API key and base URL
        # APIキーとベースURLを設定
        if api_key:
            client_args['api_key'] = api_key
        elif provider == "groq":
            client_args['api_key'] = os.environ.get("GROQ_API_KEY")
        elif provider == "openrouter":
            client_args['api_key'] = os.environ.get("OPENROUTER_API_KEY")
        elif provider == "lmstudio":
            # LM Studio typically doesn't require API key
            # LM Studioは通常APIキーを必要としない
            client_args['api_key'] = "lm-studio"
        
        if base_url:
            client_args['base_url'] = base_url
        elif provider in ["groq", "lmstudio", "openrouter"]:
            client_args['base_url'] = provider_config.get("base_url")

        # Set model name
        # モデル名を設定
        model_args['model'] = provider_config["model"]

        # Add other kwargs
        # 他のkwargsを追加
        for key, value in kwargs.items():
            if key not in ['api_key', 'base_url', 'thinking', 'temperature', 'tracing']:
                model_args[key] = value

        model_args.pop('thinking', None)

        # Create client
        # クライアントを作成
        openai_client = AsyncOpenAI(**client_args)

        # Use appropriate model class based on endpoint type
        # エンドポイントタイプに基づいて適切なモデルクラスを使用
        if provider_config["use_chat_completions"]:
            return OpenAIChatCompletionsModel(
                openai_client=openai_client,
                **model_args
            )
        else:
            return OpenAIResponsesModel(
                openai_client=openai_client,
                **model_args
            )
    elif provider == "azure":
        # Use Azure OpenAI
        # Azure OpenAIを使用
        azure_kwargs = kwargs.copy()
        client_args = {}
        
        # Azure requires specific configuration
        # Azureは特定の設定が必要
        client_args['api_key'] = api_key or os.environ.get("AZURE_OPENAI_API_KEY")
        client_args['api_version'] = provider_config["api_version"]
        client_args['azure_endpoint'] = base_url or os.environ.get("AZURE_OPENAI_ENDPOINT")
        
        # Create Azure client
        # Azureクライアントを作成
        azure_client = AsyncAzureOpenAI(**client_args)
        
        # Azure always uses chat completions
        # Azureは常にchat completionsを使用
        return OpenAIChatCompletionsModel(
            openai_client=azure_client,
            model=provider_config["deployment_name"],
            **azure_kwargs
        )
    elif provider == "google":
        gemini_kwargs = kwargs.copy()
        # Use parsed model name
        # 解析されたモデル名を使用
        gemini_kwargs['model'] = model_name
        # thinking is not used by GeminiModel
        gemini_kwargs.pop('thinking', None)
        return GeminiModel(
            temperature=temperature,
            api_key=api_key,
            base_url=base_url, # Although Gemini doesn't typically use base_url, pass it if provided
            **gemini_kwargs
        )
    elif provider == "anthropic":
        claude_kwargs = kwargs.copy()
        # Use parsed model name
        # 解析されたモデル名を使用
        claude_kwargs['model'] = model_name
        
        # Check if using OpenAI-compatible mode via ANTHROPIC_BASE_URL
        # ANTHROPIC_BASE_URLによるOpenAI互換モードかチェック
        anthropic_base_url = base_url or os.environ.get("ANTHROPIC_BASE_URL")
        if anthropic_base_url and anthropic_base_url != "https://api.anthropic.com/v1":
            # Use OpenAI-compatible client for OpenRouter/LiteLLM etc.
            # OpenRouter/LiteLLM等でOpenAI互換クライアントを使用
            client_args = {
                'api_key': api_key or os.environ.get("ANTHROPIC_API_KEY"),
                'base_url': anthropic_base_url
            }
            openai_client = AsyncOpenAI(**client_args)
            model_args = {'model': model_name}
            for key, value in kwargs.items():
                if key not in ['api_key', 'base_url', 'thinking', 'temperature', 'tracing']:
                    model_args[key] = value
            model_args.pop('thinking', None)
            
            return OpenAIChatCompletionsModel(
                openai_client=openai_client,
                **model_args
            )
        else:
            # Use native Claude API
            # ネイティブClaude APIを使用
            return ClaudeModel(
                temperature=temperature,
                api_key=api_key,
                base_url=base_url,
                thinking=thinking,
                **claude_kwargs
            )
    elif provider == "ollama":
        ollama_kwargs = kwargs.copy()
        # Use parsed model configuration
        # 解析されたモデル設定を使用
        ollama_kwargs['model'] = provider_config["model"]
        ollama_kwargs.pop('thinking', None)
        return OllamaModel(
            temperature=temperature,
            base_url=base_url or provider_config.get("base_url"),
            api_key=api_key,
            **ollama_kwargs
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}. Must be one of {ProviderType.__args__}") 

async def get_available_models_async(
    providers: List[ProviderType],
    ollama_base_url: Optional[str] = None
) -> dict[str, List[str]]:
    """
    Get available model names for specified providers.
    
    English:
    Get available model names for specified providers.
    
    日本語:
    指定されたプロバイダーの利用可能なモデル名を取得します。
    
    Args:
        providers (List[ProviderType]): List of providers to get models for.
            モデルを取得するプロバイダーのリスト。
        ollama_base_url (Optional[str]): Base URL for Ollama API. If None, uses environment variable or default.
            Ollama API のベース URL。None の場合、環境変数またはデフォルトを使用。
    
    Returns:
        dict[str, List[str]]: Dictionary mapping provider names to lists of available models.
                             プロバイダー名と利用可能なモデルのリストのマッピング辞書。
    
    Raises:
        ValueError: If an unsupported provider is specified.
                    サポートされていないプロバイダーが指定された場合。
        httpx.RequestError: If there's an error connecting to the Ollama API.
                           Ollama API への接続エラーが発生した場合。
    """
    result = {}
    
    for provider in providers:
        if provider == "openai":
            # English: OpenAI models - latest available models
            # 日本語: OpenAI モデル - 最新の利用可能なモデル
            result["openai"] = [
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4.1",
                "o3",
                "o4-mini"
            ]
        elif provider == "google":
            # English: Google Gemini models - latest 2.5 series models
            # 日本語: Google Gemini モデル - 最新の 2.5 シリーズモデル
            result["google"] = [
                "gemini-2.5-pro",
                "gemini-2.5-flash"
            ]
        elif provider == "anthropic":
            # English: Anthropic Claude models - latest Claude-4 series models
            # 日本語: Anthropic Claude モデル - 最新の Claude-4 シリーズモデル
            result["anthropic"] = [
                "claude-opus-4",
                "claude-sonnet-4"
            ]
        elif provider == "ollama":
            # English: Get Ollama base URL from parameter, environment variable, or default
            # 日本語: パラメータ、環境変数、またはデフォルトから Ollama ベース URL を取得
            if ollama_base_url is None:
                ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
            
            try:
                # English: Fetch available models from Ollama API
                # 日本語: Ollama API から利用可能なモデルを取得
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"{ollama_base_url}/api/tags")
                    response.raise_for_status()
                    
                    # English: Parse the response to extract model names
                    # 日本語: レスポンスを解析してモデル名を抽出
                    data = response.json()
                    models = []
                    if "models" in data:
                        for model_info in data["models"]:
                            if "name" in model_info:
                                models.append(model_info["name"])
                    
                    result["ollama"] = models
                    
            except httpx.RequestError as e:
                # English: If connection fails, return empty list with error info
                # 日本語: 接続に失敗した場合、エラー情報と共に空のリストを返す
                result["ollama"] = []
                from .exceptions import map_httpx_exception
                raise map_httpx_exception(e, "ollama")
            except Exception as e:
                # English: Handle other errors
                # 日本語: その他のエラーを処理
                result["ollama"] = []
                from .exceptions import RefinireError
                raise RefinireError(f"Error fetching Ollama models: {e}", provider="ollama")
        else:
            raise ValueError(f"Unsupported provider: {provider}. Must be one of {ProviderType.__args__}")
    
    return result

def get_available_models(
    providers: List[ProviderType],
    ollama_base_url: Optional[str] = None
) -> dict[str, List[str]]:
    """
    Get available model names for specified providers (synchronous version).
    
    English:
    Get available model names for specified providers (synchronous version).
    
    日本語:
    指定されたプロバイダーの利用可能なモデル名を取得します（同期版）。
    
    Args:
        providers (List[ProviderType]): List of providers to get models for.
            モデルを取得するプロバイダーのリスト。
        ollama_base_url (Optional[str]): Base URL for Ollama API. If None, uses environment variable or default.
            Ollama API のベース URL。None の場合、環境変数またはデフォルトを使用。
    
    Returns:
        dict[str, List[str]]: Dictionary mapping provider names to lists of available models.
                             プロバイダー名と利用可能なモデルのリストのマッピング辞書。
    """
    try:
        # English: Try to get the current event loop
        # 日本語: 現在のイベントループを取得しようとする
        loop = asyncio.get_running_loop()
        # English: If we're in a running loop, we need to handle this differently
        # 日本語: 実行中のループ内にいる場合、異なる方法で処理する必要がある
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, get_available_models_async(providers, ollama_base_url))
            return future.result()
    except RuntimeError:
        # English: No running event loop, safe to use asyncio.run()
        # 日本語: 実行中のイベントループがない場合、asyncio.run() を安全に使用
        return asyncio.run(get_available_models_async(providers, ollama_base_url)) 
