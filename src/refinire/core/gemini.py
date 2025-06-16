"""
Gemini model implementation for OpenAI Agents
OpenAI AgentsのためのGeminiモデル実装
"""
import os
from typing import Any, Dict, List, Optional, Union
from agents import OpenAIChatCompletionsModel
from openai import AsyncOpenAI


class GeminiModel(OpenAIChatCompletionsModel):
    """
    Gemini model implementation that extends OpenAI's chat completions model
    OpenAIのチャット補完モデルを拡張したGeminiモデルの実装
    """

    def __init__(
        self,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.3,
        api_key: str = None,
        base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/",
        **kwargs: Any,
    ) -> None:
        """
        Initialize the Gemini model with OpenAI compatible interface
        OpenAI互換インターフェースでGeminiモデルを初期化する

        Args:
            model (str): Name of the Gemini model to use (e.g. "gemini-2.0-flash")
                使用するGeminiモデルの名前（例："gemini-2.0-flash"）
            temperature (float): Sampling temperature between 0 and 1
                サンプリング温度（0から1の間）
            api_key (str): Gemini API key
                Gemini APIキー
            base_url (str): Base URL for the Gemini API
                Gemini APIのベースURL
            **kwargs: Additional arguments to pass to the OpenAI API
                OpenAI APIに渡す追加の引数
        """
        if base_url == None:
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"

        # api_key が None の場合は環境変数から取得
        if api_key is None:
            api_key = os.environ.get("GOOGLE_API_KEY")
            if api_key is None:
                raise ValueError("Google API key is required. Get one from https://ai.google.dev/")
        
        # Create AsyncOpenAI client with Gemini base URL
        # GeminiのベースURLでAsyncOpenAIクライアントを作成
        openai_client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        
        # Store parameters for later use in API calls
        # 後でAPIコールで使用するためにパラメータを保存
        self.temperature = temperature
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
        """Override to include temperature and other parameters"""
        kwargs["temperature"] = self.temperature
        kwargs.update(self.kwargs)
        return await super()._create_chat_completion(*args, **kwargs)
