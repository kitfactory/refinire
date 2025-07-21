#!/usr/bin/env python3
"""
Flow Routing Sample - FlowクラスとRouting Instructionを組み合わせたルーティングサンプル
フロールーティングサンプル - FlowとRefinireAgentのrouting_instructionを使用したシンプルなルーティング

This demonstrates how to combine Flow and routing_instruction for smart request routing.
FlowとrRouting_instructionを組み合わせたスマートリクエストルーティングを実演します。
"""

import asyncio
import os
from refinire.agents.flow import Flow, FunctionStep, ConditionStep, Context
from refinire import RefinireAgent


async def flow_routing_demo():
    """
    Demonstrate Flow routing with routing_instruction
    routing_instructionを使用したFlowルーティングのデモンストレーション
    """
    print("🔀🌊 Flow Routing Sample - Smart Request Routing")
    print("🔀🌊 フロールーティングサンプル - スマートリクエストルーティング")
    print("=" * 60)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        print("❌ OPENAI_API_KEY環境変数を設定してください。")
        return
    
    # Step 1: Router step using routing_instruction / ルーターステップ（routing_instruction使用）
    async def route_request(user_input: str, context: Context) -> Context:
        """Route user request to appropriate handler"""
        print("🔀 Step 1: Routing request...")
        print("🔀 ステップ1: リクエストルーティング中...")
        
        router_agent = RefinireAgent(
            name="smart_router",
            generation_instructions="""
You are a smart router. Analyze the user's request and choose the best category.

Categories:
- greeting: For hello, hi, how are you, etc.
- math: For math problems, calculations, numbers  
- creative: For writing, stories, creative content
- general: For any other questions

あなたはスマートルーターです。ユーザーのリクエストを分析し、最適なカテゴリを選択してください。
            """,
            model="gpt-4o-mini",
            routing_instruction="Choose exactly one category: greeting, math, creative, or general",
            timeout=30
        )
        
        query = context.shared_state.get('user_query', 'Hello')
        result = await router_agent.run_async(query)
        
        if result.success:
            route_response = result.content.strip().lower()
            # Extract just the category name from responses like "Category: greeting"
            if 'greeting' in route_response:
                route = 'greeting'
            elif 'math' in route_response:
                route = 'math'
            elif 'creative' in route_response:
                route = 'creative'
            else:
                route = 'general'
            
            context.shared_state['route'] = route
            print(f"   ✅ Routed to: {route}")
        else:
            context.shared_state['route'] = 'general'
            print(f"   ❌ Routing failed, defaulting to general: {result.content}")
        
        return context
    
    # Step 2: Greeting handler / あいさつハンドラー
    async def handle_greeting(user_input: str, context: Context) -> Context:
        """Handle greeting requests"""
        print("👋 Step 2a: Handling greeting...")
        print("👋 ステップ2a: あいさつ処理中...")
        
        greeter = RefinireAgent(
            name="greeter",
            generation_instructions="You are a friendly assistant. Respond warmly to greetings in 1-2 sentences.",
            model="gpt-4o-mini"
        )
        
        query = context.shared_state.get('user_query', '')
        result = await greeter.run_async(query)
        
        if result.success:
            context.shared_state['response'] = result.content
            print(f"   ✅ Greeting response generated: {len(result.content)} characters")
        else:
            context.shared_state['response'] = "Hello! How can I help you today?"
            print(f"   ❌ Greeting failed, using default response")
        
        return context
    
    # Step 3: Math handler / 数学ハンドラー
    async def handle_math(user_input: str, context: Context) -> Context:
        """Handle math calculations"""
        print("🔢 Step 2b: Handling math...")
        print("🔢 ステップ2b: 数学処理中...")
        
        calculator = RefinireAgent(
            name="calculator",
            generation_instructions="You are a math expert. Solve the problem step by step and show your work clearly.",
            model="gpt-4o-mini"
        )
        
        query = context.shared_state.get('user_query', '')
        result = await calculator.run_async(query)
        
        if result.success:
            context.shared_state['response'] = result.content
            print(f"   ✅ Math solution generated: {len(result.content)} characters")
        else:
            context.shared_state['response'] = "I couldn't solve this math problem."
            print(f"   ❌ Math calculation failed")
        
        return context
    
    # Step 4: Creative handler / クリエイティブハンドラー
    async def handle_creative(user_input: str, context: Context) -> Context:
        """Handle creative writing requests"""
        print("✨ Step 2c: Handling creative request...")
        print("✨ ステップ2c: クリエイティブ処理中...")
        
        writer = RefinireAgent(
            name="creative_writer",
            generation_instructions="You are a creative writer. Create engaging, imaginative content based on the request.",
            model="gpt-4o-mini"
        )
        
        query = context.shared_state.get('user_query', '')
        result = await writer.run_async(query)
        
        if result.success:
            context.shared_state['response'] = result.content
            print(f"   ✅ Creative content generated: {len(result.content)} characters")
        else:
            context.shared_state['response'] = "I couldn't create content for this request."
            print(f"   ❌ Creative writing failed")
        
        return context
    
    # Step 5: General handler / 一般ハンドラー
    async def handle_general(user_input: str, context: Context) -> Context:
        """Handle general questions"""
        print("💬 Step 2d: Handling general question...")
        print("💬 ステップ2d: 一般質問処理中...")
        
        assistant = RefinireAgent(
            name="general_assistant",
            generation_instructions="You are a helpful assistant. Provide clear, informative answers to questions.",
            model="gpt-4o-mini"
        )
        
        query = context.shared_state.get('user_query', '')
        result = await assistant.run_async(query)
        
        if result.success:
            context.shared_state['response'] = result.content
            print(f"   ✅ General response generated: {len(result.content)} characters")
        else:
            context.shared_state['response'] = "I couldn't answer this question."
            print(f"   ❌ General response failed")
        
        return context
    
    # Condition functions for routing / ルーティング用条件関数
    def is_greeting(context: Context) -> bool:
        return context.shared_state.get('route') == 'greeting'
    
    def is_math(context: Context) -> bool:
        return context.shared_state.get('route') == 'math'
    
    def is_creative(context: Context) -> bool:
        return context.shared_state.get('route') == 'creative'
    
    # Create flow with conditional routing / 条件分岐ルーティングでフローを作成
    steps = {
        "router": FunctionStep("router", route_request, next_step="check_greeting"),
        "check_greeting": ConditionStep("check_greeting", is_greeting, "greeting_handler", "check_math"),
        "check_math": ConditionStep("check_math", is_math, "math_handler", "check_creative"),
        "check_creative": ConditionStep("check_creative", is_creative, "creative_handler", "general_handler"),
        "greeting_handler": FunctionStep("greeting_handler", handle_greeting),
        "math_handler": FunctionStep("math_handler", handle_math),
        "creative_handler": FunctionStep("creative_handler", handle_creative),
        "general_handler": FunctionStep("general_handler", handle_general)
    }
    
    workflow = Flow(start="router", steps=steps)
    
    # Test queries / テストクエリ
    test_queries = [
        "Hello! How are you doing today?",
        "What is 25 + 17?",
        "Write a short poem about cats",
        "What is the capital of Japan?",
        "Calculate the square root of 144",
        "Tell me a story about a robot"
    ]
    
    print("\n🚀 Starting flow routing demonstrations...")
    print("🚀 フロールーティングデモ開始...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"📋 Test {i}: {query}")
        print(f"📋 テスト{i}: {query}")
        print("-" * 40)
        
        context = Context()
        context.shared_state['user_query'] = query
        
        try:
            start_time = asyncio.get_event_loop().time()
            result = await workflow.run()
            execution_time = asyncio.get_event_loop().time() - start_time
            
            if result:
                print(f"\n✅ Flow {i} completed successfully!")
                print(f"✅ フロー{i}正常完了！")
                print(f"⏱️  Execution time: {execution_time:.2f} seconds")
                print(f"⏱️  実行時間: {execution_time:.2f} 秒")
                
                # Show results / 結果を表示
                route = result.shared_state.get('route', 'unknown')
                response = result.shared_state.get('response', 'No response generated')
                
                print(f"\n📊 Results for: '{query[:50]}{'...' if len(query) > 50 else ''}'")
                print(f"📊 結果: '{query[:50]}{'...' if len(query) > 50 else ''}'")
                print(f"   🔀 Route: {route}")
                print(f"   📝 Response length: {len(response)} characters")
                print(f"   💬 Response preview: {response[:200]}{'...' if len(response) > 200 else ''}")
                
            else:
                print(f"❌ Flow {i} failed")
                print(f"❌ フロー{i}失敗")
                
        except Exception as e:
            print(f"❌ Flow {i} error: {e}")
            print(f"❌ フロー{i}エラー: {e}")
    
    print(f"\n{'='*60}")
    print("🎉 Flow routing demo completed!")
    print("🎉 フロールーティングデモ完了！")
    
    print(f"\n💡 Features Demonstrated:")
    print(f"💡 実演された機能:")
    print(f"   ✅ RefinireAgent routing_instruction for smart categorization")
    print(f"   ✅ Flow conditional routing with ConditionStep")
    print(f"   ✅ Multiple specialized handlers")
    print(f"   ✅ Context state sharing between steps")
    print(f"   ✅ Error handling and fallbacks")


if __name__ == "__main__":
    asyncio.run(flow_routing_demo())