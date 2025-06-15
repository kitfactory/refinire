"""
Simple generation example using GenAgent (Flow/Step architecture)
GenAgent（Flow/Stepアーキテクチャ）を使用したシンプルな生成の例

This example demonstrates the recommended way to replace AgentPipeline usage.
この例は、AgentPipelineの使用を置き換える推奨方法を示しています。
"""

import asyncio
from refinire import create_simple_gen_agent, create_simple_flow

async def main():
    """
    Main function demonstrating GenAgent simple generation
    GenAgentシンプル生成をデモンストレーションするメイン関数
    """
    
    # Method 1: Using utility function (Recommended)
    # 方法1: ユーティリティ関数を使用（推奨）
    print("=== Method 1: Using create_simple_gen_agent ===")
    gen_agent = create_simple_gen_agent(
        name="simple_generator",
        instructions="""
        You are a helpful assistant that generates creative stories.
        あなたは創造的な物語を生成する役立つアシスタントです。

        Please generate a short story based on the user's input.
        ユーザーの入力に基づいて短い物語を生成してください。
        """,
        model="gpt-3.5-turbo"  # Using GPT-3.5
    )

    # Create and run simple flow
    # シンプルフローを作成して実行
    flow = create_simple_flow(gen_agent)
    user_input = "A story about a robot learning to paint"
    
    try:
        result = await flow.run(input_data=user_input)
        print("\nGenerated Story:")
        print(result.get_result("simple_generator_result"))
    except Exception as e:
        print(f"Error: {e}")

    # Method 2: Manual GenAgent creation
    # 方法2: 手動でGenAgent作成
    print("\n\n=== Method 2: Manual GenAgent creation ===")
    
    from refinire import GenAgent, Flow
    
    # Create GenAgent manually
    # GenAgentを手動で作成
    gen_agent2 = GenAgent(
        name="manual_generator", 
        generation_instructions="""
        You are a creative writing assistant.
        あなたは創造的ライティングアシスタントです。
        
        Create an engaging short story.
        魅力的な短編小説を作成してください。
        """,
        model="gpt-3.5-turbo",
        store_result_key="story_result"
    )
    
    # Create Flow manually 
    # Flowを手動で作成
    flow2 = Flow("manual_story_flow")
    flow2.add_step(gen_agent2)
    
    try:
        result2 = await flow2.run(input_data="A tale of two cats becoming friends")
        print("\nManual Generated Story:")
        print(result2.get_result("story_result"))
    except Exception as e:
        print(f"Error: {e}")

def sync_main():
    """
    Synchronous wrapper for the async main function
    非同期main関数の同期ラッパー
    """
    asyncio.run(main())

if __name__ == "__main__":
    sync_main() 
