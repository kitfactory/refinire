#!/usr/bin/env python3
"""
包括的Flow・Routing統合テスト
複数回会話後のrouting/evaluation動作、Flow終了処理を検証
"""

import asyncio
import sys
import os

# Add the src directory to the path for local development  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent, Flow
from refinire.agents.flow import Context


def create_conversation_agent():
    """会話継続/終了判定を行うエージェント"""
    return RefinireAgent(
        name="conversation_agent",
        generation_instructions="""
あなたは親しみやすい会話エージェントです。
ユーザーとの会話を継続し、適切なタイミングで終了判定を行ってください。

会話履歴を考慮して、自然な応答をしてください。
        """.strip(),
        model="gpt-4o-mini",
        context_providers_config=[
            {"type": "conversation_history", "max_items": 10}
        ],
        routing_instruction="""
会話履歴を確認して、以下のルーティング判断を行ってください：

1. "continue_chat" - まだ会話を継続する場合
2. "summarize_chat" - 会話をまとめる場合（3回以上やりとりがあった場合）
3. "_FLOW_END_" - ユーザーが明確に終了を希望した場合

【判定基準】
- ユーザーが「終了」「quit」「さようなら」などを使用 → "_FLOW_END_"
- 会話が3回以上のやりとりがあり自然な区切り → "summarize_chat"
- それ以外 → "continue_chat"
        """.strip()
    )


def create_chat_summarizer():
    """会話要約エージェント"""
    return RefinireAgent(
        name="chat_summarizer",
        generation_instructions="""
これまでの会話履歴を分析し、要約を作成してください。

以下の形式で要約してください：
=== 会話要約 ===
- 参加者: [参加者情報]
- 会話回数: [やりとりの回数]
- 主な話題: [話題の要約]
- 重要なポイント: [重要な情報]

会話終了です。ありがとうございました！
        """.strip(),
        model="gpt-4o-mini",
        context_providers_config=[
            {"type": "conversation_history", "max_items": 20}
        ]
    )


def create_user_input_step():
    """ユーザー入力ステップ"""
    from refinire.agents.flow.step import UserInputStep
    step = UserInputStep(
        name="user_input",
        prompt="何かお話しください（'quit'で終了）："
    )
    step.next_step = "conversation_agent"
    return step


def create_continue_input_step():
    """会話継続入力ステップ"""
    from refinire.agents.flow.step import UserInputStep
    step = UserInputStep(
        name="continue_input", 
        prompt="続けてお話しください："
    )
    step.next_step = "conversation_agent"
    return step


async def test_multiple_conversation_routing():
    """複数回会話後のrouting動作テスト"""
    print("=== 複数回会話後のrouting動作テスト ===")
    
    # エージェント作成
    conv_agent = create_conversation_agent()
    summarizer = create_chat_summarizer()
    user_input = create_user_input_step()
    continue_input = create_continue_input_step()
    
    # Flow作成 - continue_chatステップを追加
    flow = Flow(
        name="conversation_flow",
        start="user_input",
        steps={
            "user_input": user_input,
            "continue_input": continue_input,
            "conversation_agent": conv_agent,
            "continue_chat": continue_input,  # continue_chatルートを定義
            "summarize_chat": summarizer
        }
    )
    
    # テスト会話シーケンス
    test_inputs = [
        "こんにちは！私は田中です。",
        "今日はいい天気ですね。",
        "最近読書にはまっています。",
        "特にSF小説が好きです。",
        "そろそろ時間ですね。"
    ]
    
    print("テスト会話を開始します...")
    
    for i, test_input in enumerate(test_inputs):
        print(f"\n--- 会話 {i+1} ---")
        print(f"ユーザー: {test_input}")
        
        try:
            result = await flow.run(test_input)
            print(f"エージェント: {result.content}")
            print(f"現在のステップ: {flow.context.next_label}")
            print(f"メッセージ数: {len(flow.context.messages)}")
            print(f"フロー完了: {flow.finished}")
            
            if flow.finished:
                print("フローが終了しました")
                break
                
        except Exception as e:
            print(f"エラー: {e}")
            break
    
    return flow


async def test_routing_decision_accuracy():
    """routing判定精度テスト"""
    print("\n=== routing判定精度テスト ===")
    
    # シンプルなrouting判定エージェント
    routing_agent = RefinireAgent(
        name="routing_tester",
        generation_instructions="簡潔に応答してください。",
        model="gpt-4o-mini",
        context_providers_config=[
            {"type": "conversation_history", "max_items": 5}
        ],
        routing_instruction="""
CRITICAL: ユーザーの入力内容を分析して、必ず以下の4つの選択肢のうち、どれか1つを正確に返してください：

1. "positive" - ユーザーの入力がポジティブな内容の場合
2. "negative" - ユーザーの入力がネガティブな内容の場合  
3. "neutral" - ユーザーの入力が中立的な内容の場合
4. "_FLOW_END_" - ユーザーの入力が終了を示す内容の場合

重要: 
- 生成結果ではなく、ユーザーの入力内容を分析してください
- 上記の選択肢以外は絶対に返さないでください
- 必ず正確に上記のいずれか1つを返してください
        """.strip()
    )
    
    # テストケース
    test_cases = [
        ("ありがとうございます！", "positive"),
        ("困っています。", "negative"), 
        ("今日は晴れです。", "neutral"),
        ("さようなら", "_FLOW_END_")
    ]
    
    for test_input, expected in test_cases:
        print(f"\nテスト: {test_input} -> 期待: {expected}")
        
        ctx = Context()
        result = await routing_agent.run_async(test_input, ctx)
        
        print(f"結果: {result.content}")
        if hasattr(ctx, 'routing_result') and ctx.routing_result:
            actual = ctx.routing_result.next_route
            print(f"ルーティング: {actual}")
            print(f"判定: {'✅ 正確' if actual == expected else '❌ 不正確'}")
        else:
            print("❌ ルーティング結果なし")


async def test_evaluation_with_history():
    """会話履歴を使った評価テスト"""
    print("\n=== 会話履歴を使った評価テスト ===")
    
    eval_agent = RefinireAgent(
        name="evaluation_tester",
        generation_instructions="""
提供された情報と会話履歴全体を分析して評価してください。

評価基準：
1. 会話の自然さ (1-5)
2. 情報の有用性 (1-5)  
3. 応答の適切さ (1-5)

会話履歴から具体的な例を挙げて評価してください。
        """.strip(),
        model="gpt-4o-mini", 
        context_providers_config=[
            {"type": "conversation_history", "max_items": 10}
        ]
    )
    
    # 複数回の会話を蓄積
    ctx = Context()
    
    conversation_sequence = [
        "こんにちは",
        "元気です", 
        "今日は仕事でした",
        "プログラミングをしています"
    ]
    
    for msg in conversation_sequence:
        await eval_agent.run_async(msg, ctx)
        print(f"追加: {msg}")
    
    print(f"\n最終的な会話履歴数: {len(ctx.messages)}")
    
    # 評価実行
    print("評価を実行中...")
    eval_result = await eval_agent.run_async("評価してください", ctx)
    print(f"評価結果: {eval_result.content}")


async def test_flow_termination_conditions():
    """Flow終了条件テスト"""
    print("\n=== Flow終了条件テスト ===")
    
    # 終了条件テスト用の簡単なエージェント
    termination_agent = RefinireAgent(
        name="termination_tester",
        generation_instructions="簡潔に応答してください。",
        model="gpt-4o-mini",
        routing_instruction="""
入力に応じて以下のいずれかを返してください：
1. "continue" - 継続する場合
2. "_FLOW_END_" - 終了する場合
3. "_FLOW_TERMINATE_" - 強制終了する場合
4. "_FLOW_FINISH_" - 完了終了する場合
        """.strip()
    )
    
    from refinire.agents.flow.step import FunctionStep
    
    def simple_step(user_input, context):
        context.content = f"処理完了: {user_input}"
        context.goto("termination_tester")
        return context
    
    simple = FunctionStep("simple", simple_step)
    
    flow = Flow(
        name="termination_test",
        start="simple",
        steps={
            "simple": simple,
            "termination_tester": termination_agent
        }
    )
    
    # 終了条件テスト
    termination_tests = [
        ("続けてください", False),  # 継続
        ("終了してください", True),   # 終了
        ("quit", True),            # 終了
        ("_FLOW_END_", True)       # 強制終了
    ]
    
    for test_input, should_end in termination_tests:
        print(f"\nテスト: {test_input} -> 終了予想: {should_end}")
        
        # 新しいFlowインスタンスで毎回テスト
        test_flow = Flow(
            name="termination_test",
            start="simple", 
            steps={
                "simple": simple,
                "termination_tester": termination_agent
            }
        )
        
        result = await test_flow.run(test_input)
        print(f"結果: {result.content}")
        print(f"フロー終了: {test_flow.finished}")
        print(f"判定: {'✅ 正確' if test_flow.finished == should_end else '❌ 不正確'}")


async def main():
    """メインテスト実行"""
    print("🚀 包括的Flow・Routing統合テスト開始")
    
    try:
        # 1. 複数回会話routing テスト
        await test_multiple_conversation_routing()
        
        # 2. routing判定精度テスト  
        await test_routing_decision_accuracy()
        
        # 3. 評価での会話履歴活用テスト
        await test_evaluation_with_history()
        
        # 4. Flow終了条件テスト
        await test_flow_termination_conditions()
        
        print("\n✅ 全テスト完了")
        
    except Exception as e:
        print(f"\n❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())