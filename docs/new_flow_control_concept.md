# 新しいフローコントール

## 現在のフローコントロール（オーケストレーションモード）

現在、RefinireAgentにはオーケストレーション・モードが存在する。これはAgent自身が次のルーティングに関する示唆を行い、それを次のオーケストレーターにより、次エージェントを決定するといった手法である。

この手法で行われている方法は、一定の完成度のあるエージェントの出力へのインストラクションに、次エージェントの情報を示唆する内容を含むように指示するものであり、その追加の指示によって精度に影響が発生する可能性がある。

## 新規ルーティング手法について

新規手法としてRefinireAgentにrouting_instruction、routing_mode=accurate_routing/fast_routingを設けるものとする。

routing_instructionが存在する場合、指示に従ったルーティング情報を生成する。Flowでは、そのルーティング情報を確認して、次のエージェントを実行することが可能である。

routing_mode:accurate_routingでは、生成用のエージェントが生成した内容を、新たなRefinireAgentにより評価し、ルーティング情報を生成する。これによりrouting_instructionの影響を受けずに生成エージェントは動作することが可能である。

routing_mode：fast_routingでは、現在のオーケストレーションモードの動作をする。generation_instructionで指示される生成の指示をコンテンツに持つ、データクラスを構造化出力させる。これにより、ルーティングの判断とコンテンツの生成を同時に行う。

ただし、Flowから見て、どちらのモードであっても次の情報を取得するひつようがあるため、そこは基本的に同一のデータ型を基本クラスに持つよう出力する。

refinireは高品質生成を念頭におくため、無指定時はrouting_mode=accurate_routingをデフォルトとする。

## routing_instruction の標準データ型設計

### 基本設計方針

- **evaluation_instruction との一貫性**: 既存の評価システムと同様の構造とパターンを採用
- **型安全性**: 明確なデータ型制約により実行時エラーを防止
- **柔軟性**: ユーザーの多様な生成コンテンツ（文字列/構造化JSON）に対応
- **標準化**: 一貫したルーティング判断のための標準フォーマット
- **シンプル性**: 単一のルーティング用データクラスで対応

### 標準データ型定義

#### RoutingResult (統一クラス)

```python
from typing import Union, Any
from pydantic import BaseModel, Field

class RoutingResult(BaseModel):
    """
    ルーティング判断の標準出力形式
    contentはoutput_model指定時はその型、未指定時は文字列
    """
    content: Union[str, Any] = Field(
        description="生成されたコンテンツ（output_model指定時はその型、未指定時は文字列）"
    )
    
    # 定型のルーティング情報
    next_route: str = Field(
        description="次に実行するルート名",
        examples=["simple_processor", "complex_analyzer", "end"]
    )
    
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="ルーティング判断の信頼度 (0.0-1.0)",
        examples=[0.95, 0.78, 0.65]
    )
    
    reasoning: str = Field(
        description="ルーティング判断の理由",
        examples=["コンテンツは十分に詳細で、追加処理は不要", "部分的な情報のため、専門エージェントが必要"]
    )
```

### APIの設計

```python
class RefinireAgent:
    def __init__(
        self,
        # 既存パラメータ...
        routing_instruction: Optional[str] = None,
        routing_mode: str = "accurate_routing"
    ):
        self.routing_instruction = routing_instruction
        self.routing_mode = routing_mode
```

#### 使用パターン

```python
# パターン1: output_model指定あり
class UserTaskResult(BaseModel):
    task_result: str
    score: float

agent = RefinireAgent(
    name="router_agent",
    generation_instructions="タスクを実行してください",
    routing_instruction="スコアが0.8以上なら'complete'、未満なら'retry'",
    output_model=UserTaskResult
)
# 結果: RoutingResult[content=UserTaskResult, next_route=str, confidence=float, reasoning=str]

# パターン2: output_model指定なし
agent = RefinireAgent(
    name="text_router",
    generation_instructions="レポートを作成してください",
    routing_instruction="完了なら'end'、追加情報必要なら'enhance'"
)
# 結果: RoutingResult[content=str, next_route=str, confidence=float, reasoning=str]
```

### シンプルなrouting_instruction例

ユーザーは出力形式を指定する必要がない。システムが自動的に適切な出力形式を付与する。

```python
routing_instructions = {
    "simple": "コンテンツが完成していれば'end'、追加処理が必要なら'enhance'を選択",
    
    "quality_based": """
    品質基準で判断してください：
    - 高品質（85点以上）: 'publish'
    - 中品質（70-84点）: 'improve' 
    - 低品質（70点未満）: 'regenerate'
    """,
    
    "complexity_based": """
    複雑さに応じて判断：
    - 簡単な内容: 'simple_processor'
    - 中程度の内容: 'standard_processor'
    - 複雑な内容: 'expert_processor'
    """,
    
    "content_type_based": """
    コンテンツの種類に応じて選択：
    - テキスト形式: 'text_formatter'
    - データ形式: 'data_validator'
    - 混合形式: 'mixed_processor'
    """
}
```

### 制約とバリデーション

```python
class RoutingConstraints:
    """ルーティングデータの制約定義"""
    
    # next_route制約
    VALID_ROUTE_PATTERN = r'^[a-zA-Z][a-zA-Z0-9_-]*$'
    MAX_ROUTE_LENGTH = 50
    
    # confidence制約
    CONFIDENCE_MIN = 0.0
    CONFIDENCE_MAX = 1.0
    CONFIDENCE_PRECISION = 2
    
    # reasoning制約
    MIN_REASONING_LENGTH = 10
    MAX_REASONING_LENGTH = 500
    
    # content_type制約
    VALID_CONTENT_TYPES = {"text", "json", "structured", "mixed", "unknown"}
    
    # complexity_level制約
    VALID_COMPLEXITY_LEVELS = {"simple", "moderate", "complex", "expert_level"}
    
    # completion_status制約
    VALID_COMPLETION_STATUSES = {
        "complete", "partial", "needs_refinement", 
        "requires_validation", "failed", "unknown"
    }
```

### 実装の流れ

```python
def _execute_routing(self, content: Any) -> RoutingResult:
    """ルーティング判断の実行"""
    # 1. output_modelに基づいてRoutingResultを動的生成
    routing_output_model = self._create_routing_output_model()
    
    # 2. プロンプト自動構築（出力形式を自動付与）
    routing_prompt = self._build_routing_prompt(content, self.routing_instruction)
    
    # 3. ルーティング専用エージェントで実行
    routing_agent = RefinireAgent(
        name=f"{self.name}_router",
        generation_instructions=routing_prompt,
        output_model=routing_output_model,  # 動的生成されたモデル
        model=self.model
    )
    
    # 4. 実行と結果取得
    result = routing_agent.run("")
    
    # 5. 型安全な結果返却
    return result.content  # RoutingResult型で構造化済み

def _create_routing_output_model(self) -> Type[BaseModel]:
    """output_modelに基づいてRoutingResultを動的生成"""
    from typing import create_model
    
    # ベースのルーティングフィールド
    base_fields = {
        'next_route': (str, Field(description="次に実行するルート名")),
        'confidence': (float, Field(ge=0.0, le=1.0, description="ルーティング判断の信頼度")),
        'reasoning': (str, Field(description="ルーティング判断の理由")),
    }
    
    # contentフィールドの型を決定
    if self.output_model:
        content_type = self.output_model
    else:
        content_type = str
    
    base_fields['content'] = (content_type, Field(description="生成されたコンテンツ"))
    
    # 動的にRoutingResultクラスを生成
    return create_model('RoutingResult', **base_fields)

def _build_routing_prompt(self, content: Any, routing_instruction: str) -> str:
    """ルーティング用プロンプトを自動構築"""
    return f"""
生成されたコンテンツを分析し、次のルーティング判断を行ってください。

=== 生成コンテンツ ===
{{content}}

=== ルーティング指示 ===
{{routing_instruction}}
"""
```

## 設計の利点

### 1. **開発者体験の向上**
- 出力形式を毎回指示する必要がない
- シンプルで直感的なrouting_instruction
- 型安全性は自動的に保証

### 2. **柔軟性の保持**
- `output_model`未指定時: `content`は文字列型
- `output_model`指定時: `content`はユーザー定義型
- ルーティング情報は常に統一フォーマット

### 3. **保守性の向上**
- 単一のルーティングクラスで管理
- 動的な型生成により柔軟性を保持
- 型定義とプロンプトの整合性保証

### 4. **品質重視の設計**
- accurate_routingをデフォルトとし、生成品質を最優先
- 型安全性により実行時エラーを防止
- 一貫したルーティング判断の実現

## Flowを使った新しいエージェント連携サンプル

### 基本的な品質向上フロー

```python
from refinire.agents.flow import Flow
from refinire.agents.pipeline import RefinireAgent
from refinire.core.context import Context
from pydantic import BaseModel, Field

class ContentResult(BaseModel):
    """コンテンツ生成結果"""
    content: str = Field(description="生成されたコンテンツ")
    quality_score: float = Field(description="品質スコア (0.0-1.0)")

# 各エージェントの定義
initial_agent = RefinireAgent(
    name="content_generator",
    generation_instructions="ユーザーの要求に基づいて初期コンテンツを生成してください",
    routing_instruction="品質スコアが0.8以上なら'publish'、未満なら'improve'を選択",
    output_model=ContentResult,
    routing_mode="accurate_routing"
)

enhancement_agent = RefinireAgent(
    name="content_enhancer", 
    generation_instructions="既存のコンテンツを改善し、品質を向上させてください",
    routing_instruction="改善後の品質スコアが0.8以上なら'publish'、未満なら'regenerate'を選択",
    output_model=ContentResult,
    routing_mode="accurate_routing"
)

regeneration_agent = RefinireAgent(
    name="content_regenerator",
    generation_instructions="全く新しいアプローチでコンテンツを再生成してください",
    routing_instruction="完了したら'publish'を選択",
    output_model=ContentResult,
    routing_mode="fast_routing"
)

# フローの定義
quality_flow = Flow({
    "start": initial_agent,
    "improve": enhancement_agent,
    "regenerate": regeneration_agent,
    "publish": "end"
})

# 実行
context = Context()
context.shared_state["user_request"] = "技術記事を作成してください"

result = quality_flow.run("start", context)
print(f"最終コンテンツ: {result.content}")
print(f"品質スコア: {result.quality_score}")
```

### 複雑性に応じた処理分岐フロー

```python
from refinire.agents.flow import Flow
from refinire.agents.pipeline import RefinireAgent
from refinire.core.context import Context
from pydantic import BaseModel, Field

class TaskAnalysis(BaseModel):
    """タスク分析結果"""
    analysis: str = Field(description="分析結果")
    complexity: str = Field(description="複雑性レベル")
    estimated_time: int = Field(description="推定処理時間（分）")

class TaskResult(BaseModel):
    """タスク実行結果"""
    result: str = Field(description="実行結果")
    completion_status: str = Field(description="完了状態")

# エージェントの定義
analyzer_agent = RefinireAgent(
    name="task_analyzer",
    generation_instructions="タスクを分析し、複雑性レベルを判定してください",
    routing_instruction="""
    複雑性レベルに応じて次の処理を選択：
    - simple: 'simple_processor'
    - moderate: 'standard_processor'  
    - complex: 'expert_processor'
    """,
    output_model=TaskAnalysis,
    routing_mode="accurate_routing"
)

simple_processor = RefinireAgent(
    name="simple_processor",
    generation_instructions="シンプルなタスクを迅速に処理してください",
    routing_instruction="処理完了後は'complete'を選択",
    output_model=TaskResult,
    routing_mode="fast_routing"
)

standard_processor = RefinireAgent(
    name="standard_processor", 
    generation_instructions="標準的なタスクを丁寧に処理してください",
    routing_instruction="結果が満足できるなら'complete'、追加検証が必要なら'validate'を選択",
    output_model=TaskResult,
    routing_mode="accurate_routing"
)

expert_processor = RefinireAgent(
    name="expert_processor",
    generation_instructions="複雑なタスクを専門的に処理してください",
    routing_instruction="処理完了後は必ず'validate'を選択",
    output_model=TaskResult,
    routing_mode="accurate_routing"
)

validator_agent = RefinireAgent(
    name="validator",
    generation_instructions="処理結果を検証し、必要に応じて修正してください",
    routing_instruction="検証完了後は'complete'を選択",
    output_model=TaskResult,
    routing_mode="fast_routing"
)

# フローの定義
task_flow = Flow({
    "start": analyzer_agent,
    "simple_processor": simple_processor,
    "standard_processor": standard_processor,
    "expert_processor": expert_processor,
    "validate": validator_agent,
    "complete": "end"
})

# 実行
context = Context()
context.shared_state["user_task"] = "データ分析レポートを作成してください"

result = task_flow.run("start", context)
print(f"最終結果: {result.result}")
print(f"完了状態: {result.completion_status}")
```

### 並列処理と統合フロー

```python
from refinire.agents.flow import Flow
from refinire.agents.pipeline import RefinireAgent
from refinire.core.context import Context
from pydantic import BaseModel, Field
from typing import List

class AnalysisResult(BaseModel):
    """分析結果"""
    analysis_type: str = Field(description="分析タイプ")
    findings: str = Field(description="発見事項")
    recommendations: str = Field(description="推奨事項")

class IntegratedReport(BaseModel):
    """統合レポート"""
    summary: str = Field(description="統合要約")
    key_insights: List[str] = Field(description="主要洞察")
    final_recommendations: List[str] = Field(description="最終推奨事項")

# 並列処理用エージェント
technical_analyst = RefinireAgent(
    name="technical_analyst",
    generation_instructions="技術的側面から分析してください",
    routing_instruction="分析完了後は'integrate'を選択",
    output_model=AnalysisResult,
    routing_mode="accurate_routing"
)

business_analyst = RefinireAgent(
    name="business_analyst", 
    generation_instructions="ビジネス視点から分析してください",
    routing_instruction="分析完了後は'integrate'を選択",
    output_model=AnalysisResult,
    routing_mode="accurate_routing"
)

user_analyst = RefinireAgent(
    name="user_analyst",
    generation_instructions="ユーザー体験の観点から分析してください", 
    routing_instruction="分析完了後は'integrate'を選択",
    output_model=AnalysisResult,
    routing_mode="accurate_routing"
)

# 統合処理エージェント
integrator_agent = RefinireAgent(
    name="integrator",
    generation_instructions="各分析結果を統合し、包括的なレポートを作成してください",
    routing_instruction="統合完了後は'finalize'を選択",
    output_model=IntegratedReport,
    routing_mode="accurate_routing"
)

# レビュー・最終化エージェント
finalizer_agent = RefinireAgent(
    name="finalizer",
    generation_instructions="統合レポートを最終レビューし、必要に応じて調整してください",
    routing_instruction="最終化完了後は'complete'を選択",
    output_model=IntegratedReport,
    routing_mode="fast_routing"
)

# 並列処理と統合フローの定義
analysis_flow = Flow({
    "start": {
        "parallel": [
            ("technical", technical_analyst),
            ("business", business_analyst), 
            ("user", user_analyst)
        ]
    },
    "integrate": integrator_agent,
    "finalize": finalizer_agent,
    "complete": "end"
})

# 実行
context = Context()
context.shared_state["target_system"] = "新しいEコマースプラットフォーム"

result = analysis_flow.run("start", context)
print(f"統合要約: {result.summary}")
print(f"主要洞察: {result.key_insights}")
print(f"最終推奨事項: {result.final_recommendations}")
```

### 実行時のルーティング情報アクセス

```python
# フロー実行中にルーティング情報にアクセス
def custom_flow_handler(step_name: str, result: Any, context: Context):
    """カスタムフローハンドラー"""
    if hasattr(result, 'next_route'):
        print(f"ステップ '{step_name}' の次のルート: {result.next_route}")
        print(f"信頼度: {result.confidence}")
        print(f"理由: {result.reasoning}")
        
        # ルーティング情報をコンテキストに保存
        context.shared_state[f"{step_name}_routing"] = {
            "next_route": result.next_route,
            "confidence": result.confidence,
            "reasoning": result.reasoning
        }
        
        # 信頼度が低い場合の処理
        if result.confidence < 0.7:
            print(f"警告: {step_name} の信頼度が低いです ({result.confidence})")
    
    return result

# フローにハンドラーを設定
quality_flow.add_step_handler(custom_flow_handler)

# 実行
result = quality_flow.run("start", context)

# 保存されたルーティング情報を確認
for key, value in context.shared_state.items():
    if key.endswith("_routing"):
        print(f"{key}: {value}")
```

### 条件分岐とループ処理

```python
from refinire.agents.flow import Flow, ConditionStep
from refinire.agents.pipeline import RefinireAgent
from refinire.core.context import Context
from pydantic import BaseModel, Field

class IterativeResult(BaseModel):
    """反復処理結果"""
    current_result: str = Field(description="現在の結果")
    iteration_count: int = Field(description="反復回数")
    is_satisfactory: bool = Field(description="満足できる結果か")

def check_completion(context: Context) -> str:
    """完了チェック条件"""
    result = context.shared_state.get("latest_result")
    if result and hasattr(result, 'is_satisfactory'):
        if result.is_satisfactory or result.iteration_count >= 3:
            return "complete"
    return "iterate"

# 反復処理エージェント
iterative_agent = RefinireAgent(
    name="iterative_processor",
    generation_instructions="結果を改善してください。反復回数も記録してください",
    routing_instruction="結果が満足できるなら'check_completion'、さらに改善が必要なら'check_completion'を選択",
    output_model=IterativeResult,
    routing_mode="accurate_routing"
)

# 条件分岐を含むフロー
iterative_flow = Flow({
    "start": iterative_agent,
    "check_completion": ConditionStep("completion_check", check_completion, "complete", "iterate"),
    "iterate": iterative_agent,
    "complete": "end"
})

# 実行
context = Context()
context.shared_state["target_quality"] = "プロフェッショナルレベル"

result = iterative_flow.run("start", context)
print(f"最終結果: {result.current_result}")
print(f"反復回数: {result.iteration_count}")
print(f"満足度: {result.is_satisfactory}")
```

## 新しいルーティング手法の利点

### 1. **精度向上**
- `accurate_routing`モードにより、生成とルーティングの分離
- 専用エージェントによる客観的な判断
- 生成精度への影響を最小化

### 2. **開発効率**
- シンプルな`routing_instruction`で複雑な分岐を実現
- 型安全性による実行時エラーの防止
- 統一されたインターフェースによる保守性向上

### 3. **柔軟性**
- ユーザー定義の`output_model`に完全対応
- 並列処理、条件分岐、ループ処理の組み合わせ
- 実行時のルーティング情報へのアクセス

### 4. **監視・デバッグ**
- 各ステップのルーティング情報を記録
- 信頼度に基づく品質監視
- フローの実行パスを完全に追跡可能


