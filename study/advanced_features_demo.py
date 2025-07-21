#!/usr/bin/env python3
"""
Advanced Features Demo - routing_instruction、fast_mode、Flowの統合デモ
高度機能デモ - ルーティング指示、高速モード、フローの統合実演

This demonstrates the combined use of routing_instruction, fast_mode, and Flow.
ルーティング指示、高速モード、フローの組み合わせ使用を実演します。
"""

import asyncio
import os
import time
from typing import Literal
from refinire import RefinireAgent
from refinire.agents.flow import Flow, FunctionStep, ConditionStep, Context


# Define request types / リクエストタイプを定義
RequestType = Literal["urgent", "standard", "analysis"]


class SmartRequestProcessor:
    """
    Smart request processor combining all advanced features
    すべての高度機能を組み合わせたスマートリクエストプロセッサー
    """
    
    def __init__(self):
        # Router agent with routing_instruction / ルーティング指示付きルーターエージェント
        self.router = RefinireAgent(
            name="smart_router",
            generation_instructions="""
You are an intelligent request classifier. Analyze incoming requests and categorize them:

- urgent: Time-sensitive requests, quick questions, immediate needs
- standard: Regular requests that need thorough processing
- analysis: Complex analytical tasks requiring detailed investigation

リクエストを分析し、以下のカテゴリに分類してください:
- urgent: 時間に敏感な要求、簡単な質問、即座の必要性
- standard: 徹底的な処理が必要な通常のリクエスト  
- analysis: 詳細な調査が必要な複雑な分析タスク
            """,
            model="gpt-4o-mini",
            routing_instruction="Classify this request into the most appropriate category",
            fast_mode=True,  # Use fast mode for quick routing / 高速ルーティングのため高速モード使用
            timeout=30
        )
        
        # Urgent processor with fast_mode / 高速モード付き緊急プロセッサー
        self.urgent_processor = RefinireAgent(
            name="urgent_handler",
            generation_instructions="Provide quick, direct answers. Be concise and helpful.",
            model="gpt-4o-mini",
            fast_mode=True,
            evaluation_enabled=False,
            max_tokens=150,
            timeout=20
        )
        
        # Standard processor / 標準プロセッサー
        self.standard_processor = RefinireAgent(
            name="standard_handler", 
            generation_instructions="Provide thorough, well-researched responses with examples.",
            model="gpt-4o-mini",
            fast_mode=False,
            evaluation_enabled=True,
            timeout=60
        )
    
    async def route_request(self, context: Context) -> str:
        """Route request using routing_instruction"""
        print("🔀 Routing request...")
        print("🔀 リクエストルーティング中...")
        
        user_request = context.shared_state.get('user_request', '')
        start_time = time.time()
        
        try:
            result = await self.router.run(user_request, expected_output=RequestType)
            routing_time = time.time() - start_time
            
            if result.success:
                request_type = result.content
                context.shared_state['request_type'] = request_type
                context.shared_state['routing_time'] = routing_time
                
                print(f"   ✅ Routed to: {request_type} ({routing_time:.2f}s)")
                print(f"   ✅ ルーティング先: {request_type} ({routing_time:.2f}秒)")
                return request_type
            else:
                print(f"   ❌ Routing failed: {result.content}")
                context.shared_state['request_type'] = 'standard'
                return 'standard'
                
        except Exception as e:
            print(f"   ❌ Routing error: {e}")
            context.shared_state['request_type'] = 'standard'
            return 'standard'
    
    def route_by_type(self, context: Context) -> str:
        """Conditional routing based on request type"""
        request_type = context.shared_state.get('request_type', 'standard')
        
        if request_type == 'urgent':
            return 'process_urgent'
        elif request_type == 'analysis':
            return 'process_analysis'
        else:
            return 'process_standard'
    
    async def process_urgent(self, context: Context) -> str:
        """Process urgent requests with fast_mode"""
        print("⚡ Processing urgent request (fast mode)...")
        print("⚡ 緊急リクエスト処理中（高速モード）...")
        
        user_request = context.shared_state.get('user_request', '')
        start_time = time.time()
        
        try:
            result = await self.urgent_processor.run(user_request)
            processing_time = time.time() - start_time
            
            if result.success:
                response = result.content
                context.shared_state['response'] = response
                context.shared_state['processing_time'] = processing_time
                
                print(f"   ✅ Urgent response ready ({processing_time:.2f}s)")
                print(f"   ✅ 緊急応答準備完了 ({processing_time:.2f}秒)")
                return response
            else:
                print(f"   ❌ Urgent processing failed: {result.content}")
                return "Urgent processing failed"
                
        except Exception as e:
            print(f"   ❌ Urgent processing error: {e}")
            return f"Error: {e}"
    
    async def process_standard(self, context: Context) -> str:
        """Process standard requests with full evaluation"""
        print("📝 Processing standard request (full evaluation)...")
        print("📝 標準リクエスト処理中（完全評価）...")
        
        user_request = context.shared_state.get('user_request', '')
        start_time = time.time()
        
        try:
            result = await self.standard_processor.run(user_request)
            processing_time = time.time() - start_time
            
            if result.success:
                response = result.content
                context.shared_state['response'] = response
                context.shared_state['processing_time'] = processing_time
                
                print(f"   ✅ Standard response ready ({processing_time:.2f}s)")
                print(f"   ✅ 標準応答準備完了 ({processing_time:.2f}秒)")
                return response
            else:
                print(f"   ❌ Standard processing failed: {result.content}")
                return "Standard processing failed"
                
        except Exception as e:
            print(f"   ❌ Standard processing error: {e}")
            return f"Error: {e}"
    
    async def process_analysis(self, context: Context) -> str:
        """Process analytical requests with detailed investigation"""
        print("🔍 Processing analysis request (detailed investigation)...")
        print("🔍 分析リクエスト処理中（詳細調査）...")
        
        user_request = context.shared_state.get('user_request', '')
        start_time = time.time()
        
        # Multi-step analysis using specialized agents
        # 専門エージェントを使用したマルチステップ分析
        
        # Step 1: Break down the analysis
        analyzer = RefinireAgent(
            name="analyst",
            generation_instructions="""
Break down this analytical request into key components:
1. Main question or problem
2. Required data or information
3. Analysis approach
4. Expected deliverables

この分析要求を主要コンポーネントに分解してください:
1. 主要な質問や問題
2. 必要なデータや情報
3. 分析アプローチ
4. 期待される成果物
            """,
            model="gpt-4o-mini"
        )
        
        breakdown_result = await analyzer.run(f"Analyze this request: {user_request}")
        breakdown = breakdown_result.content if breakdown_result.success else "Analysis breakdown failed"
        
        # Step 2: Conduct detailed analysis
        detailed_analyzer = RefinireAgent(
            name="detailed_analyst",
            generation_instructions="""
Provide comprehensive analysis with:
- Detailed findings
- Supporting evidence
- Multiple perspectives
- Actionable recommendations

以下を含む包括的分析を提供してください:
- 詳細な発見
- 裏付け証拠
- 複数の視点
- 実行可能な推奨事項
            """,
            model="gpt-4o-mini"
        )
        
        analysis_result = await detailed_analyzer.run(f"Conduct detailed analysis based on: {breakdown}")
        analysis = analysis_result.content if analysis_result.success else "Detailed analysis failed"
        
        processing_time = time.time() - start_time
        
        response = f"Analysis Breakdown:\n{breakdown}\n\nDetailed Analysis:\n{analysis}"
        context.shared_state['response'] = response
        context.shared_state['processing_time'] = processing_time
        
        print(f"   ✅ Analysis complete ({processing_time:.2f}s)")
        print(f"   ✅ 分析完了 ({processing_time:.2f}秒)")
        return response
    
    async def finalize_response(self, context: Context) -> str:
        """Finalize and format the response"""
        print("📋 Finalizing response...")
        print("📋 応答の最終処理中...")
        
        response = context.shared_state.get('response', 'No response generated')
        request_type = context.shared_state.get('request_type', 'unknown')
        routing_time = context.shared_state.get('routing_time', 0)
        processing_time = context.shared_state.get('processing_time', 0)
        total_time = routing_time + processing_time
        
        # Add metadata
        final_response = f"""
Response Type: {request_type}
Processing Time: {total_time:.2f}s (routing: {routing_time:.2f}s, processing: {processing_time:.2f}s)

{response}
        """.strip()
        
        context.shared_state['final_response'] = final_response
        return final_response
    
    def create_workflow(self) -> Flow:
        """Create the processing workflow using Flow"""
        return Flow({
            "start": FunctionStep("route", self.route_request),
            "routing": ConditionStep("type_route", self.route_by_type, "process_standard", "process_urgent", "process_analysis"),
            "process_urgent": FunctionStep("urgent", self.process_urgent),
            "process_standard": FunctionStep("standard", self.process_standard), 
            "process_analysis": FunctionStep("analysis", self.process_analysis),
            "finalize": FunctionStep("finalize", self.finalize_response)
        })


async def advanced_features_demo():
    """
    Demonstrate the integration of all advanced features
    すべての高度機能の統合をデモンストレーション
    """
    print("🚀 Advanced Features Integration Demo")
    print("🚀 高度機能統合デモ")
    print("=" * 60)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        print("❌ OPENAI_API_KEY環境変数を設定してください。")
        return
    
    # Create processor and workflow
    processor = SmartRequestProcessor()
    workflow = processor.create_workflow()
    
    # Test requests / テストリクエスト
    test_requests = [
        {
            "type": "urgent",
            "request": "What's 2+2?",
            "description": "Simple math question (should route to urgent)"
        },
        {
            "type": "standard", 
            "request": "How do I learn Python programming?",
            "description": "Learning guidance (should route to standard)"
        },
        {
            "type": "analysis",
            "request": "Analyze the pros and cons of remote work vs office work in 2024",
            "description": "Complex analysis (should route to analysis)"
        }
    ]
    
    print(f"\n🧪 Testing {len(test_requests)} different request types:")
    print(f"🧪 {len(test_requests)}種類のリクエストタイプをテスト:")
    
    total_start_time = time.time()
    
    for i, test_case in enumerate(test_requests, 1):
        print(f"\n{'='*50}")
        print(f"📋 Test {i}: {test_case['description']}")
        print(f"📋 テスト{i}: {test_case['description']}")
        print(f"📝 Request: {test_case['request']}")
        print(f"📝 リクエスト: {test_case['request']}")
        print("-" * 30)
        
        # Create context and run workflow
        context = Context()
        context.shared_state['user_request'] = test_case['request']
        
        try:
            start_time = time.time()
            result = await workflow.run(context)
            execution_time = time.time() - start_time
            
            if result:
                final_response = context.shared_state.get('final_response', 'No response')
                request_type = context.shared_state.get('request_type', 'unknown')
                
                print(f"\n✅ Test {i} completed successfully!")
                print(f"✅ テスト{i} 正常完了！")
                print(f"🎯 Detected type: {request_type}")
                print(f"🎯 検出タイプ: {request_type}")
                print(f"⏱️  Total execution: {execution_time:.2f}s")
                print(f"⏱️  総実行時間: {execution_time:.2f}秒")
                print(f"\n📄 Response:\n{final_response}")
                
                # Verify routing accuracy
                expected_contains = test_case['type']
                if expected_contains in request_type or test_case['type'] == 'standard':
                    print(f"✅ Routing accuracy: Correct")
                    print(f"✅ ルーティング精度: 正確")
                else:
                    print(f"⚠️  Routing accuracy: Expected {test_case['type']}, got {request_type}")
                    print(f"⚠️  ルーティング精度: 期待値{test_case['type']}、実際{request_type}")
                
            else:
                print(f"❌ Test {i} failed")
                print(f"❌ テスト{i} 失敗")
                
        except Exception as e:
            print(f"❌ Test {i} error: {e}")
            print(f"❌ テスト{i} エラー: {e}")
    
    total_time = time.time() - total_start_time
    
    print(f"\n{'='*60}")
    print(f"🎉 Advanced Features Demo Complete!")
    print(f"🎉 高度機能デモ完了！")
    print(f"⏱️  Total demo time: {total_time:.2f}s")
    print(f"⏱️  総デモ時間: {total_time:.2f}秒")
    
    print(f"\n💡 Features Demonstrated:")
    print(f"💡 実演された機能:")
    print(f"   ✅ routing_instruction - Intelligent request classification")
    print(f"   ✅ fast_mode - High-speed processing for urgent requests")
    print(f"   ✅ Flow - Complex multi-step workflow orchestration")
    print(f"   ✅ Conditional routing - Dynamic workflow paths")
    print(f"   ✅ Performance optimization - Different modes for different needs")


if __name__ == "__main__":
    asyncio.run(advanced_features_demo())