#!/usr/bin/env python3
"""
Advanced Context Management Example
高度なコンテキスト管理機能の使用例

This example demonstrates advanced context management features
including context compression, dynamic selection, and chained processing.
この例では、コンテキスト圧縮、動的選択、連鎖処理を含む
高度なコンテキスト管理機能の使用方法を示します。
"""

import asyncio
from refinire.agents.pipeline import RefinireAgent

async def main():
    # Advanced context configuration with chained providers
    # 連鎖プロバイダーを含む高度なコンテキスト設定
    context_config = [
        {
            "type": "conversation_history",
            "max_items": 10
        },
        {
            "type": "source_code",
            "base_path": ".",  # 明示的にプロジェクトルートを指定
            "max_files": 5,
            "max_file_size": 1000
        },
        {
            "type": "cut_context",
            "provider": {
                "type": "source_code",
                "base_path": ".",  # 明示的にプロジェクトルートを指定
                "max_files": 5,
                "max_file_size": 1000
            },
            "max_chars": 3000,
            "cut_strategy": "middle",
            "preserve_sections": True
        }
    ]
    
    # Create agent with advanced context management
    # 高度なコンテキスト管理機能付きエージェントの作成
    agent = RefinireAgent(
        name="AdvancedContextAgent",
        generation_instructions="You are an advanced AI assistant with sophisticated context management capabilities. Use the provided context effectively to provide comprehensive and accurate responses.",
        model="gpt-4",
        context_providers_config=context_config
    )
    
    print("🚀 Advanced Context Management Example")
    print("=" * 50)
    
    # Simulate a long conversation to demonstrate context compression
    # コンテキスト圧縮を実証するための長い会話をシミュレート
    print("\n📝 Simulating long conversation...")
    
    messages = [
        "What is Refinire?",
        "How does the agent system work?",
        "Can you show me examples of different agent types?",
        "What about the pipeline system?",
        "How do I use the tracing features?",
        "Tell me about the context management system",
        "What are the best practices for using Refinire?",
        "How can I customize the agent behavior?",
        "What about error handling and retries?",
        "Can you explain the flow system?"
    ]
    
    for i, message in enumerate(messages, 1):
        print(f"\n--- Message {i} ---")
        response = await agent.run_async(message)
        print(f"User: {message}")
        print(f"Assistant: {response.content[:200]}...")
        
        # Show context statistics every 3 messages
        # 3メッセージごとにコンテキスト統計を表示
        if i % 3 == 0:
            print(f"\n📊 Context stats after {i} messages:")
            # Note: In a real implementation, you might want to add
            # methods to get context statistics
            print("(Context compression and management active)")
    
    # Demonstrate context clearing
    # コンテキストクリアの実証
    print("\n🧹 Clearing context...")
    agent.clear_context()
    print("Context cleared!")
    
    # Fresh interaction after clearing
    # クリア後の新しい対話
    print("\n📝 Fresh interaction after context clear:")
    response = await agent.run_async("What is Refinire?")
    print(f"User: What is Refinire?")
    print(f"Assistant: {response.content}")

if __name__ == "__main__":
    asyncio.run(main()) 