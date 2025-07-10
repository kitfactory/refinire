#!/usr/bin/env python3
"""
Basic usage example with tracing
トレーシング付きの基本使用例

This demonstrates Refinire usage with colored tracing output.
これは、色付きトレーシング出力でのRefinireの使用方法を示しています。
"""

import os
from refinire import RefinireAgent, Context
from agents.tracing import trace


def main():
    """
    Basic usage with tracing
    トレーシング付きの基本使用法
    """
    print("=== Basic Usage with Tracing ===")
    
    # Check API key
    # APIキーをチェック
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Please set OPENAI_API_KEY environment variable.")
        return
    
    try:
        # Use trace context for colored output
        # 色付き出力のためのトレースコンテキストを使用
        with trace("basic_usage_example"):
            # Create agent
            # エージェントを作成
            agent = RefinireAgent(
                name="basic_agent",
                generation_instructions="You are a helpful assistant. Answer briefly in Japanese.",
                model="gpt-4o-mini"
            )
            
            # Create context and run
            # コンテキストを作成して実行
            context = Context()
            result_context = agent.run("Hello! What is AI?", context)
            
            # Get result
            # 結果を取得
            result = result_context.shared_state.get('basic_agent_result')
            print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()