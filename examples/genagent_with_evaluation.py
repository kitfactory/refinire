"""
GenAgent example with generation and evaluation
生成と評価を行うGenAgentの例

This example demonstrates the recommended way to replace AgentPipeline with evaluation.
この例は、評価機能付きAgentPipelineを置き換える推奨方法を示しています。
"""

import asyncio
from refinire import create_evaluated_gen_agent, create_simple_flow

async def main():
    """
    Main function demonstrating GenAgent with evaluation
    評価機能付きGenAgentをデモンストレーションするメイン関数
    """
    
    # Method 1: Using utility function (Recommended)
    # 方法1: ユーティリティ関数を使用（推奨）
    print("=== Method 1: Using create_evaluated_gen_agent ===")
    gen_agent = create_evaluated_gen_agent(
        name="evaluated_generator",
        generation_instructions="""
        You are a helpful assistant that generates creative stories.
        あなたは創造的な物語を生成する役立つアシスタントです。

        Please generate a short story based on the user's input.
        ユーザーの入力に基づいて短い物語を生成してください。
        """,
        evaluation_instructions="""
        You are a story evaluator. Please evaluate the generated story based on:
        あなたは物語の評価者です。以下の基準で生成された物語を評価してください：

        1. Creativity (0-100)
           創造性（0-100）
        2. Coherence (0-100)
           一貫性（0-100）
        3. Emotional impact (0-100)
           感情的な影響（0-100）

        Calculate the average score and provide specific comments for each aspect.
        平均スコアを計算し、各側面について具体的なコメントを提供してください。
        """,
        model="gpt-4o",  # Use GPT-4o for generation / 生成にGPT-4oを使用
        evaluation_model="gpt-4o-mini",  # Use GPT-4o-mini for evaluation / 評価にGPT-4o-miniを使用
        threshold=70  # Minimum acceptable score / 最小許容スコア
    )

    # Create and run simple flow
    # シンプルフローを作成して実行
    flow = create_simple_flow(gen_agent)
    user_input = "A story about a robot learning to paint"
    
    try:
        result = await flow.run(input_data=user_input)
        story = result.get_result("evaluated_generator_result")
        
        if story:
            print("\nGenerated Story (passed evaluation):")
            print(story)
        else:
            print("\nStory generation failed to meet quality threshold")
            
        # Show evaluation history if available
        # 利用可能な場合は評価履歴を表示
        history = gen_agent.get_pipeline_history()
        if history:
            print(f"\nTotal generations attempted: {len(history)}")
            for i, entry in enumerate(history, 1):
                if 'evaluation' in entry:
                    eval_result = entry['evaluation']
                    print(f"Attempt {i}: Score {eval_result.score}/100")
                    
    except Exception as e:
        print(f"Error: {e}")

    # Method 2: Manual GenAgent creation with evaluation
    # 方法2: 評価機能付きGenAgentの手動作成
    print("\n\n=== Method 2: Manual GenAgent creation with evaluation ===")
    
    from refinire import GenAgent, Flow
    
    # Create GenAgent manually with evaluation
    # 評価機能付きGenAgentを手動で作成
    gen_agent2 = GenAgent(
        name="manual_evaluated_generator", 
        generation_instructions="""
        You are a creative writing assistant specializing in science fiction.
        あなたはサイエンスフィクション専門の創造的ライティングアシスタントです。
        
        Create an engaging sci-fi short story.
        魅力的なSF短編小説を作成してください。
        """,
        evaluation_instructions="""
        Evaluate this science fiction story based on:
        以下の基準でこのサイエンスフィクション小説を評価してください：
        
        1. Scientific plausibility (0-100)
           科学的妥当性（0-100）
        2. Narrative structure (0-100)
           物語構造（0-100）
        3. Character development (0-100)
           キャラクター開発（0-100）
        
        Provide detailed feedback for improvement.
        改善のための詳細なフィードバックを提供してください。
        """,
        model="gpt-4o",
        evaluation_model="gpt-4o-mini",
        threshold=75,
        store_result_key="scifi_story_result"
    )
    
    # Create Flow manually 
    # Flowを手動で作成
    flow2 = Flow("evaluated_scifi_flow")
    flow2.add_step(gen_agent2)
    
    try:
        result2 = await flow2.run(input_data="A story about AI consciousness emerging in a space station")
        story2 = result2.get_result("scifi_story_result")
        
        if story2:
            print("\nManual Generated Story (passed evaluation):")
            print(story2)
        else:
            print("\nStory generation failed to meet quality threshold")
            
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
