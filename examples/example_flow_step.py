"""
Example usage of Flow/Step workflow system
Flow/Stepワークフローシステムの使用例
"""

import asyncio
import os
from typing import List

from refinire.agents.flow import (
    Flow, Context, UserInputStep, ConditionStep, FunctionStep, DebugStep,
    create_simple_condition, create_simple_flow
)


def example_simple_linear_flow():
    """
    Example of a simple linear flow
    簡単な線形フローの例
    """
    print("=== 簡単な線形フローの例 ===")
    
    # Create steps
    # ステップを作成
    welcome_step = DebugStep("welcome", "ようこそ！お名前を教えてください", next_step="process")
    
    def process_name(user_input, ctx):
        name = "田中太郎"  # ダミー値を直接セット
        ctx.shared_state["user_name"] = name
        ctx.add_assistant_message(f"こんにちは、{name}さん！")
        return ctx
    
    process_step = FunctionStep("process", process_name, "farewell")
    
    def farewell_message(user_input, ctx):
        ctx.add_assistant_message(f"さようなら、{ctx.shared_state.get('user_name', 'ゲスト')}さん！")
        return ctx
    
    farewell_step = FunctionStep("farewell", farewell_message)
    
    # Create flow
    # フローを作成
    flow = Flow(
        start="welcome",
        steps={
            "welcome": welcome_step,
            "process": process_step,
            "farewell": farewell_step
        }
    )
    
    # Simulate synchronous CLI interaction
    # 同期CLI対話をシミュレート
    print("同期CLIモード:")
    
    # Start flow
    # フロー開始
    while not flow.finished:
        # Execute next step
        # 次ステップを実行
        flow.step()
    
    print("\nフロー完了!")
    print(f"会話履歴: {flow.context.get_conversation_text()}")
    print(f"最終状態: {flow.context.shared_state}")


async def example_async_interactive_flow():
    """
    Example of async interactive flow
    非同期対話フローの例
    """
    print("\n=== 非同期対話フローの例 ===")
    
    print("ステップ1: フロー作成開始")
    # Create a more complex flow with conditions
    # 条件を含むより複雑なフローを作成
    
    # Greeting step
    # 挨拶ステップ
    greeting_step = DebugStep("greeting", "何をお手伝いしましょうか？", next_step="analyze")
    
    print("ステップ2: 分析ステップ作成")
    # Analysis step
    # 分析ステップ
    def analyze_request(user_input, ctx):
        # シミュレートされたユーザー入力を使用
        request = "質問があります"
        if "質問" in request or "聞きたい" in request:
            ctx.shared_state["request_type"] = "question"
        elif "作成" in request or "作って" in request:
            ctx.shared_state["request_type"] = "creation"
        else:
            ctx.shared_state["request_type"] = "other"
        return ctx
    
    analyze_step = FunctionStep("analyze", analyze_request, "route")
    
    print("ステップ3: ルーティング条件作成")
    # Routing condition
    # ルーティング条件
    def route_condition(ctx):
        return ctx.shared_state.get("request_type") == "question"
    
    route_step = ConditionStep("route", route_condition, "handle_question", "handle_other")
    
    print("ステップ4: 質問処理ステップ作成")
    # Question handling
    # 質問処理
    question_step = DebugStep("handle_question", "どんな質問ですか？", next_step="answer")
    
    def answer_question(user_input, ctx):
        # ダミー値を直接セット
        question = "Pythonの基本的な使い方について教えてください"
        ctx.add_assistant_message(f"ご質問「{question}」について調べてお答えします。")
        return ctx
    
    answer_step = FunctionStep("answer", answer_question)
    
    print("ステップ5: その他処理ステップ作成")
    # Other handling
    # その他処理
    def handle_other_request(user_input, ctx):
        ctx.add_assistant_message("申し訳ございませんが、現在その機能は対応しておりません。")
        return ctx
    
    other_step = FunctionStep("handle_other", handle_other_request)
    
    print("ステップ6: フロー作成")
    # Create flow
    # フローを作成
    flow = Flow(
        start="greeting",
        steps={
            "greeting": greeting_step,
            "analyze": analyze_step,
            "route": route_step,
            "handle_question": question_step,
            "answer": answer_step,
            "handle_other": other_step
        }
    )
    
    print("ステップ7: フロー実行開始")
    # Simulate async interaction
    # 非同期対話をシミュレート
    print("非同期モード:")
    
    # Execute flow using async run method
    # 非同期runメソッドを使用してフローを実行
    try:
        await flow.run()
        print("ステップ8: フロー完了")
        print("\nフロー完了!")
        print(f"会話履歴:\n{flow.context.get_conversation_text()}")
        print(f"リクエストタイプ: {flow.context.shared_state.get('request_type')}")
    except Exception as e:
        print(f"フロー実行中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


def example_agent_pipeline_integration():
    """
    Example of integrating RefinireAgent with Flow
    RefinireAgentとFlowの統合例
    """
    print("\n=== RefinireAgent統合の例 ===")
    
    try:
        # Create a simple agent
        # 簡単なエージェントを作成
        from refinire import RefinireAgent
        
        agent = RefinireAgent(
            name="summary_agent",
            generation_instructions="ユーザーの入力を簡潔に要約してください。",
            model="gpt-4o"
        )
        
        # Create steps with agent integration
        # エージェント統合でステップを作成
        input_step = DebugStep("input", "要約したいテキストを入力してください", next_step="process")
        
        # Wrap agent in a step
        # エージェントをステップでラップ
        def process_with_agent(user_input, ctx):
            # ダミー値を直接セット
            sample_text = "Pythonは、プログラミング言語の一つです。読みやすく、書きやすい言語として知られています。"
            result = agent.run(sample_text)
            if result.success:
                return result.content
            else:
                return f"エラー: {result.metadata.get('error', 'Unknown error')}"
        
        process_step = FunctionStep("process", process_with_agent, next_step="show_result")
        
        def show_result(user_input, ctx):
            result = ctx.prev_outputs.get("process")
            if result:
                ctx.add_system_message(f"要約結果: {result}")
            return ctx
        
        result_step = FunctionStep("show_result", show_result)
        
        # Create flow
        # フローを作成
        flow = Flow(
            start="input",
            steps={
                "input": input_step,
                "process": process_step,
                "show_result": result_step
            }
        )
        
        print("RefinireAgent統合フローを作成しました")
        print("実際の実行にはOPENAI_API_KEYが必要です")
        
        # Execute flow for demo
        # デモ用にフローを実行
        while not flow.finished:
            flow.step()
        
        print("\nフロー完了!")
        print(f"会話履歴: {flow.context.get_conversation_text()}")
        
    except Exception as e:
        print(f"エージェント統合例の実行中にエラーが発生しました: {e}")
        print("OPENAI_API_KEYが設定されていない可能性があります")


def example_utility_functions():
    """
    Example of utility functions
    ユーティリティ関数の例
    """
    print("\n=== ユーティリティ関数の例 ===")
    
    # Create simple condition
    # 簡単な条件を作成
    condition = create_simple_condition("shared_state.count", 5)
    
    # Test condition
    # 条件をテスト
    ctx = Context()
    ctx.shared_state["count"] = 3
    print(f"Count=3の時の条件結果: {condition(ctx)}")
    
    ctx.shared_state["count"] = 5
    print(f"Count=5の時の条件結果: {condition(ctx)}")
    
    # Create simple flow using utility
    # ユーティリティを使用して簡単なフローを作成
    step1 = DebugStep("debug1", "ステップ1実行", next_step="debug2")
    step2 = DebugStep("debug2", "ステップ2実行")
    
    simple_flow = create_simple_flow([
        ("debug1", step1),
        ("debug2", step2)
    ])
    
    print(f"簡単なフロー作成: {simple_flow}")


async def example_observability():
    """
    Example of observability features
    オブザーバビリティ機能の例
    """
    print("\n=== オブザーバビリティの例 ===")
    
    # Create flow with debug steps
    # デバッグステップでフローを作成
    debug1 = DebugStep("debug1", "開始", print_context=False, next_step="debug2")
    debug2 = DebugStep("debug2", "処理中", print_context=False, next_step="debug3")
    debug3 = DebugStep("debug3", "完了", print_context=False)
    
    flow = Flow(
        start="debug1",
        steps={
            "debug1": debug1,
            "debug2": debug2,
            "debug3": debug3
        }
    )
    
    # Add hooks
    # フックを追加
    def before_step_hook(step_name, context):
        print(f"🚀 ステップ開始: {step_name}")
    
    def after_step_hook(step_name, context, result):
        print(f"✅ ステップ完了: {step_name}")
    
    def error_hook(step_name, context, error):
        print(f"❌ ステップエラー: {step_name} - {error}")
    
    flow.add_hook("before_step", before_step_hook)
    flow.add_hook("after_step", after_step_hook)
    flow.add_hook("error", error_hook)
    
    # Run flow
    # フローを実行
    print("フック付きフロー実行:")
    await flow.run()
    
    # Show history
    # 履歴を表示
    print("\n実行履歴:")
    history = flow.get_step_history()
    for entry in history:
        timestamp = entry.get('timestamp', 'Unknown')
        message = entry.get('message', 'No message')
        print(f"  {timestamp}: {message}")
    
    # Show summary
    # サマリーを表示
    print(f"\nフローサマリー:")
    summary = flow.get_flow_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")


def main():
    """
    Main function to run all examples
    全ての例を実行するメイン関数
    """
    print("Flow/Step ワークフローシステム使用例\n")
    
    # Check if API key is available
    # APIキーが利用可能かチェック
    has_api_key = bool(os.getenv("OPENAI_API_KEY"))
    if not has_api_key:
        print("⚠️  注意: OPENAI_API_KEYが設定されていません")
        print("RefinireAgent統合機能は制限されます\n")
    
    # Run examples
    # 例を実行
    try:
        print("1. 簡単な線形フローを実行中...")
        example_simple_linear_flow()
        
        print("2. 非同期対話フローを実行中...")
        # 非同期フローを同期実行に変更
        import asyncio
        asyncio.run(example_async_interactive_flow())
        
        print("3. RefinireAgent統合例を実行中...")
        example_agent_pipeline_integration()
        
        print("4. ユーティリティ関数例を実行中...")
        example_utility_functions()
        
        print("5. オブザーバビリティ例を実行中...")
        # オブザーバビリティ例も同期実行
        asyncio.run(example_observability())
        
        print("\n🎉 全ての例が正常に実行されました！")
        
    except Exception as e:
        print(f"\n❌ 例の実行中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 
