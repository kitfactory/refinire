#!/usr/bin/env python3
"""
Minimal usage example for Refinire
Refinireの最小使用例

This demonstrates the simplest possible usage of Refinire with clean output.
これは、クリーンな出力でのRefinireの最も簡単な使用法を示しています。
"""

import os
from refinire import RefinireAgent, Context, disable_tracing


def main():
    """
    Minimal usage example
    最小使用例
    """
    print("=== Minimal Refinire Usage ===")
    
    # Disable tracing for clean output
    # クリーンな出力のためトレーシングを無効化
    disable_tracing()
    
    # Check API key
    # APIキーをチェック
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Please set OPENAI_API_KEY environment variable.")
        return
    
    try:
        # Create agent
        # エージェントを作成
        agent = RefinireAgent(
            name="minimal_agent",
            generation_instructions="You are a helpful assistant. Answer briefly in Japanese.",
            model="gpt-4o-mini"
        )
        
        # Create context and run
        # コンテキストを作成して実行
        context = Context()
        result_context = agent.run("Hello! What is AI?", context)
        
        # Get result
        # 結果を取得
        result = result_context.shared_state.get('minimal_agent_result')
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()