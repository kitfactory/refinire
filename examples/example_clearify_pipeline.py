"""
Example usage of ClearifyPipeline for requirement clarification
ClearifyPipelineの使用例 - 要件明確化
"""

import os
from typing import List
from pydantic import BaseModel

from agents_sdk_models import ClearifyPipeline, ClarificationQuestion


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


def example_interactive_clarification():
    """
    Example of interactive clarification process
    対話的明確化プロセスの例
    """
    print("=== 対話的明確化プロセスの例 ===")
    
    pipeline = ClearifyPipeline(
        name="interactive_clearify",
        generation_instructions="""
        あなたは要件明確化の専門家です。
        ユーザーの要求を理解し、不明確な点や不足している情報を特定してください。
        より良い結果のために必要な追加情報を質問し、要件が十分に明確になった場合のみ確定してください。
        """,
        output_data=ReportRequirements,
        clerify_max_turns=5,
        model="gpt-4o"
    )
    
    print("📝 要件明確化セッションを開始します")
    print(f"最大ターン数: {pipeline.clerify_max_turns}")
    
    # Simulate user inputs (実際の実装では、これはユーザーからの入力になります)
    user_inputs = [
        "テックカンファレンスのレポートを作りたい",
        "PyCon Japan 2024に参加しました",
        "2024年10月に東京で開催されました",
        "AIと機械学習、Webフレームワークについて学びました",
        "特にLLMの実装方法が印象的で、今後のプロジェクトに活用したいと思いました"
    ]
    
    result = None
    input_index = 0
    
    try:
        # Initial call
        # 初回呼び出し
        if input_index < len(user_inputs):
            user_input = user_inputs[input_index]
            print(f"\n👤 ユーザー: {user_input}")
            result = pipeline.run(user_input)
            input_index += 1
        
        # Continue clarification loop
        # 明確化ループを継続
        while input_index < len(user_inputs) and not pipeline.is_complete:
            if isinstance(result, ClarificationQuestion):
                print(f"\n🤖 AI質問: {result}")
                
                if input_index < len(user_inputs):
                    user_response = user_inputs[input_index]
                    print(f"👤 ユーザー回答: {user_response}")
                    result = pipeline.continue_clarification(user_response)
                    input_index += 1
                else:
                    print("⚠️  シミュレート用の入力が不足しました")
                    break
            else:
                # Final result obtained
                # 最終結果を取得
                break
        
        # Display final result
        # 最終結果を表示
        print(f"\n📊 結果:")
        print(f"使用したターン数: {pipeline.current_turn}/{pipeline.clerify_max_turns}")
        
        if isinstance(result, ReportRequirements):
            print("✅ 要件明確化完了!")
            print(f"  イベント名: {result.event}")
            print(f"  日付: {result.date}")
            print(f"  場所: {result.place}")
            print(f"  トピック: {', '.join(result.topics)}")
            print(f"  印象に残ったこと: {result.interested}")
            print(f"  感想: {result.expression}")
        elif isinstance(result, ClarificationQuestion):
            print(f"⏸️  明確化途中で停止: {result}")
        else:
            print(f"📄 その他の結果: {result}")
        
        # Show conversation history
        # 会話履歴を表示
        print(f"\n📝 会話履歴:")
        for i, interaction in enumerate(pipeline.conversation_history, 1):
            print(f"  {i}. ユーザー: {interaction['user_input']}")
            print(f"     AI: {interaction['ai_response'][:100]}...")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")


def example_manual_clarification():
    """
    Example showing manual step-by-step clarification
    手動ステップバイステップ明確化の例
    """
    print("\n=== 手動ステップバイステップ明確化の例 ===")
    
    pipeline = ClearifyPipeline(
        name="manual_clearify",
        generation_instructions="""
        あなたは要件明確化の専門家です。
        ユーザーの要求を理解し、一度に一つずつ質問をして要件を明確化してください。
        """,
        clerify_max_turns=3,
        model="gpt-4o"
    )
    
    # Step 1: Initial request
    # ステップ1: 初期要求
    print("\n--- ステップ1: 初期要求 ---")
    result1 = pipeline.run("何かアプリを作りたい")
    print(f"結果タイプ: {type(result1).__name__}")
    if isinstance(result1, ClarificationQuestion):
        print(f"AI質問: {result1}")
    
    # Initialize result2 and result3
    # result2とresult3を初期化
    result2 = None
    result3 = None
    
    # Step 2: Continue with more details
    # ステップ2: 詳細追加で継続
    if isinstance(result1, ClarificationQuestion) and not pipeline.is_complete:
        print("\n--- ステップ2: 詳細追加 ---")
        result2 = pipeline.continue_clarification("ToDoアプリを作りたいです")
        print(f"結果タイプ: {type(result2).__name__}")
        if isinstance(result2, ClarificationQuestion):
            print(f"AI質問: {result2}")
    
    # Step 3: Final details
    # ステップ3: 最終詳細
    if isinstance(result2, ClarificationQuestion) and not pipeline.is_complete:
        print("\n--- ステップ3: 最終詳細 ---")
        result3 = pipeline.continue_clarification("React Nativeで、チーム共有機能付きにしたいです")
        print(f"結果タイプ: {type(result3).__name__}")
        print(f"最終結果: {result3}")
    
    # Show session status
    # セッション状態を表示
    print(f"\n📊 セッション状態:")
    print(f"  現在のターン: {pipeline.current_turn}")
    print(f"  残りターン: {pipeline.remaining_turns}")
    print(f"  完了状態: {pipeline.is_complete}")


def example_typed_clearify():
    """
    Example with typed output (Pydantic model)
    型付き出力での例（Pydanticモデル）
    """
    print("=== 型付き出力でのClearifyPipeline例 ===")
    
    pipeline = ClearifyPipeline(
        name="clearify_report_requirements",
        generation_instructions="""
        あなたはレポート作成の準備を行います。
        レポートに記載する要件を整理し、魅力的なレポートとなるよう聞き手として、ユーザーと対話し要件を引き出してください。
        要件が明確でなかったり、魅力的でない場合は、さらに質問を繰り返してください。
        必要な項目と、それを魅力的にするポイントを伝えたり、サンプルを提示して、ユーザーの体験からレポートを作成するための、できるだけ詳細な材料を集めてください。
        """,
        output_data=ReportRequirements,
        clerify_max_turns=20,
        evaluation_instructions=None,
        model="gpt-4o"
    )
    
    user_input = "I would like to make a report about a tech conference"
    
    print(f"ユーザー入力: {user_input}")
    print(f"最大ターン数: {pipeline.clerify_max_turns}")
    print("\n--- 明確化プロセス開始 ---")
    
    try:
        result = pipeline.run(user_input)
        
        if isinstance(result, ClarificationQuestion):
            print(f"🤖 AI質問: {result}")
            print("💡 実際の使用では、この質問にユーザーが回答し、continue_clarification()で継続します")
        elif isinstance(result, ReportRequirements):
            print(f"\n✅ 要件明確化完了!")
            print(f"使用したターン数: {pipeline.current_turn}")
            print(f"確定した要件:")
            print(f"  イベント名: {result.event}")
            print(f"  日付: {result.date}")
            print(f"  場所: {result.place}")
            print(f"  トピック: {', '.join(result.topics)}")
            print(f"  印象に残ったこと: {result.interested}")
            print(f"  感想: {result.expression}")
        else:
            print(f"  結果: {result}")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")


def example_string_clearify():
    """
    Example with string output (no specific model)
    文字列出力での例（特定のモデルなし）
    """
    print("\n=== 文字列出力でのClearifyPipeline例 ===")
    
    pipeline = ClearifyPipeline(
        name="clearify_general_request",
        generation_instructions="""
        あなたは要件明確化の専門家です。
        ユーザーの要求を理解し、不明確な点や不足している情報を特定してください。
        より良い結果のために必要な追加情報を質問し、要件が十分に明確になった場合のみ確定してください。
        """,
        clerify_max_turns=10,
        model="gpt-4o"
    )
    
    user_input = "何かいいアプリを作りたい"
    
    print(f"ユーザー入力: {user_input}")
    print(f"最大ターン数: {pipeline.clerify_max_turns}")
    print("\n--- 明確化プロセス開始 ---")
    
    try:
        result = pipeline.run(user_input)
        
        if isinstance(result, ClarificationQuestion):
            print(f"🤖 AI質問: {result}")
            print("💡 実際の使用では、この質問にユーザーが回答し、continue_clarification()で継続します")
        else:
            print(f"\n✅ 要件明確化完了!")
            print(f"使用したターン数: {pipeline.current_turn}")
            print(f"確定した要件: {result}")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")


def example_turn_management():
    """
    Example of turn management features
    ターン管理機能の例
    """
    print("\n=== ターン管理機能の例 ===")
    
    pipeline = ClearifyPipeline(
        name="turn_management_example",
        generation_instructions="簡単な要件明確化テスト",
        clerify_max_turns=5,
        model="gpt-4o"
    )
    
    print(f"初期状態:")
    print(f"  現在のターン: {pipeline.current_turn}")
    print(f"  残りターン数: {pipeline.remaining_turns}")
    print(f"  最大ターン数: {pipeline.clerify_max_turns}")
    print(f"  完了状態: {pipeline.is_complete}")
    
    # Simulate some turns
    # いくつかのターンをシミュレート
    pipeline._turn_count = 3
    print(f"\n3ターン後:")
    print(f"  現在のターン: {pipeline.current_turn}")
    print(f"  残りターン数: {pipeline.remaining_turns}")
    print(f"  完了状態: {pipeline.is_complete}")
    
    # Reset session
    # セッションをリセット
    pipeline.reset_session()
    print(f"\nセッションリセット後:")
    print(f"  現在のターン: {pipeline.current_turn}")
    print(f"  残りターン数: {pipeline.remaining_turns}")
    print(f"  完了状態: {pipeline.is_complete}")
    print(f"  会話履歴: {len(pipeline.conversation_history)}件")


def main():
    """
    Main function to demonstrate ClearifyPipeline usage
    ClearifyPipelineの使用方法を実演するメイン関数
    """
    print("ClearifyPipeline使用例\n")
    
    # Check if API key is available
    # APIキーが利用可能かチェック
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  注意: OPENAI_API_KEYが設定されていません")
        print("実際のLLM呼び出しは行えませんが、構造の例を表示します\n")
    
    # Run examples
    # 例を実行
    example_turn_management()
    
    if os.getenv("OPENAI_API_KEY"):
        try:
            example_manual_clarification()
            example_interactive_clarification()
            example_string_clearify()
            example_typed_clearify()
        except Exception as e:
            print(f"LLM呼び出しエラー: {e}")
    else:
        print("\n=== 構造の例（実際のLLM呼び出しなし） ===")
        print("OPENAI_API_KEYを設定して実際の動作を確認してください")


if __name__ == "__main__":
    main() 