#!/usr/bin/env python3
"""
Flow Identification and Tracing Example
Flowの識別とトレース機能の例

This example demonstrates how to use Flow names, IDs, and tracing features
to track and debug workflow execution.

この例では、Flow名、ID、およびトレース機能を使用してワークフロー実行を
追跡およびデバッグする方法を示します。
"""

import asyncio
from refinire import (
    Flow, Context, UserInputStep, FunctionStep, DebugStep,
    create_simple_flow, enable_console_tracing
)


async def main():
    """
    Demonstrate Flow identification and tracing capabilities
    Flowの識別とトレース機能を実証
    """
    print("Flow Identification and Tracing Examples")
    print("Flow識別とトレース機能の例")
    print("=" * 80)
    
    # Enable tracing for observability
    # オブザーバビリティのためにトレースを有効化
    enable_console_tracing()
    
    # Example 1: Named Flow with automatic trace ID
    # 例1: 自動トレースIDを持つ名前付きFlow
    print("\n" + "=" * 60)
    print("Example 1: Named Flow with Automatic Trace ID")
    print("例1: 自動トレースIDを持つ名前付きFlow")
    print("=" * 60)
    
    welcome_step = UserInputStep("welcome", prompt="Welcome! What's your name?")
    
    def process_name(user_input, ctx):
        ctx.add_assistant_message(f"Hello, {ctx.last_user_input}!")
        return ctx
    
    process_step = FunctionStep("process_name", process_name)
    log_step = DebugStep("log_result")
    
    # Set up sequential flow
    welcome_step.next_step = "process_name"
    process_step.next_step = "log_result"
    
    named_flow = Flow(
        name="user_onboarding_flow",
        start="welcome",
        steps={
            "welcome": welcome_step,
            "process_name": process_step,
            "log_result": log_step,
        }
    )
    
    print(f"Flow Name: {named_flow.flow_name}")
    print(f"Flow ID: {named_flow.flow_id}")
    print(f"Trace ID: {named_flow.trace_id}")
    print()
    
    # Simulate user input and run
    # ユーザー入力をシミュレートして実行
    await named_flow.run("Alice")
    
    # Show flow summary with identification
    # 識別情報付きフローサマリーを表示
    summary = named_flow.get_flow_summary()
    print("\nFlow Summary:")
    print(f"  Name: {summary['flow_name']}")
    print(f"  ID: {summary['flow_id']}")
    print(f"  Steps executed: {summary['step_count']}")
    print(f"  Finished: {summary['finished']}")
    print(f"  Execution history: {len(summary['execution_history'])} steps")
    
    # Example 2: Custom trace ID for correlation
    # 例2: 相関のためのカスタムトレースID
    print("\n" + "=" * 60)
    print("Example 2: Custom Trace ID for Correlation")
    print("例2: 相関のためのカスタムトレースID")
    print("=" * 60)
    
    def validate_payment(user_input, ctx):
        ctx.add_assistant_message("Payment validated")
        return ctx
    
    def process_payment(user_input, ctx):
        ctx.add_assistant_message("Payment processed")
        return ctx
    
    def notify_payment(user_input, ctx):
        ctx.add_assistant_message("Notification sent")
        return ctx
    
    validate_step = FunctionStep("validate", validate_payment)
    process_step = FunctionStep("process", process_payment)
    notify_step = FunctionStep("notify", notify_payment)
    
    # Set up sequential flow manually
    validate_step.next_step = "process"
    process_step.next_step = "notify"
    
    custom_trace_flow = Flow(
        name="payment_processing",
        trace_id="payment_req_12345_20240101",
        start="validate",
        steps={
            "validate": validate_step,
            "process": process_step,
            "notify": notify_step,
        }
    )
    
    print(f"Custom Flow:")
    print(f"  Name: {custom_trace_flow.flow_name}")
    print(f"  Custom Trace ID: {custom_trace_flow.trace_id}")
    print()
    
    await custom_trace_flow.run("process_payment")
    
    # Example 3: Multiple flows with different names for tracking
    # 例3: 追跡のための異なる名前を持つ複数のFlow
    print("\n" + "=" * 60)
    print("Example 3: Multiple Flows for Comparison")
    print("例3: 比較のための複数のFlow")
    print("=" * 60)
    
    flows = []
    flow_names = ["data_pipeline_a", "data_pipeline_b", "error_recovery"]
    
    for flow_name in flow_names:
        def make_start_func(name):
            def start_func(user_input, ctx):
                ctx.add_assistant_message(f"Starting {name}")
                return ctx
            return start_func
        
        def make_process_func(name):
            def process_func(user_input, ctx):
                ctx.add_assistant_message(f"Processing in {name}")
                return ctx
            return process_func
        
        def make_end_func(name):
            def end_func(user_input, ctx):
                ctx.add_assistant_message(f"Completed {name}")
                return ctx
            return end_func
        
        flow = create_simple_flow(
            name=flow_name,
            steps=[
                ("start", FunctionStep("start", make_start_func(flow_name))),
                ("process", FunctionStep("process", make_process_func(flow_name))),
                ("end", FunctionStep("end", make_end_func(flow_name)))
            ]
        )
        flows.append(flow)
        
        print(f"{flow_name}:")
        print(f"  Flow ID: {flow.flow_id}")
        print(f"  Trace ID: {flow.trace_id}")
        
        # Run each flow
        # 各フローを実行
        await flow.run(f"input_for_{flow_name}")
    
    # Example 4: Flow identification in error scenarios
    # 例4: エラーシナリオでのFlow識別
    print("\n" + "=" * 60)
    print("Example 4: Flow Identification in Error Scenarios")
    print("例4: エラーシナリオでのFlow識別")
    print("=" * 60)
    
    def safe_function(user_input, ctx):
        ctx.add_assistant_message("This works fine")
        return ctx
    
    def error_function(user_input, ctx):
        raise ValueError("Simulated error for demonstration")
    
    def recovery_function(user_input, ctx):
        ctx.add_assistant_message("This won't execute")
        return ctx
    
    safe_step = FunctionStep("safe_step", safe_function)
    error_step = FunctionStep("error_step", error_function)
    recovery_step = FunctionStep("recovery", recovery_function)
    
    # Set up sequential flow
    safe_step.next_step = "error_step"
    error_step.next_step = "recovery"
    
    error_flow = Flow(
        name="error_prone_workflow",
        start="safe_step",
        steps={
            "safe_step": safe_step,
            "error_step": error_step,
            "recovery": recovery_step,
        }
    )
    
    print(f"Error Flow:")
    print(f"  Name: {error_flow.flow_name}")
    print(f"  ID: {error_flow.flow_id}")
    print()
    
    try:
        await error_flow.run("test_error")
    except Exception as e:
        print(f"Error caught in flow '{error_flow.flow_name}' (ID: {error_flow.flow_id})")
        print(f"Error: {e}")
        
        # Show execution history up to the error
        # エラーまでの実行履歴を表示
        summary = error_flow.get_flow_summary()
        print(f"Steps completed before error: {summary['step_count']}")
    
    # Example 5: Using flow summary for debugging
    # 例5: デバッグ用のフローサマリー使用
    print("\n" + "=" * 60)
    print("Example 5: Comprehensive Flow Summary")
    print("例5: 包括的なフローサマリー")
    print("=" * 60)
    
    input_step = UserInputStep("input", prompt="Enter debug data:")
    
    def analyze_function(user_input, ctx):
        analysis = {"input": ctx.last_user_input, "length": len(ctx.last_user_input or "")}
        ctx.shared_state["analysis"] = analysis
        ctx.add_assistant_message(f"Analysis: {analysis}")
        return ctx
    
    analyze_step = FunctionStep("analyze", analyze_function)
    output_step = DebugStep("output")
    
    # Set up sequential flow
    input_step.next_step = "analyze"
    analyze_step.next_step = "output"
    
    debug_flow = Flow(
        name="debug_workflow",
        start="input",
        steps={
            "input": input_step,
            "analyze": analyze_step,
            "output": output_step,
        }
    )
    
    await debug_flow.run("debug test data")
    
    # Comprehensive summary
    # 包括的なサマリー
    summary = debug_flow.get_flow_summary()
    print("\nComprehensive Flow Summary:")
    print("-" * 40)
    for key, value in summary.items():
        if key == "execution_history":
            print(f"{key}: {len(value)} steps")
            for i, step in enumerate(value):
                print(f"  {i+1}. {step.get('step_name', 'Unknown')} at {step.get('timestamp', 'N/A')}")
        elif key == "artifacts":
            print(f"{key}: {len(value)} items")
        else:
            print(f"{key}: {value}")
    
    # Example 6: Show flow diagram with identification
    # 例6: 識別情報付きフロー図を表示
    print("\n" + "=" * 60)
    print("Example 6: Flow Diagram with Identification")
    print("例6: 識別情報付きフロー図")
    print("=" * 60)
    
    def step1_func(user_input, ctx):
        ctx.add_assistant_message("Step 1 complete")
        return ctx
    
    def step2_func(user_input, ctx):
        ctx.add_assistant_message("Step 2 complete")
        return ctx
    
    def step3_func(user_input, ctx):
        ctx.add_assistant_message("Step 3 complete")
        return ctx
    
    step1 = FunctionStep("step1", step1_func)
    step2 = FunctionStep("step2", step2_func)
    step3 = FunctionStep("step3", step3_func)
    
    # Set up sequential flow
    step1.next_step = "step2"
    step2.next_step = "step3"
    
    diagram_flow = Flow(
        name="visualization_demo",
        start="step1",
        steps={
            "step1": step1,
            "step2": step2,
            "step3": step3,
        }
    )
    
    # Run the flow
    # フローを実行
    await diagram_flow.run("demo")
    
    print(f"Flow: {diagram_flow.flow_name} (ID: {diagram_flow.flow_id})")
    print("\nFlow Structure and Execution:")
    print(diagram_flow.show(format="text", include_history=True))
    
    print("\n" + "=" * 80)
    print("All examples completed!")
    print("すべての例が完了しました！")
    
    print("\n📋 Key Features Demonstrated:")
    print("実証された主要機能:")
    print("  ✅ Automatic Flow ID generation")
    print("     自動Flow ID生成")
    print("  ✅ Custom trace ID support")
    print("     カスタムトレースID対応")
    print("  ✅ Named flows for identification")
    print("     識別用の名前付きFlow")
    print("  ✅ Comprehensive execution tracking")
    print("     包括的な実行追跡")
    print("  ✅ Error scenario identification")
    print("     エラーシナリオの識別")
    print("  ✅ Flow summary and debugging")
    print("     フローサマリーとデバッグ")


if __name__ == "__main__":
    asyncio.run(main()) 
