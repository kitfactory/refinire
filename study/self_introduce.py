from refinire import RefinireAgent, Flow
from refinire.agents.flow.step import UserInputStep
from pydantic import BaseModel
from typing import List, Optional

# 自己紹介情報を構造化するためのデータモデル
class PersonalInfo(BaseModel):
    """個人の自己紹介情報を表すデータモデル"""
    name: str
    age: Optional[int] = None
    personality: List[str]
    hobbies: List[str]
    occupation: Optional[str] = None
    special_skills: Optional[List[str]] = None

def create_info_collector_agent():
    """個人情報収集エージェント"""
    return RefinireAgent(
        name="collect_personal_info",
        generation_instructions="""
あなたは親しみやすい自己紹介アシスタントです。
ユーザーから自己紹介に必要な情報を収集します。

【収集すべき必須情報】
1. 名前 - お名前やニックネーム
2. 年齢 - 年齢（おおよそでも可）
3. 性格 - どんな性格か（複数可）
4. 趣味 - 好きなことや趣味（複数可）

【任意情報】
- 職業や学年
- 特技や得意なこと

対応方針：
- 不足している項目について親しみやすく質問してください
- 質問は1つずつ、分かりやすく日本語で行ってください
- ユーザーが話しやすい雰囲気を作ってください
- 具体的な例を提示して、ユーザーが答えやすくしてください
        """.strip(),
        model="gpt-4o-mini",
        routing_instruction="""
これまでの会話履歴を確認して、以下の必須情報がすべて揃っているかを判断してください：

1. 名前 - 具体的な名前やニックネーム
2. 年齢 - 年齢情報（おおよそでも可）
3. 性格 - 性格の特徴（1つ以上）
4. 趣味 - 趣味や好きなこと（1つ以上）

すべての必須情報が揃っている場合: "create_introduction"
まだ不足している情報がある場合: "user_input"
        """.strip()
    )

def create_introduction_generator_agent():
    """自己紹介文生成エージェント"""
    return RefinireAgent(
        name="create_introduction",
        generation_instructions="""
あなたは魅力的な自己紹介文を作成する専門家です。
これまでの会話で収集した情報をもとに、親しみやすい自己紹介文を作成してください。

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
        """.strip(),
        model="gpt-4o-mini",
        next_step=None  # フロー終了
    )

def main():
    print("=== 自己紹介文作成システム ===")
    print("あなたについて教えてください！")
    print("素敵な自己紹介文を一緒に作りましょう。")
    print("（'quit'で終了）\n")
    
    # ステップ定義
    user_input_step = UserInputStep(
        name="user_input",
        prompt="まずは、あなたのことを教えてください（名前、年齢、性格、趣味など）："
    )
    user_input_step.next_step = "collect_personal_info"
    
    collector_step = create_info_collector_agent()
    generator_step = create_introduction_generator_agent()
    
    # フロー定義
    flow = Flow(
        name="self_introduction_flow",
        start="user_input",
        steps={
            "user_input": user_input_step,
            "collect_personal_info": collector_step,
            "create_introduction": generator_step
        }
    )
    
    # インタラクティブフロー実行
    import asyncio
    
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
                    print("自己紹介文が完成しました！")
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
    
    # デモ用のシンプルなフロー
    collector_step = create_info_collector_agent()
    collector_step.next_step = "create_introduction"
    
    generator_step = create_introduction_generator_agent()
    
    flow = Flow(
        name="demo_self_introduction_flow",
        start="collect_personal_info",
        steps={
            "collect_personal_info": collector_step,
            "create_introduction": generator_step
        }
    )
    
    demo_input = "こんにちは！田中太郎です。25歳で、明るくて人懐っこい性格です。趣味は読書と映画鑑賞で、特にSF小説が大好きです。プログラマーとして働いています。"
    
    print(f"\nユーザー: {demo_input}")
    
    import asyncio
    
    try:
        result = asyncio.run(flow.run(demo_input))
        print(f"\nシステム: {result.result}")
        
        print("\n" + "="*50)
        print("自己紹介文作成完了！")
        print("="*50)
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo_mode()
    else:
        main()