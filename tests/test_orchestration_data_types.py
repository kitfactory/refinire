#!/usr/bin/env python3
"""
Test data types used in orchestration mode
オーケストレーションモードで使用されるデータ型をテスト
"""

from refinire import RefinireAgent
from pydantic import BaseModel, Field
from typing import List

# カスタムPydanticモデル
class BusinessAnalysis(BaseModel):
    summary: str = Field(description="ビジネス分析の要約")
    strengths: List[str] = Field(description="強みのリスト")
    risks: List[str] = Field(description="リスクのリスト")
    confidence_score: float = Field(ge=0.0, le=1.0, description="信頼度スコア")

def test_orchestration_without_output_model():
    """Test orchestration mode without output_model"""
    print("=== Test 1: Orchestration mode without output_model ===")
    print("テスト1: output_modelなしのオーケストレーションモード")
    
    agent = RefinireAgent(
        name="basic_orchestration",
        generation_instructions="Analyze the business data and provide insights",
        orchestration_mode=True,
        # output_model なし
        model="gpt-4o-mini"
    )
    
    result = agent.run("Revenue increased by 20%")
    
    print(f"Result type: {type(result)}")
    print(f"Result['result'] type: {type(result['result'])}")
    print(f"Result['result'] value: {result['result']}")
    print(f"Result structure keys: {list(result.keys())}")
    print()

def test_orchestration_with_output_model():
    """Test orchestration mode with output_model"""
    print("=== Test 2: Orchestration mode with output_model ===")
    print("テスト2: output_modelありのオーケストレーションモード")
    
    agent = RefinireAgent(
        name="structured_orchestration",
        generation_instructions="Analyze the business data and provide structured insights",
        orchestration_mode=True,
        output_model=BusinessAnalysis,  # Pydanticモデル指定
        model="gpt-4o-mini"
    )
    
    result = agent.run("Our company had 25% revenue growth, but customer complaints increased by 10%")
    
    print(f"Result type: {type(result)}")
    print(f"Result['result'] type: {type(result['result'])}")
    
    if isinstance(result['result'], BusinessAnalysis):
        print("✅ Pydantic object successfully returned in result field")
        print(f"Summary: {result['result'].summary}")
        print(f"Strengths: {result['result'].strengths}")
        print(f"Risks: {result['result'].risks}")
        print(f"Confidence Score: {result['result'].confidence_score}")
    else:
        print(f"❌ Expected BusinessAnalysis, got: {type(result['result'])}")
        print(f"Value: {result['result']}")
    
    print(f"Orchestration metadata - Status: {result['status']}")
    print(f"Orchestration metadata - Reasoning: {result['reasoning']}")
    print(f"Orchestration metadata - Next hint: {result['next_hint']}")
    print()

def test_normal_mode_with_output_model():
    """Test normal mode with output_model for comparison"""
    print("=== Test 3: Normal mode with output_model (for comparison) ===")
    print("テスト3: 比較用の通常モード + output_model")
    
    agent = RefinireAgent(
        name="normal_structured",
        generation_instructions="Analyze the business data and provide structured insights",
        orchestration_mode=False,  # 通常モード
        output_model=BusinessAnalysis,
        model="gpt-4o-mini"
    )
    
    result = agent.run("Revenue grew 30%, but market competition increased")
    
    print(f"Result type: {type(result)}")  # Context オブジェクト
    print(f"result.result type: {type(result.result)}")
    
    if isinstance(result.result, BusinessAnalysis):
        print("✅ Normal mode: Pydantic object in Context.result")
        print(f"Summary: {result.result.summary}")
    else:
        print(f"❌ Expected BusinessAnalysis, got: {type(result.result)}")
    print()

def test_data_type_inspection():
    """Inspect the data types more thoroughly"""
    print("=== Test 4: Data Type Inspection ===")
    print("テスト4: データ型の詳細検査")
    
    agent = RefinireAgent(
        name="inspector",
        generation_instructions="Provide a business analysis",
        orchestration_mode=True,
        output_model=BusinessAnalysis,
        model="gpt-4o-mini"
    )
    
    result = agent.run("Sales up 15%, costs down 5%")
    
    print("Orchestration result structure:")
    for key, value in result.items():
        print(f"  {key}: {type(value)} = {value}")
    
    print(f"\nDetailed result field inspection:")
    result_field = result['result']
    print(f"  Type: {type(result_field)}")
    print(f"  Module: {result_field.__class__.__module__}")
    print(f"  Class name: {result_field.__class__.__name__}")
    
    if hasattr(result_field, '__dict__'):
        print(f"  Attributes: {list(result_field.__dict__.keys())}")
    
    # Pydantic固有のメソッドチェック
    if hasattr(result_field, 'model_dump'):
        print(f"  model_dump(): {result_field.model_dump()}")

if __name__ == "__main__":
    print("Testing data types in orchestration mode")
    print("オーケストレーションモードでのデータ型テスト")
    print("=" * 60)
    
    test_orchestration_without_output_model()
    test_orchestration_with_output_model()
    test_normal_mode_with_output_model()
    test_data_type_inspection()