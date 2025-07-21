#!/usr/bin/env python3
"""
改良版自己紹介文作成システム - 会話履歴付きインテリジェントフロー

主な特徴:
- RefinireAgentを使用したステップ実装
- 会話履歴による自然な対話
- routing_instructionによる動的フロー制御
- Flow特別定数による適切な終了処理
"""

import asyncio
from refinire import RefinireAgent, Flow
from refinire.agents.flow import Context, UserInputStep


def create_info_collector_agent():
    """個人情報収集エージェント - 会話履歴付きヒアリング"""
    return RefinireAgent(
        name="collect_personal_info",
        generation_instructions="""
あなたは親しみやすい自己紹介アシスタントです。
これまでの会話の流れを考慮して、自然な対話を続けながら情報を収集してください。

【収集すべき必須情報】
1. 名前 - お名前やニックネーム
2. 年齢 - 年齢（おおよそでも可）
3. 性格 - どんな性格か（複数可）
4. 趣味 - 好きなことや趣味（複数可）

【任意情報】
- 職業や学年
- 特技や得意なこと

対応方針：
- これまでの会話で既に聞いた質問は繰り返さない
- すでに得られた情報を確認・深掘りする場合は自然に行う
- 不足している項目について親しみやすく質問する
- 質問は1つずつ、分かりやすく日本語で行う
- ユーザーが話しやすい雰囲気を作る
- 具体的な例を提示して答えやすくする
- ユーザーが終了を希望する場合は丁寧にお別れを告げる
        """.strip(),
        model="gpt-4o-mini",
        context_providers_config=[
            {"type": "conversation_history", "max_items": 10}
        ],
        routing_instruction="""
これまでの会話履歴とユーザーの最新入力を確認してください。

【終了判定】
ユーザーが以下のような終了を示すキーワードを使用した場合
- "quit", "exit", "終了", "やめる", "中止" など
→ "_FLOW_END_" （フロー終了）

【情報完了判定】
以下の必須情報がすべて揃っているかを判断してください：
1. 名前 - 具体的な名前やニックネーム
2. 年齢 - 年齢情報（おおよそでも可）
3. 性格 - 性格の特徴（1つ）
4. 趣味 - 趣味や好きなこと（1つ）

すべての必須情報を一つずつ、順番にチェックして、出力する
すべての必須情報が揃っている場合: "create_introduction"
まだ不足している情報がある場合: "additional_input" （追加入力を求める）

重要: 終了する場合は必ず "_FLOW_END_" を返してフローを終了してください。
        """.strip()
    )


def create_introduction_generator_agent():
    """自己紹介文生成エージェント - 会話履歴を活用"""
    return RefinireAgent(
        name="create_introduction",
        generation_instructions="""
あなたは魅力的な自己紹介文を作成する専門家です。
これまでの会話で収集した情報をもとに、ユーザーの人柄が伝わる親しみやすい自己紹介文を作成してください。

会話の中で現れたユーザーの個性や話し方も反映して、より人間らしい自己紹介文にしてください。

以下の形式で自己紹介文を作成してください：

## 🌟 あなたの自己紹介文

### 基本情報
**名前**: [名前]
**年齢**: [年齢]

### 私について
[性格や人柄について温かく表現]

### 趣味・好きなこと
[趣味について具体的に、楽しそうに表現]

### ひとこと
[親しみやすいメッセージ]

---
*この自己紹介文は、あなたの魅力が伝わるように作成しました！*

自然で親しみやすく、相手に好印象を与える自己紹介文を心がけてください。
生成完了後は「自己紹介文作成完了！」と表示してください。
        """.strip(),
        model="gpt-4o-mini",
        context_providers_config=[
            {"type": "conversation_history", "max_items": 15}
        ],
        next_step=None  # フロー終了 - ルーティング指示なしで直接終了
    )


def main():
    """メイン関数 - 会話履歴付きインテリジェントフロー"""
    print("=== 自己紹介文作成システム（改良版） ===")
    print("あなたについて教えてください！")
    print("自然な会話を通して、素敵な自己紹介文を一緒に作りましょう。")
    print("（いつでも'quit'で終了できます）\n")
    
    # ステップ定義
    user_input_step = UserInputStep(
        name="user_input",
        prompt="まずは、あなたのことを教えてください（名前、年齢、性格、趣味など何でも大丈夫です）："
    )
    user_input_step.next_step = "collect_personal_info"
    
    # 追加情報入力ステップ
    additional_input_step = UserInputStep(
        name="additional_input",
        prompt="もう少し詳しく教えてください："
    )
    additional_input_step.next_step = "collect_personal_info"
    
    # エージェント作成
    collector_step = create_info_collector_agent()
    generator_step = create_introduction_generator_agent()
    
    # フロー定義
    flow = Flow(
        name="self_introduction_flow",
        start="user_input",
        steps={
            "user_input": user_input_step,
            "additional_input": additional_input_step,
            "collect_personal_info": collector_step,
            "create_introduction": generator_step
        }
    )
    
    # インタラクティブフロー実行
    async def run_interactive_flow():
        # フローをバックグラウンドタスクとして開始
        task = await flow.start_background_task()
        
        while not flow.finished:
            try:
                # フローからのプロンプトを取得
                prompt = flow.next_prompt()
                if prompt:
                    user_input = input(prompt + " ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', '終了']:
                        print("システムを終了します。")
                        flow.stop()
                        break
                    
                    # ユーザー入力をフローに渡す
                    flow.feed(user_input)
                
                # 少し待機
                await asyncio.sleep(0.1)
                
                # フローが完了したかチェック
                if flow.finished:
                    print("\n" + "="*50)
                    print("🎉 自己紹介文が完成しました！")
                    print("="*50)
                    break
                    
            except KeyboardInterrupt:
                print("\nシステムを終了します。")
                flow.stop()
                break
            except Exception as e:
                print(f"エラーが発生しました: {e}")
    
    try:
        asyncio.run(run_interactive_flow())
    except Exception as e:
        print(f"フロー実行エラー: {e}")


def demo_mode():
    """デモ用の自動実行モード"""
    print("\n=== デモモード ===")
    
    # デモ用のダイレクト生成エージェント
    demo_generator = RefinireAgent(
        name="demo_generator",
        generation_instructions="""
提供された情報をもとに、親しみやすい自己紹介文を作成してください。

以下の形式で自己紹介文を作成してください：

## 🌟 あなたの自己紹介文

### 基本情報
**名前**: [名前]
**年齢**: [年齢]

### 私について
[性格や人柄について温かく表現]

### 趣味・好きなこと
[趣味について具体的に、楽しそうに表現]

### ひとこと
[親しみやすいメッセージ]

---
*この自己紹介文は、あなたの魅力が伝わるように作成しました！*
        """.strip(),
        model="gpt-4o-mini",
        next_step=None  # フロー終了 - ルーティング指示なしで直接終了
    )
    
    # シンプルなデモフロー
    demo_flow = Flow(
        name="demo_self_introduction_flow",
        start="demo_generator",
        steps={
            "demo_generator": demo_generator
        }
    )
    
    demo_input = "こんにちは！田中太郎です。25歳で、明るくて人懐っこい性格です。趣味は読書と映画鑑賞で、特にSF小説が大好きです。プログラマーとして働いています。"
    
    print(f"\nユーザー: {demo_input}")
    
    async def run_demo():
        try:
            result = await demo_flow.run(demo_input)
            
            print("\n" + "="*50)
            print("🎉 デモ自己紹介文完成！")
            print("="*50)
            if result and hasattr(result, 'result') and result.result:
                print(f"\n{result.result}")
            print("\n✨ デモ完了！")
            
        except Exception as e:
            print(f"エラーが発生しました: {e}")
    
    try:
        asyncio.run(run_demo())
    except Exception as e:
        print(f"デモ実行エラー: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo_mode()
    else:
        main()