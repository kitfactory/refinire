"""
Example usage of Flow/Step workflow system
Flow/Stepワークフローシステムの使用例
"""

import asyncio
import os
from typing import List

from refinire.flow import (
    Flow, Context, UserInputStep, ConditionStep, FunctionStep, DebugStep,
    create_simple_condition, create_simple_flow
)
from refinire.pipeline import (
    AgentPipelineStep, AgentPipeline
)


def example_simple_linear_flow():
    """
    Example of a simple linear flow
    簡単な線形フローの例
    """
    print("=== 簡単な線形フローの例 ===")
    
    # Create steps
    # ステップを作成
    welcome_step = UserInputStep("welcome", "ようこそ！お名前を教えてください", "process")
    
    def process_name(user_input, ctx):
        name = ctx.last_user_input
        ctx.shared_state["user_name"] = name
        ctx.add_assistant_message(f"こんにちは、{name}さん！")
        return ctx
    
    process_step = FunctionStep("process", process_name, "farewell")
    
    farewell_step = FunctionStep("farewell", 
        lambda ui, ctx: ctx.add_assistant_message(f"さようなら、{ctx.shared_state.get('user_name', 'ゲスト')}さん！"))
    
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
        # Check for prompt
        # プロンプトをチェック
        prompt = flow.next_prompt()
        if prompt:
            print(f"システム: {prompt}")
            user_input = "田中太郎"  # シミュレートされたユーザー入力
            print(f"ユーザー: {user_input}")
            flow.feed(user_input)
        else:
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
    
    # Create a more complex flow with conditions
    # 条件を含むより複雑なフローを作成
    
    # Greeting step
    # 挨拶ステップ
    greeting_step = UserInputStep("greeting", "何をお手伝いしましょうか？", "analyze")
    
    # Analysis step
    # 分析ステップ
    def analyze_request(user_input, ctx):
        request = ctx.last_user_input.lower()
        if "質問" in request or "聞きたい" in request:
            ctx.shared_state["request_type"] = "question"
        elif "作成" in request or "作って" in request:
            ctx.shared_state["request_type"] = "creation"
        else:
            ctx.shared_state["request_type"] = "other"
        return ctx
    
    analyze_step = FunctionStep("analyze", analyze_request, "route")
    
    # Routing condition
    # ルーティング条件
    def route_condition(ctx):
        return ctx.shared_state.get("request_type") == "question"
    
    route_step = ConditionStep("route", route_condition, "handle_question", "handle_other")
    
    # Question handling
    # 質問処理
    question_step = UserInputStep("handle_question", "どんな質問ですか？", "answer")
    
    def answer_question(user_input, ctx):
        question = ctx.last_user_input
        ctx.add_assistant_message(f"ご質問「{question}」について調べてお答えします。")
        return ctx
    
    answer_step = FunctionStep("answer", answer_question)
    
    # Other handling
    # その他処理
    def handle_other_request(user_input, ctx):
        ctx.add_assistant_message("申し訳ございませんが、現在その機能は対応しておりません。")
        return ctx
    
    other_step = FunctionStep("handle_other", handle_other_request)
    
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
    
    # Simulate async interaction
    # 非同期対話をシミュレート
    print("非同期モード:")
    
    # Start flow as background task
    # フローをバックグラウンドタスクとして開始
    task = await flow.start_background_task()
    
    # Simulate user inputs
    # ユーザー入力をシミュレート
    user_inputs = [
        "質問があります",
        "Pythonの基本的な使い方について教えてください"
    ]
    
    input_index = 0
    
    while not flow.finished and input_index < len(user_inputs):
        # Wait for prompt
        # プロンプトを待機
        try:
            prompt = await asyncio.wait_for(flow.context.wait_for_prompt_event(), timeout=1.0)
            if prompt:
                print(f"システム: {prompt}")
                if input_index < len(user_inputs):
                    user_input = user_inputs[input_index]
                    print(f"ユーザー: {user_input}")
                    flow.feed(user_input)
                    input_index += 1
        except asyncio.TimeoutError:
            # No prompt waiting, continue
            # プロンプト待機なし、継続
            await asyncio.sleep(0.1)
    
    # Wait for task completion
    # タスク完了を待機
    await task
    
    print("\nフロー完了!")
    print(f"会話履歴:\n{flow.context.get_conversation_text()}")
    print(f"リクエストタイプ: {flow.context.shared_state.get('request_type')}")


def example_agent_pipeline_integration():
    """
    Example of integrating AgentPipeline with Flow
    AgentPipelineとFlowの統合例
    """
    print("\n=== AgentPipeline統合の例 ===")
    
    try:
        # Create a simple pipeline
        # 簡単なパイプラインを作成
        pipeline = AgentPipeline(
            name="summary_agent",
            generation_instructions="ユーザーの入力を簡潔に要約してください。",
            model="gpt-4o"
        )
        
        # Create steps with pipeline integration
        # パイプライン統合でステップを作成
        input_step = UserInputStep("input", "要約したいテキストを入力してください", "process")
        
        # Wrap pipeline in a step
        # パイプラインをステップでラップ
        pipeline_step = AgentPipelineStep("process", pipeline, "show_result")
        
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
                "process": pipeline_step,
                "show_result": result_step
            }
        )
        
        print("AgentPipeline統合フローを作成しました")
        print("実際の実行にはOPENAI_API_KEYが必要です")
        
        # Show flow structure
        # フロー構造を表示
        summary = flow.get_flow_summary()
        print(f"フロー情報: {summary}")
        
    except Exception as e:
        print(f"AgentPipeline統合例でエラー: {e}")


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
        print(f"  {entry['timestamp']}: {entry['message']}")
    
    # Show summary
    # サマリーを表示
    print(f"\nフローサマリー:")
    summary = flow.get_flow_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")


async def main():
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
        print("AgentPipeline統合機能は制限されます\n")
    
    # Run examples
    # 例を実行
    try:
        example_simple_linear_flow()
        await example_async_interactive_flow()
        example_agent_pipeline_integration()
        example_utility_functions()
        await example_observability()
        
        print("\n🎉 全ての例が正常に実行されました！")
        
    except Exception as e:
        print(f"\n❌ 例の実行中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 
