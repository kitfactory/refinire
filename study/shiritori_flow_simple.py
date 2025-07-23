#!/usr/bin/env python3
"""
シンプルしりとりFlow - FlowとUserInputStepを使った基本的なしりとりゲーム
Simple Shiritori Flow - Basic word chain game using Flow and UserInputStep
"""

import asyncio
import sys
import os

# Add the src directory to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent, Flow
from refinire.agents.flow import Context, UserInputStep


def create_game_starter():
    """ゲーム開始エージェント"""
    return RefinireAgent(
        name="game_starter",
        generation_instructions="""
あなたはしりとりゲームの司会者です。

ゲームを開始してください：

=== しりとりゲームへようこそ！ ===

【ルール】
1. 私が単語を言うので、その最後の文字から始まる単語を答えてください
2. 「ん」で終わる単語を言ったら負けです
3. 日本語の名詞でお願いします

それでは始めましょう！
私の最初の単語は「さくら」です。

「ら」から始まる単語をどうぞ！
        """.strip(),
        model="gpt-4o-mini",
        routing_instruction="""
ゲーム開始後は必ず "get_user_word" を返してください。
        """.strip()
    )


def create_shiritori_agent():
    """しりとりエージェント"""
    return RefinireAgent(
        name="shiritori_agent",
        generation_instructions="""
あなたはしりとりゲームのプレイヤーです。

会話履歴を確認して：
1. ユーザーの単語をチェック
2. 次の単語を考える

【応答形式】
正しい場合：「{ユーザーの単語}ですね！では私は「{次の単語}」です。「{最後の文字}」から始まる単語をどうぞ！」
        """.strip(),
        model="gpt-4o-mini",
        context_providers_config=[
            {"type": "conversation_history", "max_items": 10}
        ],
        routing_instruction="""
ユーザーの単語を分析してください：

1. ユーザーが「ん」で終わる単語を言った場合 → "user_loses"
2. 正常にゲームが続く場合 → "get_user_word"

重要：「ん」で終わる単語（例：みかん、らーめん、etc）かチェックしてください。
        """.strip()
    )


def create_victory_agent():
    """勝利宣言エージェント"""
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


async def test_shiritori_flow():
    """しりとりFlowテスト"""
    print("=== しりとりFlowテスト ===\n")
    
    # エージェント作成
    starter = create_game_starter()
    shiritori = create_shiritori_agent()
    victory = create_victory_agent()
    
    # UserInputStep作成
    user_input = UserInputStep(
        name="get_user_word",
        prompt="あなたの単語："
    )
    user_input.next_step = "shiritori_agent"
    
    # Flow作成
    flow = Flow(
        name="shiritori_game",
        start="game_starter",
        steps={
            "game_starter": starter,
            "get_user_word": user_input, 
            "shiritori_agent": shiritori,
            "user_loses": victory
        }
    )
    
    # Context作成
    context = Context()
    
    # Flow実行開始
    print("【ゲーム開始】")
    result_context = await flow.run("", initial_input="")
    print(f"司会者: {result_context.content}")
    
    # 第1回戦：正常な単語
    print("\n【第1回戦】")
    print("ユーザー: らっぱ")
    result_context.add_user_message("らっぱ")
    
    result_context = await flow.run("らっぱ")
    print(f"エージェント: {result_context.content}")
    
    # ルーティング結果確認
    if hasattr(result_context, 'routing_result') and result_context.routing_result:
        next_route = getattr(result_context.routing_result, 'next_route', None)
        if not next_route and hasattr(result_context.routing_result, 'get'):
            next_route = result_context.routing_result.get('next_route')
        print(f"次のルート: {next_route}")
    
    # 第2回戦：「ん」で終わる単語
    print("\n【第2回戦】")
    print("ユーザー: ぱん")
    result_context.add_user_message("ぱん")
    
    result_context = await flow.run("ぱん")
    print(f"エージェント: {result_context.content}")
    
    # 最終ルーティング結果確認
    if hasattr(result_context, 'routing_result') and result_context.routing_result:
        next_route = getattr(result_context.routing_result, 'next_route', None)
        if not next_route and hasattr(result_context.routing_result, 'get'):
            next_route = result_context.routing_result.get('next_route')
        print(f"最終ルート: {next_route}")
        
        if next_route == "user_loses":
            print("\n【勝負決定】")
            # 勝利エージェント実行
            victory_result = await victory.run_async("", result_context)
            print(f"勝利宣言: {victory_result.content}")


async def main():
    """メインテスト実行"""
    try:
        await test_shiritori_flow()
        print("\n✅ しりとりFlowテスト完了")
        
    except Exception as e:
        print(f"❌ エラー発生: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())