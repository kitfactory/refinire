# オーケストレーション・モード・チュートリアル - マルチエージェント連携

このチュートリアルでは、複雑なマルチエージェントシステムを構築するための標準化された通信プロトコルを提供するRefinireAgentのオーケストレーション・モードについて説明します。

## 目次

1. [オーケストレーション・モードの理解](#オーケストレーション・モードの理解)
2. [基本的なオーケストレーション設定](#基本的なオーケストレーション設定)
3. [構造化出力との統合](#構造化出力との統合)
4. [マルチエージェント・ワークフロー連携](#マルチエージェント・ワークフロー連携)
5. [高度なオーケストレーション・パターン](#高度なオーケストレーション・パターン)
6. [エラーハンドリングとリカバリ](#エラーハンドリングとリカバリ)
7. [ベストプラクティス](#ベストプラクティス)

## オーケストレーション・モードの理解

### 課題

従来のAIエージェントは非構造化テキストやコンテキストオブジェクトを返すため、以下の問題がありました：
- ワークフロー内で複数のエージェントを連携させることが困難
- エージェントがタスクを正常に完了したかどうかの判断が困難
- 次に取るべきアクションの把握が困難
- 堅牢なエラーハンドリングとリカバリ機構の構築が困難

### 解決策

オーケストレーション・モードは、RefinireAgentの出力を標準化されたJSON形式に変換します：

```json
{
  "status": "completed",          // "completed" または "failed"
  "result": "タスクの成果",         // 実際の結果（文字列または型付きオブジェクト）
  "reasoning": "この結果の理由",     // エージェントの推論過程
  "next_hint": {                  // 次ステップの推奨
    "task": "validation",
    "confidence": 0.85,
    "rationale": "検証ステップの準備完了"
  }
}
```

### 主要なメリット

- **標準化された通信**: エージェント間相互作用の統一インターフェース
- **ステータスの明確化**: ワークフロー制御のための明確な成功/失敗表示
- **スマートな推奨**: エージェントが最適な次ステップを提案
- **型安全性**: resultフィールドのオプションPydanticモデル統合
- **エラーの透明性**: 堅牢なシステムのための構造化エラー報告

## 基本的なオーケストレーション設定

### シンプルなオーケストレーション・エージェント

```python
from refinire import RefinireAgent

# オーケストレーション対応エージェントを作成
agent = RefinireAgent(
    name="data_analyzer",
    generation_instructions="提供されたデータを分析し、主要な洞察を特定する",
    orchestration_mode=True,  # 構造化出力を有効化
    model="gpt-4o-mini"
)

# エージェントを実行
result = agent.run("顧客満足度調査データを分析してください")

# 構造化レスポンスにアクセス
print(f"ステータス: {result['status']}")
print(f"分析結果: {result['result']}")
print(f"推論: {result['reasoning']}")

# 次ステップの推奨を確認
next_step = result['next_hint']
print(f"推奨される次タスク: {next_step['task']}")
print(f"信頼度レベル: {next_step['confidence']}")
print(f"根拠: {next_step['rationale']}")
```

### オーケストレーション vs 通常モード

```python
from refinire import RefinireAgent

# 通常モードエージェント（デフォルト）
normal_agent = RefinireAgent(
    name="normal_agent",
    generation_instructions="有用な分析を提供する",
    orchestration_mode=False,  # デフォルト
    model="gpt-4o-mini"
)

# オーケストレーション・モード・エージェント
orchestration_agent = RefinireAgent(
    name="orchestration_agent", 
    generation_instructions="有用な分析を提供する",
    orchestration_mode=True,
    model="gpt-4o-mini"
)

input_text = "このデータを分析してください"

# 通常モードはContextを返す
normal_result = normal_agent.run(input_text)
print(f"通常結果の型: {type(normal_result)}")  # <class 'Context'>
print(f"コンテンツ: {normal_result.result}")

# オーケストレーション・モードは辞書を返す
orch_result = orchestration_agent.run(input_text)
print(f"オーケストレーション結果の型: {type(orch_result)}")  # <class 'dict'>
print(f"ステータス: {orch_result['status']}")
print(f"結果: {orch_result['result']}")
```

## 構造化出力との統合

### オーケストレーションでのPydanticモデル使用

`output_model`を指定すると、`result`フィールドには型付きオブジェクトが含まれます：

```python
from pydantic import BaseModel, Field
from refinire import RefinireAgent
from typing import List

class DataAnalysisReport(BaseModel):
    """構造化分析レポート"""
    summary: str = Field(description="発見事項の要約")
    key_findings: List[str] = Field(description="重要な発見のリスト")
    recommendations: List[str] = Field(description="実行可能な推奨事項")
    confidence_score: float = Field(description="分析の信頼度（0-1）")
    data_quality: str = Field(description="データ品質の評価")

# 構造化出力エージェント
structured_agent = RefinireAgent(
    name="structured_analyst",
    generation_instructions="""
    提供されたデータを徹底的に分析し、包括的なレポートを生成してください。
    主要な発見、推奨事項を含め、データ品質を評価してください。
    """,
    orchestration_mode=True,
    output_model=DataAnalysisReport,  # 結果が型付きになる
    model="gpt-4o-mini"
)

# 分析実行
result = structured_agent.run("2024年Q3の顧客フィードバックデータを分析してください")

# 型付き結果にアクセス
report = result['result']  # これはDataAnalysisReportオブジェクト
print(f"ステータス: {result['status']}")
print(f"要約: {report.summary}")
print(f"主要発見: {report.key_findings}")
print(f"推奨事項: {report.recommendations}")
print(f"信頼度: {report.confidence_score}")
print(f"データ品質: {report.data_quality}")

# オーケストレーション・メタデータにアクセス
print(f"エージェントの推論: {result['reasoning']}")
print(f"次の推奨タスク: {result['next_hint']['task']}")
```

### 混合出力タイプ

```python
from pydantic import BaseModel

class TaskResult(BaseModel):
    task_id: str
    completed: bool
    details: str

# 時々構造化出力を使用するエージェント
flexible_agent = RefinireAgent(
    name="flexible_worker",
    generation_instructions="""
    リクエストを処理してください。複雑なタスクには構造化出力を提供し、
    シンプルなタスクには文字列レスポンスを提供してください。
    """,
    orchestration_mode=True,
    output_model=TaskResult,  # 適切な場合に使用される
    model="gpt-4o-mini"
)

# シンプルなリクエスト - 結果は文字列
simple_result = flexible_agent.run("2 + 2は？")
print(f"シンプル結果: {simple_result['result']}")  # 文字列: "4"

# 複雑なリクエスト - 結果はTaskResultオブジェクト
complex_result = flexible_agent.run("顧客注文#12345を処理してください")
task = complex_result['result']  # TaskResultオブジェクト
print(f"タスクID: {task.task_id}")
print(f"完了: {task.completed}")
```

## マルチエージェント・ワークフロー連携

### オーケストレーション・ベースのルーティング

```python
from refinire import RefinireAgent, Flow, ConditionStep, FunctionStep

# オーケストレーション対応エージェントを定義
data_collector = RefinireAgent(
    name="data_collector",
    generation_instructions="""
    分析に必要なデータを収集し、検証してください。
    データが分析に十分かどうか、または追加が必要かを判断してください。
    """,
    orchestration_mode=True,
    model="gpt-4o-mini"
)

data_analyzer = RefinireAgent(
    name="data_analyzer",
    generation_instructions="""
    包括的なデータ分析を実行し、洞察を生成してください。
    結果がレポート作成に進むべきか、最初に検証が必要かを判断してください。
    """,
    orchestration_mode=True,
    model="gpt-4o-mini"
)

validator = RefinireAgent(
    name="validator",
    generation_instructions="""
    分析結果の正確性と完全性を検証してください。
    結果がレポート作成の準備ができているか、修正が必要かを判断してください。
    """,
    orchestration_mode=True,
    model="gpt-4o-mini"
)

reporter = RefinireAgent(
    name="reporter",
    generation_instructions="""
    推奨事項を含む最終レポートを生成してください。
    ワークフローを完了としてマークしてください。
    """,
    orchestration_mode=True,
    model="gpt-4o-mini"
)

def orchestration_router(ctx):
    """エージェント推奨に基づいてルーティング"""
    if hasattr(ctx, 'result') and isinstance(ctx.result, dict):
        next_task = ctx.result.get('next_hint', {}).get('task', 'unknown')
        confidence = ctx.result.get('next_hint', {}).get('confidence', 0.0)
        
        # 高信頼度ルーティング
        if confidence > 0.8:
            if next_task == 'analysis':
                return 'analyze'
            elif next_task == 'validation':
                return 'validate'
            elif next_task == 'reporting':
                return 'report'
        
        # ステータスに基づくフォールバック・ルーティング
        if ctx.result.get('status') == 'failed':
            return 'error_handler'
    
    return 'end'

# オーケストレーション・ルーティングでワークフローを作成
workflow = Flow({
    "collect": data_collector,
    "route_after_collect": ConditionStep("route", orchestration_router, "analyze", "end"),
    "analyze": data_analyzer,
    "route_after_analyze": ConditionStep("route", orchestration_router, "validate", "report"),
    "validate": validator,
    "route_after_validate": ConditionStep("route", orchestration_router, "report", "analyze"),
    "report": reporter,
    "error_handler": FunctionStep("error_handler", handle_errors)
})

# ワークフロー実行
result = await workflow.run("Q3分析用の顧客調査データを処理してください")
```

### コンテキスト渡しによるエージェント・チェーン

```python
from refinire import RefinireAgent, Context

# オーケストレーション・エージェントのチェーンを作成
agents = {
    "preprocessor": RefinireAgent(
        name="preprocessor",
        generation_instructions="分析用にデータをクリーニングし準備する",
        orchestration_mode=True,
        model="gpt-4o-mini"
    ),
    "analyzer": RefinireAgent(
        name="analyzer", 
        generation_instructions="前処理されたデータを分析し、パターンを特定する",
        orchestration_mode=True,
        model="gpt-4o-mini"
    ),
    "summarizer": RefinireAgent(
        name="summarizer",
        generation_instructions="分析の要約を作成する",
        orchestration_mode=True,
        model="gpt-4o-mini"
    )
}

def run_agent_chain(input_data, agent_sequence):
    """オーケストレーション・エージェントのシーケンスを実行"""
    ctx = Context()
    results = []
    
    for agent_name in agent_sequence:
        agent = agents[agent_name]
        
        # 前の結果を次のエージェントの入力として使用
        if results:
            previous_result = results[-1]['result']
            input_text = f"このデータを処理してください: {previous_result}"
        else:
            input_text = input_data
        
        # エージェント実行
        result = agent.run(input_text, ctx)
        results.append(result)
        
        # 失敗をチェック
        if result['status'] == 'failed':
            print(f"エージェント {agent_name} が失敗: {result['reasoning']}")
            break
        
        # 進捗をログ
        print(f"{agent_name} 完了: {result['next_hint']['task']} 推奨")
        
        # 結果でコンテキストを更新
        ctx.shared_state[f"{agent_name}_result"] = result['result']
    
    return results

# チェーン実行
chain_results = run_agent_chain(
    "2024年Q3からの生の顧客フィードバックデータ",
    ["preprocessor", "analyzer", "summarizer"]
)

# 結果レビュー
for i, result in enumerate(chain_results):
    agent_name = ["preprocessor", "analyzer", "summarizer"][i]
    print(f"\n{agent_name.upper()} 結果:")
    print(f"ステータス: {result['status']}")
    print(f"結果: {result['result'][:100]}...")
    print(f"次の推奨: {result['next_hint']['task']}")
```

## 高度なオーケストレーション・パターン

### 条件付きエージェント選択

```python
from refinire import RefinireAgent

class OrchestrationController:
    """オーケストレーション・エージェント管理コントローラー"""
    
    def __init__(self):
        self.agents = {
            "simple_analyzer": RefinireAgent(
                name="simple_analyzer",
                generation_instructions="小規模データセットの基本データ分析を実行",
                orchestration_mode=True,
                model="gpt-4o-mini"
            ),
            "advanced_analyzer": RefinireAgent(
                name="advanced_analyzer",
                generation_instructions="大規模データセットの複雑な分析を実行",
                orchestration_mode=True,
                model="gpt-4o"  # より強力なモデル
            ),
            "specialist_analyzer": RefinireAgent(
                name="specialist_analyzer",
                generation_instructions="専門ドメイン分析を実行",
                orchestration_mode=True,
                model="gpt-4o-mini"
            )
        }
    
    def select_agent(self, task_description, data_size, domain):
        """タスク特性に基づいて適切なエージェントを選択"""
        if data_size > 1000 and "複雑" in task_description:
            return "advanced_analyzer"
        elif domain in ["金融", "医療", "法律"]:
            return "specialist_analyzer"
        else:
            return "simple_analyzer"
    
    def execute_task(self, task_description, data_size=100, domain="一般"):
        """最適なエージェント選択でタスクを実行"""
        agent_name = self.select_agent(task_description, data_size, domain)
        agent = self.agents[agent_name]
        
        # メタデータ付きで実行
        task_input = f"""
        タスク: {task_description}
        データサイズ: {data_size} レコード
        ドメイン: {domain}
        選択エージェント: {agent_name}
        """
        
        result = agent.run(task_input)
        
        # 選択メタデータを追加
        result['metadata'] = {
            'selected_agent': agent_name,
            'data_size': data_size,
            'domain': domain
        }
        
        return result

# 使用例
controller = OrchestrationController()

# シンプルなタスク
simple_result = controller.execute_task(
    "基本的な顧客満足度分析",
    data_size=50,
    domain="一般"
)

# 複雑なタスク
complex_result = controller.execute_task(
    "機械学習洞察を含む複雑なパターン分析",
    data_size=5000,
    domain="金融"
)

print(f"シンプルタスクエージェント: {simple_result['metadata']['selected_agent']}")
print(f"複雑タスクエージェント: {complex_result['metadata']['selected_agent']}")
```

### 並列オーケストレーション

```python
from refinire import RefinireAgent, Flow
import asyncio

# 並列処理用の複数オーケストレーション・エージェントを作成
parallel_agents = [
    RefinireAgent(
        name=f"analyzer_{i}",
        generation_instructions=f"データセグメント{i}を分析し、洞察を提供",
        orchestration_mode=True,
        model="gpt-4o-mini"
    )
    for i in range(3)
]

async def parallel_orchestration(data_segments):
    """複数エージェントを並列実行"""
    tasks = []
    
    for i, (agent, segment) in enumerate(zip(parallel_agents, data_segments)):
        # 各エージェント用の非同期タスクを作成
        task = asyncio.create_task(
            agent.run_async(f"セグメント{i}を分析: {segment}")
        )
        tasks.append(task)
    
    # すべてのエージェントの完了を待機
    results = await asyncio.gather(*tasks)
    
    # 結果を集約
    successful = [r for r in results if r['status'] == 'completed']
    failed = [r for r in results if r['status'] == 'failed']
    
    return {
        'total_agents': len(results),
        'successful': len(successful),
        'failed': len(failed),
        'results': results,
        'aggregated_insights': [r['result'] for r in successful]
    }

# 並列処理実行
data_segments = [
    "Q1の顧客フィードバック",
    "Q2の顧客フィードバック", 
    "Q3の顧客フィードバック"
]

parallel_result = await parallel_orchestration(data_segments)
print(f"完了: {parallel_result['successful']}/{parallel_result['total_agents']} エージェント")
```

## エラーハンドリングとリカバリ

### 堅牢なエラーハンドリング

```python
from refinire import RefinireAgent
import logging

logger = logging.getLogger(__name__)

class RobustOrchestrationAgent:
    """強化されたエラーハンドリングを持つオーケストレーション・エージェントのラッパー"""
    
    def __init__(self, agent_config):
        self.agent = RefinireAgent(**agent_config, orchestration_mode=True)
        self.max_retries = 3
        self.retry_count = 0
    
    def run_with_recovery(self, input_text, recovery_strategies=None):
        """自動エラーリカバリでエージェントを実行"""
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
                    logger.warning(f"試行{attempt + 1}でエージェント失敗: {result['reasoning']}")
                    
                    # リカバリ戦略を適用
                    if attempt < len(recovery_strategies):
                        strategy = recovery_strategies[attempt]
                        input_text = self._apply_recovery_strategy(input_text, strategy, result)
                        logger.info(f"リカバリ戦略適用: {strategy}")
                
            except Exception as e:
                logger.error(f"試行{attempt + 1}でエージェント実行エラー: {e}")
                
                if attempt == self.max_retries - 1:
                    return {
                        'status': 'failed',
                        'result': None,
                        'reasoning': f"{self.max_retries}回の試行すべてが失敗。最後のエラー: {str(e)}",
                        'next_hint': {
                            'task': 'manual_intervention',
                            'confidence': 0.0,
                            'rationale': '手動レビューと介入が必要'
                        }
                    }
        
        return {
            'status': 'failed',
            'result': None,
            'reasoning': f"最大リトライ数（{self.max_retries}）を超過",
            'next_hint': {
                'task': 'escalate',
                'confidence': 0.0,
                'rationale': '人間オペレーターにエスカレート'
            }
        }
    
    def _apply_recovery_strategy(self, input_text, strategy, failed_result):
        """入力修正のためのリカバリ戦略を適用"""
        if strategy == "simplify_request":
            return f"簡略化されたリクエスト: {input_text[:100]}..."
        elif strategy == "provide_context":
            return f"これを段階的に分析してください: {input_text}"
        elif strategy == "reduce_scope":
            return f"主要な側面に焦点を当ててください: {input_text}"
        return input_text

# 使用例
robust_agent = RobustOrchestrationAgent({
    'name': 'robust_analyzer',
    'generation_instructions': '複雑なデータパターンを分析',
    'model': 'gpt-4o-mini'
})

result = robust_agent.run_with_recovery(
    "47変数を持つ極めて複雑な多次元データを分析",
    recovery_strategies=["simplify_request", "provide_context", "reduce_scope"]
)

print(f"最終ステータス: {result['status']}")
if result['status'] == 'completed':
    print(f"分析: {result['result']}")
else:
    print(f"失敗: {result['reasoning']}")
    print(f"推奨アクション: {result['next_hint']['task']}")
```

## ベストプラクティス

### 1. オーケストレーション用エージェント設計

```python
# 良い例: オーケストレーションを考慮した明確で具体的な指示
good_agent = RefinireAgent(
    name="data_validator",
    generation_instructions="""
    提供されたデータの完全性と正確性を検証してください。
    
    あなたのタスク:
    1. データの完全性チェック（欠損値、必須フィールド）
    2. データ精度の確認（形式、範囲、一貫性）
    3. データ品質スコアの評価（0-1）
    
    検証合格（スコア > 0.8）の場合、次タスクとして'analysis'を推奨。
    検証失敗（スコア < 0.5）の場合、次タスクとして'data_cleanup'を推奨。
    境界線（0.5-0.8）の場合、次タスクとして'manual_review'を推奨。
    
    常に検証の推論を明確に説明してください。
    """,
    orchestration_mode=True,
    model="gpt-4o-mini"
)

# 悪い例: オーケストレーションを導かない曖昧な指示
bad_agent = RefinireAgent(
    name="generic_agent",
    generation_instructions="データで何かをする",
    orchestration_mode=True,
    model="gpt-4o-mini"
)
```

### 2. 信頼度レベルガイドライン

```python
def interpret_confidence_levels(confidence):
    """エージェント信頼度レベルの解釈ガイドライン"""
    if confidence >= 0.9:
        return "高信頼度 - 即座に進行"
    elif confidence >= 0.7:
        return "良好な信頼度 - 監視付きで進行"
    elif confidence >= 0.5:
        return "中程度の信頼度 - 検証を考慮"
    elif confidence >= 0.3:
        return "低信頼度 - 検証推奨"
    else:
        return "非常に低い信頼度 - 手動レビュー必要"

# ワークフロー決定で使用
def confidence_based_routing(ctx):
    """エージェント信頼度レベルに基づくルーティング"""
    if hasattr(ctx, 'result') and isinstance(ctx.result, dict):
        confidence = ctx.result.get('next_hint', {}).get('confidence', 0.0)
        
        if confidence >= 0.8:
            return ctx.result['next_hint']['task']  # 推奨に従う
        elif confidence >= 0.5:
            return 'validation'  # 最初に検証
        else:
            return 'manual_review'  # 人間による監視
    
    return 'error'
```

### 3. オーケストレーション用構造化ログ

```python
import logging
import json

class OrchestrationLogger:
    """オーケストレーション・ワークフロー用専用ロガー"""
    
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 構造化フォーマッターを作成
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_orchestration_result(self, agent_name, result, execution_time=None):
        """構造化データでオーケストレーション結果をログ"""
        log_data = {
            'agent_name': agent_name,
            'status': result.get('status', 'unknown'),
            'next_task': result.get('next_hint', {}).get('task', 'none'),
            'confidence': result.get('next_hint', {}).get('confidence', 0.0),
            'execution_time': execution_time,
            'result_length': len(str(result.get('result', '')))
        }
        
        if result['status'] == 'completed':
            self.logger.info(f"エージェント完了: {json.dumps(log_data, ensure_ascii=False)}")
        else:
            log_data['error_reason'] = result.get('reasoning', '不明なエラー')
            self.logger.error(f"エージェント失敗: {json.dumps(log_data, ensure_ascii=False)}")
    
    def log_workflow_progress(self, workflow_name, step_name, total_steps, current_step):
        """ワークフロー進捗をログ"""
        progress_data = {
            'workflow': workflow_name,
            'step': step_name,
            'progress': f"{current_step}/{total_steps}",
            'completion_percentage': (current_step / total_steps) * 100
        }
        self.logger.info(f"ワークフロー進捗: {json.dumps(progress_data, ensure_ascii=False)}")

# 使用例
logger = OrchestrationLogger("orchestration_workflow")

# ワークフロー内で
import time
start_time = time.time()
result = agent.run("データを分析")
execution_time = time.time() - start_time

logger.log_orchestration_result("data_analyzer", result, execution_time)
```

### 4. オーケストレーション・エージェントのテスト

```python
import pytest
from refinire import RefinireAgent

class TestOrchestrationAgent:
    """オーケストレーション・エージェントのテストスイート"""
    
    def setup_method(self):
        """テストエージェントをセットアップ"""
        self.agent = RefinireAgent(
            name="test_agent",
            generation_instructions="テストデータを分析し、結果を提供",
            orchestration_mode=True,
            model="gpt-4o-mini"
        )
    
    def test_successful_execution(self):
        """成功エージェント実行をテスト"""
        result = self.agent.run("分析用テストデータ")
        
        # オーケストレーション構造を検証
        assert isinstance(result, dict)
        assert 'status' in result
        assert 'result' in result
        assert 'reasoning' in result
        assert 'next_hint' in result
        
        # ステータスを検証
        assert result['status'] in ['completed', 'failed']
        
        # next_hint構造を検証
        next_hint = result['next_hint']
        assert 'task' in next_hint
        assert 'confidence' in next_hint
        assert 0.0 <= next_hint['confidence'] <= 1.0
    
    def test_with_structured_output(self):
        """Pydanticモデルでのオーケストレーションをテスト"""
        from pydantic import BaseModel
        
        class TestOutput(BaseModel):
            summary: str
            score: float
        
        structured_agent = RefinireAgent(
            name="structured_test_agent",
            generation_instructions="構造化テスト出力を生成",
            orchestration_mode=True,
            output_model=TestOutput,
            model="gpt-4o-mini"
        )
        
        result = structured_agent.run("テストレポートを生成")
        
        # 構造化結果を検証
        if result['status'] == 'completed':
            assert isinstance(result['result'], TestOutput)
            assert hasattr(result['result'], 'summary')
            assert hasattr(result['result'], 'score')
    
    def test_error_handling(self):
        """オーケストレーション・モードでのエラーハンドリングをテスト"""
        # これは失敗をシミュレートするためのモッキングが必要
        # 実装はテストフレームワークに依存
        pass

# テスト実行
if __name__ == "__main__":
    pytest.main([__file__])
```

## まとめ

オーケストレーション・モードは、RefinireAgentをシンプルなテキスト生成器から複雑なマルチエージェントシステムの調整されたメンバーに変換します。主要なポイント：

1. **`orchestration_mode=True`で有効化** 構造化JSON出力のため
2. **`output_model`と組み合わせ** 型安全な結果のため
3. **`next_hint`を使用** インテリジェントなワークフロー・ルーティングのため
4. **`confidence`レベルを監視** 品質制御のため
5. **エラーリカバリを実装** 堅牢なハンドリングパターンで
6. **明確な指示を設計** オーケストレーション決定を導く
7. **構造化データをログ** 監視とデバッグのため

オーケストレーション・モードにより、エージェントがステータス、結果、推奨事項を標準化形式で通信する洗練されたAIワークフローを構築でき、複雑なマルチエージェント調整を信頼性が高く保守可能にします。

より高度なパターンについては：
- [Flow完全ガイド](flow_complete_guide_ja.md) - 複雑なワークフローの構築
- [コンテキスト管理](context_management_ja.md) - エージェント間でのデータ共有
- [高度な機能](advanced_ja.md) - 追加のRefinireAgent機能