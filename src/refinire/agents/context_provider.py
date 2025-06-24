"""
Context Provider Interface
コンテキストプロバイダーインターフェース

This module provides the base interface for all context providers in RefinireAgent.
RefinireAgentのすべてのコンテキストプロバイダーの基本インターフェースを提供します。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, ClassVar, Optional


class ContextProvider(ABC):
    """
    Single interface for all context providers
    すべてのコンテキストプロバイダーの唯一のインターフェース
    
    This abstract base class defines the contract that all context providers
    must implement. It provides a unified way to manage context information
    such as conversation history, file contents, and external data sources.
    
    この抽象基底クラスは、すべてのコンテキストプロバイダーが実装しなければならない
    契約を定義します。会話履歴、ファイル内容、外部データソースなどの
    コンテキスト情報を管理する統一された方法を提供します。
    """
    
    # Class variable for provider name
    # プロバイダー名のクラス変数
    provider_name: ClassVar[str] = "base"
    
    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """
        Get configuration schema for this provider
        このプロバイダーの設定スキーマを取得
        
        Returns:
            Dict[str, Any]: Configuration schema with parameter descriptions
            Dict[str, Any]: パラメータ説明を含む設定スキーマ
        """
        return {
            "description": "Base context provider",
            "parameters": {},
            "example": "base: {}"
        }
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'ContextProvider':
        """
        Create provider instance from configuration
        設定からプロバイダーインスタンスを作成
        
        Args:
            config: Configuration dictionary / 設定辞書
            
        Returns:
            ContextProvider: Provider instance / プロバイダーインスタンス
        """
        return cls(**config)
    
    @abstractmethod
    def get_context(self, query: str, previous_context: Optional[str] = None, **kwargs) -> str:
        """
        Get context for the given query
        与えられたクエリ用のコンテキストを取得
        
        Args:
            query: Current user query / 現在のユーザークエリ
            previous_context: Context provided by previous providers / 前のプロバイダーが提供したコンテキスト
            **kwargs: Additional parameters / 追加パラメータ
            
        Returns:
            str: Context string (empty string if no context) / コンテキスト文字列（コンテキストがない場合は空文字列）
        """
        pass
    
    @abstractmethod
    def update(self, interaction: Dict[str, Any]) -> None:
        """
        Update provider with new interaction
        新しい対話でプロバイダーを更新
        
        Args:
            interaction: Interaction data / 対話データ
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """
        Clear all stored context
        保存されたすべてのコンテキストをクリア
        """
        pass 