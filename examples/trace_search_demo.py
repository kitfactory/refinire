#!/usr/bin/env python3
"""
Trace Search Demo - Search traces by flow name and agent name
トレース検索デモ - フロー名とエージェント名でトレースを検索

This example demonstrates how to search traces using the TraceRegistry
この例では、TraceRegistryを使用してトレースを検索する方法を実演します
"""

import asyncio
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import (
    Flow, Context, FunctionStep, TraceRegistry, 
    get_global_registry, set_global_registry
)


def create_agent_step(agent_name: str, task_description: str):
    """Create a step that simulates an agent / エージェントをシミュレートするステップを作成"""
    def agent_function(input_data: str, ctx: Context) -> Context:
        print(f"🤖 Agent '{agent_name}' executing: {task_description}")
        result = f"Agent {agent_name} completed: {task_description} with input '{input_data}'"
        ctx.set_artifact(f"{agent_name}_result", result)
        # Add agent name to context for tracking
        # 追跡用にエージェント名をコンテキストに追加
        if not hasattr(ctx, 'agent_names'):
            ctx.agent_names = []
        ctx.agent_names.append(agent_name)
        return ctx
    
    # Create step with agent information
    # エージェント情報付きのステップを作成
    step = FunctionStep(name=f"{agent_name}_step", function=agent_function)
    step.agent_name = agent_name  # Add agent name for extraction
    return step


async def create_sample_flows():
    """
    Create sample flows with different names and agents
    異なる名前とエージェントでサンプルフローを作成
    """
    print("📋 Creating Sample Flows...")
    
    # Flow 1: Customer Support Workflow
    # フロー1: カスタマーサポートワークフロー
    support_steps = {
        "intake": create_agent_step("SupportAgent", "Collect customer inquiry"),
        "analysis": create_agent_step("AnalysisAgent", "Analyze customer issue"),
        "resolution": create_agent_step("ResolutionAgent", "Provide solution")
    }
    support_steps["intake"].next_step = "analysis"
    support_steps["analysis"].next_step = "resolution"
    
    support_flow = Flow(
        name="customer_support_workflow",
        steps=support_steps,
        start="intake"
    )
    
    # Flow 2: Data Processing Pipeline
    # フロー2: データ処理パイプライン
    data_steps = {
        "extract": create_agent_step("ExtractorAgent", "Extract data from source"),
        "transform": create_agent_step("TransformAgent", "Transform data format"),
        "load": create_agent_step("LoaderAgent", "Load data to destination")
    }
    data_steps["extract"].next_step = "transform"
    data_steps["transform"].next_step = "load"
    
    data_flow = Flow(
        name="data_processing_pipeline",
        steps=data_steps,
        start="extract"
    )
    
    # Flow 3: Document Analysis
    # フロー3: ドキュメント分析
    doc_steps = {
        "scan": create_agent_step("ScannerAgent", "Scan document"),
        "ocr": create_agent_step("OCRAgent", "Extract text from document"),
        "classify": create_agent_step("ClassifyAgent", "Classify document type"),
        "summarize": create_agent_step("SummaryAgent", "Create document summary")
    }
    doc_steps["scan"].next_step = "ocr"
    doc_steps["ocr"].next_step = "classify"
    doc_steps["classify"].next_step = "summarize"
    
    doc_flow = Flow(
        name="document_analysis_flow",
        steps=doc_steps,
        start="scan"
    )
    
    # Execute all flows
    # すべてのフローを実行
    flows = [support_flow, data_flow, doc_flow]
    inputs = ["customer complaint about billing", "sales_data.csv", "contract_document.pdf"]
    
    for flow, input_data in zip(flows, inputs):
        print(f"\n⚡ Executing {flow.name}...")
        await flow.run(input_data)
        print(f"✅ Completed {flow.name}")
    
    return flows


def demonstrate_search_functionality():
    """
    Demonstrate various search capabilities
    様々な検索機能をデモンストレーション
    """
    print("\n\n🔍 Trace Search Demonstration")
    print("=" * 60)
    
    registry = get_global_registry()
    
    # 1. Search by Flow Name
    # 1. フロー名で検索
    print("\n1️⃣ Search by Flow Name:")
    print("-" * 30)
    
    # Exact match
    # 完全一致
    exact_matches = registry.search_by_flow_name("customer_support_workflow", exact_match=True)
    print(f"📍 Exact match for 'customer_support_workflow': {len(exact_matches)} traces")
    for trace in exact_matches:
        print(f"   - {trace.trace_id} (Start: {trace.start_time.strftime('%H:%M:%S')})")
    
    # Partial match
    # 部分一致
    partial_matches = registry.search_by_flow_name("support", exact_match=False)
    print(f"🔎 Partial match for 'support': {len(partial_matches)} traces")
    for trace in partial_matches:
        print(f"   - {trace.flow_name} | {trace.trace_id}")
    
    # 2. Search by Agent Name
    # 2. エージェント名で検索
    print("\n2️⃣ Search by Agent Name:")
    print("-" * 30)
    
    # Search for specific agent
    # 特定のエージェントを検索
    agent_traces = registry.search_by_agent_name("SupportAgent", exact_match=True)
    print(f"🤖 Traces using 'SupportAgent': {len(agent_traces)} traces")
    for trace in agent_traces:
        print(f"   - Flow: {trace.flow_name}")
        print(f"     Agents: {', '.join(trace.agent_names)}")
    
    # Search for agent pattern
    # エージェントパターンを検索
    ocr_traces = registry.search_by_agent_name("OCR", exact_match=False)
    print(f"📝 Traces with OCR-related agents: {len(ocr_traces)} traces")
    for trace in ocr_traces:
        print(f"   - Flow: {trace.flow_name} | Agents: {', '.join(trace.agent_names)}")
    
    # 3. Search by Tags
    # 3. タグで検索
    print("\n3️⃣ Search by Tags:")
    print("-" * 30)
    
    tag_traces = registry.search_by_tags({"flow_type": "default"})
    print(f"🏷️ Traces with tag 'flow_type=default': {len(tag_traces)} traces")
    
    # 4. Search by Status
    # 4. ステータスで検索
    print("\n4️⃣ Search by Status:")
    print("-" * 30)
    
    completed_traces = registry.search_by_status("completed")
    print(f"✅ Completed traces: {len(completed_traces)} traces")
    
    error_traces = registry.search_by_status("error")
    print(f"❌ Error traces: {len(error_traces)} traces")
    
    # 5. Search by Time Range
    # 5. 時間範囲で検索
    print("\n5️⃣ Search by Time Range:")
    print("-" * 30)
    
    recent_traces = registry.get_recent_traces(hours=1)
    print(f"⏰ Recent traces (last 1 hour): {len(recent_traces)} traces")
    
    # 6. Complex Search
    # 6. 複合検索
    print("\n6️⃣ Complex Search:")
    print("-" * 30)
    
    complex_results = registry.complex_search(
        flow_name="data",
        agent_name="Extract",
        status="completed",
        max_results=5
    )
    print(f"🎯 Complex search (flow contains 'data', agent contains 'Extract', status='completed'): {len(complex_results)} traces")
    for trace in complex_results:
        print(f"   - {trace.flow_name} | Agents: {', '.join(trace.agent_names)}")


def demonstrate_statistics():
    """
    Show trace statistics
    トレース統計を表示
    """
    print("\n\n📊 Trace Statistics")
    print("=" * 60)
    
    registry = get_global_registry()
    stats = registry.get_statistics()
    
    print(f"📈 Total Traces: {stats['total_traces']}")
    print(f"📈 Unique Flow Names: {stats['unique_flow_names']}")
    print(f"📈 Unique Agent Names: {stats['unique_agent_names']}")
    print(f"📈 Total Spans: {stats['total_spans']}")
    print(f"📈 Total Errors: {stats['total_errors']}")
    print(f"📈 Average Duration: {stats['average_duration_seconds']:.2f} seconds")
    
    print(f"\n📝 Flow Names:")
    for flow_name in stats['flow_names']:
        print(f"   - {flow_name}")
    
    print(f"\n🤖 Agent Names:")
    for agent_name in stats['agent_names']:
        print(f"   - {agent_name}")
    
    print(f"\n📊 Status Distribution:")
    for status, count in stats['status_distribution'].items():
        print(f"   - {status}: {count}")


def demonstrate_export_import():
    """
    Demonstrate export/import functionality
    エクスポート/インポート機能をデモンストレーション
    """
    print("\n\n💾 Export/Import Demonstration")
    print("=" * 60)
    
    registry = get_global_registry()
    
    # Export traces
    # トレースをエクスポート
    export_file = "trace_export.json"
    print(f"📤 Exporting traces to {export_file}...")
    registry.export_traces(export_file)
    print("✅ Export completed")
    
    # Create new registry and import
    # 新しいレジストリを作成してインポート
    new_registry = TraceRegistry()
    print(f"📥 Importing traces from {export_file}...")
    imported_count = new_registry.import_traces(export_file)
    print(f"✅ Imported {imported_count} traces")
    
    # Verify import
    # インポートを検証
    original_stats = registry.get_statistics()
    new_stats = new_registry.get_statistics()
    
    print(f"🔍 Verification:")
    print(f"   Original traces: {original_stats['total_traces']}")
    print(f"   Imported traces: {new_stats['total_traces']}")
    print(f"   Match: {'✅' if original_stats['total_traces'] == new_stats['total_traces'] else '❌'}")


async def demonstrate_real_time_search():
    """
    Demonstrate real-time search during flow execution
    フロー実行中のリアルタイム検索をデモンストレーション
    """
    print("\n\n⚡ Real-time Search During Execution")
    print("=" * 60)
    
    registry = get_global_registry()
    
    # Create a long-running flow
    # 長時間実行されるフローを作成
    def slow_task(task_name: str):
        def inner(input_data: str, ctx: Context) -> Context:
            print(f"🔄 {task_name} starting...")
            import time
            time.sleep(0.5)  # Simulate work
            print(f"✅ {task_name} completed")
            return ctx
        return inner
    
    slow_flow = Flow(
        name="long_running_process",
        steps={
            "step1": FunctionStep(name="step1", function=slow_task("Phase 1"), next_step="step2"),
            "step2": FunctionStep(name="step2", function=slow_task("Phase 2"), next_step="step3"),
            "step3": FunctionStep(name="step3", function=slow_task("Phase 3"), next_step=None)
        },
        start="step1"
    )
    
    # Start flow execution in background
    # フロー実行をバックグラウンドで開始
    print("🚀 Starting long-running flow...")
    flow_task = asyncio.create_task(slow_flow.run("background_data"))
    
    # Search for running flows
    # 実行中のフローを検索
    await asyncio.sleep(0.1)  # Give time for registration
    
    running_traces = registry.search_by_status("running")
    print(f"🏃 Currently running traces: {len(running_traces)}")
    for trace in running_traces:
        print(f"   - {trace.flow_name} (Started: {trace.start_time.strftime('%H:%M:%S')})")
    
    # Wait for completion
    # 完了を待機
    await flow_task
    
    # Search for completed flows
    # 完了したフローを検索
    completed_traces = registry.search_by_flow_name("long_running_process")
    print(f"✅ Completed 'long_running_process' traces: {len(completed_traces)}")


async def main():
    """Main demonstration function / メインデモ関数"""
    print("🚀 Trace Search Demo - Search by Flow Name and Agent Name")
    print("=" * 70)
    
    # Create sample flows with different agents
    # 異なるエージェントでサンプルフローを作成
    await create_sample_flows()
    
    # Demonstrate search functionality
    # 検索機能をデモンストレーション
    demonstrate_search_functionality()
    
    # Show statistics
    # 統計を表示
    demonstrate_statistics()
    
    # Show export/import
    # エクスポート/インポートを表示
    demonstrate_export_import()
    
    # Real-time search
    # リアルタイム検索
    await demonstrate_real_time_search()
    
    print("\n\n✅ Trace Search Demo Complete!")
    print("\n🎯 Key Features Demonstrated:")
    print("   ✅ Search by Flow Name (exact and partial match)")
    print("   ✅ Search by Agent Name (exact and partial match)")
    print("   ✅ Search by Tags, Status, Time Range")
    print("   ✅ Complex multi-criteria search")
    print("   ✅ Real-time search during execution")
    print("   ✅ Export/Import trace data")
    print("   ✅ Comprehensive statistics")
    
    print("\n💡 Use Cases:")
    print("   🔍 Find all flows that used a specific agent")
    print("   📊 Monitor flow execution patterns")
    print("   🐛 Debug issues by searching error traces")
    print("   📈 Analyze performance across different flows")
    print("   🕐 Track recent activity and long-running processes")


if __name__ == "__main__":
    asyncio.run(main()) 
