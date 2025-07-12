#!/usr/bin/env python3
"""
Test default value of orchestration_mode
orchestration_modeのデフォルト値をテスト
"""

from refinire import RefinireAgent

def test_default_orchestration_mode():
    """Test that orchestration_mode defaults to False"""
    # orchestration_modeを指定せずにエージェント作成
    agent = RefinireAgent(
        name="default_agent",
        generation_instructions="Provide a simple analysis"
        # orchestration_mode は指定しない
    )
    
    # デフォルト値を確認
    assert agent.orchestration_mode == False
    assert isinstance(agent.orchestration_mode, bool)
    
    # 実際の動作確認
    result = agent.run("Test input")
    
    # Context オブジェクトが返されることを確認
    assert hasattr(result, 'result')
    assert not isinstance(result, dict)

def test_explicit_false():
    """Test explicitly setting orchestration_mode=False"""
    agent = RefinireAgent(
        name="explicit_false_agent",
        generation_instructions="Provide analysis",
        orchestration_mode=False  # 明示的にFalse指定
    )
    
    assert agent.orchestration_mode == False
    
    result = agent.run("Test input")
    
    # Context オブジェクトが返されることを確認
    assert hasattr(result, 'result')
    assert not isinstance(result, dict)

def test_explicit_true():
    """Test explicitly setting orchestration_mode=True"""
    agent = RefinireAgent(
        name="explicit_true_agent",
        generation_instructions="Provide analysis",
        orchestration_mode=True  # 明示的にTrue指定
    )
    
    assert agent.orchestration_mode == True
    
    result = agent.run("Test input")
    
    # 辞書オブジェクトが返されることを確認
    assert isinstance(result, dict)
    assert 'status' in result
    assert 'result' in result
    assert 'reasoning' in result
    assert 'next_hint' in result