#!/usr/bin/env python3
"""
シンプルな自己紹介文作成システム（ルーティング指示なし）

ルーティング指示の問題を回避するため、段階的にフローを実行する方式を採用
"""

import asyncio
import sys
import os

# Add the src directory to the path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent, Flow
from refinire.agents.flow import Context, UserInputStep


def create_info_collector_agent():
    """情報収集エージェント - next_stepで明示的に次のステップを指定"""
    return RefinireAgent(
        name="collect_personal_info",
        generation_instructions="""
あなたは親しみやすい自己紹介アシスタントです。
ユーザーから自己紹介に必要な情報を収集してください。

【収集すべき必須情報】
1. 名前 - お名前やニックネーム
2. 年齢 - 年齢（おおよそでも可）
3. 性格 - どんな性格か（複数可）
4. 趣味 - 好きなことや趣味（複数可）

【任意情報】
- 職業や学年
- 特技や得意なこと

対応方針：
- 不足している項目について親しみやすく質問する
- 質問は1つずつ、分かりやすく日本語で行う
- ユーザーが話しやすい雰囲気を作る
- 情報が十分に揃った場合は「情報が揃いました。自己紹介文を作成します。」と伝える

すべての必須情報が揃っている場合のみ、最後に「情報収集完了」と出力してください。
        """.strip(),
        model="gpt-4o-mini",
        context_providers_config=[
            {"type": "conversation_history", "max_items": 10}
        ],
        next_step="create_introduction"  # 情報が十分な場合は次のステップへ
    )


def create_introduction_generator_agent():
    """自己紹介文生成エージェント - 会話履歴を活用して自己紹介文を作成"""
    return RefinireAgent(
        name="create_introduction",
        generation_instructions="""
あなたは魅力的な自己紹介文を作成する専門家です。
これまでの会話で収集した情報をもとに、ユーザーの人柄が伝わる親しみやすい自己紹介文を作成してください。

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
        context_providers_config=[
            {"type": "conversation_history", "max_items": 15}
        ],
        next_step=None  # フロー終了
    )


async def run_simple_flow():
    """段階的フロー実行"""
    print("=== シンプルな自己紹介文作成システム ===")
    print("あなたについて教えてください！")
    print("自然な会話を通して、素敵な自己紹介文を一緒に作りましょう。")
    print("（いつでも'quit'で終了できます）\\n")
    
    # Phase 1: 情報収集フェーズ
    print("--- Phase 1: 情報収集 ---")
    
    collector_agent = create_info_collector_agent()
    collection_context = Context()
    
    # 初回入力
    user_input = input("まずは、あなたのことを教えてください（名前、年齢、性格、趣味など何でも大丈夫です）: ").strip()
    
    if user_input.lower() in ['quit', 'exit', '終了']:
        print("システムを終了します。")
        return
    
    # 情報収集ループ
    max_rounds = 5  # 最大5回の対話
    for round_num in range(max_rounds):
        print(f"\\n--- 対話 {round_num + 1} ---")
        
        # エージェント実行
        result = await collector_agent.run_async(user_input, collection_context)
        
        print(f"\\nアシスタント: {result.content}")
        
        # 情報収集完了のチェック
        if "情報収集完了" in result.content:
            print("\\n✅ 情報収集が完了しました！")
            break
        
        # 追加情報の入力
        user_input = input("\\nあなた: ").strip()
        
        if user_input.lower() in ['quit', 'exit', '終了']:
            print("システムを終了します。")
            return
    
    # Phase 2: 自己紹介文生成フェーズ  
    print("\\n--- Phase 2: 自己紹介文生成 ---")
    
    generator_agent = create_introduction_generator_agent()
    
    # 収集した情報をコピー
    generation_context = Context()
    generation_context.messages = collection_context.messages.copy()
    
    # 自己紹介文生成
    final_result = await generator_agent.run_async("これまでの情報をもとに自己紹介文を作成してください", generation_context)
    
    print("\\n" + "="*50)
    print("🎉 自己紹介文が完成しました！")
    print("="*50)
    print(f"\\n{final_result.content}")
    print("\\n✨ 完了！")


async def demo_mode():
    """デモ用の自動実行モード"""
    print("\\n=== デモモード ===")
    
    # Phase 1: 情報収集
    collector_agent = create_info_collector_agent()
    collection_context = Context()
    
    demo_input = "こんにちは！田中太郎です。25歳で、明るくて人懐っこい性格です。趣味は読書と映画鑑賞で、特にSF小説が大好きです。プログラマーとして働いています。"
    
    print(f"\\nユーザー: {demo_input}")
    
    result1 = await collector_agent.run_async(demo_input, collection_context)
    print(f"\\nアシスタント: {result1.content}")
    
    # Phase 2: 自己紹介文生成
    generator_agent = create_introduction_generator_agent()
    generation_context = Context()
    generation_context.messages = collection_context.messages.copy()
    
    final_result = await generator_agent.run_async("これまでの情報をもとに自己紹介文を作成してください", generation_context)
    
    print("\\n" + "="*50)
    print("🎉 デモ自己紹介文完成！")
    print("="*50)
    print(f"\\n{final_result.content}")
    print("\\n✨ デモ完了！")


def main():
    """メイン関数"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        asyncio.run(demo_mode())
    else:
        asyncio.run(run_simple_flow())


if __name__ == "__main__":
    main()