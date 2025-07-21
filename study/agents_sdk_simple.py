#!/usr/bin/env python3
"""
OpenAI Agents SDK Simple Example - Direct SDK Usage
OpenAI Agents SDKの直接使用例

This demonstrates the same functionality as refinire_simple.py but using
the OpenAI Agents SDK directly to compare behavior and exceptions.

これは refinire_simple.py と同じ機能を OpenAI Agents SDK を直接使用して実装し、
動作と例外を比較するためのものです。
"""

import os
import asyncio

try:
    from agents import Agent, Runner
    print("✅ Successfully imported Agent and Runner from agents")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Available agents attributes:")
    import agents
    print([attr for attr in dir(agents) if not attr.startswith('_')][:10])  # First 10 for brevity
    raise


async def main():
    """
    Direct OpenAI Agents SDK example with error handling
    エラーハンドリング付きの直接OpenAI Agents SDK例
    """
    print("🤖 OpenAI Agents SDK Simple Example")
    print("=" * 40)
    
    # Check API key
    # APIキーをチェック
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        print("❌ OPENAI_API_KEY環境変数を設定してください。")
        return
    
    try:
        # Create OpenAI Agents SDK Agent directly
        # OpenAI Agents SDK Agentを直接作成
        agent = Agent(
            name="simple_assistant",
            instructions="You are a helpful assistant. / あなたは親切なアシスタントです。",
            model="gpt-4o-mini"
        )
        
        print("🚀 Agent created successfully")
        print("🚀 エージェントが正常に作成されました")
        
        # Run agent with user input using Runner
        # RunnerでユーザーサイドプロンプトでエージェントにUserRequestを実行
        user_input = "Hello! Please introduce yourself."
        print(f"📝 Sending: {user_input}")
        print(f"📝 送信中: {user_input}")
        
        # Direct SDK execution
        # 直接SDK実行
        result = await Runner.run(agent, user_input)
        
        # Display result
        # 結果表示
        print("✅ Response received from OpenAI Agents SDK:")
        print("✅ OpenAI Agents SDKから応答を受信:")
        print(f"📄 Final Output: {result.final_output}")
        
        # Display additional result information
        # 追加の結果情報を表示
        print(f"\n🔍 Result Details:")
        print(f"   - Type: {type(result)}")
        print(f"   - Has output: {hasattr(result, 'output')}")
        if hasattr(result, 'output'):
            print(f"   - Output: {result.output}")
        print(f"   - Has final_output: {hasattr(result, 'final_output')}")
        print(f"   - Attributes: {[attr for attr in dir(result) if not attr.startswith('_')]}")
        
    except Exception as e:
        print(f"❌ OpenAI Agents SDK Exception occurred:")
        print(f"❌ OpenAI Agents SDK例外が発生しました:")
        print(f"   - Exception Type: {type(e).__name__}")
        print(f"   - Exception Module: {type(e).__module__}")
        print(f"   - Exception Message: {str(e)}")
        print(f"   - Exception Args: {e.args}")
        
        # Analyze exception types
        # 例外の種類を分析
        print(f"\n🔍 Exception Analysis:")
        
        import httpx
        try:
            from openai import OpenAIError
            if isinstance(e, OpenAIError):
                print(f"   - This is an OpenAI SDK Exception")
        except ImportError:
            print(f"   - OpenAI package not available for type checking")
        
        if isinstance(e, httpx.TimeoutException):
            print(f"   - This is an HTTPX Timeout Exception")
        elif isinstance(e, httpx.ConnectError):
            print(f"   - This is an HTTPX Connection Exception")
        elif isinstance(e, httpx.RequestError):
            print(f"   - This is an HTTPX Request Exception")
        elif isinstance(e, ConnectionError):
            print(f"   - This is a Python Connection Exception")
        elif isinstance(e, TimeoutError):
            print(f"   - This is a Python Timeout Exception")
        else:
            print(f"   - This is some other exception type")
        
        # Full traceback for debugging
        # デバッグ用の完全なトレースバック
        import traceback
        print(f"\n🗂️  Full Traceback:")
        traceback.print_exc()
        
        print("\n💡 Comparison Notes:")
        print("   - This shows the raw OpenAI Agents SDK exception behavior")
        print("   - Compare this with Refinire's exception handling")
        print("   - Refinire converts exceptions to Context messages")
        print("\n💡 比較ノート:")
        print("   - これは生のOpenAI Agents SDK例外動作を示します")
        print("   - これをRefinireの例外処理と比較してください")
        print("   - RefinireはContextメッセージに例外を変換します")


if __name__ == "__main__":
    print("🎯 Running direct OpenAI Agents SDK example...")
    print("🎯 直接OpenAI Agents SDK例を実行中...")
    asyncio.run(main())