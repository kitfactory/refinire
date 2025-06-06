"""
Example usage of ClarifyAgent for requirement clarification in Flow workflows
FlowワークフローでのClarifyAgentの使用侁E- 要件明確匁E
"""

import asyncio
from typing import List
from pydantic import BaseModel

from agents_sdk_models import (
    ClarifyAgent, Flow, DebugStep, create_simple_clarify_agent, 
    create_evaluated_clarify_agent, ClarificationResult
)


class ReportRequirements(BaseModel):
    """
    Model for report requirements
    レポ�Eト要件用モチE��
    """
    event: str  # Event name / イベント名
    date: str   # Date / 日仁E
    place: str  # Place / 場所
    topics: List[str]  # Topics / トピチE��
    interested: str  # What was impressive / 印象に残ったこと
    expression: str  # Thoughts and feelings / 感想・所愁E


async def example_simple_clearify_agent():
    """
    Example of simple ClarifyAgent usage
    シンプルなClarifyAgent使用侁E
    """
    print("=== シンプルなClarifyAgent使用侁E===")
    
    # Create a simple ClarifyAgent
    # シンプルなClarifyAgentを作�E
    clearify_agent = create_simple_clarify_agent(
        name="simple_clarifier",
        instructions="""
        あなた�E要件明確化�E専門家です、E
        ユーザーの要求を琁E��し、不�E確な点めE��足してぁE��惁E��を特定してください、E
        より良ぁE��果のために忁E��な追加惁E��を質問し、要件が十刁E��明確になった場合�Eみ確定してください、E
        """,
        output_data=ReportRequirements,
        max_turns=5,
        model="gpt-4o-mini",
        next_step="debug"
    )
    
    # Create a simple Flow with the ClarifyAgent
    # ClarifyAgentを使ったシンプルなFlowを作�E
    flow = Flow(
        start="simple_clarifier",
        steps={
            "simple_clarifier": clearify_agent,
            "debug": DebugStep("debug", "明確化結果を確誁E)
        },
        max_steps=20
    )
    
    print("📝 要件明確化セチE��ョンを開始しまぁE)
    
    # Simulate user interaction
    # ユーザー対話をシミュレーチE
    try:
        # Initial request
        # 初期要汁E
        result = await flow.run(input_data="チE��クカンファレンスのレポ�Eトを作りたい")
        
        print(f"\n結果:")
        clearify_result = result.shared_state.get("simple_clarifier_result")
        if isinstance(clearify_result, ClarificationResult):
            if clearify_result.is_complete:
                print(f"✁E明確化完亁E {clearify_result.data}")
            else:
                print(f"❁E追加質啁E {clearify_result.data}")
        else:
            print(f"📄 結果: {clearify_result}")
        
    except Exception as e:
        print(f"❁Eエラーが発生しました: {e}")


async def example_evaluated_clearify_agent():
    """
    Example of ClarifyAgent with evaluation capabilities
    評価機�E付きClarifyAgentの侁E
    """
    print("\n=== 評価機�E付きClarifyAgent侁E===")
    
    # Create ClarifyAgent with evaluation
    # 評価機�E付きClarifyAgentを作�E
    clearify_agent = create_evaluated_clarify_agent(
        name="evaluated_clarifier",
        generation_instructions="""
        あなた�E要件明確化�E専門家です、E
        ユーザーの要求を琁E��し、不�E確な点めE��足してぁE��惁E��を特定してください、E
        """,
        evaluation_instructions="""
        あなた�E明確化品質の評価老E��す。以下�E基準で明確化�E質を評価してください�E�E
        1. 完�E性�E�E-100�E�E 忁E��な惁E��がすべて含まれてぁE��ぁE
        2. 明確性�E�E-100�E�E 要求が明確で曖昧さがなぁE��
        3. 実現可能性�E�E-100�E�E 現実的で実現可能な要求か
        平坁E��コアを計算し、各側面につぁE��具体的なコメントを提供してください、E
        """,
        output_data=ReportRequirements,
        max_turns=5,
        model="gpt-4o-mini",
        evaluation_model="gpt-4o-mini",
        threshold=75,
        next_step="debug"
    )
    
    # Create Flow with debug step
    # チE��チE��スチE��プ付きFlowを作�E
    flow = Flow(
        start="evaluated_clarifier",
        steps={
            "evaluated_clarifier": clearify_agent,
            "debug": DebugStep("debug", "評価付き明確化結果を確誁E)
        },
        max_steps=20
    )
    
    try:
        result = await flow.run(input_data="AIアプリケーションを開発したぁE)
        
        print(f"\n結果:")
        clearify_result = result.shared_state.get("evaluated_clarifier_result")
        if isinstance(clearify_result, ClarificationResult):
            if clearify_result.is_complete:
                print(f"✁E評価付き明確化完亁E {clearify_result.data}")
            else:
                print(f"❁E評価後�E追加質啁E {clearify_result.data}")
        else:
            print(f"📄 結果: {clearify_result}")
        
    except Exception as e:
        print(f"❁Eエラーが発生しました: {e}")


async def example_multi_turn_clarification():
    """
    Example of multi-turn clarification process
    褁E��ターンの明確化�Eロセス侁E
    """
    print("\n=== 褁E��ターン明確化�Eロセス侁E===")
    
    # Create ClarifyAgent with custom configuration
    # カスタム設定でClarifyAgentを作�E
    clearify_agent = ClarifyAgent(
        name="multi_turn_clarifier",
        generation_instructions="""
        あなた�E丁寧な要件聞き取りの専門家です、E
        一度に褁E��の質問をせず、一つずつ段階的に質問して要件を�E確化してください、E
        ユーザーの回答に基づぁE��、次に忁E��な惁E��を特定し、E��刁E��質問をしてください、E
        """,
        output_data=ReportRequirements,
        clerify_max_turns=10,
        model="gpt-4o-mini",
        next_step="debug"
    )
    
    # Create context-aware Flow
    # コンチE��スト認識Flowを作�E
    flow = Flow(
        start="multi_turn_clarifier",
        steps={
            "multi_turn_clarifier": clearify_agent,
            "debug": DebugStep("debug", "ターン管琁E��誁E)
        },
        max_steps=20
    )
    
    # Simulate multiple turns of conversation
    # 褁E��ターンの会話をシミュレーチE
    user_inputs = [
        "プロジェクト�E報告書を作りたい",
        "機械学習�EプロジェクトでぁE,
        "2024年12月に東京で実施しました",
        "画像認識と自然言語�E琁E��絁E��合わせたシスチE��でぁE,
        "精度向上とユーザーエクスペリエンスの改喁E��印象皁E��した"
    ]
    
    try:
        # Start with first input
        # 最初�E入力で開姁E
        result = await flow.run(input_data=user_inputs[0])
        
        # Continue conversation if needed
        # 忁E��に応じて会話を継綁E
        for i, user_input in enumerate(user_inputs[1:], 1):
            clearify_result = result.shared_state.get("multi_turn_clarifier_result")
            
            if isinstance(clearify_result, ClarificationResult) and not clearify_result.is_complete:
                print(f"\nターン {i}: {user_input}")
                
                # Continue Flow with new input
                # 新しい入力でFlowを継綁E
                result = await flow.run(input_data=user_input)
            else:
                print(f"明確化が完亁E��ました�E�ターン {i-1}�E�E)
                break
        
        # Show final result
        # 最終結果を表示
        final_result = result.shared_state.get("multi_turn_clarifier_result")
        if isinstance(final_result, ClarificationResult):
            if final_result.is_complete:
                print(f"\n✁E最終結果�E�ターン {final_result.turn}�E�E")
                if isinstance(final_result.data, ReportRequirements):
                    report = final_result.data
                    print(f"  イベンチE {report.event}")
                    print(f"  日仁E {report.date}")
                    print(f"  場所: {report.place}")
                    print(f"  トピチE��: {report.topics}")
                    print(f"  印象: {report.interested}")
                    print(f"  感想: {report.expression}")
                else:
                    print(f"  チE�Eタ: {final_result.data}")
            else:
                print(f"⏸�E�E明確化未完亁E {final_result.data}")
        
    except Exception as e:
        print(f"❁Eエラーが発生しました: {e}")


async def example_conversation_history():
    """
    Example showing conversation history management
    会話履歴管琁E�E侁E
    """
    print("\n=== 会話履歴管琁E��E===")
    
    clearify_agent = create_simple_clarify_agent(
        name="history_clarifier",
        instructions="""
        あなた�E要件明確化�E専門家です、E
        前�E会話を参老E��しながら、段階的に要件を�E確化してください、E
        """,
        max_turns=3,
        model="gpt-4o-mini"
    )
    
    flow = Flow(steps=[clearify_agent], max_steps=20)
    
    try:
        # First interaction
        # 最初�E対話
        result1 = await flow.run(input_data="Webアプリを作りたい")
        print("📝 会話履歴:")
        history = clearify_agent.get_conversation_history()
        for i, interaction in enumerate(history, 1):
            print(f"  {i}. ユーザー: {interaction.get('user_input', 'N/A')}")
            print(f"     AI: {str(interaction.get('ai_response', 'N/A'))[:100]}...")
        
        print(f"\n現在のターン: {clearify_agent.current_turn}")
        print(f"残りターン: {clearify_agent.remaining_turns}")
        print(f"完亁E��慁E {clearify_agent.is_clarification_complete()}")
        
    except Exception as e:
        print(f"❁Eエラーが発生しました: {e}")


async def main():
    """
    Main function to run all examples
    すべての例を実行するメイン関数
    """
    print("🚀 ClarifyAgent使用例集")
    
    await example_simple_clearify_agent()
    await example_evaluated_clearify_agent()
    await example_multi_turn_clarification()
    await example_conversation_history()
    
    print("\n✨ すべての例が完亁E��ました�E�E)


if __name__ == "__main__":
    asyncio.run(main()) 
