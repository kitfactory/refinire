#!/usr/bin/env python3
"""
Fast Mode Sample - RefinireAgentでの高速モード機能サンプル
高速モードサンプル - 応答速度を重視した設定での処理

This demonstrates how to use fast_mode for quicker responses with reduced evaluation.
評価を削減してより高速な応答を得るためのfast_modeの使用方法を実演します。
"""

import asyncio
import os
import time
from refinire import RefinireAgent


async def fast_mode_demo():
    """
    Demonstrate fast_mode functionality
    fast_mode機能のデモンストレーション
    """
    print("⚡ Fast Mode Sample")
    print("⚡ 高速モードサンプル")
    print("=" * 40)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        print("❌ OPENAI_API_KEY環境変数を設定してください。")
        return
    
    # Test query / テストクエリ
    test_query = "Write a short poem about technology and AI"
    
    print(f"📝 Test Query: {test_query}")
    print(f"📝 テストクエリ: {test_query}")
    
    # Test 1: Normal mode (with evaluation) / 通常モード（評価あり）
    print("\n📋 Test 1: Normal Mode (with evaluation)")
    print("📋 テスト1: 通常モード（評価あり）")
    
    normal_agent = RefinireAgent(
        name="normal_poet",
        generation_instructions="""
You are a creative poet. Write engaging and thoughtful poetry.
創造的な詩人として、魅力的で思慮深い詩を書いてください。
        """,
        evaluation_instructions="Rate the creativity and quality of the poetry on a scale of 1-10.",
        model="gpt-4o-mini",
        timeout=120
    )
    
    start_time = time.time()
    try:
        result = await normal_agent.run_async(test_query)
        normal_duration = time.time() - start_time
        
        print(f"   ⏱️  Duration: {normal_duration:.2f} seconds")
        print(f"   ⏱️  実行時間: {normal_duration:.2f} 秒")
        print(f"   ✅ Success: {result.success}")
        print(f"   📄 Content: {result.content[:150]}...")
        
        if hasattr(result, 'evaluation_score'):
            print(f"   📊 Evaluation Score: {result.evaluation_score}")
        
    except Exception as e:
        normal_duration = time.time() - start_time
        print(f"   ❌ Error: {e}")
    
    # Test 2: Fast mode (minimal evaluation) / 高速モード（最小評価）
    print("\n📋 Test 2: Fast Mode (minimal evaluation)")
    print("📋 テスト2: 高速モード（最小評価）")
    
    fast_agent = RefinireAgent(
        name="fast_poet",
        generation_instructions="""
You are a creative poet. Write engaging and thoughtful poetry.
創造的な詩人として、魅力的で思慮深い詩を書いてください。
        """,
        model="gpt-4o-mini",
        # No evaluation_instructions for faster processing / 高速処理のため評価指示なし
        timeout=60
    )
    
    start_time = time.time()
    try:
        result = await fast_agent.run_async(test_query)
        fast_duration = time.time() - start_time
        
        print(f"   ⏱️  Duration: {fast_duration:.2f} seconds")
        print(f"   ⏱️  実行時間: {fast_duration:.2f} 秒")
        print(f"   ✅ Success: {result.success}")
        print(f"   📄 Content: {result.content[:150]}...")
        
        # Speed comparison / 速度比較
        if 'normal_duration' in locals():
            speedup = normal_duration / fast_duration
            print(f"   🚀 Speed improvement: {speedup:.2f}x faster")
            print(f"   🚀 速度改善: {speedup:.2f}倍高速")
        
    except Exception as e:
        fast_duration = time.time() - start_time
        print(f"   ❌ Error: {e}")
    
    # Test 3: Ultra-fast mode (minimal settings) / 超高速モード（最小設定）
    print("\n📋 Test 3: Ultra-Fast Mode (minimal settings)")
    print("📋 テスト3: 超高速モード（最小設定）")
    
    ultra_fast_agent = RefinireAgent(
        name="ultra_fast_poet",
        generation_instructions="Write a short poem about technology.",  # Shorter instruction
        model="gpt-4o-mini",
        temperature=0.7,  # Lower temperature for faster processing / 高速処理のため温度を下げる
        timeout=30
    )
    
    start_time = time.time()
    try:
        result = await ultra_fast_agent.run_async("Write a haiku about AI")  # Simpler query
        ultra_fast_duration = time.time() - start_time
        
        print(f"   ⏱️  Duration: {ultra_fast_duration:.2f} seconds")
        print(f"   ⏱️  実行時間: {ultra_fast_duration:.2f} 秒")
        print(f"   ✅ Success: {result.success}")
        print(f"   📄 Content: {result.content}")
        
    except Exception as e:
        ultra_fast_duration = time.time() - start_time
        print(f"   ❌ Error: {e}")
    
    # Performance summary / パフォーマンスサマリー
    print("\n📊 Performance Summary:")
    print("📊 パフォーマンスサマリー:")
    
    if 'normal_duration' in locals():
        print(f"   📈 Normal mode: {normal_duration:.2f}s")
    if 'fast_duration' in locals():
        print(f"   ⚡ Fast mode: {fast_duration:.2f}s")
    if 'ultra_fast_duration' in locals():
        print(f"   🚀 Ultra-fast mode: {ultra_fast_duration:.2f}s")
    
    print("\n💡 Fast Mode Tips:")
    print("💡 高速モードのコツ:")
    print("   • Omit evaluation_instructions for no evaluation") 
    print("   • Use shorter generation_instructions")
    print("   • Use lower temperature")
    print("   • Reduce timeout values")
    print("   • Choose faster models (gpt-4o-mini vs gpt-4o)")
    print("   • Simplify prompts and queries")


if __name__ == "__main__":
    asyncio.run(fast_mode_demo())