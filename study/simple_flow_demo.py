#!/usr/bin/env python3
"""
Simple Flow Demo - 最もシンプルなワークフロー実演
シンプルフローデモ - SimpleFlowクラスを使用した直感的なワークフロー

This demonstrates the simplest way to create and execute workflows.
これは最もシンプルなワークフロー作成・実行方法を実演します。
"""

import asyncio
import os
from refinire import RefinireAgent
from refinire.agents.flow import SimpleFlow, simple_step, Context


async def simple_flow_demo():
    """
    Demonstrate SimpleFlow with a 3-step content creation workflow
    3ステップのコンテンツ作成ワークフローでSimpleFlowをデモンストレーション
    """
    print("🌊 Simple Flow Demo - Easy Workflow Creation")
    print("🌊 シンプルフローデモ - 簡単ワークフロー作成")
    print("=" * 50)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        print("❌ OPENAI_API_KEY環境変数を設定してください。")
        return
    
    # Define steps using simple functions
    # シンプルな関数でステップを定義
    
    async def brainstorm_ideas(user_input: str, context: Context) -> Context:
        """Step 1: Brainstorm content ideas"""
        agent = RefinireAgent(
            name="brainstormer",
            generation_instructions="Generate 3 creative ideas for the given topic. Be brief and innovative.",
            model="gpt-4o-mini"
        )
        
        topic = context.last_user_input or "technology"
        result = await agent.run_async(f"Brainstorm ideas for: {topic}")
        
        # Store result in shared state
        context.shared_state["ideas"] = result.content
        context.add_assistant_message(f"💡 Ideas generated: {result.content}")
        
        return context
    
    async def create_outline(user_input: str, context: Context) -> Context:
        """Step 2: Create content outline"""
        agent = RefinireAgent(
            name="outliner", 
            generation_instructions="Create a structured outline based on the ideas. Use clear headings and bullet points.",
            model="gpt-4o-mini"
        )
        
        ideas = context.shared_state.get("ideas", "No ideas available")
        result = await agent.run_async(f"Create an outline for these ideas: {ideas}")
        
        # Store result
        context.shared_state["outline"] = result.content
        context.add_assistant_message(f"📝 Outline created: {result.content}")
        
        return context
    
    async def write_summary(user_input: str, context: Context) -> Context:
        """Step 3: Write final summary"""
        agent = RefinireAgent(
            name="writer",
            generation_instructions="Write a concise, engaging summary based on the outline. Keep it under 200 words.",
            model="gpt-4o-mini"
        )
        
        outline = context.shared_state.get("outline", "No outline available")
        result = await agent.run_async(f"Write a summary based on this outline: {outline}")
        
        # Store final result
        context.shared_state["final_content"] = result.content
        context.add_assistant_message(f"✨ Final content: {result.content}")
        
        return context
    
    # Create SimpleFlow with 3 steps
    # 3ステップでSimpleFlowを作成
    flow = SimpleFlow([
        simple_step("brainstorm", brainstorm_ideas),
        simple_step("outline", create_outline), 
        simple_step("summarize", write_summary)
    ], name="content_creation_flow")
    
    # Execute the flow
    # フローを実行
    print("\n🚀 Starting content creation workflow...")
    print("🚀 コンテンツ作成ワークフロー開始...")
    
    try:
        # Run with user input
        # ユーザー入力で実行
        topic = "artificial intelligence"
        print(f"📝 Topic: {topic}")
        print(f"📝 トピック: {topic}")
        
        result_context = await flow.run(topic)
        
        # Display results
        # 結果を表示
        if not result_context.has_error():
            print(f"\n{'='*50}")
            print("🎉 Workflow completed successfully!")
            print("🎉 ワークフロー正常完了！")
            
            print(f"\n📊 Results:")
            print(f"📊 結果:")
            
            # Show final content
            final_content = result_context.shared_state.get("final_content")
            if final_content:
                print(f"\n✨ Final Content:")
                print(f"✨ 最終コンテンツ:")
                print(f"   {final_content}")
            
            # Show execution summary
            print(f"\n📈 Execution Summary:")
            print(f"📈 実行サマリー:")
            print(f"   • Steps executed: {len(flow.steps)}")
            print(f"   • Messages: {len(result_context.messages)}")
            print(f"   • Shared data: {len(result_context.shared_state)} items")
            
        else:
            print(f"\n❌ Workflow failed: {result_context.error}")
            print(f"❌ ワークフロー失敗: {result_context.error}")
            
    except Exception as e:
        print(f"\n💥 Error during workflow execution: {e}")
        print(f"💥 ワークフロー実行中エラー: {e}")
    
    print(f"\n{'='*50}")
    print("🎯 What was demonstrated:")
    print("🎯 実演された内容:")
    print("   • SimpleFlow for easy workflow creation")
    print("   • Sequential step execution")
    print("   • Shared state between steps")
    print("   • Error handling and result management")
    print("   • Clean, readable workflow definition")


async def builder_pattern_demo():
    """
    Demonstrate SimpleFlow builder pattern
    SimpleFlowビルダーパターンのデモンストレーション
    """
    print("\n🔧 Builder Pattern Demo")
    print("🔧 ビルダーパターンデモ")
    print("-" * 30)
    
    # Create flow using builder pattern
    # ビルダーパターンでフローを作成
    async def step1(user_input: str, context: Context) -> Context:
        context.shared_state["step1_done"] = True
        print("  ✅ Step 1 completed")
        return context
    
    async def step2(user_input: str, context: Context) -> Context:
        context.shared_state["step2_done"] = True
        print("  ✅ Step 2 completed")
        return context
    
    # Build flow step by step
    # ステップバイステップでフローを構築
    flow = SimpleFlow([], name="builder_demo") \
        .add_step(simple_step("first", step1)) \
        .add_step(simple_step("second", step2))
    
    # Execute
    # 実行
    result = await flow.run("test input")
    
    print(f"🎉 Builder pattern demo completed!")
    print(f"   Step 1 done: {result.shared_state.get('step1_done')}")
    print(f"   Step 2 done: {result.shared_state.get('step2_done')}")


if __name__ == "__main__":
    async def main():
        await simple_flow_demo()
        await builder_pattern_demo()
    
    asyncio.run(main())