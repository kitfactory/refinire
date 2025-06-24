"""
Context Provider Interface
コンテキストプロバイダーインターフェース

This is a test file for SourceCodeProvider testing.
SourceCodeProviderのテスト用ファイルです。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class ContextProvider(ABC):
    """
    Abstract base class for context providers
    コンテキストプロバイダーの抽象基底クラス
    """
    
    @abstractmethod
    def get_context(self, query: str, previous_context: Optional[str] = None, **kwargs) -> str:
        """Get context for the given query"""
        pass
    
    @abstractmethod
    def update(self, interaction: Dict[str, Any]) -> None:
        """Update provider with new interaction"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear stored data"""
        pass 