#!/usr/bin/env python3
"""
RefinireAgent Streaming Example
RefinireAgentストリーミング使用例

This example demonstrates how to use RefinireAgent with streaming output
for real-time response display.
このサンプルはリアルタイム応答表示のためのRefinireAgentストリーミング出力の使用方法を示します。
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent, Context

async def basic_streaming_example():
    """
    Basic streaming example with real-time output
    リアルタイム出力の基本ストリーミング例
    """
    print("🔄 Basic Streaming Example")
    print("=" * 40)
    
    # Create agent with longer response instruction for better streaming demonstration
    # より良いストリーミングデモのため、長い応答指示でエージェントを作成
    agent = RefinireAgent(
        name="StreamingAgent",
        generation_instructions="""
        Provide a detailed, thoughtful response about the topic. 
        Explain concepts clearly and give examples. 
        Write in a conversational tone with multiple paragraphs.
        """,
        model="gpt-4o-mini",
        temperature=0.7
    )
    
    user_input = "Explain how artificial intelligence is changing the world"
    
    print(f"User: {user_input}")
    print("Assistant: ", end="", flush=True)
    
    # Stream the response
    async for chunk in agent.run_streamed(user_input):
        print(chunk, end="", flush=True)
    
    print("\n")

async def streaming_with_callback_example():
    """
    Streaming with callback function for custom processing
    カスタム処理用のコールバック関数付きストリーミング
    """
    print("🔄 Streaming with Callback Example")
    print("=" * 40)
    
    agent = RefinireAgent(
        name="CallbackAgent",
        generation_instructions="Provide a helpful response with examples.",
        model="gpt-4o-mini"
    )
    
    # Callback function to process each chunk
    # 各チャンクを処理するコールバック関数
    chunks_received = []
    def chunk_processor(chunk: str):
        chunks_received.append(chunk)
        # You could add custom processing here, like:
        # ここにカスタム処理を追加できます。例：
        # - Save to file / ファイルに保存
        # - Send to websocket / WebSocketに送信
        # - Update UI / UIを更新
        # - Log to database / データベースにログ
    
    user_input = "What are the benefits of renewable energy?"
    
    print(f"User: {user_input}")
    print("Assistant: ", end="", flush=True)
    
    # Stream with callback
    async for chunk in agent.run_streamed(user_input, callback=chunk_processor):
        print(chunk, end="", flush=True)
    
    print(f"\n\n📊 Received {len(chunks_received)} chunks")
    print(f"📏 Total characters: {sum(len(chunk) for chunk in chunks_received)}")

async def streaming_with_context_example():
    """
    Streaming with shared context for conversation continuity
    会話継続のための共有コンテキスト付きストリーミング
    """
    print("🔄 Streaming with Context Example")
    print("=" * 40)
    
    agent = RefinireAgent(
        name="ContextAgent",
        generation_instructions="Continue the conversation naturally, referencing previous messages.",
        model="gpt-4o-mini"
    )
    
    # Create shared context for conversation
    # 会話用の共有コンテキストを作成
    ctx = Context()
    
    messages = [
        "Hello, can you help me understand Python?",
        "What about async/await in Python?",
        "Can you give me a practical example?"
    ]
    
    for i, user_input in enumerate(messages):
        print(f"\n--- Message {i + 1} ---")
        print(f"User: {user_input}")
        print("Assistant: ", end="", flush=True)
        
        # Add user message to context
        # ユーザーメッセージをコンテキストに追加
        ctx.add_user_message(user_input)
        
        # Stream response with shared context
        # 共有コンテキストで応答をストリーミング
        async for chunk in agent.run_streamed(user_input, ctx=ctx):
            print(chunk, end="", flush=True)
        
        print()  # New line after each response

async def error_handling_streaming_example():
    """
    Demonstrate error handling in streaming
    ストリーミングでのエラーハンドリングを実証
    """
    print("🔄 Error Handling Streaming Example")
    print("=" * 40)
    
    agent = RefinireAgent(
        name="ErrorTestAgent",
        generation_instructions="Respond helpfully to user input.",
        model="gpt-4o-mini"
    )
    
    try:
        # Test with empty input
        print("Testing with empty input...")
        async for chunk in agent.run_streamed(""):
            print(chunk, end="", flush=True)
        
        print("\n\nTesting with normal input...")
        async for chunk in agent.run_streamed("Tell me about Python"):
            print(chunk, end="", flush=True)
        
    except Exception as e:
        print(f"Error occurred: {e}")

async def main():
    """Run all streaming examples"""
    try:
        await basic_streaming_example()
        await streaming_with_callback_example()
        await streaming_with_context_example()
        await error_handling_streaming_example()
        
        print("\n✅ All streaming examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())