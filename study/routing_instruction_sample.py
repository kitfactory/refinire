#!/usr/bin/env python3
"""
Routing Instruction Sample - RefinireAgentでのルーティング機能サンプル
ルーティング指示サンプル - 複数の選択肢から適切なルートを選択する機能

This demonstrates how to use routing_instruction to route user queries to different handlers.
ユーザークエリを異なるハンドラーにルーティングするルーティング指示の使用方法を実演します。
"""

import asyncio
import os
from typing import Literal
from refinire import RefinireAgent


# Define routing choices / ルーティング選択肢を定義
RouteChoice = Literal["greeting", "calculation", "translation", "general"]


async def routing_instruction_demo():
    """
    Demonstrate routing_instruction functionality
    routing_instruction機能のデモンストレーション
    """
    print("🔀 Routing Instruction Sample")
    print("ルーティング指示サンプル")
    print("=" * 50)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        print("❌ OPENAI_API_KEY環境変数を設定してください。")
        return
    
    # Create router agent / ルーターエージェントを作成
    router_agent = RefinireAgent(
        name="smart_router",
        generation_instructions="""
You are a smart router that categorizes user requests.
Analyze the user's request and determine the most appropriate category.

Categories:
- greeting: For hello, hi, how are you, etc.
- calculation: For math problems, calculations, numbers
- translation: For translate requests between languages
- general: For any other general questions

あなたはユーザーリクエストを分類するスマートルーターです。
ユーザーのリクエストを分析し、最も適切なカテゴリを決定してください。
        """,
        model="gpt-4o-mini",
        routing_instruction="Choose the most appropriate category for this request",
        timeout=60
    )
    
    # Test queries / テストクエリ
    test_queries = [
        "Hello, how are you today?",
        # "What is 15 + 27?",
        # "Please translate 'good morning' to Japanese",
        # "What is the capital of France?",
        # "こんにちは、元気ですか？",
        # "Calculate the square root of 144",
        # "Translate this to English: ありがとうございます"
    ]
    
    print("\n🧪 Testing routing for different queries:")
    print("🧪 異なるクエリのルーティングをテスト:")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: {query}")
        try:
            # Route the query / クエリをルーティング
            result = await router_agent.run_async(query)
            print(result)

            if result.success:
                route = result.content
                print(f"   ✅ Routed to: {route}")
                
                # Handle each route / 各ルートを処理
                await handle_routed_request(route, query)
            else:
                print(f"   ❌ Routing failed: {result.content}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n🎯 Routing instruction demo completed!")
    print("🎯 ルーティング指示デモ完了！")


async def handle_routed_request(route: str, original_query: str):
    """
    Handle the request based on the route
    ルートに基づいてリクエストを処理
    """
    try:
        if route == "greeting":
            agent = RefinireAgent(
                name="greeter",
                generation_instructions="You are a friendly greeter. Respond warmly to greetings.",
                model="gpt-4o-mini"
            )
        elif route == "calculation":
            agent = RefinireAgent(
                name="calculator",
                generation_instructions="You are a math expert. Solve calculations accurately and show your work.",
                model="gpt-4o-mini"
            )
        elif route == "translation":
            agent = RefinireAgent(
                name="translator",
                generation_instructions="You are a professional translator. Provide accurate translations.",
                model="gpt-4o-mini"
            )
        else:  # general
            agent = RefinireAgent(
                name="assistant",
                generation_instructions="You are a helpful general assistant. Provide informative answers.",
                model="gpt-4o-mini"
            )
        
        # Process the query with the specialized agent
        # 専門エージェントでクエリを処理
        result = await agent.run_async(original_query)
        
        if result.success:
            print(f"   💬 Response: {result.content[:100]}...")
        else:
            print(f"   💬 Handler failed: {result.content}")
            
    except Exception as e:
        print(f"   💬 Handler error: {e}")


if __name__ == "__main__":
    asyncio.run(routing_instruction_demo())