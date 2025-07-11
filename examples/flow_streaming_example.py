#!/usr/bin/env python3
"""
Flow Streaming Example
Flowストリーミング使用例

This example demonstrates how to use Flow with streaming output
for steps that support streaming (like RefinireAgent).
このサンプルはストリーミングをサポートするステップ（RefinireAgentなど）で
Flowのストリーミング出力を使用する方法を示します。
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent, Flow, FunctionStep

async def flow_streaming_example():
    """
    Example of Flow with streaming RefinireAgent
    ストリーミングRefinireAgentを使用したFlowの例
    """
    print("🔄 Flow Streaming Example")
    print("=" * 40)
    
    # Create streaming-capable agent
    # ストリーミング対応エージェントを作成
    streaming_agent = RefinireAgent(
        name="StreamingAgent",
        generation_instructions="""
        Provide a detailed, helpful response about the topic. 
        Explain concepts clearly with examples.
        Write in a conversational tone.
        """,
        model="gpt-4o-mini"
    )
    
    # Create non-streaming function step
    # 非ストリーミング関数ステップを作成
    def process_input(user_input, context):
        """Simple processing step"""
        context.result = f"Processing input: {user_input}"
        return context
    
    def add_summary(user_input, context):
        """Add summary to previous result"""
        previous = getattr(context, 'result', '')
        context.result = f"{previous}\n\n[Summary completed]"
        return context
    
    # Create Flow with mixed streaming and non-streaming steps
    # ストリーミングと非ストリーミングステップを混合したFlowを作成
    flow = Flow(
        start="process",
        steps={
            "process": FunctionStep("process", process_input, "stream_agent"),
            "stream_agent": streaming_agent,  # This will be streaming-capable
            "summary": FunctionStep("summary", add_summary)
        },
        name="mixed_flow"
    )
    
    # Set next step for streaming agent
    # ストリーミングエージェントの次ステップを設定
    streaming_agent.next_step = "summary"
    
    user_input = "Explain the benefits of renewable energy"
    
    print(f"User: {user_input}")
    print("Flow Output: ", end="", flush=True)
    
    try:
        # Stream the flow execution
        # フロー実行をストリーミング
        async for chunk in flow.run_streamed(user_input):
            print(chunk, end="", flush=True)
        
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Flow streaming failed: {e}")
        import traceback
        traceback.print_exc()

async def simple_flow_streaming_example():
    """
    Simple example with just RefinireAgent in Flow
    FlowでRefinireAgentのみのシンプルな例
    """
    print("\n🔄 Simple Flow Streaming Example")
    print("=" * 40)
    
    # Create simple streaming agent
    # シンプルなストリーミングエージェントを作成
    agent = RefinireAgent(
        name="SimpleAgent",
        generation_instructions="Respond helpfully to the user's question with examples.",
        model="gpt-4o-mini"
    )
    
    # Create Flow with just the agent
    # エージェントのみでFlowを作成
    flow = Flow(
        start="agent",
        steps={
            "agent": agent
        },
        name="simple_streaming_flow"
    )
    
    user_input = "What are the key principles of good software design?"
    
    print(f"User: {user_input}")
    print("Agent: ", end="", flush=True)
    
    try:
        # Stream the flow execution
        # フロー実行をストリーミング
        chunks_received = []
        async for chunk in flow.run_streamed(user_input):
            print(chunk, end="", flush=True)
            chunks_received.append(chunk)
        
        print(f"\n\n📊 Received {len(chunks_received)} chunks")
        
    except Exception as e:
        print(f"\n❌ Simple flow streaming failed: {e}")
        import traceback
        traceback.print_exc()

async def flow_streaming_with_callback_example():
    """
    Flow streaming with callback for custom processing
    カスタム処理用コールバック付きFlowストリーミング
    """
    print("\n🔄 Flow Streaming with Callback Example")
    print("=" * 40)
    
    agent = RefinireAgent(
        name="CallbackAgent",
        generation_instructions="Provide a step-by-step explanation.",
        model="gpt-4o-mini"
    )
    
    flow = Flow(
        start="agent",
        steps={"agent": agent},
        name="callback_flow"
    )
    
    # Callback to process chunks
    # チャンクを処理するコールバック
    chunk_count = 0
    def process_chunk(chunk):
        nonlocal chunk_count
        chunk_count += 1
        # Here you could add custom processing:
        # ここにカスタム処理を追加できます：
        # - Save to file / ファイルに保存
        # - Send to WebSocket / WebSocketに送信
        # - Update database / データベースを更新
    
    user_input = "How do you make a good cup of coffee?"
    
    print(f"User: {user_input}")
    print("Agent: ", end="", flush=True)
    
    try:
        # Stream with callback
        # コールバック付きでストリーミング
        async for chunk in flow.run_streamed(user_input, callback=process_chunk):
            print(chunk, end="", flush=True)
        
        print(f"\n\n📊 Callback processed {chunk_count} chunks")
        
    except Exception as e:
        print(f"\n❌ Callback flow streaming failed: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all Flow streaming examples"""
    try:
        await flow_streaming_example()
        await simple_flow_streaming_example()
        await flow_streaming_with_callback_example()
        
        print("\n✅ All Flow streaming examples completed!")
        
    except Exception as e:
        print(f"❌ Examples failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())