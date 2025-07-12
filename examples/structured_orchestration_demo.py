#!/usr/bin/env python3
"""
Structured Output Orchestration Demo - Practical Example

This demo shows how RefinireAgent's orchestration mode works with 
structured output (Pydantic models) for building robust multi-agent workflows.

構造化出力オーケストレーション・デモ - 実践例

このデモでは、堅牢なマルチエージェント・ワークフローを構築するために
RefinireAgentのオーケストレーション・モードが構造化出力（Pydanticモデル）と
どのように連携するかを示します。
"""

import json
import logging
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

from refinire import RefinireAgent

# Configure logging / ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Pydantic models for structured outputs / 構造化出力用Pydanticモデル

class RiskLevel(str, Enum):
    """Risk assessment levels / リスク評価レベル"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Priority(str, Enum):
    """Task priority levels / タスク優先度レベル"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class DataValidationResult(BaseModel):
    """Data validation result structure / データ検証結果構造"""
    is_valid: bool = Field(description="Whether the data passes validation")
    quality_score: float = Field(ge=0.0, le=1.0, description="Data quality score between 0 and 1")
    missing_fields: List[str] = Field(default=[], description="List of missing required fields")
    data_issues: List[str] = Field(default=[], description="List of identified data issues")
    recommended_action: str = Field(description="Next recommended action based on validation")
    
class BusinessAnalysis(BaseModel):
    """Business analysis result structure / ビジネス分析結果構造"""
    executive_summary: str = Field(description="High-level summary for executives")
    key_findings: List[str] = Field(description="List of key business findings")
    opportunities: List[str] = Field(description="Identified business opportunities")
    risks: List[str] = Field(description="Identified business risks")
    financial_impact: Optional[str] = Field(default=None, description="Estimated financial impact")
    risk_level: RiskLevel = Field(description="Overall risk assessment")
    
class ActionPlan(BaseModel):
    """Action plan structure / アクションプラン構造"""
    immediate_actions: List[str] = Field(description="Actions to take immediately")
    short_term_goals: List[str] = Field(description="Goals for next 1-3 months")
    long_term_strategy: List[str] = Field(description="Strategic initiatives for 6+ months")
    required_resources: List[str] = Field(description="Resources needed for implementation")
    success_metrics: List[str] = Field(description="How to measure success")
    priority_level: Priority = Field(description="Overall priority level")

def create_structured_orchestration_agents():
    """
    Create orchestration agents with structured outputs
    構造化出力を持つオーケストレーション・エージェントを作成
    """
    
    # Data Validator Agent / データ検証エージェント
    validator = RefinireAgent(
        name="data_validator",
        generation_instructions="""
        You are a data validation specialist. Analyze the provided business data carefully.
        
        Your tasks:
        1. Check data completeness and identify missing critical information
        2. Assess data quality and assign a score (0.0 = very poor, 1.0 = excellent)
        3. Identify any data inconsistencies or issues
        4. Recommend the appropriate next action based on data quality
        
        Quality score guidelines:
        - 0.8-1.0: High quality, proceed to analysis
        - 0.5-0.8: Medium quality, consider cleanup or proceed with caution
        - 0.0-0.5: Poor quality, requires cleanup or manual review
        
        あなたはデータ検証の専門家です。提供されたビジネスデータを注意深く分析してください。
        
        タスク:
        1. データの完全性をチェックし、不足している重要な情報を特定
        2. データ品質を評価し、スコアを割り当て (0.0 = 非常に悪い, 1.0 = 優秀)
        3. データの不整合や問題を特定
        4. データ品質に基づいて適切な次のアクションを推奨
        """,
        orchestration_mode=True,
        output_model=DataValidationResult,
        model="gpt-4o-mini"
    )
    
    # Business Analyst Agent / ビジネス分析エージェント
    analyst = RefinireAgent(
        name="business_analyst",
        generation_instructions="""
        You are a senior business analyst with expertise in market analysis and strategic planning.
        
        Your tasks:
        1. Analyze the business data thoroughly
        2. Identify key business insights and patterns
        3. Spot opportunities for growth and improvement
        4. Assess potential risks and challenges
        5. Estimate financial impact when possible
        6. Provide overall risk assessment
        
        Focus on actionable insights that can drive business decisions.
        
        あなたは市場分析と戦略計画の専門知識を持つシニア・ビジネス・アナリストです。
        
        タスク:
        1. ビジネスデータを徹底的に分析
        2. 主要なビジネス洞察とパターンを特定
        3. 成長と改善の機会を発見
        4. 潜在的リスクと課題を評価
        5. 可能な場合は財務的影響を推定
        6. 全体的なリスク評価を提供
        """,
        orchestration_mode=True,
        output_model=BusinessAnalysis,
        model="gpt-4o-mini"
    )
    
    # Action Planner Agent / アクションプランナー・エージェント
    planner = RefinireAgent(
        name="action_planner",
        generation_instructions="""
        You are a strategic planning expert who creates actionable business plans.
        
        Your tasks:
        1. Review the business analysis and create a comprehensive action plan
        2. Prioritize actions based on impact and urgency
        3. Define clear short-term and long-term objectives
        4. Identify required resources and success metrics
        5. Assign appropriate priority level to the overall plan
        
        Make sure all recommendations are specific, measurable, and achievable.
        
        あなたは実行可能なビジネスプランを作成する戦略計画の専門家です。
        
        タスク:
        1. ビジネス分析をレビューし、包括的なアクションプランを作成
        2. 影響と緊急性に基づいてアクションを優先順位付け
        3. 明確な短期・長期目標を定義
        4. 必要なリソースと成功指標を特定
        5. 全体プランに適切な優先度レベルを割り当て
        """,
        orchestration_mode=True,
        output_model=ActionPlan,
        model="gpt-4o-mini"
    )
    
    return validator, analyst, planner

def demonstrate_structured_orchestration():
    """
    Demonstrate structured orchestration workflow
    構造化オーケストレーション・ワークフローのデモンストレーション
    """
    print("=" * 80)
    print("Structured Output Orchestration Demo")
    print("構造化出力オーケストレーション・デモ")
    print("=" * 80)
    
    # Create agents / エージェント作成
    validator, analyst, planner = create_structured_orchestration_agents()
    
    # Sample business data / サンプル・ビジネスデータ
    business_data = """
    E-commerce Platform Performance Report Q4 2024:
    
    Revenue Metrics:
    - Total Revenue: $4.2M (up 23% from Q3)
    - Monthly Recurring Revenue: $350K
    - Average Order Value: $127 (up 8% from Q3)
    - Customer Acquisition Cost: $45
    - Customer Lifetime Value: $890
    
    Customer Metrics:
    - Total Active Users: 28,500 (up 15% from Q3)
    - New Customer Registrations: 3,200
    - Customer Retention Rate: 72%
    - Monthly Churn Rate: 4.2%
    - Customer Satisfaction Score: 4.1/5.0
    
    Product Performance:
    - Best Selling Category: Electronics (35% of revenue)
    - Fastest Growing Category: Home & Garden (45% growth)
    - Product Return Rate: 8.5%
    - Inventory Turnover: 6.2x per year
    
    Technical Metrics:
    - Website Uptime: 99.7%
    - Page Load Speed: 2.1 seconds
    - Mobile Traffic: 68% of total traffic
    - Conversion Rate: 3.4% (desktop), 2.8% (mobile)
    
    Market Context:
    - Industry Growth Rate: 12% annually
    - Competitor Analysis: 3 main competitors, we rank #2 in market share
    - Economic Factors: Inflation at 3.2%, consumer confidence index at 108
    """
    
    print(f"Processing Business Data...")
    print("-" * 50)
    
    # Step 1: Data Validation / ステップ1: データ検証
    print("\n🔍 Step 1: Data Validation")
    print("ステップ1: データ検証")
    print("-" * 30)
    
    validation_result = validator.run(business_data)
    
    if validation_result['status'] == 'completed':
        validation_data = validation_result['result']  # DataValidationResult object
        
        print(f"✅ Validation Status: {validation_result['status']}")
        print(f"📊 Data Quality Score: {validation_data.quality_score:.2f}")
        print(f"✔️ Data Valid: {validation_data.is_valid}")
        
        if validation_data.missing_fields:
            print(f"❌ Missing Fields: {', '.join(validation_data.missing_fields)}")
        
        if validation_data.data_issues:
            print(f"⚠️ Data Issues:")
            for issue in validation_data.data_issues:
                print(f"   - {issue}")
        
        print(f"💡 Recommended Action: {validation_data.recommended_action}")
        print(f"🤖 Agent Reasoning: {validation_result['reasoning']}")
        print(f"➡️ Next Hint: {validation_result['next_hint']['task']} (confidence: {validation_result['next_hint']['confidence']:.2f})")
        
        # Decision based on validation / 検証に基づく決定
        if validation_data.quality_score >= 0.6:
            proceed_to_analysis = True
            print("✅ Data quality sufficient for analysis")
        else:
            proceed_to_analysis = False
            print("❌ Data quality too low, analysis skipped")
            
    else:
        print(f"❌ Validation failed: {validation_result['reasoning']}")
        proceed_to_analysis = False
    
    # Step 2: Business Analysis (if validation passed) / ステップ2: ビジネス分析（検証通過時）
    if proceed_to_analysis:
        print("\n📈 Step 2: Business Analysis")
        print("ステップ2: ビジネス分析")
        print("-" * 30)
        
        analysis_input = f"""
        Based on the validated data, please analyze:
        {business_data}
        
        Validation Results:
        - Quality Score: {validation_data.quality_score}
        - Issues Found: {len(validation_data.data_issues)}
        """
        
        analysis_result = analyst.run(analysis_input)
        
        if analysis_result['status'] == 'completed':
            analysis_data = analysis_result['result']  # BusinessAnalysis object
            
            print(f"✅ Analysis Status: {analysis_result['status']}")
            print(f"📋 Executive Summary: {analysis_data.executive_summary}")
            
            print(f"\n🔍 Key Findings:")
            for i, finding in enumerate(analysis_data.key_findings, 1):
                print(f"   {i}. {finding}")
            
            print(f"\n🚀 Opportunities:")
            for i, opportunity in enumerate(analysis_data.opportunities, 1):
                print(f"   {i}. {opportunity}")
            
            print(f"\n⚠️ Risks:")
            for i, risk in enumerate(analysis_data.risks, 1):
                print(f"   {i}. {risk}")
            
            if analysis_data.financial_impact:
                print(f"\n💰 Financial Impact: {analysis_data.financial_impact}")
            
            print(f"\n🎯 Risk Level: {analysis_data.risk_level.value.upper()}")
            print(f"🤖 Agent Reasoning: {analysis_result['reasoning']}")
            print(f"➡️ Next Hint: {analysis_result['next_hint']['task']} (confidence: {analysis_result['next_hint']['confidence']:.2f})")
            
            proceed_to_planning = True
        else:
            print(f"❌ Analysis failed: {analysis_result['reasoning']}")
            proceed_to_planning = False
    else:
        proceed_to_planning = False
    
    # Step 3: Action Planning (if analysis completed) / ステップ3: アクションプラン（分析完了時）
    if proceed_to_planning:
        print("\n📋 Step 3: Action Planning")
        print("ステップ3: アクションプラン")
        print("-" * 30)
        
        planning_input = f"""
        Based on the business analysis, create an action plan:
        
        Executive Summary: {analysis_data.executive_summary}
        Key Findings: {', '.join(analysis_data.key_findings[:2])}...
        Risk Level: {analysis_data.risk_level.value}
        Top Opportunities: {', '.join(analysis_data.opportunities[:2])}...
        Main Risks: {', '.join(analysis_data.risks[:2])}...
        """
        
        planning_result = planner.run(planning_input)
        
        if planning_result['status'] == 'completed':
            plan_data = planning_result['result']  # ActionPlan object
            
            print(f"✅ Planning Status: {planning_result['status']}")
            
            print(f"\n🚨 Immediate Actions:")
            for i, action in enumerate(plan_data.immediate_actions, 1):
                print(f"   {i}. {action}")
            
            print(f"\n📅 Short-term Goals (1-3 months):")
            for i, goal in enumerate(plan_data.short_term_goals, 1):
                print(f"   {i}. {goal}")
            
            print(f"\n🎯 Long-term Strategy (6+ months):")
            for i, strategy in enumerate(plan_data.long_term_strategy, 1):
                print(f"   {i}. {strategy}")
            
            print(f"\n🛠️ Required Resources:")
            for i, resource in enumerate(plan_data.required_resources, 1):
                print(f"   {i}. {resource}")
            
            print(f"\n📊 Success Metrics:")
            for i, metric in enumerate(plan_data.success_metrics, 1):
                print(f"   {i}. {metric}")
            
            print(f"\n⭐ Priority Level: {plan_data.priority_level.value.upper()}")
            print(f"🤖 Agent Reasoning: {planning_result['reasoning']}")
            print(f"➡️ Next Hint: {planning_result['next_hint']['task']} (confidence: {planning_result['next_hint']['confidence']:.2f})")
            
        else:
            print(f"❌ Planning failed: {planning_result['reasoning']}")
    
    print("\n" + "=" * 80)
    print("🎉 Structured Orchestration Demo Completed!")
    print("構造化オーケストレーション・デモ完了！")
    print("=" * 80)
    
    # Summary of structured outputs / 構造化出力のサマリー
    print(f"\n📋 Summary of Structured Outputs:")
    print(f"構造化出力のサマリー:")
    print("-" * 40)
    
    if 'validation_data' in locals():
        print(f"✅ Validation: Quality Score {validation_data.quality_score:.2f}")
    
    if 'analysis_data' in locals():
        print(f"📈 Analysis: {len(analysis_data.key_findings)} findings, Risk: {analysis_data.risk_level.value}")
    
    if 'plan_data' in locals():
        print(f"📋 Planning: {len(plan_data.immediate_actions)} immediate actions, Priority: {plan_data.priority_level.value}")

def test_individual_agents():
    """
    Test individual agents with structured output
    構造化出力での個別エージェントテスト
    """
    print("\n" + "=" * 60)
    print("Individual Agent Testing / 個別エージェントテスト")
    print("=" * 60)
    
    validator, analyst, planner = create_structured_orchestration_agents()
    
    # Test simple inputs / シンプル入力でテスト
    simple_data = """
    Sales Report:
    - Revenue: $100K
    - Customers: 500
    - Orders: 250
    """
    
    print("\n🧪 Testing with simple data:")
    print("シンプルデータでのテスト:")
    print(f"Input: {simple_data}")
    
    # Test validator / バリデーターテスト
    val_result = validator.run(simple_data)
    if val_result['status'] == 'completed':
        val_data = val_result['result']
        print(f"✅ Validator: Quality {val_data.quality_score:.2f}, Valid: {val_data.is_valid}")
        print(f"   Missing: {val_data.missing_fields}")
        print(f"   Issues: {val_data.data_issues}")
    
    # Test analyst / アナリストテスト
    ana_result = analyst.run(simple_data)
    if ana_result['status'] == 'completed':
        ana_data = ana_result['result']
        print(f"📊 Analyst: {len(ana_data.key_findings)} findings, Risk: {ana_data.risk_level.value}")
        print(f"   Summary: {ana_data.executive_summary[:100]}...")
    
    # Test planner / プランナーテスト
    plan_result = planner.run(f"Create action plan based on: {simple_data}")
    if plan_result['status'] == 'completed':
        plan_data = plan_result['result']
        print(f"📋 Planner: {len(plan_data.immediate_actions)} actions, Priority: {plan_data.priority_level.value}")

if __name__ == "__main__":
    try:
        # Main demonstration / メインデモンストレーション
        demonstrate_structured_orchestration()
        
        # Individual agent testing / 個別エージェントテスト
        test_individual_agents()
        
    except Exception as e:
        logger.error(f"Demo execution failed: {e}")
        print(f"\n❌ Demo failed with error: {e}")
        raise