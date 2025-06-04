"""
GenAgent example with conversation history
会話履歴（history）を活用したGenAgentの例

This example demonstrates how to use GenAgent with conversation history (Flow/Step architecture).
この例は、会話履歴機能付きGenAgent（Flow/Stepアーキテクチャ）の使用方法を示しています。
"""

import asyncio
from agents_sdk_models import GenAgent, create_simple_flow

async def main():
    """
    Main function demonstrating GenAgent with conversation history
    会話履歴付きGenAgentをデモンストレーションするメイン関数
    """
    
    print("=== GenAgent with Conversation History Example ===")

    # Method 1: Single agent with history management
    # 方法1: 履歴管理付き単一エージェント
    print("\n--- Single Agent with History Management ---")
    
    gen_agent = GenAgent(
        name="history_agent",
        generation_instructions="""
        You are a helpful assistant. Answer concisely and remember the conversation context.
        あなたは親切なアシスタントです。簡潔に答え、会話の文脈を覚えてください。
        
        Reference previous exchanges when relevant to provide coherent responses.
        関連する場合は以前のやり取りを参照して、一貫性のある回答を提供してください。
        """,
        model="gpt-4o",
        history_size=3,  # 直近3件のみ履歴に含める / Keep only recent 3 entries in history
        store_result_key="history_result"
    )

    flow = create_simple_flow(gen_agent)
    
    # 連続した会話を実施 / Conduct continuous conversation
    conversation_inputs = [
        "What is the capital of France?",
        "And what is the population?", 
        "What about the famous landmarks there?",
        "What was my first question?",
        "Summarize our conversation so far in one sentence."
    ]

    for i, user_input in enumerate(conversation_inputs, 1):
        print(f"\n[{i}] User: {user_input}")
        try:
            result = await flow.run(input_data=user_input)
            response = result.get_result("history_result")
            print(f"AI: {response}")
            
            # Show current history size
            # 現在の履歴サイズを表示
            history = gen_agent.get_pipeline_history()
            print(f"   (History entries: {len(history)})")
            
        except Exception as e:
            print(f"❌ Error: {e}")

    # Method 2: Flow with multiple agents sharing context
    # 方法2: コンテキストを共有する複数エージェントのフロー
    print("\n\n--- Multi-Agent Flow with Shared Context ---")
    
    from agents_sdk_models import Flow
    
    # Agent 1: Information gatherer
    # エージェント1: 情報収集者
    info_agent = GenAgent(
        name="info_gatherer",
        generation_instructions="""
        You are an information gathering specialist. Collect and provide factual information.
        あなたは情報収集の専門家です。事実に基づく情報を収集し、提供してください。
        
        Remember what information you've already provided to avoid repetition.
        重複を避けるため、すでに提供した情報を覚えておいてください。
        """,
        model="gpt-4o-mini",
        history_size=5,
        store_result_key="gathered_info",
        next_step="analyst"
    )
    
    # Agent 2: Information analyst
    # エージェント2: 情報分析者
    analyst_agent = GenAgent(
        name="analyst",
        generation_instructions="""
        You are an information analyst. Analyze and synthesize information provided by the info gatherer.
        あなたは情報分析者です。情報収集者によって提供された情報を分析し、統合してください。
        
        Build upon previous analyses and show how new information relates to what was discussed before.
        以前の分析を基に、新しい情報が以前に議論されたことにどう関連するかを示してください。
        """,
        model="gpt-4o-mini",
        history_size=5,
        store_result_key="analysis_result"
    )
    
    # Create multi-agent flow
    # マルチエージェントフローを作成
    multi_flow = Flow("context_sharing_flow")
    multi_flow.add_step(info_agent)
    multi_flow.add_step(analyst_agent)
    
    flow_inputs = [
        "Tell me about renewable energy technologies.",
        "How do solar panels compare to wind turbines?",
        "What are the environmental impacts we discussed?",
        "Compare the cost-effectiveness of the technologies mentioned."
    ]
    
    for i, user_input in enumerate(flow_inputs, 1):
        print(f"\n[Flow {i}] User: {user_input}")
        try:
            result = await multi_flow.run(input_data=user_input)
            
            # Show results from both agents
            # 両エージェントからの結果を表示
            info = result.get_result("gathered_info")
            analysis = result.get_result("analysis_result")
            
            print(f"📊 Info Gatherer: {info}")
            print(f"🔍 Analyst: {analysis}")
            
            # Show history status
            # 履歴状況を表示
            info_history = info_agent.get_pipeline_history()
            analyst_history = analyst_agent.get_pipeline_history()
            print(f"   (Info history: {len(info_history)}, Analyst history: {len(analyst_history)})")
            
        except Exception as e:
            print(f"❌ Flow Error: {e}")

    # Method 3: Demonstrating history management methods
    # 方法3: 履歴管理メソッドのデモンストレーション
    print("\n\n--- History Management Methods ---")
    
    demo_agent = GenAgent(
        name="demo_agent",
        generation_instructions="""
        You are a demo assistant. Respond briefly to demonstrate history functionality.
        あなたはデモアシスタントです。履歴機能をデモンストレーションするため簡潔に応答してください。
        """,
        model="gpt-4o-mini",
        history_size=2,
        store_result_key="demo_result"
    )
    
    demo_flow = create_simple_flow(demo_agent)
    
    # Build up some history
    # 履歴を蓄積
    print("Building conversation history...")
    setup_inputs = ["Hello", "What's 2+2?", "Tell me a joke"]
    
    for setup_input in setup_inputs:
        await demo_flow.run(input_data=setup_input)
    
    # Show current history
    # 現在の履歴を表示
    current_history = demo_agent.get_pipeline_history()
    print(f"\nCurrent history ({len(current_history)} entries):")
    for i, entry in enumerate(current_history, 1):
        print(f"  {i}. Input: {entry.get('input', 'N/A')}")
        print(f"     Output: {entry.get('output', 'N/A')[:50]}...")

    # Test session history
    # セッション履歴をテスト
    session_history = demo_agent.get_session_history()
    print(f"\nSession history: {session_history}")
    
    # Clear history demonstration
    # 履歴クリアのデモンストレーション
    print(f"\nHistory before clear: {len(demo_agent.get_pipeline_history())} entries")
    demo_agent.clear_history()
    print(f"History after clear: {len(demo_agent.get_pipeline_history())} entries")
    
    # Test conversation after clear
    # クリア後の会話をテスト
    print("\nTesting conversation after history clear:")
    result = await demo_flow.run(input_data="Do you remember our previous conversation?")
    response = result.get_result("demo_result")
    print(f"Response: {response}")

def sync_main():
    """
    Synchronous wrapper for the async main function
    非同期main関数の同期ラッパー
    """
    asyncio.run(main())

if __name__ == "__main__":
    sync_main() 