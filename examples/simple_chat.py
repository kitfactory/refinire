#!/usr/bin/env python3
"""
Simple chat function example
シンプルなチャット関数の例

This provides a simple one-line function to chat with AI.
これは、AIとチャットするためのシンプルなワンライン関数を提供します。
"""

import os
from refinire import RefinireAgent, Context, disable_tracing


def ask_ai(question: str) -> str:
    """
    Ask AI a question - simplest possible interface
    AIに質問する - 最も簡単なインターフェース
    
    Args:
        question: Question to ask / 質問
    
    Returns:
        AI response / AI応答
    """
    # Disable tracing for clean output
    # クリーンな出力のためトレーシングを無効化
    disable_tracing()
    
    # Create agent and get response
    # エージェントを作成して応答を取得
    agent = RefinireAgent(
        name="chat_ai", 
        generation_instructions="Answer briefly in Japanese.", 
        model="gpt-4o-mini"
    )
    
    context = Context()
    result = agent.run(question, context)
    
    return result.shared_state.get('chat_ai_result', 'No response')


def main():
    """
    Simple chat example
    シンプルなチャット例
    """
    print("=== Simple Chat Example ===")
    
    # Check API key
    # APIキーをチェック
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Please set OPENAI_API_KEY environment variable.")
        return
    
    # Simple usage examples
    # シンプルな使用例
    print("AI:", ask_ai("What is Python?"))
    print("AI:", ask_ai("What is machine learning?"))
    print("AI:", ask_ai("How does AI work?"))


if __name__ == "__main__":
    main()