#!/usr/bin/env python3
"""
Practical Context Management Example
実用的なコンテキスト管理機能の使用例

This example demonstrates practical use cases of context management
including code review, documentation generation, and debugging assistance.
この例では、コードレビュー、ドキュメント生成、デバッグ支援を含む
コンテキスト管理機能の実用的な使用例を示します。
"""

import asyncio
from refinire.agents.pipeline import RefinireAgent

async def code_review_example():
    """Code review with context management"""
    print("🔍 Code Review Example")
    print("-" * 30)
    
    # Configure agent for code review
    # コードレビュー用のエージェント設定
    context_config = [
        {
            "type": "source_code",
            "max_files": 10,
            "max_file_size": 2000
        },
        {
            "type": "fixed_file",
            "file_path": "README.md"
        },
        {
            "type": "conversation_history",
            "max_items": 5
        }
    ]
    
    agent = RefinireAgent(
        name="CodeReviewAgent",
        generation_instructions="You are a code review expert. Analyze the provided source code for quality, best practices, error handling, performance considerations, and documentation completeness. Provide constructive feedback and suggestions for improvement.",
        model="gpt-4",
        context_providers_config=context_config
    )
    
    # Simulate code review request
    # コードレビュー要求をシミュレート
    review_request = """
    Please review the RefinireAgent implementation in the pipeline module.
    Focus on:
    1. Code quality and best practices
    2. Error handling
    3. Performance considerations
    4. Documentation completeness
    """
    
    response = await agent.run_async(review_request)
    print(f"Review Request: {review_request.strip()}")
    print(f"Review Response: {response.content}")
    print()

async def documentation_generation_example():
    """Documentation generation with context management"""
    print("📚 Documentation Generation Example")
    print("-" * 40)
    
    # Configure agent for documentation generation
    # ドキュメント生成用のエージェント設定
    context_config = [
        {
            "type": "source_code",
            "max_files": 15,
            "max_file_size": 1500
        },
        {
            "type": "fixed_file",
            "file_path": "docs/README.md"
        },
        {
            "type": "cut_context",
            "provider": {
                "type": "source_code",
                "max_files": 15,
                "max_file_size": 1500
            },
            "max_chars": 4000,
            "cut_strategy": "start",
            "preserve_sections": True
        }
    ]
    
    agent = RefinireAgent(
        name="DocGenAgent",
        generation_instructions="You are a technical documentation expert. Generate comprehensive and well-structured documentation based on the provided source code and existing documentation. Use clear, concise language and proper formatting.",
        model="gpt-4",
        context_providers_config=context_config
    )
    
    # Generate API documentation
    # APIドキュメントの生成
    doc_request = """
    Generate comprehensive API documentation for the context management system.
    Include:
    1. Overview of context providers
    2. Configuration options for each provider
    3. Usage examples
    4. Best practices
    Format the output in Markdown.
    """
    
    response = await agent.run_async(doc_request)
    print(f"Documentation Request: {doc_request.strip()}")
    print(f"Generated Documentation:\n{response.content}")
    print()

async def debugging_assistance_example():
    """Debugging assistance with context management"""
    print("🐛 Debugging Assistance Example")
    print("-" * 35)
    
    # Configure agent for debugging assistance
    # デバッグ支援用のエージェント設定
    context_config = [
        {
            "type": "source_code",
            "max_files": 8,
            "max_file_size": 1000
        },
        {
            "type": "conversation_history",
            "max_items": 10
        },
        {
            "type": "fixed_file",
            "file_path": "tests/test_context_provider.py"
        }
    ]
    
    agent = RefinireAgent(
        name="DebugAgent",
        generation_instructions="You are a debugging expert. Help users understand and resolve errors by analyzing the provided source code, error messages, and context. Provide clear explanations and step-by-step solutions.",
        model="gpt-4",
        context_providers_config=context_config
    )
    
    # Simulate debugging scenario
    # デバッグシナリオをシミュレート
    debug_request = """
    I'm getting an error when using the SourceCodeProvider:
    "FileNotFoundError: [Errno 2] No such file or directory: 'nonexistent.py'"
    
    The error occurs when I try to search for source code files.
    Can you help me understand what's happening and how to fix it?
    """
    
    response = await agent.run_async(debug_request)
    print(f"Debug Request: {debug_request.strip()}")
    print(f"Debug Response: {response.content}")
    print()

async def main():
    """Run all practical examples"""
    print("🛠️ Practical Context Management Examples")
    print("=" * 50)
    
    # Run code review example
    # コードレビュー例を実行
    await code_review_example()
    
    # Run documentation generation example
    # ドキュメント生成例を実行
    await documentation_generation_example()
    
    # Run debugging assistance example
    # デバッグ支援例を実行
    await debugging_assistance_example()
    
    print("✅ All practical examples completed!")

if __name__ == "__main__":
    asyncio.run(main()) 