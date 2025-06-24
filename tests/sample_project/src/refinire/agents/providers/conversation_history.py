"""
Conversation History Provider
会話履歴プロバイダー

This is a test file for SourceCodeProvider testing.
SourceCodeProviderのテスト用ファイルです。
"""

from typing import List, Dict, Any, Optional
from src.refinire.agents.context_provider import ContextProvider


class ConversationHistoryProvider(ContextProvider):
    """
    Provides conversation history context
    会話履歴コンテキストを提供
    """
    
    def __init__(self, history: List[str] = None, max_items: int = 10):
        self.history = history or []
        self.max_items = max_items
    
    def get_context(self, query: str, previous_context: Optional[str] = None, **kwargs) -> str:
        """Get conversation history context"""
        if not self.history:
            return ""
        recent_history = self.history[-self.max_items:]
        return "\n".join(recent_history)
    
    def update(self, interaction: Dict[str, Any]) -> None:
        """Update with new interaction"""
        user_input = interaction.get("user_input", "")
        result = interaction.get("result", "")
        if user_input and result:
            conversation_entry = f"User: {user_input}\nAssistant: {result}"
            self.history.append(conversation_entry)
            if len(self.history) > self.max_items:
                self.history = self.history[-self.max_items:]
    
    def clear(self) -> None:
        """Clear conversation history"""
        self.history.clear() 