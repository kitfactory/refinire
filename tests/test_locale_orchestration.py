#!/usr/bin/env python3
"""
Test orchestration mode with different locales
異なるロケールでのオーケストレーション・モードをテスト
"""

from refinire import RefinireAgent

def test_japanese_orchestration():
    """Test orchestration with Japanese locale"""
    print("Testing Japanese orchestration mode...")
    print("日本語オーケストレーション・モードをテスト...")
    
    agent = RefinireAgent(
        name="japanese_agent",
        generation_instructions="提供されたデータを分析し、主要な洞察を特定してください。",
        orchestration_mode=True,
        locale="ja",  # 日本語ロケール
        model="gpt-4o-mini"
    )
    
    result = agent.run("売上が25%増加しました")
    
    print(f"Result type: {type(result)}")
    print(f"Status: {result.get('status', 'unknown')}")
    print(f"Result: {result.get('result', 'none')}")
    print(f"Reasoning: {result.get('reasoning', 'none')}")
    
    if result.get('status') == 'completed':
        print("✅ Japanese orchestration working")
        return True
    else:
        print("❌ Japanese orchestration failed")
        return False

def test_english_orchestration():
    """Test orchestration with English locale"""
    print("\nTesting English orchestration mode...")
    print("英語オーケストレーション・モードをテスト...")
    
    agent = RefinireAgent(
        name="english_agent", 
        generation_instructions="Analyze the provided data and identify key insights.",
        orchestration_mode=True,
        locale="en",  # 英語ロケール
        model="gpt-4o-mini"
    )
    
    result = agent.run("Sales increased by 25%")
    
    print(f"Result type: {type(result)}")
    print(f"Status: {result.get('status', 'unknown')}")
    print(f"Result: {result.get('result', 'none')}")
    print(f"Reasoning: {result.get('reasoning', 'none')}")
    
    if result.get('status') == 'completed':
        print("✅ English orchestration working")
        return True
    else:
        print("❌ English orchestration failed")
        return False

def test_default_locale():
    """Test orchestration with default locale (should be English)"""
    print("\nTesting default locale orchestration mode...")
    print("デフォルトロケール・オーケストレーション・モードをテスト...")
    
    agent = RefinireAgent(
        name="default_agent",
        generation_instructions="Analyze the provided business metrics.",
        orchestration_mode=True,
        # locale not specified - should default to "en"
        model="gpt-4o-mini"
    )
    
    result = agent.run("Revenue grew by 30%")
    
    print(f"Agent locale: {agent.locale}")
    print(f"Result type: {type(result)}")
    print(f"Status: {result.get('status', 'unknown')}")
    print(f"Result: {result.get('result', 'none')}")
    
    if result.get('status') == 'completed':
        print("✅ Default locale orchestration working")
        return True
    else:
        print("❌ Default locale orchestration failed")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Locale-based Orchestration Mode Test")
    print("ロケールベース・オーケストレーション・モード・テスト")
    print("=" * 60)
    
    japanese_success = test_japanese_orchestration()
    english_success = test_english_orchestration()
    default_success = test_default_locale()
    
    print("\n" + "=" * 60)
    print("SUMMARY / サマリー:")
    print(f"Japanese orchestration: {'✅ PASS' if japanese_success else '❌ FAIL'}")
    print(f"English orchestration: {'✅ PASS' if english_success else '❌ FAIL'}")
    print(f"Default orchestration: {'✅ PASS' if default_success else '❌ FAIL'}")
    print("=" * 60)