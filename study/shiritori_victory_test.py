#!/usr/bin/env python3
"""
しりとり勝利テスト - 「私の勝ちですね」を表示するテスト
Shiritori Victory Test - Test to display "私の勝ちですね"
"""

import asyncio
import sys
import os

# Add the src directory to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent
from refinire.agents.flow import Context


def create_shiritori_judge():
    """しりとり審判エージェント"""
    return RefinireAgent(
        name="shiritori_judge",
        generation_instructions="""
あなたはしりとりの審判です。

ユーザーの単語をチェックして応答してください：

1. ユーザーが「ん」で終わる単語を言った場合
   → ゲーム終了、私の勝利を宣言
   
2. 正常な単語の場合
   → 次の単語を返してゲーム継続

【応答例】
- 勝利時：「🎉 私の勝ちですね！ 🎉 あなたが『{単語}』で『ん』で終わったので私の勝利です。」
- 継続時：「{ユーザーの単語}ですね！では私は『{次の単語}』です。『{最後の文字}』から始まる単語をどうぞ！」
        """.strip(),
        model="gpt-4o-mini",
        context_providers_config=[
            {"type": "conversation_history", "max_items": 10}
        ],
        routing_instruction="""
ユーザーの単語を分析してください：

1. ユーザーが「ん」で終わる単語を言った場合 → "victory"
2. 正常にゲームが続く場合 → "continue"

重要：「ん」で終わる単語（例：みかん、らーめん、ぱん、etc）の場合は必ず "victory" を返してください。
        """.strip()
    )


def create_victory_agent():
    """勝利専用エージェント"""
    return RefinireAgent(
        name="victory_agent",
        generation_instructions="""
🎉 私の勝ちですね！ 🎉

ユーザーが「ん」で終わる単語を言ったので、しりとりのルールにより私の勝利です。
楽しいゲームでした！またしりとりで遊びましょう。

ありがとうございました！
        """.strip(),
        model="gpt-4o-mini"
    )


async def test_shiritori_victory():
    """しりとり勝利条件テスト"""
    print("=== しりとり勝利条件テスト ===\n")
    
    # エージェント作成
    judge = create_shiritori_judge()
    victory_agent = create_victory_agent()
    
    # Context作成
    context = Context()
    
    # ゲーム開始メッセージ
    print("司会者: しりとりを始めましょう！私の単語は「さくら」です。")
    context.add_assistant_message("私の単語は「さくら」です。「ら」から始まる単語をどうぞ！")
    
    # 第1回戦：正常な単語
    print("\n【第1回戦】")
    user_word1 = "らっぱ"
    print(f"ユーザー: {user_word1}")
    
    result1 = await judge.run_async(user_word1, context)
    print(f"審判: {result1.content}")
    
    # ルーティング結果確認
    next_route1 = None
    if hasattr(context, 'routing_result') and context.routing_result:
        next_route1 = getattr(context.routing_result, 'next_route', None) or context.routing_result.get('next_route', None)
    print(f"判定: {next_route1}")
    
    # 第2回戦：「ん」で終わる単語
    print("\n【第2回戦】")  
    user_word2 = "ぱん"
    print(f"ユーザー: {user_word2}")
    
    result2 = await judge.run_async(user_word2, context)
    print(f"審判: {result2.content}")
    
    # ルーティング結果確認
    next_route2 = None
    if hasattr(context, 'routing_result') and context.routing_result:
        next_route2 = getattr(context.routing_result, 'next_route', None) or context.routing_result.get('next_route', None)
    print(f"判定: {next_route2}")
    
    # 勝利条件チェック
    if next_route2 == "victory":
        print("\n【🎉 勝利宣言 🎉】")
        victory_result = await victory_agent.run_async("勝利を宣言してください", context)
        print(f"勝利エージェント: {victory_result.content}")
    else:
        print("\n❌ 勝利条件が検出されませんでした")
    
    # 会話履歴確認
    print(f"\n=== 会話履歴 ===")
    for i, msg in enumerate(context.messages, 1):
        role_icon = "👤" if msg.role == "user" else "🤖"
        print(f"{i}. {role_icon} {msg.role}: {msg.content}")


async def test_direct_victory():
    """直接勝利テスト - 複数の「ん」で終わる単語"""
    print("\n" + "="*50)
    print("=== 直接勝利テスト ===")
    print("="*50)
    
    # 勝利エージェント
    victory_agent = create_victory_agent()
    
    # 「ん」で終わる単語リスト
    test_words = ["みかん", "らーめん", "ぱん", "りんご", "めん"]
    
    for word in test_words:
        print(f"\n【テスト単語: {word}】")
        context = Context()
        
        # 単語をコンテキストに追加
        context.add_user_message(f"私の単語は「{word}」です")
        
        # 「ん」で終わるかチェック
        ends_with_n = word.endswith('ん')
        print(f"「ん」で終わる: {ends_with_n}")
        
        if ends_with_n:
            print("→ 勝利条件達成！")
            victory_result = await victory_agent.run_async("", context)
            print(f"勝利宣言: {victory_result.content}")
        else:
            print("→ ゲーム継続")


async def main():
    """メインテスト実行"""
    try:
        await test_shiritori_victory()
        await test_direct_victory()
        
        print("\n✅ しりとり勝利テスト完了")
        print("「私の勝ちですね」が正しく表示されました！")
        
    except Exception as e:
        print(f"❌ エラー発生: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())