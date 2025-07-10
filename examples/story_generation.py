#!/usr/bin/env python3
"""
Simple story generation example using RefinireAgent
RefinireAgentを使用したシンプルな物語生成の例

This demonstrates creative content generation with current API.
これは、現在のAPIでの創作コンテンツ生成を示しています。
"""

import os
from refinire import RefinireAgent, Context, disable_tracing


def main():
    """
    Story generation example
    物語生成の例
    """
    print("=== Story Generation Example ===")
    
    # Note: Tracing enabled by default for better observability
    # 注意: デフォルトでトレーシングが有効になっており、より良いオブザーバビリティを提供します
    
    # Check API key
    # APIキーをチェック
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Please set OPENAI_API_KEY environment variable.")
        return
    
    try:
        # Create story generation agent
        # 物語生成エージェントを作成
        agent = RefinireAgent(
            name="story_generator",
            generation_instructions="""
            You are a creative storyteller. Generate engaging short stories 
            based on user prompts. Write in a creative and imaginative style.
            日本語で短い物語を生成してください。創造的で想像力豊かなスタイルで書いてください。
            """,
            model="gpt-4o-mini"
        )
        
        # Story prompts
        # 物語のプロンプト
        prompts = [
            "A robot discovers the meaning of friendship",
            "魔法の森で迷子になった少女の話",
            "Time traveler accidentally changes history"
        ]
        
        for i, prompt in enumerate(prompts, 1):
            print(f"\n--- Story {i} ---")
            print(f"Prompt: {prompt}")
            print("Generated story:")
            print("-" * 40)
            
            # Generate story
            # 物語を生成
            context = Context()
            result_context = agent.run(prompt, context)
            story = result_context.shared_state.get('story_generator_result')
            
            if story:
                print(story)
            else:
                print("Failed to generate story")
            
            print("-" * 40)
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()