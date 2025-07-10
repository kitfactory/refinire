#!/usr/bin/env python3
"""
Simple ClarifyAgent Example
シンプルなClarifyAgentの例

This demonstrates how to use ClarifyAgent to clarify ambiguous requests.
これは、曖昧な要求を明確化するためのClarifyAgentの使用方法を示しています。
"""

import os
from refinire import RefinireAgent, Context, disable_tracing


def main():
    """
    Simple clarification example using RefinireAgent
    RefinireAgentを使用したシンプルな明確化例
    """
    print("=== Simple Clarification Example ===")
    
    # Note: Tracing enabled by default for better observability
    # 注意: デフォルトでトレーシングが有効になっており、より良いオブザーバビリティを提供します
    
    # Check API key
    # APIキーをチェック
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Please set OPENAI_API_KEY environment variable.")
        return
    
    try:
        # Create clarification agent using RefinireAgent
        # RefinireAgentを使用して明確化エージェントを作成
        agent = RefinireAgent(
            name="clarify_agent",
            generation_instructions="""
            ユーザーの曖昧な要求を分析し、より具体的で実行可能な要求に明確化してください。
            以下の観点から質問し、詳細を確認してください：
            1. 技術的仕様（どんな機能が必要か）
            2. 対象ユーザー（誰が使うか）
            3. 期限や制約（いつまでに、どのような制限があるか）
            
            明確化された要求を簡潔にまとめて回答してください。
            """,
            model="gpt-4o-mini"
        )
        
        # Test with ambiguous request
        # 曖昧な要求でテスト
        ambiguous_request = "APIを作りたいです"
        context = Context()
        
        print(f"Original request: {ambiguous_request}")
        print("Clarifying...")
        
        # Run clarification
        # 明確化を実行
        result_context = agent.run(ambiguous_request, context)
        
        # Get result
        # 結果を取得
        result = result_context.shared_state.get('clarify_agent_result')
        print(f"Clarified analysis: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()