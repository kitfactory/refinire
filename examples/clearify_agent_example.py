"""
Example usage of ClearifyAgent for requirement clarification in Flow workflows
FlowワークフローでのClearifyAgentの使用例 - 要件明確化
"""

import asyncio
from typing import List
from pydantic import BaseModel

from agents_sdk_models import (
    ClearifyAgent, Flow, DebugStep, create_simple_clearify_agent, 
    create_evaluated_clearify_agent, ClarificationResult
)


class ReportRequirements(BaseModel):
    """
    Model for report requirements
    レポート要件用モデル
    """
    event: str  # Event name / イベント名
    date: str   # Date / 日付
    place: str  # Place / 場所
    topics: List[str]  # Topics / トピック
    interested: str  # What was impressive / 印象に残ったこと
    expression: str  # Thoughts and feelings / 感想・所感


async def example_simple_clearify_agent():
    """
    Example of simple ClearifyAgent usage
    シンプルなClearifyAgent使用例
    """
    print("=== シンプルなClearifyAgent使用例 ===")
    
    # Create a simple ClearifyAgent
    # シンプルなClearifyAgentを作成
    clearify_agent = create_simple_clearify_agent(
        name="simple_clarifier",
        instructions="""
        あなたは要件明確化の専門家です。
        ユーザーの要求を理解し、不明確な点や不足している情報を特定してください。
        より良い結果のために必要な追加情報を質問し、要件が十分に明確になった場合のみ確定してください。
        """,
        output_data=ReportRequirements,
        max_turns=5,
        model="gpt-4o-mini",
        next_step="debug"
    )
    
    # Create a simple Flow with the ClearifyAgent
    # ClearifyAgentを使ったシンプルなFlowを作成
    flow = Flow(
        start="simple_clarifier",
        steps={
            "simple_clarifier": clearify_agent,
            "debug": DebugStep("debug", "明確化結果を確認")
        },
        max_steps=20
    )
    
    print("📝 要件明確化セッションを開始します")
    
    # Simulate user interaction
    # ユーザー対話をシミュレート
    try:
        # Initial request
        # 初期要求
        result = await flow.run(input_data="テックカンファレンスのレポートを作りたい")
        
        print(f"\n結果:")
        clearify_result = result.shared_state.get("simple_clarifier_result")
        if isinstance(clearify_result, ClarificationResult):
            if clearify_result.is_complete:
                print(f"✅ 明確化完了: {clearify_result.data}")
            else:
                print(f"❓ 追加質問: {clearify_result.data}")
        else:
            print(f"📄 結果: {clearify_result}")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")


async def example_evaluated_clearify_agent():
    """
    Example of ClearifyAgent with evaluation capabilities
    評価機能付きClearifyAgentの例
    """
    print("\n=== 評価機能付きClearifyAgent例 ===")
    
    # Create ClearifyAgent with evaluation
    # 評価機能付きClearifyAgentを作成
    clearify_agent = create_evaluated_clearify_agent(
        name="evaluated_clarifier",
        generation_instructions="""
        あなたは要件明確化の専門家です。
        ユーザーの要求を理解し、不明確な点や不足している情報を特定してください。
        """,
        evaluation_instructions="""
        あなたは明確化品質の評価者です。以下の基準で明確化の質を評価してください：
        1. 完全性（0-100）: 必要な情報がすべて含まれているか
        2. 明確性（0-100）: 要求が明確で曖昧さがないか
        3. 実現可能性（0-100）: 現実的で実現可能な要求か
        平均スコアを計算し、各側面について具体的なコメントを提供してください。
        """,
        output_data=ReportRequirements,
        max_turns=5,
        model="gpt-4o-mini",
        evaluation_model="gpt-4o-mini",
        threshold=75,
        next_step="debug"
    )
    
    # Create Flow with debug step
    # デバッグステップ付きFlowを作成
    flow = Flow(
        start="evaluated_clarifier",
        steps={
            "evaluated_clarifier": clearify_agent,
            "debug": DebugStep("debug", "評価付き明確化結果を確認")
        },
        max_steps=20
    )
    
    try:
        result = await flow.run(input_data="AIアプリケーションを開発したい")
        
        print(f"\n結果:")
        clearify_result = result.shared_state.get("evaluated_clarifier_result")
        if isinstance(clearify_result, ClarificationResult):
            if clearify_result.is_complete:
                print(f"✅ 評価付き明確化完了: {clearify_result.data}")
            else:
                print(f"❓ 評価後の追加質問: {clearify_result.data}")
        else:
            print(f"📄 結果: {clearify_result}")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")


async def example_multi_turn_clarification():
    """
    Example of multi-turn clarification process
    複数ターンの明確化プロセス例
    """
    print("\n=== 複数ターン明確化プロセス例 ===")
    
    # Create ClearifyAgent with custom configuration
    # カスタム設定でClearifyAgentを作成
    clearify_agent = ClearifyAgent(
        name="multi_turn_clarifier",
        generation_instructions="""
        あなたは丁寧な要件聞き取りの専門家です。
        一度に複数の質問をせず、一つずつ段階的に質問して要件を明確化してください。
        ユーザーの回答に基づいて、次に必要な情報を特定し、適切な質問をしてください。
        """,
        output_data=ReportRequirements,
        clerify_max_turns=10,
        model="gpt-4o-mini",
        next_step="debug"
    )
    
    # Create context-aware Flow
    # コンテキスト認識Flowを作成
    flow = Flow(
        start="multi_turn_clarifier",
        steps={
            "multi_turn_clarifier": clearify_agent,
            "debug": DebugStep("debug", "ターン管理確認")
        },
        max_steps=20
    )
    
    # Simulate multiple turns of conversation
    # 複数ターンの会話をシミュレート
    user_inputs = [
        "プロジェクトの報告書を作りたい",
        "機械学習のプロジェクトです",
        "2024年12月に東京で実施しました",
        "画像認識と自然言語処理を組み合わせたシステムです",
        "精度向上とユーザーエクスペリエンスの改善が印象的でした"
    ]
    
    try:
        # Start with first input
        # 最初の入力で開始
        result = await flow.run(input_data=user_inputs[0])
        
        # Continue conversation if needed
        # 必要に応じて会話を継続
        for i, user_input in enumerate(user_inputs[1:], 1):
            clearify_result = result.shared_state.get("multi_turn_clarifier_result")
            
            if isinstance(clearify_result, ClarificationResult) and not clearify_result.is_complete:
                print(f"\nターン {i}: {user_input}")
                
                # Continue Flow with new input
                # 新しい入力でFlowを継続
                result = await flow.run(input_data=user_input)
            else:
                print(f"明確化が完了しました（ターン {i-1}）")
                break
        
        # Show final result
        # 最終結果を表示
        final_result = result.shared_state.get("multi_turn_clarifier_result")
        if isinstance(final_result, ClarificationResult):
            if final_result.is_complete:
                print(f"\n✅ 最終結果（ターン {final_result.turn}）:")
                if isinstance(final_result.data, ReportRequirements):
                    report = final_result.data
                    print(f"  イベント: {report.event}")
                    print(f"  日付: {report.date}")
                    print(f"  場所: {report.place}")
                    print(f"  トピック: {report.topics}")
                    print(f"  印象: {report.interested}")
                    print(f"  感想: {report.expression}")
                else:
                    print(f"  データ: {final_result.data}")
            else:
                print(f"⏸️ 明確化未完了: {final_result.data}")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")


async def example_conversation_history():
    """
    Example showing conversation history management
    会話履歴管理の例
    """
    print("\n=== 会話履歴管理例 ===")
    
    clearify_agent = create_simple_clearify_agent(
        name="history_clarifier",
        instructions="""
        あなたは要件明確化の専門家です。
        前の会話を参考にしながら、段階的に要件を明確化してください。
        """,
        max_turns=3,
        model="gpt-4o-mini"
    )
    
    flow = Flow(steps=[clearify_agent], max_steps=20)
    
    try:
        # First interaction
        # 最初の対話
        result1 = await flow.run(input_data="Webアプリを作りたい")
        print("📝 会話履歴:")
        history = clearify_agent.get_conversation_history()
        for i, interaction in enumerate(history, 1):
            print(f"  {i}. ユーザー: {interaction.get('user_input', 'N/A')}")
            print(f"     AI: {str(interaction.get('ai_response', 'N/A'))[:100]}...")
        
        print(f"\n現在のターン: {clearify_agent.current_turn}")
        print(f"残りターン: {clearify_agent.remaining_turns}")
        print(f"完了状態: {clearify_agent.is_clarification_complete()}")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")


async def main():
    """
    Main function to run all examples
    すべての例を実行するメイン関数
    """
    print("🚀 ClearifyAgent使用例集")
    
    await example_simple_clearify_agent()
    await example_evaluated_clearify_agent()
    await example_multi_turn_clarification()
    await example_conversation_history()
    
    print("\n✨ すべての例が完了しました！")


if __name__ == "__main__":
    asyncio.run(main()) 