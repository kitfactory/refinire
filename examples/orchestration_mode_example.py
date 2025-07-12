#!/usr/bin/env python3
"""
Orchestration Mode Example - Multi-Agent Coordination

This example demonstrates RefinireAgent's orchestration mode for building
coordinated multi-agent systems with standardized communication protocols.

オーケストレーション・モード例 - マルチエージェント連携

この例では、標準化された通信プロトコルで連携されたマルチエージェント
システムを構築するRefinireAgentのオーケストレーション・モードを実演します。
"""

import asyncio
import json
import logging
from typing import List, Dict, Any
from pydantic import BaseModel, Field

from refinire import RefinireAgent, Flow, ConditionStep, FunctionStep, Context

# Configure logging / ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for structured output / 構造化出力用Pydanticモデル
class AnalysisReport(BaseModel):
    """Structured analysis report / 構造化分析レポート"""
    summary: str = Field(description="Executive summary / エグゼクティブサマリー")
    key_findings: List[str] = Field(description="Important discoveries / 重要な発見")
    recommendations: List[str] = Field(description="Actionable recommendations / 実行可能な推奨事項")
    confidence_score: float = Field(description="Confidence level 0-1 / 信頼度レベル 0-1")
    risk_level: str = Field(description="Risk assessment / リスク評価")

class ValidationResult(BaseModel):
    """Data validation result / データ検証結果"""
    is_valid: bool = Field(description="Whether data is valid / データが有効かどうか")
    quality_score: float = Field(description="Data quality score 0-1 / データ品質スコア 0-1")
    issues_found: List[str] = Field(description="List of issues / 問題リスト")
    next_action: str = Field(description="Recommended next action / 推奨次アクション")

def example_1_basic_orchestration():
    """
    Example 1: Basic orchestration mode usage
    例1: 基本的なオーケストレーション・モード使用
    """
    print("\n" + "="*60)
    print("Example 1: Basic Orchestration Mode / 例1: 基本オーケストレーション・モード")
    print("="*60)
    
    # Create orchestration-enabled agent / オーケストレーション対応エージェント作成
    agent = RefinireAgent(
        name="basic_analyzer",
        generation_instructions="""
        Analyze the provided business data and provide insights.
        Focus on trends, patterns, and actionable recommendations.
        
        提供されたビジネスデータを分析し、洞察を提供してください。
        トレンド、パターン、実行可能な推奨事項に焦点を当ててください。
        """,
        orchestration_mode=True,  # Enable structured output / 構造化出力を有効化
        model="gpt-4o-mini"
    )
    
    # Execute agent / エージェント実行
    input_data = """
    Q3 2024 Sales Data:
    - Total Revenue: $2.5M (up 15% from Q2)
    - Customer Acquisition: 1,200 new customers
    - Customer Retention: 85%
    - Top Product Categories: Software (40%), Consulting (35%), Training (25%)
    """
    
    result = agent.run(input_data)
    
    # Display structured results / 構造化結果を表示
    print(f"Status / ステータス: {result['status']}")
    print(f"Analysis Result / 分析結果:\n{result['result']}")
    print(f"Reasoning / 推論: {result['reasoning']}")
    print(f"Next Recommended Task / 次の推奨タスク: {result['next_hint']['task']}")
    print(f"Confidence Level / 信頼度レベル: {result['next_hint']['confidence']}")
    print(f"Rationale / 根拠: {result['next_hint']['rationale']}")
    
    return result

def example_2_structured_output():
    """
    Example 2: Orchestration with Pydantic models
    例2: Pydanticモデルでのオーケストレーション
    """
    print("\n" + "="*60)
    print("Example 2: Structured Output Orchestration / 例2: 構造化出力オーケストレーション")
    print("="*60)
    
    # Agent with structured output / 構造化出力エージェント
    structured_agent = RefinireAgent(
        name="structured_analyzer",
        generation_instructions="""
        Analyze the business data and generate a comprehensive structured report.
        Include key findings, actionable recommendations, and risk assessment.
        
        ビジネスデータを分析し、包括的な構造化レポートを生成してください。
        主要な発見、実行可能な推奨事項、リスク評価を含めてください。
        """,
        orchestration_mode=True,
        output_model=AnalysisReport,  # Typed result / 型付き結果
        model="gpt-4o-mini"
    )
    
    input_data = """
    Market Analysis Data:
    - Market Growth: 8% annually
    - Competition Level: High (15 major competitors)
    - Customer Satisfaction: 4.2/5.0
    - Technology Adoption: 78% cloud-based solutions
    - Regulatory Changes: New data privacy laws in 2024
    """
    
    result = structured_agent.run(input_data)
    
    if result['status'] == 'completed':
        # Access typed result / 型付き結果にアクセス
        report = result['result']  # This is an AnalysisReport object / これはAnalysisReportオブジェクト
        
        print(f"Report Summary / レポートサマリー: {report.summary}")
        print(f"Key Findings / 主要発見:")
        for i, finding in enumerate(report.key_findings, 1):
            print(f"  {i}. {finding}")
        
        print(f"Recommendations / 推奨事項:")
        for i, rec in enumerate(report.recommendations, 1):
            print(f"  {i}. {rec}")
        
        print(f"Confidence Score / 信頼度スコア: {report.confidence_score}")
        print(f"Risk Level / リスクレベル: {report.risk_level}")
        
        # Orchestration metadata / オーケストレーション・メタデータ
        print(f"\nOrchestration Info / オーケストレーション情報:")
        print(f"Next Task / 次タスク: {result['next_hint']['task']}")
        print(f"Agent Confidence / エージェント信頼度: {result['next_hint']['confidence']}")
    else:
        print(f"Analysis failed / 分析失敗: {result['reasoning']}")
    
    return result

def create_orchestration_workflow():
    """
    Create a multi-agent workflow using orchestration
    オーケストレーションを使用したマルチエージェント・ワークフローを作成
    """
    # Data validation agent / データ検証エージェント
    validator = RefinireAgent(
        name="data_validator",
        generation_instructions="""
        Validate the provided data for completeness, accuracy, and quality.
        Check for missing values, inconsistencies, and data integrity issues.
        
        If quality score > 0.8, recommend 'analysis' as next task.
        If quality score 0.5-0.8, recommend 'cleanup' as next task.
        If quality score < 0.5, recommend 'manual_review' as next task.
        
        提供されたデータの完全性、正確性、品質を検証してください。
        欠損値、不整合、データ整合性問題をチェックしてください。
        
        品質スコア > 0.8の場合、次タスクとして'analysis'を推奨。
        品質スコア 0.5-0.8の場合、次タスクとして'cleanup'を推奨。
        品質スコア < 0.5の場合、次タスクとして'manual_review'を推奨。
        """,
        orchestration_mode=True,
        output_model=ValidationResult,
        model="gpt-4o-mini"
    )
    
    # Data analyzer agent / データ分析エージェント
    analyzer = RefinireAgent(
        name="data_analyzer",
        generation_instructions="""
        Perform comprehensive data analysis and generate insights.
        Focus on patterns, trends, and business implications.
        
        If analysis is successful, recommend 'reporting' as next task.
        If additional validation needed, recommend 'validation' as next task.
        
        包括的なデータ分析を実行し、洞察を生成してください。
        パターン、トレンド、ビジネスへの影響に焦点を当ててください。
        
        分析が成功の場合、次タスクとして'reporting'を推奨。
        追加検証が必要の場合、次タスクとして'validation'を推奨。
        """,
        orchestration_mode=True,
        output_model=AnalysisReport,
        model="gpt-4o-mini"
    )
    
    # Report generator agent / レポート生成エージェント
    reporter = RefinireAgent(
        name="report_generator",
        generation_instructions="""
        Generate final comprehensive report with executive summary.
        Include visual data representation suggestions and next steps.
        
        Mark the workflow as complete when report is generated.
        
        エグゼクティブサマリーを含む最終包括レポートを生成してください。
        視覚的データ表現の提案と次ステップを含めてください。
        
        レポート生成時にワークフローを完了としてマークしてください。
        """,
        orchestration_mode=True,
        model="gpt-4o-mini"
    )
    
    def orchestration_router(ctx):
        """
        Route based on agent recommendations
        エージェント推奨に基づくルーティング
        """
        if hasattr(ctx, 'result') and isinstance(ctx.result, dict):
            next_task = ctx.result.get('next_hint', {}).get('task', 'unknown')
            confidence = ctx.result.get('next_hint', {}).get('confidence', 0.0)
            
            logger.info(f"Routing decision: next_task={next_task}, confidence={confidence}")
            
            # High confidence routing / 高信頼度ルーティング
            if confidence > 0.7:
                if next_task == 'analysis':
                    return 'analyze'
                elif next_task == 'reporting':
                    return 'report'
                elif next_task == 'validation':
                    return 'validate'
                elif next_task == 'cleanup':
                    return 'cleanup'
            
            # Fallback based on status / ステータスベースのフォールバック
            if ctx.result.get('status') == 'failed':
                return 'error'
        
        return 'end'
    
    def cleanup_step(ctx):
        """
        Data cleanup step (placeholder)
        データクリーンアップ・ステップ（プレースホルダー）
        """
        logger.info("Performing data cleanup...")
        ctx.shared_state['cleanup_performed'] = True
        return {
            'status': 'completed',
            'result': 'Data cleanup completed',
            'reasoning': 'Applied standard data cleaning procedures',
            'next_hint': {
                'task': 'analysis',
                'confidence': 0.9,
                'rationale': 'Data is now ready for analysis'
            }
        }
    
    def error_handler(ctx):
        """
        Error handling step
        エラーハンドリング・ステップ
        """
        logger.error("Workflow encountered errors, initiating recovery...")
        return "Error recovery initiated - manual intervention may be required"
    
    # Create workflow / ワークフロー作成
    workflow = Flow({
        "validate": validator,
        "route_after_validate": ConditionStep("route", orchestration_router, "analyze", "cleanup"),
        "cleanup": FunctionStep("cleanup", cleanup_step),
        "route_after_cleanup": ConditionStep("route", orchestration_router, "analyze", "end"),
        "analyze": analyzer,
        "route_after_analyze": ConditionStep("route", orchestration_router, "report", "validate"),
        "report": reporter,
        "error": FunctionStep("error", error_handler),
        "end": FunctionStep("end", lambda ctx: "Workflow completed successfully")
    })
    
    return workflow

async def example_3_multi_agent_workflow():
    """
    Example 3: Multi-agent orchestration workflow
    例3: マルチエージェント・オーケストレーション・ワークフロー
    """
    print("\n" + "="*60)
    print("Example 3: Multi-Agent Orchestration Workflow / 例3: マルチエージェント・オーケストレーション・ワークフロー")
    print("="*60)
    
    workflow = create_orchestration_workflow()
    
    # Sample data with varying quality / 品質の異なるサンプルデータ
    test_datasets = [
        {
            "name": "High Quality Dataset / 高品質データセット",
            "data": """
            Customer Survey Results Q3 2024:
            - Response Rate: 78% (1,560 out of 2,000 customers)
            - Satisfaction Score: 4.3/5.0 (complete data)
            - Net Promoter Score: 72 (industry benchmark: 50)
            - Customer Demographics: Complete profiles for all respondents
            - Response Categories: Product Quality (92%), Service (88%), Value (85%)
            """
        },
        {
            "name": "Medium Quality Dataset / 中品質データセット", 
            "data": """
            Sales Performance Data:
            - Q1 Revenue: $1.2M
            - Q2 Revenue: Missing
            - Q3 Revenue: $1.8M  
            - Customer Count: ~500 (estimated)
            - Product Lines: A, B, C (no detailed breakdown)
            """
        }
    ]
    
    for dataset in test_datasets:
        print(f"\nProcessing: {dataset['name']}")
        print("-" * 40)
        
        try:
            result = await workflow.run(dataset['data'])
            print(f"Workflow Result / ワークフロー結果: {result}")
            
        except Exception as e:
            print(f"Workflow Error / ワークフローエラー: {e}")

def example_4_error_handling():
    """
    Example 4: Error handling and recovery in orchestration
    例4: オーケストレーションでのエラーハンドリングとリカバリ
    """
    print("\n" + "="*60)
    print("Example 4: Error Handling and Recovery / 例4: エラーハンドリングとリカバリ")
    print("="*60)
    
    class RobustOrchestrationAgent:
        """Robust orchestration agent with error recovery / エラーリカバリ付き堅牢オーケストレーション・エージェント"""
        
        def __init__(self, agent_config):
            self.agent = RefinireAgent(**agent_config, orchestration_mode=True)
            self.max_retries = 3
        
        def run_with_recovery(self, input_text, recovery_strategies=None):
            """Run agent with automatic error recovery / 自動エラーリカバリでエージェント実行"""
            recovery_strategies = recovery_strategies or [
                "simplify_request",
                "provide_context", 
                "reduce_scope"
            ]
            
            for attempt in range(self.max_retries):
                try:
                    result = self.agent.run(input_text)
                    
                    if result['status'] == 'completed':
                        return result
                    elif result['status'] == 'failed':
                        logger.warning(f"Attempt {attempt + 1} failed: {result['reasoning']}")
                        
                        # Apply recovery strategy / リカバリ戦略を適用
                        if attempt < len(recovery_strategies):
                            strategy = recovery_strategies[attempt]
                            input_text = self._apply_recovery_strategy(input_text, strategy)
                            logger.info(f"Applying recovery strategy: {strategy}")
                
                except Exception as e:
                    logger.error(f"Execution error on attempt {attempt + 1}: {e}")
                    
                    if attempt == self.max_retries - 1:
                        return {
                            'status': 'failed',
                            'result': None,
                            'reasoning': f"All {self.max_retries} attempts failed. Last error: {str(e)}",
                            'next_hint': {
                                'task': 'manual_intervention',
                                'confidence': 0.0,
                                'rationale': 'Requires manual review and intervention'
                            }
                        }
            
            return {
                'status': 'failed',
                'result': None,
                'reasoning': f"Max retries ({self.max_retries}) exceeded",
                'next_hint': {
                    'task': 'escalate',
                    'confidence': 0.0,
                    'rationale': 'Escalate to human operator'
                }
            }
        
        def _apply_recovery_strategy(self, input_text, strategy):
            """Apply recovery strategy to modify input / 入力修正のためのリカバリ戦略適用"""
            if strategy == "simplify_request":
                return f"Simplified analysis request: {input_text[:100]}..."
            elif strategy == "provide_context":
                return f"Please analyze this step by step: {input_text}"
            elif strategy == "reduce_scope":
                return f"Focus on the main aspects of: {input_text}"
            return input_text
    
    # Test robust agent / 堅牢エージェントのテスト
    robust_agent = RobustOrchestrationAgent({
        'name': 'robust_analyzer',
        'generation_instructions': 'Analyze complex business data patterns',
        'model': 'gpt-4o-mini'
    })
    
    # Test with challenging input / 困難な入力でテスト
    challenging_input = """
    Extremely complex multi-dimensional financial data with 47 variables,
    missing timestamps, inconsistent formats, and potential data corruption.
    Requires advanced statistical analysis and machine learning techniques.
    """
    
    result = robust_agent.run_with_recovery(
        challenging_input,
        recovery_strategies=["simplify_request", "provide_context", "reduce_scope"]
    )
    
    print(f"Final Status / 最終ステータス: {result['status']}")
    if result['status'] == 'completed':
        print(f"Analysis / 分析: {result['result']}")
    else:
        print(f"Failed / 失敗: {result['reasoning']}")
        print(f"Recommended Action / 推奨アクション: {result['next_hint']['task']}")

def example_5_confidence_monitoring():
    """
    Example 5: Confidence level monitoring and quality control
    例5: 信頼度レベル監視と品質制御
    """
    print("\n" + "="*60)
    print("Example 5: Confidence Monitoring / 例5: 信頼度監視")
    print("="*60)
    
    def interpret_confidence(confidence):
        """Interpret confidence levels / 信頼度レベルの解釈"""
        if confidence >= 0.9:
            return "Very High - Proceed immediately / 非常に高い - 即座に進行"
        elif confidence >= 0.7:
            return "High - Proceed with monitoring / 高い - 監視付きで進行"
        elif confidence >= 0.5:
            return "Medium - Consider validation / 中程度 - 検証を考慮"
        elif confidence >= 0.3:
            return "Low - Validation recommended / 低い - 検証推奨"
        else:
            return "Very Low - Manual review required / 非常に低い - 手動レビュー必要"
    
    # Agent with quality monitoring / 品質監視エージェント
    quality_agent = RefinireAgent(
        name="quality_monitor",
        generation_instructions="""
        Analyze the data and provide confidence assessment.
        Consider data quality, complexity, and your certainty in the analysis.
        
        Provide confidence level based on:
        - Data completeness and quality
        - Analysis complexity and certainty
        - Potential risks and limitations
        
        データを分析し、信頼度評価を提供してください。
        データ品質、複雑さ、分析の確実性を考慮してください。
        
        以下に基づいて信頼度レベルを提供：
        - データの完全性と品質
        - 分析の複雑さと確実性
        - 潜在的リスクと制限
        """,
        orchestration_mode=True,
        model="gpt-4o-mini"
    )
    
    # Test with different data qualities / 異なるデータ品質でテスト
    test_cases = [
        {
            "name": "High Quality Data / 高品質データ",
            "data": "Complete customer dataset with 10,000 records, no missing values, validated entries"
        },
        {
            "name": "Medium Quality Data / 中品質データ", 
            "data": "Customer dataset with 5,000 records, 10% missing values, mostly validated"
        },
        {
            "name": "Low Quality Data / 低品質データ",
            "data": "Incomplete dataset with 1,000 records, 40% missing values, unvalidated entries"
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        print("-" * 30)
        
        result = quality_agent.run(test_case['data'])
        
        if result['status'] == 'completed':
            confidence = result['next_hint']['confidence']
            interpretation = interpret_confidence(confidence)
            
            print(f"Confidence Level / 信頼度レベル: {confidence:.2f}")
            print(f"Interpretation / 解釈: {interpretation}")
            print(f"Analysis / 分析: {result['result'][:150]}...")
            print(f"Next Action / 次アクション: {result['next_hint']['task']}")
        else:
            print(f"Analysis failed / 分析失敗: {result['reasoning']}")

async def main():
    """
    Main function to run all orchestration examples
    すべてのオーケストレーション例を実行するメイン関数
    """
    print("Refinire Orchestration Mode Examples")
    print("Refinire オーケストレーション・モード例")
    print("=" * 60)
    
    try:
        # Example 1: Basic orchestration / 例1: 基本オーケストレーション
        example_1_basic_orchestration()
        
        # Example 2: Structured output / 例2: 構造化出力
        example_2_structured_output()
        
        # Example 3: Multi-agent workflow / 例3: マルチエージェント・ワークフロー
        await example_3_multi_agent_workflow()
        
        # Example 4: Error handling / 例4: エラーハンドリング
        example_4_error_handling()
        
        # Example 5: Confidence monitoring / 例5: 信頼度監視
        example_5_confidence_monitoring()
        
        print("\n" + "="*60)
        print("All orchestration examples completed successfully!")
        print("すべてのオーケストレーション例が正常に完了しました！")
        print("="*60)
        
    except Exception as e:
        logger.error(f"Example execution failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())