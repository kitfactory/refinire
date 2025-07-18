"""
Gemini model implementation for OpenAI Agents
OpenAI AgentsのためのGeminiモデル実装
"""
import os
from typing import Any, Dict, List, Optional, Union
from agents import OpenAIChatCompletionsModel
from openai import AsyncOpenAI

# English: Import oneenv for environment variable management
# 日本語: 環境変数管理のためのoneenvをインポート
try:
    import oneenv
except ImportError:
    oneenv = None


def _get_env_var(key: str, default: str = "", namespace: Optional[str] = None) -> str:
    """
    Get environment variable value using oneenv or fallback to os.environ.
    
    English: Get environment variable value using oneenv or fallback to os.environ.
    日本語: oneenvを使用して環境変数値を取得、利用できない場合はos.environにフォールバック。
    
    Args:
        key (str): Environment variable key
        default (str): Default value if key not found
        namespace (Optional[str]): oneenv namespace
        
    Returns:
        str: Environment variable value
    """
    if oneenv is not None:
        try:
            return oneenv.env().load(namespace or "").get(key, default)
        except Exception:
            # Fallback to os.environ if oneenv fails
            return os.environ.get(key, default)
    else:
        # Fallback to os.environ if oneenv is not available
        return os.environ.get(key, default)


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
        namespace: Optional[str] = None,
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
            namespace (Optional[str]): Environment variable namespace for oneenv
                oneenv用の環境変数名前空間
            **kwargs: Additional arguments to pass to the OpenAI API
                OpenAI APIに渡す追加の引数
        """
        if base_url == None:
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"

        # api_key が None の場合は環境変数から取得
        if api_key is None:
            api_key = _get_env_var("GOOGLE_API_KEY", "", namespace)
            if not api_key:
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
