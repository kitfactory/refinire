"""
Unified model implementation for OpenAI Agents
OpenAI Agentsのための統合モデル実装
"""

from typing import Any, Dict, Literal, Optional, Union
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI

from .ollama import OllamaAIChatCompletionsModel
from .gemini import GeminiAIChatCompletionsModel
from .anthropic import AnthropicAIChatCompletionsModel

# Provider types
# プロバイダータイプ
ProviderType = Literal["openai", "ollama", "gemini", "claude"]

# Default models for each provider
# 各プロバイダーのデフォルトモデル
DEFAULT_MODELS = {
    "openai": "o3-mini",
    "ollama": "phi4-mini:latest",
    "claude": "claude-3-7-sonnet-20250219",
    "gemini": "gemini-2.0-flash"
}

class UnifiedChatCompletionModel(OpenAIChatCompletionsModel):
    """
    Unified model implementation that delegates to specific provider models
    特定のプロバイダーモデルに委譲する統合モデル実装
    """

    def __init__(
        self,
        provider: ProviderType = "openai",
        model: Optional[str] = None,
        temperature: float = 0.3,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        thinking: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the unified model with provider selection
        プロバイダー選択で統合モデルを初期化する

        Args:
            provider (ProviderType): Provider to use ("openai", "ollama", "gemini", "claude")
                使用するプロバイダー（"openai", "ollama", "gemini", "claude"）
                Default is "openai"
                デフォルトは "openai"
            model (Optional[str]): Name of the model to use
                使用するモデルの名前
                If None, a default model is selected based on provider:
                Noneの場合、プロバイダーに基づいてデフォルトモデルが選択されます：
                - openai: "o3-mini"
                - ollama: "phi4-mini:latest"
                - claude: "claude-3-7-sonnet-20250219"
                - gemini: "gemini-2.0-flash"
            temperature (float): Sampling temperature between 0 and 1
                サンプリング温度（0から1の間）
            api_key (Optional[str]): API key for the selected provider
                選択したプロバイダーのAPIキー
            base_url (Optional[str]): Base URL for the API
                APIのベースURL
            thinking (bool): Enable extended thinking for Claude
                Claudeの拡張思考を有効にする
            **kwargs: Additional arguments to pass to the provider API
                プロバイダーAPIに渡す追加の引数
        """
        self.provider = provider
        
        # Use default model if not specified
        # 指定されていない場合はデフォルトモデルを使用
        self.model = model if model is not None else DEFAULT_MODELS.get(provider, DEFAULT_MODELS["openai"])
        
        self.temperature = temperature
        self.api_key = api_key
        self.base_url = base_url
        self.thinking = thinking
        self.kwargs = kwargs
        
        # Create the appropriate model based on provider
        # プロバイダーに基づいて適切なモデルを作成
        self._create_delegated_model()

    def _create_delegated_model(self) -> None:
        """
        Create the delegated model based on provider
        プロバイダーに基づいて委譲モデルを作成する
        """
        if self.provider == "openai":
            # For OpenAI, we need an API key
            # OpenAIの場合はAPIキーが必要
            if not self.api_key:
                raise ValueError("API key is required for OpenAI provider")
            
            # Create AsyncOpenAI client
            # AsyncOpenAIクライアントを作成
            client_args = {"api_key": self.api_key}
            if self.base_url:
                client_args["base_url"] = self.base_url
            
            openai_client = AsyncOpenAI(**client_args)
            
            # Initialize the parent class directly for OpenAI
            # OpenAIの場合は親クラスを直接初期化
            super().__init__(
                model=self.model,
                openai_client=openai_client
            )
            
            # Store the model instance for method delegation
            # メソッド委譲のためにモデルインスタンスを保存
            self.delegated_model = self
            
        elif self.provider == "ollama":
            # For Ollama
            # Ollama用
            ollama_args = {
                "model": self.model,
                "temperature": self.temperature
            }
            
            # Add base_url if provided
            # base_urlが提供されている場合は追加
            if self.base_url:
                ollama_args["base_url"] = self.base_url
            
            # Add any additional kwargs
            # 追加のkwargsを追加
            ollama_args.update(self.kwargs)
            
            # Create Ollama model
            # Ollamaモデルを作成
            self.delegated_model = OllamaAIChatCompletionsModel(**ollama_args)
            
            # Initialize parent with dummy values (won't be used)
            # ダミー値で親を初期化（使用されない）
            super().__init__(model="dummy")
            
        elif self.provider == "gemini":
            # For Gemini
            # Gemini用
            if not self.api_key:
                raise ValueError("API key is required for Gemini provider")
            
            gemini_args = {
                "model": self.model,
                "temperature": self.temperature,
                "api_key": self.api_key
            }
            
            # Add base_url if provided
            # base_urlが提供されている場合は追加
            if self.base_url:
                gemini_args["base_url"] = self.base_url
            
            # Add any additional kwargs
            # 追加のkwargsを追加
            gemini_args.update(self.kwargs)
            
            # Create Gemini model
            # Geminiモデルを作成
            self.delegated_model = GeminiAIChatCompletionsModel(**gemini_args)
            
            # Initialize parent with dummy values (won't be used)
            # ダミー値で親を初期化（使用されない）
            super().__init__(model="dummy")
            
        elif self.provider == "claude":
            # For Claude
            # Claude用
            if not self.api_key:
                raise ValueError("API key is required for Claude provider")
            
            claude_args = {
                "model": self.model,
                "temperature": self.temperature,
                "api_key": self.api_key,
                "thinking": self.thinking
            }
            
            # Add base_url if provided
            # base_urlが提供されている場合は追加
            if self.base_url:
                claude_args["base_url"] = self.base_url
            
            # Add any additional kwargs
            # 追加のkwargsを追加
            claude_args.update(self.kwargs)
            
            # Create Claude model
            # Claudeモデルを作成
            self.delegated_model = AnthropicAIChatCompletionsModel(**claude_args)
            
            # Initialize parent with dummy values (won't be used)
            # ダミー値で親を初期化（使用されない）
            super().__init__(model="dummy")
            
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    # Override all methods to delegate to the appropriate model
    # 適切なモデルに委譲するためにすべてのメソッドをオーバーライド
    async def _create_chat_completion(self, *args, **kwargs):
        """Delegate to the provider model"""
        if self.provider == "openai":
            # For OpenAI, use the parent class implementation
            # OpenAIの場合は親クラスの実装を使用
            kwargs["temperature"] = self.temperature
            kwargs.update(self.kwargs)
            return await super()._create_chat_completion(*args, **kwargs)
        else:
            # For other providers, delegate to the specific model
            # 他のプロバイダーの場合は、特定のモデルに委譲
            return await self.delegated_model._create_chat_completion(*args, **kwargs)

# Create an alias for convenience
# 利便性のためのエイリアスを作成
UnifiedModel = UnifiedChatCompletionModel 