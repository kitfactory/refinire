#!/usr/bin/env python3
"""
Simple Code Generation - シンプルなコード生成ワークフロー
シンプルコード生成 - SimpleFlowを使用した分かりやすいコード生成

This demonstrates code generation using SimpleFlow for clean, easy-to-understand workflows.
SimpleFlowを使用した分かりやすく理解しやすいコード生成ワークフローを実演します。
"""

import asyncio
import os
from refinire import RefinireAgent
from refinire.agents.flow import SimpleFlow, simple_step, Context


async def code_generation_demo():
    """
    Simple code generation workflow using SimpleFlow
    SimpleFlowを使用したシンプルなコード生成ワークフロー
    """
    print("💻 Simple Code Generation Workflow")
    print("💻 シンプルコード生成ワークフロー")
    print("=" * 50)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        print("❌ OPENAI_API_KEY環境変数を設定してください。")
        return
    
    # Step 1: Generate code
    # ステップ1: コード生成
    async def generate_code(user_input: str, context: Context) -> Context:
        """Generate Python code based on user request"""
        agent = RefinireAgent(
            name="code_generator",
            generation_instructions="""
Generate clean, working Python code for the user's request.
Include comments and make it easy to understand.
At the end, add a complexity assessment: COMPLEXITY: [basic|intermediate|advanced]

ユーザーの要求に対してクリーンで動作するPythonコードを生成してください。
コメントを含め、理解しやすくしてください。
最後に複雑度評価を追加: COMPLEXITY: [basic|intermediate|advanced]
            """,
            model="gpt-4o-mini"
        )
        
        request = context.last_user_input
        result = await agent.run_async(f"Generate Python code for: {request}")
        
        # Store generated code
        context.shared_state["generated_code"] = result.content
        context.add_assistant_message(f"💻 Code generated successfully")
        
        return context
    
    # Step 2: Assess complexity
    # ステップ2: 複雑度評価
    async def assess_complexity(user_input: str, context: Context) -> Context:
        """Extract and assess code complexity"""
        code = context.shared_state.get("generated_code", "")
        
        # Simple complexity extraction
        complexity = "basic"
        if "COMPLEXITY: intermediate" in code.lower():
            complexity = "intermediate"
        elif "COMPLEXITY: advanced" in code.lower():
            complexity = "advanced"
        elif "class" in code.lower() or "algorithm" in code.lower():
            complexity = "advanced"
        elif "function" in code.lower() or "def " in code:
            complexity = "intermediate"
        
        context.shared_state["complexity"] = complexity
        context.add_assistant_message(f"📊 Complexity assessed: {complexity}")
        
        return context
    
    # Step 3: Provide recommendation
    # ステップ3: 推奨事項提供
    async def provide_recommendation(user_input: str, context: Context) -> Context:
        """Provide recommendations based on complexity"""
        complexity = context.shared_state.get("complexity", "basic")
        
        recommendations = {
            "basic": "✅ Ready to use! Great for beginners.",
            "intermediate": "🔍 Review recommended. Good for learning.",
            "advanced": "⚠️ Expert review needed. Complex implementation."
        }
        
        recommendation = recommendations.get(complexity, "❓ Unknown complexity")
        context.shared_state["recommendation"] = recommendation
        context.add_assistant_message(f"💡 Recommendation: {recommendation}")
        
        return context
    
    # Create simple workflow
    # シンプルなワークフローを作成
    flow = SimpleFlow([
        simple_step("generate", generate_code),
        simple_step("assess", assess_complexity),
        simple_step("recommend", provide_recommendation)
    ], name="code_generation")
    
    # Test with different requests
    # 異なる要求でテスト
    test_requests = [
        "Write a function that adds two numbers",
        "Create a class for a simple calculator",
        # "Implement a binary search tree with balancing"
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n{'='*50}")
        print(f"🔧 Test {i}: {request}")
        print(f"🔧 テスト{i}: {request}")
        print("-" * 30)
        
        try:
            # Execute workflow
            result = await flow.run(request)
            
            if not result.has_error():
                # Display results
                code = result.shared_state.get("generated_code", "")
                complexity = result.shared_state.get("complexity", "unknown")
                recommendation = result.shared_state.get("recommendation", "")
                
                print(f"✅ Generation completed!")
                print(f"✅ 生成完了!")
                print(f"📊 Complexity: {complexity}")
                print(f"💡 Recommendation: {recommendation}")
                
                # Show code preview (first few lines)
                if code:
                    lines = code.split('\n')
                    code_lines = [line for line in lines if line.strip() and not line.strip().startswith('COMPLEXITY:')][:5]
                    print(f"💻 Code preview:")
                    for line in code_lines:
                        if line.strip():
                            print(f"   {line}")
                    if len(code_lines) >= 5:
                        print(f"   ... (truncated)")
                
            else:
                print(f"❌ Generation failed: {result.error}")
                
        except Exception as e:
            print(f"💥 Error: {e}")
    
    print(f"\n{'='*50}")
    print("🎯 SimpleFlow Benefits Demonstrated:")
    print("🎯 SimpleFlowの利点を実演:")
    print("   • Clean, readable workflow definition")
    print("   • Sequential step execution")
    print("   • Automatic error handling")
    print("   • Simple result management")
    print("   • Easy to understand and modify")


if __name__ == "__main__":
    asyncio.run(code_generation_demo())