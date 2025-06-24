"""
Conversation History Provider
会話履歴プロバイダー

This module provides conversation history context for RefinireAgent.
RefinireAgentの会話履歴コンテキストを提供します。
"""

from typing import List, Dict, Any, ClassVar, Optional
from refinire.agents.context_provider import ContextProvider


class ConversationHistoryProvider(ContextProvider):
    """
    Provides conversation history context
    会話履歴コンテキストを提供
    
    This provider manages conversation history and provides it as context
    for the current query. It maintains a list of conversation items and
    can limit the number of items to prevent context overflow.
    
    このプロバイダーは会話履歴を管理し、現在のクエリ用のコンテキストとして
    提供します。会話アイテムのリストを維持し、コンテキストオーバーフローを
    防ぐためにアイテム数を制限できます。
    """
    
    provider_name: ClassVar[str] = "conversation"
    
    def __init__(self, history: List[str] = None, max_items: int = 10):
        """
        Initialize conversation history provider
        会話履歴プロバイダーを初期化
        
        Args:
            history: Initial conversation history / 初期会話履歴
            max_items: Maximum number of conversation items to keep / 保持する最大会話アイテム数
        """
        self.history = history or []
        self.max_items = max_items
    
    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """
        Get configuration schema for conversation history provider
        会話履歴プロバイダーの設定スキーマを取得
        
        Returns:
            Dict[str, Any]: Configuration schema with parameter descriptions
            Dict[str, Any]: パラメータ説明を含む設定スキーマ
        """
        return {
            "description": "Provides conversation history context",
            "parameters": {
                "max_items": {
                    "type": "int",
                    "default": 10,
                    "description": "Maximum number of conversation items to keep"
                }
            },
            "example": "conversation:\n  max_items: 10"
        }
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'ConversationHistoryProvider':
        """
        Create conversation history provider from configuration
        設定から会話履歴プロバイダーを作成
        
        Args:
            config: Configuration dictionary / 設定辞書
            
        Returns:
            ConversationHistoryProvider: Provider instance / プロバイダーインスタンス
        """
        return cls(**config)
    
    def get_context(self, query: str, previous_context: Optional[str] = None, **kwargs) -> str:
        """
        Get conversation history context
        会話履歴コンテキストを取得
        
        Args:
            query: Current user query / 現在のユーザークエリ
            previous_context: Context provided by previous providers / 前のプロバイダーが提供したコンテキスト
            **kwargs: Additional parameters / 追加パラメータ
            
        Returns:
            str: Conversation history as context string / コンテキスト文字列としての会話履歴
        """
        if not self.history or self.max_items <= 0:
            return ""
        
        # Return the most recent conversation items up to max_items
        # 最大アイテム数までの最新の会話アイテムを返す
        recent_history = self.history[-self.max_items:]
        return "\n".join(recent_history)
    
    def update(self, interaction: Dict[str, Any]) -> None:
        """
        Update provider with new interaction
        新しい対話でプロバイダーを更新
        
        Args:
            interaction: Interaction data containing user_input and result / user_inputとresultを含む対話データ
        """
        user_input = interaction.get("user_input", "")
        result = interaction.get("result", "")
        
        if user_input and result and self.max_items > 0:
            # Create conversation entry in the format "User: ...\nAssistant: ..."
            # "User: ...\nAssistant: ..." 形式で会話エントリを作成
            conversation_entry = f"User: {user_input}\nAssistant: {result}"
            self.history.append(conversation_entry)
            
            # Trim history if it exceeds max_items
            # 履歴が最大アイテム数を超えた場合は切り詰める
            if len(self.history) > self.max_items:
                self.history = self.history[-self.max_items:]
    
    def clear(self) -> None:
        """
        Clear all stored conversation history
        保存されたすべての会話履歴をクリア
        """
        self.history.clear()
    
    def add_conversation(self, user_input: str, assistant_response: str) -> None:
        """
        Add a conversation entry directly
        会話エントリを直接追加
        
        Args:
            user_input: User input / ユーザー入力
            assistant_response: Assistant response / アシスタントの応答
        """
        if self.max_items > 0:
            conversation_entry = f"User: {user_input}\nAssistant: {assistant_response}"
            self.history.append(conversation_entry)
            
            # Trim history if it exceeds max_items
            # 履歴が最大アイテム数を超えた場合は切り詰める
            if len(self.history) > self.max_items:
                self.history = self.history[-self.max_items:]
    
    def get_history_count(self) -> int:
        """
        Get the current number of conversation items
        現在の会話アイテム数を取得
        
        Returns:
            int: Number of conversation items / 会話アイテム数
        """
        return len(self.history)
    
    def is_empty(self) -> bool:
        """
        Check if the conversation history is empty
        会話履歴が空かどうかをチェック
        
        Returns:
            bool: True if history is empty, False otherwise / 履歴が空の場合はTrue、そうでなければFalse
        """
        return len(self.history) == 0 