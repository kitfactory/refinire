#!/usr/bin/env python3
"""
Trace Demo - Flow/Step to Trace/Span mapping demonstration
フロー/ステップからトレース/スパンマッピングのデモンストレーション

This example demonstrates how Flow acts as a Trace and Step acts as a Span
この例では、FlowがTraceとして、StepがSpanとして機能することを実演します
"""

import asyncio
import json
from datetime import datetime
from refinire import Flow, Context, FunctionStep


def simple_task(name: str):
    """Simple task function for demo / デモ用の簡単なタスク関数"""
    def inner(input_data: str, ctx: Context) -> Context:
        print(f"Task '{name}' executing with input: {input_data}")
        # Simulate some work / 何らかの作業をシミュレート
        import time
        time.sleep(0.1)
        result = f"Result from {name}: {input_data.upper()}"
        ctx.set_artifact(f"{name}_result", result)
        return ctx
    return inner


async def demonstrate_trace_span():
    """
    Demonstrate trace/span relationship
    トレース/スパン関係を実演
    """
    print("🚀 Trace/Span Demo - Flow as Trace, Step as Span")
    print("=" * 60)
    
    # Create steps (each becomes a Span within the Trace)
    # ステップを作成（それぞれがTrace内のSpanになる）
    steps = {
        "step1": FunctionStep(
            name="step1",
            function=simple_task("Task1"),
            next_step="step2"
        ),
        "step2": FunctionStep(
            name="step2",
            function=simple_task("Task2"),
            next_step="step3"
        ),
        "step3": FunctionStep(
            name="step3",
            function=simple_task("Task3"),
            next_step=None
        )
    }
    
    # Create a named flow (becomes a Trace)
    # 名前付きフローを作成（Traceになる）
    flow = Flow(name="trace_demo_flow", steps=steps, start="step1")
    
    print(f"🎯 Flow Information (Trace Level):")
    print(f"   Flow Name: {flow.flow_name}")
    print(f"   Flow ID: {flow.flow_id}")
    print(f"   Trace ID: {flow.trace_id}")
    print()
    
    # Execute the flow
    # フローを実行
    print("⚡ Starting Flow Execution...")
    context = await flow.run("hello world")
    
    print("\n📊 Trace Summary:")
    trace_summary = context.get_trace_summary()
    print(json.dumps(trace_summary, indent=2, default=str))
    
    print("\n📝 Span History (Step-by-Step):")
    span_history = context.get_span_history()
    for i, span in enumerate(span_history, 1):
        print(f"  Span {i}:")
        print(f"    Span ID: {span['span_id']}")
        print(f"    Step Name: {span['step_name']}")
        print(f"    Status: {span['status']}")
        print(f"    Start Time: {span['start_time']}")
        print(f"    End Time: {span.get('end_time', 'N/A')}")
        if span.get('end_time'):
            duration = (span['end_time'] - span['start_time']).total_seconds()
            print(f"    Duration: {duration:.3f}s")
        print()
    
    print("\n🎯 Flow Summary (Complete Trace):")
    flow_summary = flow.get_flow_summary()
    print(json.dumps({
        k: v for k, v in flow_summary.items() 
        if k not in ['span_history', 'execution_history']  # Skip detailed history for readability
    }, indent=2, default=str))


async def demonstrate_error_span():
    """
    Demonstrate error handling in span
    スパンでのエラーハンドリングを実演
    """
    print("\n\n🚨 Error Handling Demo")
    print("=" * 60)
    
    def failing_task(input_data: str, ctx: Context) -> Context:
        """Task that intentionally fails / 意図的に失敗するタスク"""
        print(f"Failing task executing - about to raise error")
        raise ValueError("Intentional error for demo")
    
    # Create error steps
    # エラーステップを作成
    error_steps = {
        "step1": FunctionStep(
            name="step1",
            function=simple_task("GoodTask"),
            next_step="error_step"
        ),
        "error_step": FunctionStep(
            name="error_step", 
            function=failing_task,
            next_step="step3"
        ),
        "step3": FunctionStep(
            name="step3",
            function=simple_task("NeverReached"),
            next_step=None
        )
    }
    
    # Create flow with error step
    # エラーステップ付きフローを作成
    error_flow = Flow(name="error_demo_flow", steps=error_steps, start="step1")
    
    print(f"🎯 Error Flow Information:")
    print(f"   Flow Name: {error_flow.flow_name}")
    print(f"   Trace ID: {error_flow.trace_id}")
    print()
    
    try:
        # Execute the flow - should fail at error_step
        # フローを実行 - error_stepで失敗するはず
        print("⚡ Starting Error Flow Execution...")
        await error_flow.run("test input")
    except Exception as e:
        print(f"❌ Flow failed as expected: {e}")
    
    print("\n📊 Error Trace Summary:")
    error_trace_summary = error_flow.context.get_trace_summary()
    print(json.dumps(error_trace_summary, indent=2, default=str))
    
    print("\n📝 Error Span History:")
    error_span_history = error_flow.context.get_span_history()
    for i, span in enumerate(error_span_history, 1):
        print(f"  Span {i}:")
        print(f"    Span ID: {span['span_id']}")
        print(f"    Step Name: {span['step_name']}")
        print(f"    Status: {span['status']}")
        if span.get('error'):
            print(f"    Error: {span['error']}")
        print()


async def demonstrate_multiple_traces():
    """
    Demonstrate multiple traces (flows) running
    複数のトレース（フロー）の実行を実演
    """
    print("\n\n🔄 Multiple Traces Demo")
    print("=" * 60)
    
    # Create multiple flows (each becomes a separate trace)
    # 複数のフローを作成（それぞれが別のトレースになる）
    flows = []
    for i in range(3):
        steps = {
            "task": FunctionStep(
                name="task",
                function=simple_task(f"ParallelTask{i+1}"),
                next_step=None
            )
        }
        flow = Flow(name=f"parallel_flow_{i+1}", steps=steps, start="task")
        flows.append(flow)
    
    print("⚡ Starting Multiple Flows (Parallel Traces)...")
    
    # Run flows in parallel
    # フローを並列実行
    results = await asyncio.gather(*[
        flow.run(f"input_{i+1}") for i, flow in enumerate(flows)
    ])
    
    print("\n📊 All Trace Summaries:")
    for i, flow in enumerate(flows):
        print(f"\n  Trace {i+1} ({flow.flow_name}):")
        trace_summary = flow.context.get_trace_summary()
        print(f"    Trace ID: {trace_summary['trace_id']}")
        print(f"    Total Spans: {trace_summary['total_spans']}")
        print(f"    Duration: {trace_summary['total_duration_seconds']:.3f}s")


def show_trace_concept():
    """
    Show the conceptual mapping between Flow/Step and Trace/Span
    FlowとStep、TraceとSpanの概念的なマッピングを表示
    """
    print("\n\n💡 Trace/Span Concept Mapping")
    print("=" * 60)
    print("""
    OpenTelemetry Tracing Concepts:
    OpenTelemetryトレーシング概念:

    📊 TRACE (全体の処理フロー)
    ├── Flow = Trace
    │   ├── trace_id: Unique identifier for the entire workflow
    │   ├── flow_name: Human-readable trace name
    │   └── flow_id: Unique flow instance identifier
    │
    └── 🔗 SPANS (個別の処理単位)
        ├── Step = Span
        │   ├── span_id: Unique identifier for each step execution
        │   ├── step_name: Human-readable span name
        │   ├── start_time/end_time: Execution timing
        │   ├── status: completed/error/started
        │   └── parent_trace_id: Links back to the flow trace
        │
        ├── Span Hierarchy: Steps execute sequentially within a Flow
        └── Error Handling: Failed steps create error spans

    🎯 Benefits for Observability:
    オブザーバビリティの利点:
    
    ✅ Distributed Tracing: Each Flow execution gets unique trace_id
    ✅ Step-by-Step Visibility: Each Step creates a span with timing
    ✅ Error Attribution: Failed steps are tracked with error details
    ✅ Performance Analysis: Span durations show step-level performance
    ✅ Flow Correlation: All spans in a flow share the same trace_id
    """)


async def main():
    """Main demo function / メインデモ関数"""
    show_trace_concept()
    await demonstrate_trace_span()
    await demonstrate_error_span()
    await demonstrate_multiple_traces()
    
    print("\n\n✅ Trace Demo Complete!")
    print("🔍 Key Takeaway: Flow = Trace, Step = Span")
    print("   Each Flow execution creates a unique trace with multiple spans")
    print("   各フロー実行は複数のスパンを持つユニークなトレースを作成します")


if __name__ == "__main__":
    asyncio.run(main()) 
