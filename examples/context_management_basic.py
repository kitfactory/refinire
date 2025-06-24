#!/usr/bin/env python3
"""
Basic Context Management Example
基本的なコンテキスト管理機能の使用例

This example demonstrates the basic usage of context management features
including conversation history, fixed files, and source code search.
この例では、会話履歴、固定ファイル、ソースコード検索を含む
基本的なコンテキスト管理機能の使用方法を示します。
"""

import asyncio
from refinire.agents.pipeline import RefinireAgent

async def main():
    # Configure context providers
    # コンテキストプロバイダーの設定
    context_config = [
        {
            "type": "conversation_history",
            "max_items": 5
        },
        {
            "type": "fixed_file",
            "file_path": "README.md"
        },
        {
            "type": "source_code",
            "max_files": 3,
            "max_file_size": 500
        }
    ]
    
    # Create agent with context management
    # コンテキスト管理機能付きエージェントの作成
    agent = RefinireAgent(
        name="ContextManagementAgent",
        generation_instructions="You are a helpful assistant with access to project context including documentation and source code.",
        model="gpt-3.5-turbo",
        context_providers_config=context_config
    )
    
    print("🤖 Basic Context Management Example")
    print("=" * 50)
    
    # First interaction - agent will have access to README.md
    # 最初の対話 - エージェントはREADME.mdにアクセス可能
    print("\n📝 First interaction (with README.md context):")
    response1 = await agent.run_async("What is this project about?")
    print(f"User: What is this project about?")
    print(f"Assistant: {response1.content}")
    
    # Second interaction - agent will have conversation history
    # 2番目の対話 - エージェントは会話履歴を持つ
    print("\n📝 Second interaction (with conversation history):")
    response2 = await agent.run_async("Can you explain the main features in more detail?")
    print(f"User: Can you explain the main features in more detail?")
    print(f"Assistant: {response2.content}")
    
    # Third interaction - agent will search for related source code
    # 3番目の対話 - エージェントは関連するソースコードを検索
    print("\n📝 Third interaction (with source code search):")
    response3 = await agent.run_async("Show me how to use the RefinireAgent class")
    print(f"User: Show me how to use the RefinireAgent class")
    print(f"Assistant: {response3.content}")
    
    # Show context provider schemas
    # コンテキストプロバイダーのスキーマを表示
    print("\n📋 Available Context Provider Schemas:")
    schemas = agent.get_context_provider_schemas()
    for provider_type, schema in schemas.items():
        print(f"- {provider_type}: {schema.get('description', 'No description')}")
        parameters = schema.get('parameters', {})
        required = [k for k, v in parameters.items() if v.get('required', False)]
        optional = [k for k, v in parameters.items() if not v.get('required', False)]
        print(f"  Required: {required}")
        print(f"  Optional: {optional}")
        print()

if __name__ == "__main__":
    asyncio.run(main()) 