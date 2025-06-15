#!/usr/bin/env python3
"""
GenAgent Example - Using AgentPipeline as Flow Steps
GenAgentの例 - AgentPipelineをFlowステップとして使用

This example demonstrates how to use GenAgent class to integrate
AgentPipeline functionality directly into Flow workflows.
この例は、GenAgentクラスを使用してAgentPipeline機能をFlowワークフローに
直接統合する方法を示しています。
"""

import asyncio
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import (
    GenAgent, 
    create_simple_gen_agent, 
    create_evaluated_gen_agent,
    Flow, 
    Context, 
    UserInputStep,
    DebugStep
)


async def basic_gen_agent_example():
    """
    Basic example of using GenAgent
    GenAgentの基本的な使用例
    """
    print("🚀 Basic GenAgent Example")
    print("=" * 50)
    
    # Create a simple GenAgent
    # シンプルなGenAgentを作成
    summarizer = GenAgent(
        name="summarizer",
        generation_instructions="You are a helpful assistant that summarizes text in a concise way.",
        model="gpt-4o-mini",
        threshold=80,
        retries=2,
        next_step="debug"
    )
    
    # Create a debug step
    # デバッグステップを作成
    debug = DebugStep(
        name="debug",
        message="Summarization completed!"
    )
    
    # Create flow
    # フローを作成
    flow = Flow({
        "start": summarizer,
        "debug": debug
    })
    
    # Run the flow
    # フローを実行
    ctx = Context()
    user_input = """
    Artificial Intelligence (AI) is a rapidly evolving field that encompasses machine learning, 
    natural language processing, computer vision, and robotics. Recent advances in deep learning 
    have led to breakthrough applications in areas such as autonomous vehicles, medical diagnosis, 
    and natural language understanding. However, challenges remain in areas such as AI safety, 
    explainability, and ethical considerations.
    """
    
    print(f"Input text: {user_input[:100]}...")
    print("\nRunning GenAgent...")
    
    final_ctx = await flow.run_async(user_input, ctx, start_step="start")
    
    # Display results
    # 結果を表示
    print(f"\nResult: {final_ctx.shared_state.get('summarizer_result', 'No result')}")
    print(f"Step count: {final_ctx.step_count}")


async def evaluated_gen_agent_example():
    """
    Example of using GenAgent with evaluation
    評価付きGenAgentの使用例
    """
    print("\n🎯 Evaluated GenAgent Example")
    print("=" * 50)
    
    # Create a GenAgent with evaluation
    # 評価付きGenAgentを作成
    creative_writer = create_evaluated_gen_agent(
        name="creative_writer",
        generation_instructions="""
        You are a creative writer. Write a short, engaging story based on the user's prompt.
        The story should be original, well-structured, and emotionally engaging.
        """,
        evaluation_instructions="""
        Evaluate the creative story on the following criteria:
        1. Originality (is it creative and unique?)
        2. Structure (does it have a clear beginning, middle, end?)
        3. Emotional engagement (does it evoke emotions?)
        
        Rate the overall quality from 0-100.
        """,
        model="gpt-4o-mini",
        threshold=75,
        retries=3,
        next_step="end"
    )
    
    # Create flow
    # フローを作成
    flow = Flow({
        "writer": creative_writer
    })
    
    # Run the flow
    # フローを実行
    ctx = Context()
    user_input = "Write a story about a robot who discovers emotions for the first time."
    
    print(f"Story prompt: {user_input}")
    print("\nRunning evaluated GenAgent...")
    
    final_ctx = await flow.run_async(user_input, ctx, start_step="writer")
    
    # Display results
    # 結果を表示
    result = final_ctx.shared_state.get('creative_writer_result')
    if result:
        print(f"\nGenerated story:\n{result}")
    else:
        print("\nStory generation failed to meet quality threshold after retries.")
    
    print(f"Step count: {final_ctx.step_count}")


async def multi_gen_agent_workflow():
    """
    Example of a workflow with multiple GenAgents
    複数のGenAgentを含むワークフローの例
    """
    print("\n🔄 Multi-GenAgent Workflow Example")
    print("=" * 50)
    
    # Create multiple GenAgents for different tasks
    # 異なるタスク用に複数のGenAgentを作成
    
    # 1. Content analyzer
    # 1. コンテンツアナライザー
    analyzer = create_simple_gen_agent(
        name="analyzer",
        instructions="""
        Analyze the given text and identify:
        1. Main topic
        2. Key themes
        3. Target audience
        4. Writing style
        
        Provide a structured analysis.
        """,
        model="gpt-4o-mini",
        next_step="improver"
    )
    
    # 2. Content improver
    # 2. コンテンツ改善者
    improver = GenAgent(
        name="improver",
        generation_instructions="""
        Based on the analysis provided, suggest specific improvements for the original text.
        Focus on clarity, engagement, and target audience alignment.
        Provide 3-5 concrete suggestions.
        """,
        model="gpt-4o-mini",
        next_step="formatter"
    )
    
    # 3. Output formatter
    # 3. 出力フォーマッター
    formatter = create_simple_gen_agent(
        name="formatter",
        instructions="""
        Create a final report with:
        1. Original text summary
        2. Analysis results
        3. Improvement suggestions
        4. Next steps
        
        Format as a professional report.
        """,
        model="gpt-4o-mini"
    )
    
    # Create workflow
    # ワークフローを作成
    flow = Flow({
        "analyze": analyzer,
        "improve": improver,
        "format": formatter
    })
    
    # Run the workflow
    # ワークフローを実行
    ctx = Context()
    user_input = """
    Our company sells software products to businesses. We help them manage their operations 
    better with our tools. Many customers like our products because they are easy to use and 
    work well. We want to grow our business and reach more customers in the future.
    """
    
    print(f"Input text: {user_input}")
    print("\nRunning multi-GenAgent workflow...")
    
    final_ctx = await flow.run_async(user_input, ctx, start_step="analyze")
    
    # Display results from each step
    # 各ステップの結果を表示
    print("\n" + "="*60)
    print("WORKFLOW RESULTS")
    print("="*60)
    
    for step_name in ["analyzer", "improver", "formatter"]:
        result = final_ctx.shared_state.get(f"{step_name}_result")
        if result:
            print(f"\n📋 {step_name.upper()} OUTPUT:")
            print("-" * 40)
            print(result)
    
    print(f"\nTotal steps executed: {final_ctx.step_count}")


async def interactive_gen_agent_example():
    """
    Example of interactive workflow with GenAgent and user input
    GenAgentとユーザー入力を含むインタラクティブワークフローの例
    """
    print("\n🗣️ Interactive GenAgent Example")
    print("=" * 50)
    
    # Create an interactive story builder
    # インタラクティブストーリービルダーを作成
    story_builder = GenAgent(
        name="story_builder",
        generation_instructions="""
        Continue the story based on the user's input. Keep the narrative engaging 
        and ask the user what should happen next. End with a question or choice 
        for the user to make.
        """,
        model="gpt-4o-mini",
        next_step="user_input"
    )
    
    # User input step
    # ユーザー入力ステップ
    user_choice = UserInputStep(
        name="user_input",
        prompt="What happens next in the story? (Type 'end' to finish)",
        next_step="continue_check"
    )
    
    # Check if user wants to continue
    # ユーザーが続行したいかチェック
    def should_continue(ctx: Context) -> bool:
        last_input = ctx.last_user_input or ""
        return last_input.lower() != "end"
    
    from refinire import ConditionStep
    continue_check = ConditionStep(
        name="continue_check",
        condition=should_continue,
        if_true="story_builder",  # Continue the story
        if_false="end"  # End the workflow
    )
    
    # Create flow
    # フローを作成
    flow = Flow({
        "start": story_builder,
        "user_input": user_choice,
        "continue_check": continue_check
    })
    
    # Run interactive session
    # インタラクティブセッションを実行
    ctx = Context()
    initial_input = "Start a mystery story about a detective who finds a strange letter."
    
    print(f"Starting story: {initial_input}")
    print("\nRunning interactive GenAgent workflow...")
    print("(This is a demo - user inputs are simulated)")
    
    # Simulate user interactions
    # ユーザーインタラクションをシミュレート
    simulated_inputs = [
        "The detective decides to investigate the address mentioned in the letter.",
        "She discovers the house is abandoned but finds fresh footprints.",
        "end"
    ]
    
    current_ctx = ctx
    input_text = initial_input
    
    for i, simulated_input in enumerate(simulated_inputs + [None]):
        print(f"\n--- Turn {i+1} ---")
        
        # Run one iteration
        # 1回のイテレーションを実行
        current_ctx = await flow.run_async(input_text, current_ctx, start_step="start")
        
        # Show story continuation
        # ストーリーの続きを表示
        story_result = current_ctx.shared_state.get("story_builder_result")
        if story_result:
            print(f"Story: {story_result}")
        
        # Check if we need user input
        # ユーザー入力が必要かチェック
        if current_ctx.waiting_for_user_input and simulated_input:
            print(f"User input: {simulated_input}")
            input_text = simulated_input
            current_ctx.provide_user_input(simulated_input)
        else:
            break
    
    print("\nInteractive story completed!")
    print(f"Total interactions: {current_ctx.step_count}")


async def main():
    """
    Main function to run all examples
    すべての例を実行するメイン関数
    """
    print("🎭 GenAgent Examples")
    print("=" * 60)
    print("Demonstrating AgentPipeline integration with Flow workflows")
    print("AgentPipelineとFlowワークフローの統合をデモンストレーション")
    print("=" * 60)
    
    try:
        # Run all examples
        # すべての例を実行
        await basic_gen_agent_example()
        await evaluated_gen_agent_example()
        await multi_gen_agent_workflow()
        await interactive_gen_agent_example()
        
        print("\n✅ All GenAgent examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 
