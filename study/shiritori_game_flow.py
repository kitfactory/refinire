#!/usr/bin/env python3
"""
しりとりゲームFlow - Flowを使ったインタラクティブしりとりゲーム
Shiritori Game Flow - Interactive word chain game using Flow
"""

import asyncio
import sys
import os

# Add the src directory to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent, Flow
from refinire.agents.flow import Context, UserInputStep


def create_game_starter_agent():
    """ゲーム開始エージェント"""
    return RefinireAgent(
        name="game_starter",
        generation_instructions="""
あなたはしりとりゲームの司会者です。

ゲームのルールを説明し、最初の単語を提供してください：

=== しりとりゲームへようこそ！ ===

【ルール】
1. 私が単語を言うので、その最後の文字から始まる単語を答えてください
2. 同じ単語は使えません  
3. 「ん」で終わる単語を言ったら負けです
4. 日本語の名詞でお願いします

それでは始めましょう！
私の最初の単語は「さくら」です。

「ら」から始まる単語をどうぞ！
        """.strip(),
        model="gpt-4o-mini",
        routing_instruction="""
常に "get_user_word" を返してください。
        """.strip()
    )


def create_shiritori_agent():
    """しりとりエージェント - ユーザーの単語をチェックして次の単語を返す"""
    return RefinireAgent(
        name="shiritori_agent",
        generation_instructions="""
あなたはしりとりゲームのエキスパートです。

会話履歴から：
1. 前回の私の単語の最後の文字を確認
2. ユーザーの単語が正しいかチェック
3. 次の単語を考えて答える

【チェック項目】
- ユーザーの単語が前回の最後の文字から始まっているか
- 日本語の名詞か
- 既に使われた単語でないか
- 「ん」で終わっていないか

【応答形式】
正しい場合：「○○ですね！では私は「○○」です。「○」から始まる単語をどうぞ！」
間違いの場合：「申し訳ありませんが、○○は使えません。理由：○○。もう一度「○」から始まる単語をお願いします。」

既に使用された単語は会話履歴から確認してください。
        """.strip(),
        model="gpt-4o-mini",
        context_providers_config=[
            {"type": "conversation_history", "max_items": 20}
        ],
        routing_instruction="""
以下のルールで判定してください：

1. ユーザーが「ん」で終わる単語を言った場合 → "user_loses"
2. ユーザーの単語が間違い（ルール違反）の場合 → "get_user_word" 
3. 私が「ん」で終わる単語しか思いつかない場合 → "ai_loses"
4. 正常にゲームが続く場合 → "get_user_word"

重要：ユーザーが負ける条件は「ん」で終わる単語を言った場合のみです。
        """.strip()
    )


def create_victory_agent():
    """勝利宣言エージェント"""
    return RefinireAgent(
        name="victory_agent",
        generation_instructions="""
ユーザーがしりとりで負けました！

勝利を宣言してください：

🎉 私の勝ちですね！ 🎉

ユーザーが「ん」で終わる単語を言ったので、しりとりのルールにより私の勝利です。
楽しいゲームでした！またしりとりで遊びましょう。

ありがとうございました！
        """.strip(),
        model="gpt-4o-mini"
    )


def create_defeat_agent():
    """敗北宣言エージェント"""
    return RefinireAgent(
        name="defeat_agent", 
        generation_instructions="""
私がしりとりで負けました...

敗北を認めて、ユーザーの勝利を称えてください：

😅 あなたの勝ちです！ 😅

私が「ん」で終わる単語しか思いつかず、降参です。
素晴らしいしりとりでした！あなたの語彙力に脱帽です。

また挑戦させてください！
        """.strip(),
        model="gpt-4o-mini"
    )


def create_user_input_step():
    """ユーザー入力ステップ"""
    step = UserInputStep(
        name="get_user_word",
        prompt="あなたの単語を入力してください："
    )
    step.next_step = "shiritori_agent"
    return step


async def main():
    """しりとりゲーム実行"""
    print("=== Flow しりとりゲーム ===\n")
    
    # エージェント作成
    starter = create_game_starter_agent()
    shiritori = create_shiritori_agent()
    victory = create_victory_agent()
    defeat = create_defeat_agent()
    user_input = create_user_input_step()
    
    # Flow作成
    flow = Flow(
        name="shiritori_game",
        start="game_starter",
        steps={
            "game_starter": starter,
            "get_user_word": user_input,
            "shiritori_agent": shiritori,
            "user_loses": victory,
            "ai_loses": defeat
        }
    )
    
    # インタラクティブフロー実行
    async def run_shiritori_game():
        # フローをバックグラウンドタスクとして開始
        task = await flow.start_background_task()
        
        while not flow.finished:
            try:
                # フローからのプロンプトを取得
                prompt = flow.next_prompt()
                if prompt:
                    user_input = input(f"{prompt} ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', '終了', 'やめる']:
                        print("ゲームを終了します。")
                        flow.stop()
                        break
                    
                    # ユーザー入力をフローに渡す
                    flow.feed(user_input)
                
                # 少し待機
                await asyncio.sleep(0.1)
                
                # フローが完了したかチェック
                if flow.finished:
                    print("\n" + "="*50)
                    print("🎮 ゲーム終了！")
                    print("="*50)
                    break
                    
            except KeyboardInterrupt:
                print("\nゲームを終了します。")
                flow.stop()
                break
            except Exception as e:
                print(f"エラーが発生しました: {e}")
                break
    
    try:
        await run_shiritori_game()
    except Exception as e:
        print(f"ゲーム実行エラー: {e}")


# デモ用の自動実行
async def demo_shiritori():
    """デモ用自動しりとり"""
    print("\n=== デモモード（自動実行） ===")
    
    # デモ用エージェント（短縮版）
    demo_agent = RefinireAgent(
        name="demo_shiritori",
        generation_instructions="""
しりとりのデモを実行してください。

以下の流れでデモ：
1. 「さくら」から開始
2. ユーザーが「らっぱ」と答えたとする
3. 私が「ぱん」と答える  
4. ユーザーが「んちき」（んで終わる）と答える
5. 私の勝利を宣言

この流れをデモとして表示してください。
        """.strip(),
        model="gpt-4o-mini"
    )
    
    result = await demo_agent.run_async("しりとりデモを実行", Context())
    print(result.content)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        asyncio.run(demo_shiritori())
    else:
        asyncio.run(main())