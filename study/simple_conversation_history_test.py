#!/usr/bin/env python3
"""
シンプルな会話履歴継続テスト
Simple conversation history continuation test
"""

import asyncio
import sys
import os

# Add the src directory to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent, Flow
from refinire.agents.flow import Context


def create_conversation_agent():
    """会話エージェント - 履歴を参照して応答"""
    return RefinireAgent(
        name="chat_agent",
        generation_instructions="""
あなたは親しみやすい会話エージェントです。
会話履歴を参照して、これまでの会話内容を考慮した自然な応答をしてください。

会話履歴から：
- ユーザーが言った内容を覚えている
- 前回の会話内容に関連した質問や応答をする
- 会話の流れを自然に継続する

簡潔で親しみやすい応答をしてください。
        """.strip(),
        model="gpt-4o-mini",
        context_providers_config=[
            {"type": "conversation_history", "max_items": 10}
        ],
        routing_instruction="""
会話が3回以上続いた場合は "end_chat" を返してください。
それ以外の場合は "continue" を返してください。
        """.strip()
    )


def create_summary_agent():
    """会話要約エージェント"""
    return RefinireAgent(
        name="summary_agent",
        generation_instructions="""
会話履歴全体を確認し、以下の形式で要約してください：

=== 会話要約 ===
参加者: ユーザーとアシスタント
会話回数: [実際の会話回数]

会話内容:
1. [1回目の内容]
2. [2回目の内容]  
3. [3回目の内容]
...

会話履歴が正しく保持されているか確認できました！
        """.strip(),
        model="gpt-4o-mini",
        context_providers_config=[
            {"type": "conversation_history", "max_items": 20}
        ]
    )


async def test_conversation_history():
    """会話履歴継続テスト"""
    print("=== シンプル会話履歴テスト ===\n")
    
    # エージェント作成
    chat_agent = create_conversation_agent()
    summary_agent = create_summary_agent()
    
    # コンテキスト作成
    context = Context()
    
    # テスト会話リスト
    test_messages = [
        "こんにちは！私は太郎です",
        "今日は晴れていて気分がいいです", 
        "あなたは私の名前を覚えていますか？"
    ]
    
    print("会話開始：")
    print("-" * 40)
    
    # 各メッセージで会話を実行
    for i, message in enumerate(test_messages, 1):
        print(f"\n【会話 {i}】")
        print(f"ユーザー: {message}")
        
        # エージェント実行
        result = await chat_agent.run_async(message, context)
        print(f"エージェント: {result.content}")
        
        # 会話履歴確認
        print(f"現在のメッセージ数: {len(context.messages)}")
        
        # ルーティング結果確認
        if hasattr(context, 'routing_result') and context.routing_result:
            next_route = context.routing_result.next_route
            print(f"次のルート: {next_route}")
            
            if next_route == "end_chat":
                print("\n会話終了判定が出ました。要約を生成します。")
                break
    
    print("\n" + "=" * 50)
    print("会話履歴詳細確認：")
    print("=" * 50)
    
    # 会話履歴詳細表示
    for i, msg in enumerate(context.messages):
        role_icon = "👤" if msg.role == "user" else "🤖"
        print(f"{i+1}. {role_icon} {msg.role}: {str(msg.content)[:100]}")
    
    print("\n" + "=" * 50)
    print("要約エージェントで履歴確認：")
    print("=" * 50)
    
    # 要約エージェント実行
    summary_result = await summary_agent.run_async("会話を要約してください", context)
    print(summary_result.content)
    
    print(f"\n最終メッセージ数: {len(context.messages)}")
    print("✅ 会話履歴継続テスト完了")


async def test_direct_context_access():
    """Context直接アクセステスト"""
    print("\n" + "=" * 50)
    print("Context直接アクセステスト：")
    print("=" * 50)
    
    # 新しいコンテキスト作成
    context = Context()
    
    # 手動でメッセージ追加
    context.add_user_message("最初のメッセージです")
    context.add_assistant_message("最初の応答です")
    context.add_user_message("2番目のメッセージです") 
    context.add_assistant_message("2番目の応答です")
    
    print("手動追加メッセージ:")
    for i, msg in enumerate(context.messages):
        print(f"{i+1}. {msg.role}: {msg.content}")
    
    # エージェント実行して履歴参照確認
    agent = RefinireAgent(
        name="history_test",
        generation_instructions="""
会話履歴を確認し、これまでのやりとり内容を教えてください。
履歴にある各メッセージの内容を簡潔にまとめてください。
        """,
        model="gpt-4o-mini",
        context_providers_config=[
            {"type": "conversation_history", "max_items": 10}
        ]
    )
    
    result = await agent.run_async("これまでの会話を教えて", context)
    print(f"\nエージェントの履歴確認結果:")
    print(result.content)
    
    print(f"最終メッセージ数: {len(context.messages)}")


async def main():
    """メインテスト実行"""
    try:
        # 1. 会話履歴継続テスト
        await test_conversation_history()
        
        # 2. Context直接アクセステスト
        await test_direct_context_access()
        
    except Exception as e:
        print(f"エラー発生: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())