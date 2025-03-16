"""
Anthropic model implementation for OpenAI Agents
OpenAI AgentsのためのAnthropic Claude モデル実装
"""

from typing import Any, Dict, List, Optional, Union
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI

class AnthropicAIChatCompletionsModel(OpenAIChatCompletionsModel):
    """
    Anthropic Claude model implementation that extends OpenAI's chat completions model
    OpenAIのチャット補完モデルを拡張したAnthropic Claudeモデルの実装
    """

    def __init__(
        self,
        model: str = "claude-3-sonnet-20240229",
        temperature: float = 0.3,
        api_key: str = None,
        base_url: str = "https://api.anthropic.com/v1/",
        thinking: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the Anthropic Claude model with OpenAI compatible interface
        OpenAI互換インターフェースでAnthropic Claudeモデルを初期化する

        Args:
            model (str): Name of the Claude model to use (e.g. "claude-3-opus-20240229")
                使用するClaudeモデルの名前（例："claude-3-opus-20240229"）
            temperature (float): Sampling temperature between 0 and 1
                サンプリング温度（0から1の間）
            api_key (str): Anthropic API key
                Anthropic APIキー
            base_url (str): Base URL for the Anthropic OpenAI compatibility API
                Anthropic OpenAI互換APIのベースURL
            thinking (bool): Enable extended thinking for complex reasoning
                複雑な推論のための拡張思考を有効にする
            **kwargs: Additional arguments to pass to the OpenAI API
                OpenAI APIに渡す追加の引数
        """
        if api_key is None:
            raise ValueError("Anthropic API key is required. Get one from https://console.anthropic.com/")
        
        # Create AsyncOpenAI client with Anthropic base URL
        # AnthropicのベースURLでAsyncOpenAIクライアントを作成
        openai_client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        
        # Store parameters for later use in API calls
        # 後でAPIコールで使用するためにパラメータを保存
        self.temperature = temperature
        self.thinking = thinking
        self.kwargs = kwargs
        
        # Initialize the parent class with our custom client
        # カスタムクライアントで親クラスを初期化
        super().__init__(
            model=model,
            openai_client=openai_client
        )
    
    # Override methods that make API calls to include our parameters
    # APIコールを行うメソッドをオーバーライドして、パラメータを含める
    async def _create_chat_completion(self, *args, **kwargs):
        """Override to include temperature, thinking and other parameters"""
        kwargs["temperature"] = self.temperature
        
        # Add thinking parameter if enabled
        # 拡張思考が有効な場合はthinkingパラメータを追加
        if self.thinking:
            kwargs["thinking"] = True
            
        # Add any other custom parameters
        # その他のカスタムパラメータを追加
        kwargs.update(self.kwargs)
        
        return await super()._create_chat_completion(*args, **kwargs)

# Create an alias for convenience
# 利便性のためのエイリアスを作成
ClaudeModel = AnthropicAIChatCompletionsModel 