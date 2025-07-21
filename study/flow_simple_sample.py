#!/usr/bin/env python3
"""
Flow Simple Sample - 簡単なFlowワークフロー機能サンプル
シンプルフローサンプル - 基本的なワークフロー機能の実演

This demonstrates a simple flow with just 2 steps.
2ステップだけのシンプルなフローを実演します。
"""

import asyncio
import os
from refinire.agents.flow import Flow, FunctionStep, Context
from refinire import RefinireAgent


async def flow_simple_demo():
    """
    Demonstrate simple Flow functionality with just 2 steps
    2ステップだけのシンプルなFlow機能をデモンストレーション
    """
    print("🌊 Simple Flow Sample - Two-Step Workflow")
    print("🌊 シンプルフローサンプル - 2ステップワークフロー")
    print("=" * 50)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        print("❌ OPENAI_API_KEY環境変数を設定してください。")
        return
    
    # Step 1: Generate a summary / ステップ1: 要約生成
    async def generate_summary(user_input: str, context: Context) -> Context:
        """Generate a summary of the topic"""
        print("📝 Step 1: Generating summary...")
        print("📝 ステップ1: 要約生成中...")
        
        summarizer = RefinireAgent(
            name="summarizer",
            generation_instructions="""
You are a summary specialist. Create a brief, clear summary about the given topic.
Keep it concise (2-3 sentences) and informative.

あなたは要約専門家です。与えられたトピックについて簡潔で明確な要約を作成してください。
簡潔（2-3文）で情報豊富にしてください。
            """,
            model="gpt-4o-mini"
        )
        
        topic = context.shared_state.get('topic', 'Technology')
        result = await summarizer.run_async(f"Create a summary about: {topic}")
        
        if result.success:
            summary = result.content
            context.shared_state['summary'] = summary
            print(f"   ✅ Summary generated: {len(summary)} characters")
        else:
            context.shared_state['summary'] = "Summary generation failed"
            print(f"   ❌ Summary failed: {result.content}")
        
        return context
    
    # Step 2: Create questions / ステップ2: 質問作成
    async def create_questions(user_input: str, context: Context) -> Context:
        """Create questions based on the summary"""
        print("❓ Step 2: Creating questions...")
        print("❓ ステップ2: 質問作成中...")
        
        questioner = RefinireAgent(
            name="questioner",
            generation_instructions="""
You are a question creator. Based on the summary provided, create 3 interesting questions
that someone might want to explore further about this topic.

あなたは質問作成者です。提供された要約に基づいて、このトピックについて
さらに探求したくなるような興味深い質問を3つ作成してください。
            """,
            model="gpt-4o-mini"
        )
        
        summary = context.shared_state.get('summary', '')
        topic = context.shared_state.get('topic', '')
        result = await questioner.run_async(f"Topic: {topic}\nSummary: {summary}\n\nCreate 3 questions:")
        
        if result.success:
            questions = result.content
            context.shared_state['questions'] = questions
            print(f"   ✅ Questions created: {len(questions)} characters")
        else:
            context.shared_state['questions'] = "Question creation failed"
            print(f"   ❌ Questions failed: {result.content}")
        
        return context
    
    # Test with different topics / 異なるトピックでテスト
    test_topics = [
        "Artificial Intelligence",
        "Climate Change", 
        "Space Exploration",
        "Renewable Energy"
    ]
    
    print("\n🚀 Starting simple workflows...")
    print("🚀 シンプルワークフロー開始...")
    
    for i, topic in enumerate(test_topics, 1):
        print(f"\n{'='*50}")
        print(f"📋 Test {i}: {topic}")
        print(f"📋 テスト{i}: {topic}")
        print("-" * 30)
        
        # Create workflow with context for this specific topic
        # このトピック専用のコンテキストでワークフローを作成
        context = Context()
        context.shared_state['topic'] = topic
        
        # Create simple 2-step workflow / シンプルな2ステップワークフローを作成
        steps = {
            "summarize": FunctionStep("summarize", generate_summary, next_step="questions"),
            "questions": FunctionStep("questions", create_questions)  # Last step, no next_step
        }
        
        # Create Flow with context and run
        # コンテキスト付きでFlowを作成して実行
        workflow = Flow(
            start="summarize", 
            steps=steps, 
            context=context,
            name=f"topic_workflow_{i}"
        )
        
        try:
            start_time = asyncio.get_event_loop().time()
            result = await workflow.run()
            execution_time = asyncio.get_event_loop().time() - start_time
            
            if result:
                print(f"\n✅ Workflow {i} completed successfully!")
                print(f"✅ ワークフロー{i}正常完了！")
                print(f"⏱️  Execution time: {execution_time:.2f} seconds")
                print(f"⏱️  実行時間: {execution_time:.2f} 秒")
                
                # Show results / 結果を表示
                summary = result.shared_state.get('summary', 'No summary generated')
                questions = result.shared_state.get('questions', 'No questions generated')
                
                print(f"\n📊 Results for '{topic}':")
                print(f"📊 '{topic}' の結果:")
                print(f"   📝 Summary: {summary}")
                print(f"   ❓ Questions: {questions[:300]}{'...' if len(questions) > 300 else ''}")
                
            else:
                print(f"❌ Workflow {i} failed")
                print(f"❌ ワークフロー{i}失敗")
                
        except Exception as e:
            print(f"❌ Workflow {i} error: {e}")
            print(f"❌ ワークフロー{i}エラー: {e}")
    
    print(f"\n{'='*50}")
    print("🎉 Simple Flow demo completed!")
    print("🎉 シンプルフローデモ完了！")
    
    print(f"\n💡 Flow Features Demonstrated:")
    print(f"💡 実演されたフロー機能:")
    print(f"   ✅ Simple 2-step sequential execution")
    print(f"   ✅ Context state sharing between steps")
    print(f"   ✅ Error handling in workflow steps")
    print(f"   ✅ Multiple workflow instances")
    print(f"   ✅ Performance measurement")


if __name__ == "__main__":
    asyncio.run(flow_simple_demo())