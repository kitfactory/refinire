"""
Test Context Provider
コンテキストプロバイダーのテスト

This is a test file for SourceCodeProvider testing.
SourceCodeProviderのテスト用ファイルです。
"""

import pytest
from src.refinire.agents.providers.conversation_history import ConversationHistoryProvider


def test_conversation_history_provider():
    """Test conversation history provider"""
    provider = ConversationHistoryProvider(max_items=3)
    assert provider.max_items == 3
    assert provider.get_context("test") == ""
    
    provider.update({
        "user_input": "Hello",
        "result": "Hi there!"
    })
    
    context = provider.get_context("test")
    assert "User: Hello" in context
    assert "Assistant: Hi there!" in context 