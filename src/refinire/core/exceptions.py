#!/usr/bin/env python3
"""
Refinire Custom Exceptions
Refinire カスタム例外

This module defines custom exceptions for Refinire that wrap underlying provider errors
to provide a consistent error interface across different LLM providers.
このモジュールでは、異なるLLMプロバイダーにわたって一貫したエラーインターフェースを提供するため、
基盤となるプロバイダーエラーをラップするRefinireのカスタム例外を定義します。
"""

from typing import Optional, Dict, Any


class RefinireError(Exception):
    """
    Base exception class for all Refinire errors
    すべてのRefinireエラーのベース例外クラス
    
    Attributes:
        message: Error message / エラーメッセージ
        details: Additional error details / 追加エラー詳細
        provider: Provider name that caused the error / エラーを引き起こしたプロバイダー名
    """
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None, 
        provider: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.provider = provider
    
    def __str__(self) -> str:
        provider_info = f" (Provider: {self.provider})" if self.provider else ""
        return f"{self.message}{provider_info}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message='{self.message}', provider='{self.provider}')"


class RefinireNetworkError(RefinireError):
    """
    Network-related errors (connection failures, timeouts, etc.)
    ネットワーク関連エラー（接続失敗、タイムアウトなど）
    
    This exception is raised when network communication with LLM providers fails.
    この例外は、LLMプロバイダーとのネットワーク通信が失敗した場合に発生します。
    """
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None, 
        provider: Optional[str] = None,
        error_type: Optional[str] = None
    ):
        super().__init__(message, details, provider)
        self.error_type = error_type  # 'connection', 'timeout', 'dns', etc.


class RefinireConnectionError(RefinireNetworkError):
    """
    Connection establishment failures
    接続確立の失敗
    
    Raised when unable to establish a connection to the LLM provider.
    LLMプロバイダーへの接続を確立できない場合に発生します。
    """
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None, 
        provider: Optional[str] = None
    ):
        super().__init__(message, details, provider, error_type="connection")


class RefinireTimeoutError(RefinireNetworkError):
    """
    Request timeout errors
    リクエストタイムアウトエラー
    
    Raised when a request to the LLM provider times out.
    LLMプロバイダーへのリクエストがタイムアウトした場合に発生します。
    """
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None, 
        provider: Optional[str] = None,
        timeout_duration: Optional[float] = None
    ):
        super().__init__(message, details, provider, error_type="timeout")
        self.timeout_duration = timeout_duration


class RefinireAuthenticationError(RefinireError):
    """
    Authentication and authorization errors
    認証・認可エラー
    
    Raised when API key is invalid, expired, or lacks required permissions.
    APIキーが無効、期限切れ、または必要な権限がない場合に発生します。
    """
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None, 
        provider: Optional[str] = None
    ):
        super().__init__(message, details, provider)


class RefinireRateLimitError(RefinireError):
    """
    Rate limiting errors
    レート制限エラー
    
    Raised when API rate limits are exceeded.
    APIレート制限を超過した場合に発生します。
    """
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None, 
        provider: Optional[str] = None,
        retry_after: Optional[float] = None
    ):
        super().__init__(message, details, provider)
        self.retry_after = retry_after  # Seconds until retry is allowed


class RefinireAPIError(RefinireError):
    """
    General API errors (4xx, 5xx status codes)
    一般的なAPIエラー（4xx、5xxステータスコード）
    
    Raised for HTTP status errors that don't fall into other categories.
    他のカテゴリーに該当しないHTTPステータスエラーに対して発生します。
    """
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None, 
        provider: Optional[str] = None,
        status_code: Optional[int] = None
    ):
        super().__init__(message, details, provider)
        self.status_code = status_code


class RefinireModelError(RefinireError):
    """
    Model-specific errors (model not found, model overloaded, etc.)
    モデル固有のエラー（モデルが見つからない、モデルが過負荷など）
    
    Raised when there are issues with the specific model being used.
    使用されている特定のモデルに問題がある場合に発生します。
    """
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None, 
        provider: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        super().__init__(message, details, provider)
        self.model_name = model_name


class RefinireConfigurationError(RefinireError):
    """
    Configuration errors (missing API keys, invalid parameters, etc.)
    設定エラー（APIキーの欠如、無効なパラメータなど）
    
    Raised when there are configuration issues with Refinire setup.
    Refinire設定に設定の問題がある場合に発生します。
    """
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None, 
        provider: Optional[str] = None
    ):
        super().__init__(message, details, provider)


class RefinireValidationError(RefinireError):
    """
    Input validation errors
    入力検証エラー
    
    Raised when input parameters fail validation.
    入力パラメータが検証に失敗した場合に発生します。
    """
    
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None, 
        provider: Optional[str] = None,
        field_name: Optional[str] = None
    ):
        super().__init__(message, details, provider)
        self.field_name = field_name


# Exception mapping utilities
# 例外マッピングユーティリティ

def map_openai_exception(exc: Exception, provider: str = "openai") -> RefinireError:
    """
    Map OpenAI exceptions to Refinire custom exceptions
    OpenAI例外をRefinireカスタム例外にマッピング
    
    Args:
        exc: Original OpenAI exception / 元のOpenAI例外
        provider: Provider name / プロバイダー名
        
    Returns:
        RefinireError: Mapped Refinire exception / マッピングされたRefinire例外
    """
    import openai
    
    exc_type = type(exc)
    message = str(exc)
    details = {"original_exception": exc_type.__name__}
    
    # Extract additional details if available
    # 利用可能な場合は追加詳細を抽出
    if hasattr(exc, 'response') and exc.response is not None:
        details["status_code"] = getattr(exc.response, 'status_code', None)
        details["headers"] = dict(getattr(exc.response, 'headers', {}))
    
    # Map specific OpenAI exceptions
    # 特定のOpenAI例外をマッピング
    if exc_type == openai.APIConnectionError:
        return RefinireConnectionError(
            message=f"Failed to connect to {provider} API: {message}",
            details=details,
            provider=provider
        )
    
    elif exc_type == openai.APITimeoutError:
        return RefinireTimeoutError(
            message=f"Request to {provider} API timed out: {message}",
            details=details,
            provider=provider
        )
    
    elif exc_type == openai.AuthenticationError:
        return RefinireAuthenticationError(
            message=f"Authentication failed for {provider}: {message}",
            details=details,
            provider=provider
        )
    
    elif exc_type == openai.RateLimitError:
        retry_after = None
        if hasattr(exc, 'response') and exc.response is not None:
            retry_after = exc.response.headers.get('retry-after')
            if retry_after:
                try:
                    retry_after = float(retry_after)
                except ValueError:
                    retry_after = None
        
        return RefinireRateLimitError(
            message=f"Rate limit exceeded for {provider}: {message}",
            details=details,
            provider=provider,
            retry_after=retry_after
        )
    
    elif exc_type == openai.APIStatusError:
        status_code = getattr(exc, 'status_code', None)
        
        # Handle specific status codes
        # 特定のステータスコードを処理
        if status_code == 401:
            return RefinireAuthenticationError(
                message=f"Authentication failed for {provider}: {message}",
                details=details,
                provider=provider
            )
        elif status_code == 429:
            return RefinireRateLimitError(
                message=f"Rate limit exceeded for {provider}: {message}",
                details=details,
                provider=provider
            )
        elif status_code == 404:
            return RefinireModelError(
                message=f"Model not found for {provider}: {message}",
                details=details,
                provider=provider
            )
        else:
            return RefinireAPIError(
                message=f"API error from {provider}: {message}",
                details=details,
                provider=provider,
                status_code=status_code
            )
    
    elif exc_type == openai.APIError:
        return RefinireAPIError(
            message=f"API error from {provider}: {message}",
            details=details,
            provider=provider
        )
    
    else:
        # Fallback for unknown OpenAI exceptions
        # 未知のOpenAI例外のフォールバック
        return RefinireError(
            message=f"Unknown error from {provider}: {message}",
            details=details,
            provider=provider
        )


def map_httpx_exception(exc: Exception, provider: str = "unknown") -> RefinireError:
    """
    Map httpx exceptions to Refinire custom exceptions
    httpx例外をRefinireカスタム例外にマッピング
    
    Args:
        exc: Original httpx exception / 元のhttpx例外
        provider: Provider name / プロバイダー名
        
    Returns:
        RefinireError: Mapped Refinire exception / マッピングされたRefinire例外
    """
    import httpx
    
    exc_type = type(exc)
    message = str(exc)
    details = {"original_exception": exc_type.__name__}
    
    if exc_type == httpx.ConnectError:
        return RefinireConnectionError(
            message=f"Failed to connect to {provider}: {message}",
            details=details,
            provider=provider
        )
    
    elif exc_type == httpx.TimeoutException:
        return RefinireTimeoutError(
            message=f"Request to {provider} timed out: {message}",
            details=details,
            provider=provider
        )
    
    elif exc_type == httpx.HTTPStatusError:
        status_code = getattr(exc, 'response', {}).status_code if hasattr(exc, 'response') else None
        return RefinireAPIError(
            message=f"HTTP error from {provider}: {message}",
            details=details,
            provider=provider,
            status_code=status_code
        )
    
    elif exc_type == httpx.RequestError:
        return RefinireNetworkError(
            message=f"Network error with {provider}: {message}",
            details=details,
            provider=provider,
            error_type="request"
        )
    
    else:
        # Fallback for unknown httpx exceptions
        # 未知のhttpx例外のフォールバック
        return RefinireError(
            message=f"Unknown network error with {provider}: {message}",
            details=details,
            provider=provider
        )