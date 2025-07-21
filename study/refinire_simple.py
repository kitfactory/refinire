#!/usr/bin/env python3
"""
Refinire Simple Example - Basic RefinireAgent Usage
RefinireAgentの最もシンプルな使用例

This demonstrates the simplest possible usage of RefinireAgent with proper error handling.
これは、適切なエラーハンドリング付きのRefinireAgentの最もシンプルな使用方法を示しています。
"""

import os
from refinire import RefinireAgent


def main():
    """
    Basic RefinireAgent example with error handling
    エラーハンドリング付きの基本的なRefinireAgent例
    """
    print("🚀 Refinire Simple Example")
    print("=" * 30)
    
    # Check API key
    # APIキーをチェック
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        print("❌ OPENAI_API_KEY環境変数を設定してください。")
        return
    
    try:
        # Create the simplest possible agent with longer timeout
        # タイムアウトを延長した最もシンプルなエージェントを作成
        agent = RefinireAgent(
            name="simple_assistant",
            generation_instructions="You are a helpful assistant. / あなたは親切なアシスタントです。",
            model="gpt-4o-mini",
            timeout=60  # Extend timeout to 60 seconds / タイムアウトを60秒に延長
        )
        
        # Run agent with user input
        # ユーザー入力でエージェントを実行
        result = agent.run("Hello! Please introduce yourself.")
        
        # Access generated content using the correct specification
        # 正しい仕様に従って生成されたコンテンツにアクセス
        print("✅ Response received:")
        print("✅ 応答を受信:")
        print(f"📄 Content: {result.content}")
        
        # Check if the result contains an error
        # 結果にエラーが含まれているかチェック
        if result.content and "[Error]" in str(result.content):
            print("\n⚠️  Note: The response contains an error message.")
            print("⚠️  注意: 応答にエラーメッセージが含まれています。")
            print("💡 Try running again or check your internet connection.")
            print("💡 再実行するか、インターネット接続を確認してください。")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        print(f"❌ エラーが発生しました: {e}")
        
        # Display detailed exception information from OpenAI Agents SDK level
        # OpenAI Agents SDKレベルからの詳細な例外情報を表示
        import traceback
        print(f"\n🔍 Exception type: {type(e).__name__}")
        print(f"🔍 Exception module: {type(e).__module__}")
        print(f"🔍 Full traceback:")
        traceback.print_exc()
        
        print("\n💡 Tips:")
        print("   - Check your OPENAI_API_KEY environment variable")
        print("   - Make sure you have internet connection")
        print("   - Verify the model name is correct")


if __name__ == "__main__":
    main()