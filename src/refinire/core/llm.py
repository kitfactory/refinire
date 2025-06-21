from typing import Literal, Optional, Any, List
from agents import Model, OpenAIChatCompletionsModel, set_tracing_disabled
# English: Import OpenAI client
# 日本語: OpenAI クライアントをインポート
from openai import AsyncOpenAI
from agents import OpenAIResponsesModel
# English: Import HTTP client for API requests
# 日本語: API リクエスト用の HTTP クライアントをインポート
import httpx
import asyncio
import logging
import os

from .anthropic import ClaudeModel
from .gemini import GeminiModel
from .ollama import OllamaModel

# Define the provider type hint
ProviderType = Literal["openai", "google", "anthropic", "ollama"]

logger = logging.getLogger(__name__)

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

    def get_provider_canditate(model: str) -> ProviderType:
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

    if provider is None:
        provider = get_provider_canditate(model)

    if provider == "openai":
        # Use the standard OpenAI model from the agents library
        # agentsライブラリの標準 OpenAI モデルを使用
        openai_kwargs = kwargs.copy()

        # English: Prepare arguments for OpenAI client and model
        # 日本語: OpenAI クライアントとモデルの引数を準備
        client_args = {}
        model_args = {}

        # English: Set API key for client
        # 日本語: クライアントに API キーを設定
        if api_key:
            client_args['api_key'] = api_key
        # English: Set base URL for client
        # 日本語: クライアントにベース URL を設定
        if base_url:
            client_args['base_url'] = base_url

        # English: Set model name for model constructor
        # 日本語: モデルコンストラクタにモデル名を設定
        model_args['model'] = model if model else "gpt-4o-mini" # Default to gpt-4o-mini

        # English: Temperature is likely handled by the runner or set post-init,
        # English: so remove it from constructor args.
        # 日本語: temperature はランナーによって処理されるか、初期化後に設定される可能性が高いため、
        # 日本語: コンストラクタ引数から削除します。
        # model_args['temperature'] = temperature # Removed based on TypeError

        # English: Add any other relevant kwargs passed in, EXCLUDING temperature
        # 日本語: 渡された他の関連する kwargs を追加 (temperature を除く)
        # Example: max_tokens, etc. Filter out args meant for the client.
        # 例: max_tokens など。クライアント向けの引数を除外します。
        for key, value in kwargs.items():
            # English: Exclude client args, thinking, temperature, and tracing
            # 日本語: クライアント引数、thinking、temperature、tracing を除外
            if key not in ['api_key', 'base_url', 'thinking', 'temperature', 'tracing']:
                model_args[key] = value

        # English: Remove 'thinking' as it's not used by OpenAI model
        # 日本語: OpenAI モデルでは使用されないため 'thinking' を削除
        model_args.pop('thinking', None)

        # English: Instantiate the OpenAI client
        # 日本語: OpenAI クライアントをインスタンス化
        openai_client = AsyncOpenAI(**client_args)

        # English: Instantiate and return the model, passing the client and model args
        # 日本語: クライアントとモデル引数を渡してモデルをインスタンス化して返す
        return OpenAIResponsesModel(
            openai_client=openai_client,
            **model_args
        )
    elif provider == "google":
        gemini_kwargs = kwargs.copy()
        if model:
            gemini_kwargs['model'] = model
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
        if model:
            claude_kwargs['model'] = model
        return ClaudeModel(
            temperature=temperature,
            api_key=api_key,
            base_url=base_url, # Although Claude doesn't typically use base_url, pass it if provided
            thinking=thinking,
            **claude_kwargs
        )
    elif provider == "ollama":
        ollama_kwargs = kwargs.copy()
        if model:
            ollama_kwargs['model'] = model
        # thinking is not used by OllamaModel
        ollama_kwargs.pop('thinking', None)
        return OllamaModel(
            temperature=temperature,
            base_url=base_url,
            api_key=api_key, # Although Ollama doesn't typically use api_key, pass it if provided
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
                logger.warning(f"Could not connect to Ollama at {ollama_base_url}: {e}")
            except Exception as e:
                # English: Handle other errors
                # 日本語: その他のエラーを処理
                result["ollama"] = []
                logger.warning(f"Error fetching Ollama models: {e}")
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
