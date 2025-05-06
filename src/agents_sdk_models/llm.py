from typing import Literal, Optional, Any
from agents.models.interface import Model
from agents import OpenAIChatCompletionsModel  # Import from agents library
from agents import set_tracing_disabled  # Import set_tracing_disabled for tracing control
# English: Import OpenAI client
# 日本語: OpenAI クライアントをインポート
from openai import AsyncOpenAI
from agents.models.openai_responses import OpenAIResponsesModel

from .anthropic import ClaudeModel
from .gemini import GeminiModel
from .ollama import OllamaModel

# Define the provider type hint
ProviderType = Literal["openai", "google", "anthropic", "ollama"]

def get_llm(
    provider: ProviderType = "openai",
    model: Optional[str] = None,
    temperature: float = 0.3,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    thinking: bool = False,
    tracing: bool = False,
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
    set_tracing_disabled(not tracing)

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
            # English: Exclude client args, thinking, and temperature
            # 日本語: クライアント引数、thinking、temperature を除外
            if key not in ['api_key', 'base_url', 'thinking', 'temperature']:
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