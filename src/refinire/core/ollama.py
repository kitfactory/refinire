"""
Ollama model implementation for OpenAI Agents
OpenAI AgentsのためのOllamaモデル実装
"""
import os
from typing import Any, Dict, List, Optional, Union
from agents import OpenAIChatCompletionsModel
from openai import AsyncOpenAI

class OllamaModel(OpenAIChatCompletionsModel):
    """
    Ollama model implementation that extends OpenAI's chat completions model
    OpenAIのチャット補完モデルを拡張したOllamaモデルの実装
    """

    def __init__(
        self,
        model: str = "phi4-mini:latest",
        temperature: float = 0.3,
        base_url: str = None, # デフォルトのURL
        **kwargs: Any,
    ) -> None:
        """
        Initialize the Ollama model with OpenAI compatible interface
        OpenAI互換インターフェースでOllamaモデルを初期化する

        Args:
            model (str): Name of the Ollama model to use (e.g. "phi4-mini")
                使用するOllamaモデルの名前（例："phi4-mini"）
            temperature (float): Sampling temperature between 0 and 1
                サンプリング温度（0から1の間）
            base_url (str): Base URL for the Ollama API
                Ollama APIのベースURL
            **kwargs: Additional arguments to pass to the OpenAI API
                OpenAI APIに渡す追加の引数
        """
        # get_llm経由で base_url が None の場合はデフォルトの URL を設定
        if base_url == None:
            base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        
        base_url = base_url.rstrip("/")
        if not base_url.endswith("v1"):
            base_url = base_url + "/v1"

        # Create AsyncOpenAI client with Ollama base URL
        # OllamaのベースURLでAsyncOpenAIクライアントを作成
        openai_client = AsyncOpenAI(base_url=base_url, api_key="ollama")
        
        # Store the AsyncOpenAI client on the instance for direct access
        # テストで参照できるよう AsyncOpenAI クライアントをインスタンスに保存する
        self.openai_client = openai_client
        
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
