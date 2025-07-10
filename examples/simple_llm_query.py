#!/usr/bin/env python3
"""
Simple LLM Query Example

English: A simple example demonstrating how to query an LLM with RefinireAgent.
日本語: RefinireAgent を使って LLM に問い合わせる簡単な例。
"""

import os
from refinire import RefinireAgent, Context, disable_tracing


def main():
    """
    Simple LLM query example
    シンプルなLLMクエリの例
    """
    print("=== Simple LLM Query Example ===")
    
    # Note: Tracing enabled by default for better observability
    # 注意: デフォルトでトレーシングが有効になっており、より良いオブザーバビリティを提供します
    
    # Check API key
    # APIキーをチェック
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Please set OPENAI_API_KEY environment variable.")
        return
    
    try:
        # Create agent
        # エージェントを作成
        agent = RefinireAgent(
            name="query_agent",
            generation_instructions="You are a helpful assistant.",
            model="gpt-4o-mini"
        )
        
        # Query LLM
        # LLMにクエリ
        context = Context()
        user_input = "Translate 'Hello, world!' into French."
        result_context = agent.run(user_input, context)
        
        # Get clean result
        # クリーンな結果を取得
        result = result_context.shared_state.get('query_agent_result')
        print(f"Query: {user_input}")
        print(f"Response: {result}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main() 
