#!/usr/bin/env python3
"""
Flow Simple Clean Sample - 最もシンプルなFlowワークフロー機能サンプル
フロークリーンサンプル - Flowクラスの最適な使用方法のデモンストレーション

This demonstrates the cleanest way to use Flow class with sequential mode.
Flowクラスをシーケンシャルモードで最もクリーンに使用する方法を実演します。
"""

import asyncio
import os
from refinire.agents.flow import Flow, FunctionStep, Context
from refinire import RefinireAgent


async def flow_clean_demo():
    """
    Demonstrate the cleanest way to use Flow with 2 steps
    2ステップでFlowを最もクリーンに使用する方法をデモンストレーション
    """
    print("🌊 Flow Clean Sample - Optimal Flow Usage")
    print("🌊 フロークリーンサンプル - 最適なFlow使用法")
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
Create a brief, clear summary about the given topic in 2-3 sentences.
Make it informative and engaging.

与えられたトピックについて2-3文で簡潔で明確な要約を作成してください。
情報豊富で魅力的にしてください。
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
Based on the summary provided, create 3 interesting questions that would help
someone explore this topic further. Make them thought-provoking.

提供された要約に基づいて、このトピックをより深く探求するのに役立つ
3つの興味深い質問を作成してください。思考を促すような質問にしてください。
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
        "Space Exploration"
    ]
    
    print("\n🚀 Starting clean workflows...")
    print("🚀 クリーンワークフロー開始...")
    
    for i, topic in enumerate(test_topics, 1):
        print(f"\n{'='*50}")
        print(f"📋 Test {i}: {topic}")
        print(f"📋 テスト{i}: {topic}")
        print("-" * 30)
        
        # Method 1: Using sequential mode with List[Step] (cleanest)
        # 方法1: List[Step]でシーケンシャルモードを使用（最もクリーン）
        step_list = [
            FunctionStep("summarize", generate_summary),
            FunctionStep("questions", create_questions)
        ]
        
        # Create context with topic
        # トピック付きでコンテキストを作成
        context = Context()
        context.shared_state['topic'] = topic
        
        # Create Flow using sequential mode
        # シーケンシャルモードでFlowを作成
        workflow = Flow(
            steps=step_list,
            context=context,
            name=f"clean_workflow_{i}"
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
                print(f"   📝 Summary: {summary[:200]}{'...' if len(summary) > 200 else ''}")
                print(f"   ❓ Questions preview: {questions[:200]}{'...' if len(questions) > 200 else ''}")
                
            else:
                print(f"❌ Workflow {i} failed")
                print(f"❌ ワークフロー{i}失敗")
                
        except Exception as e:
            print(f"❌ Workflow {i} error: {e}")
            print(f"❌ ワークフロー{i}エラー: {e}")
    
    print(f"\n{'='*50}")
    print("🎉 Clean Flow demo completed!")
    print("🎉 クリーンフローデモ完了！")
    
    print(f"\n💡 Optimal Flow Usage Demonstrated:")
    print(f"💡 最適なFlow使用法の実演:")
    print(f"   ✅ Sequential mode with List[Step] (cleanest syntax)")
    print(f"   ✅ Context initialization with Flow constructor")
    print(f"   ✅ Proper flow naming for identification")
    print(f"   ✅ Clean separation of concerns")
    print(f"   ✅ Minimal boilerplate code")


if __name__ == "__main__":
    asyncio.run(flow_clean_demo())