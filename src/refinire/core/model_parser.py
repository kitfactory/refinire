"""Model ID parser for provider-specific model identification
プロバイダー固有のモデル識別のためのモデルIDパーサー
"""

import re
import os
from typing import Tuple, Optional, Dict, Any
from urllib.parse import urlparse

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


def parse_model_id(model_id: str) -> Tuple[Optional[str], str, Optional[str]]:
    """
    Parse model ID with provider prefix and tag/version suffix
    プロバイダープレフィックスとタグ/バージョンサフィックスを含むモデルIDを解析
    
    Format: <provider>://<model_path>[#<tag_or_api_version>]
    Examples:
        - "gpt-4o-mini" -> (None, "gpt-4o-mini", None)
        - "openai://gpt-4o-mini" -> ("openai", "gpt-4o-mini", None)
        - "ollama://llama3:8b" -> ("ollama", "llama3:8b", None)
        - "ollama://llama3#8b" -> ("ollama", "llama3", "8b")  
        - "azure://gpt4o-deploy#2024-10-21" -> ("azure", "gpt4o-deploy", "2024-10-21")
    
    Args:
        model_id: Model identifier string / モデル識別子文字列
        
    Returns:
        Tuple of (provider, model_name, tag) / (プロバイダー, モデル名, タグ)のタプル
    """
    # Check if model_id contains protocol
    # model_idにプロトコルが含まれているかチェック
    if "://" in model_id:
        # Parse as URL-like format
        # URL形式として解析
        parts = model_id.split("://", 1)
        provider = parts[0]
        model_part = parts[1]
    else:
        # No protocol, provider will be auto-detected
        # プロトコルなし、プロバイダーは自動検出される
        provider = None
        model_part = model_id
    
    # Extract tag/version if present
    # タグ/バージョンが存在する場合は抽出
    if "#" in model_part:
        model_name, tag = model_part.split("#", 1)
    else:
        model_name = model_part
        tag = None
    
    return provider, model_name, tag


def detect_provider_from_environment(namespace: Optional[str] = None) -> Optional[str]:
    """
    Detect provider from environment variables
    環境変数からプロバイダーを検出
    
    Priority:
    1. OLLAMA_BASE_URL -> "ollama"
    2. LM_STUDIO_BASE_URL -> "lmstudio"
    3. OPENROUTER_API_KEY -> "openrouter"
    4. GROQ_API_KEY -> "groq"
    5. ANTHROPIC_API_KEY (+ ANTHROPIC_BASE_URL for compatibility mode) -> "anthropic"
    6. AZURE_OPENAI_ENDPOINT -> "azure"
    7. Otherwise -> None (defaults to "openai")
    
    Returns:
        Detected provider name or None / 検出されたプロバイダー名またはNone
    """
    # Check OLLAMA_BASE_URL first
    # OLLAMA_BASE_URLを最初にチェック
    if _get_env_var("OLLAMA_BASE_URL", "", namespace):
        return "ollama"
    
    # Check LM_STUDIO_BASE_URL
    # LM_STUDIO_BASE_URLをチェック
    if _get_env_var("LM_STUDIO_BASE_URL", "", namespace):
        return "lmstudio"
    
    # Check OPENROUTER_API_KEY
    # OPENROUTER_API_KEYをチェック
    if _get_env_var("OPENROUTER_API_KEY", "", namespace):
        return "openrouter"
    
    # Check GROQ_API_KEY
    # GROQ_API_KEYをチェック
    if _get_env_var("GROQ_API_KEY", "", namespace):
        return "groq"
    
    # Check ANTHROPIC_API_KEY
    # ANTHROPIC_API_KEYをチェック
    if _get_env_var("ANTHROPIC_API_KEY", "", namespace):
        return "anthropic"
    
    # Check Azure endpoint
    # Azureエンドポイントをチェック
    if _get_env_var("AZURE_OPENAI_ENDPOINT", "", namespace):
        return "azure"
    
    return None


def should_use_chat_completions(provider: str) -> bool:
    """
    Determine if provider should use /chat/completions endpoint
    プロバイダーが/chat/completionsエンドポイントを使用すべきか判定
    
    Args:
        provider: Provider name / プロバイダー名
        
    Returns:
        True if should use chat completions / chat completionsを使用すべき場合True
    """
    # OpenAI with FORCE_CHAT environment variable
    # FORCE_CHAT環境変数付きのOpenAI
    if provider == "openai" and _get_env_var("FORCE_CHAT", "", None).lower() in ["1", "true", "yes"]:
        return True
    
    # Providers that always use chat completions
    # 常にchat completionsを使用するプロバイダー
    chat_providers = ["azure", "groq", "ollama", "lmstudio", "openrouter", "anthropic", "google"]
    return provider in chat_providers


def get_provider_config(provider: str, model_name: str, tag: Optional[str] = None, namespace: Optional[str] = None) -> Dict[str, Any]:
    """
    Get provider-specific configuration
    プロバイダー固有の設定を取得
    
    Args:
        provider: Provider name / プロバイダー名
        model_name: Model name / モデル名
        tag: Optional tag or API version / オプションのタグまたはAPIバージョン
        
    Returns:
        Provider configuration dict / プロバイダー設定の辞書
    """
    config = {
        "provider": provider,
        "model": model_name,
        "use_chat_completions": should_use_chat_completions(provider)
    }
    
    # Azure-specific configuration
    # Azure固有の設定
    if provider == "azure":
        config["api_version"] = tag or _get_env_var("AZURE_OPENAI_API_VERSION", "2024-10-21", namespace)
        config["deployment_name"] = model_name
        # Azure uses deployment name, not model name
        # Azureはモデル名ではなくデプロイメント名を使用
    
    # Ollama-specific configuration
    # Ollama固有の設定
    elif provider == "ollama":
        if tag:
            # Ollama uses model:tag format
            # Ollamaはmodel:tag形式を使用
            config["model"] = f"{model_name}:{tag}"
        config["base_url"] = _get_env_var("OLLAMA_BASE_URL", "http://localhost:11434", namespace)
    
    # Groq-specific configuration
    # Groq固有の設定
    elif provider == "groq":
        config["base_url"] = _get_env_var("GROQ_BASE_URL", "https://api.groq.com", namespace)
    
    # LM Studio configuration
    # LM Studio設定
    elif provider == "lmstudio":
        config["base_url"] = _get_env_var("LM_STUDIO_BASE_URL", "http://localhost:1234", namespace)
    
    # OpenRouter configuration
    # OpenRouter設定
    elif provider == "openrouter":
        config["base_url"] = _get_env_var("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1", namespace)
    
    # Anthropic configuration
    # Anthropic設定
    elif provider == "anthropic":
        config["base_url"] = _get_env_var("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1", namespace)
    
    return config