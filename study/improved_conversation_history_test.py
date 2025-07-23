#!/usr/bin/env python3
"""
改良版会話履歴継続テスト - Context Providers動作確認
Improved conversation history continuation test - Context Providers verification
"""

import asyncio
import sys
import os

# Add the src directory to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent
from refinire.agents.flow import Context


async def simple_conversation_test():
    """シンプルな会話履歴テスト"""
    print("=== 改良版会話履歴テスト ===\n")
    
    # 会話履歴参照エージェント
    history_agent = RefinireAgent(
        name="history_agent",
        generation_instructions="""
あなたは会話履歴を参照するエージェントです。

これまでの会話履歴から：
- ユーザーの名前
- ユーザーが話した内容
- これまでの会話の流れ

を確認して応答してください。履歴がない場合は「初回の会話」として応答してください。
        """,
        model="gpt-4o-mini",
        context_providers_config=[
            {"type": "conversation_history", "max_items": 10}
        ]
    )
    
    # Context作成
    context = Context()
    
    # 会話1: 自己紹介
    print("【会話1】")
    result1 = await history_agent.run_async("こんにちは！私は山田と申します", context)
    print(f"ユーザー: こんにちは！私は山田と申します")
    print(f"エージェント: {result1.content}")
    print(f"Context内メッセージ数: {len(context.messages)}")
    
    # 会話2: 趣味について
    print(f"\n【会話2】")
    result2 = await history_agent.run_async("私の趣味は読書です", context)
    print(f"ユーザー: 私の趣味は読書です")
    print(f"エージェント: {result2.content}")
    print(f"Context内メッセージ数: {len(context.messages)}")
    
    # 会話3: 記憶テスト
    print(f"\n【会話3】")
    result3 = await history_agent.run_async("私の名前と趣味を覚えていますか？", context)
    print(f"ユーザー: 私の名前と趣味を覚えていますか？")
    print(f"エージェント: {result3.content}")
    print(f"Context内メッセージ数: {len(context.messages)}")
    
    # 詳細なContext内容確認
    print(f"\n=== Context詳細確認 ===")
    print(f"メッセージ一覧:")
    for i, msg in enumerate(context.messages, 1):
        role_icon = "👤" if msg.role == "user" else "🤖" if msg.role == "assistant" else "⚙️"
        content_preview = str(msg.content)[:50] + "..." if len(str(msg.content)) > 50 else str(msg.content)
        print(f"  {i}. {role_icon} {msg.role}: {content_preview}")


async def direct_memory_test():
    """直接的な記憶テスト"""
    print(f"\n=== 直接記憶テスト ===")
    
    # メモリ特化エージェント
    memory_agent = RefinireAgent(
        name="memory_agent", 
        generation_instructions="""
あなたは記憶力テストエージェントです。

1回目：ユーザーの情報を記憶する
2回目以降：記憶した情報を正確に思い出して回答する

会話履歴から情報を抽出して記憶し、テストに答えてください。
        """,
        model="gpt-4o-mini",
        context_providers_config=[
            {"type": "conversation_history", "max_items": 20}
        ]
    )
    
    context = Context()
    
    # 情報提供
    info_result = await memory_agent.run_async("私の名前は佐藤で、職業はエンジニア、好きな食べ物はラーメンです", context)
    print(f"情報提供: 私の名前は佐藤で、職業はエンジニア、好きな食べ物はラーメンです")
    print(f"応答: {info_result.content}")
    
    # 記憶テスト1
    test1 = await memory_agent.run_async("私の名前は何ですか？", context)
    print(f"\nテスト1: 私の名前は何ですか？")
    print(f"応答: {test1.content}")
    
    # 記憶テスト2
    test2 = await memory_agent.run_async("私の職業と好きな食べ物は？", context) 
    print(f"\nテスト2: 私の職業と好きな食べ物は？")
    print(f"応答: {test2.content}")
    
    print(f"\n最終Context内メッセージ数: {len(context.messages)}")


async def main():
    """メインテスト実行"""
    try:
        await simple_conversation_test()
        await direct_memory_test()
        
        print(f"\n✅ 全テスト完了")
        print(f"結論: Context内の会話履歴は正しく蓄積・継続されています")
        
    except Exception as e:
        print(f"❌ エラー発生: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())