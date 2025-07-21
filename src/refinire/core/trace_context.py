"""
Trace context management utilities for Refinire.

English: Provides utilities for managing trace contexts to avoid nested traces
日本語: ネストしたトレースを回避するためのトレースコンテキスト管理ユーティリティを提供
"""

from typing import Optional, Any


def get_current_trace_context() -> Optional[Any]:
    """
    Get the current active trace context if available.
    
    English: Checks if there's an active trace context from the OpenAI Agents SDK
    日本語: OpenAI Agents SDKからアクティブなトレースコンテキストがあるかチェック
    
    Returns:
        Current trace context if available, None otherwise
    """
    try:
        from agents.tracing import get_current_trace
        current_trace = get_current_trace()
        return current_trace if current_trace else None
    except ImportError:
        # agents.tracing not available
        return None
    except Exception:
        # Any other error - assume no trace context
        return None


def has_active_trace_context() -> bool:
    """
    Check if there's an active trace context.
    
    English: Simple boolean check for active trace context
    日本語: アクティブなトレースコンテキストの簡単なブール値チェック
    
    Returns:
        True if there's an active trace context, False otherwise
    """
    return get_current_trace_context() is not None


def create_trace_context_if_needed(trace_name: str):
    """
    Create a trace context only if there isn't one already active.
    
    English: Context manager that creates a trace only when no active trace exists
    日本語: アクティブなトレースが存在しない場合のみトレースを作成するコンテキストマネージャー
    
    Args:
        trace_name: Name for the trace if one needs to be created
        
    Returns:
        Context manager that handles trace creation appropriately
    """
    try:
        from agents.tracing import trace, get_current_trace
        
        current_trace = get_current_trace()
        if current_trace:
            # Already in a trace context - use no-op context manager
            # 既にトレースコンテキスト内 - 何もしないコンテキストマネージャーを使用
            from contextlib import nullcontext
            return nullcontext()
        else:
            # No active trace - create new one
            # アクティブなトレースなし - 新しいものを作成
            return trace(trace_name)
            
    except ImportError:
        # agents.tracing not available - use no-op context manager
        # agents.tracingが利用できません - 何もしないコンテキストマネージャーを使用
        from contextlib import nullcontext
        return nullcontext()
    except Exception:
        # Any other error - use no-op context manager
        # その他のエラー - 何もしないコンテキストマネージャーを使用
        from contextlib import nullcontext
        return nullcontext()


class TraceContextManager:
    """
    A context manager for intelligent trace creation.
    
    English: Manages trace context creation with awareness of existing traces
    日本語: 既存のトレースを認識してトレースコンテキスト作成を管理
    """
    
    def __init__(self, trace_name: str, force_new_trace: bool = False):
        """
        Initialize the trace context manager.
        
        Args:
            trace_name: Name for the trace if one needs to be created
            force_new_trace: If True, always create a new trace (default: False)
        """
        self.trace_name = trace_name
        self.force_new_trace = force_new_trace
        self._trace_context = None
        self._should_create_trace = False
        
    def __enter__(self):
        """Enter the trace context."""
        try:
            from agents.tracing import trace, get_current_trace
            
            current_trace = get_current_trace()
            if current_trace and not self.force_new_trace:
                # Already in a trace context - don't create new one
                # 既にトレースコンテキスト内 - 新しいものを作成しない
                self._should_create_trace = False
                return self
            else:
                # No active trace or forced new trace - create one
                # アクティブなトレースなしまたは強制新規トレース - 作成
                self._should_create_trace = True
                self._trace_context = trace(self.trace_name)
                return self._trace_context.__enter__()
                
        except ImportError:
            # agents.tracing not available
            self._should_create_trace = False
            return self
        except Exception:
            # Any other error
            self._should_create_trace = False
            return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the trace context."""
        if self._should_create_trace and self._trace_context:
            return self._trace_context.__exit__(exc_type, exc_val, exc_tb)
        return None