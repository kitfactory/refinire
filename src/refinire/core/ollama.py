"""
Ollama model implementation for OpenAI Agents
OpenAI AgentsのためのOllamaモデル実装
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
        api_key: str = None,
        namespace: Optional[str] = None,
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
            api_key (str): API key (typically not needed for Ollama)
                APIキー（通常Ollamaでは不要）
            namespace (Optional[str]): Environment variable namespace for oneenv
                oneenv用の環境変数名前空間
            **kwargs: Additional arguments to pass to the OpenAI API
                OpenAI APIに渡す追加の引数
        """
        # get_llm経由で base_url が None の場合はデフォルトの URL を設定
        if base_url == None:
            base_url = _get_env_var("OLLAMA_BASE_URL", "http://localhost:11434", namespace)
        
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
