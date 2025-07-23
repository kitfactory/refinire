# Refinire Agent Specifications

## 概要

Refinireプロジェクトにおけるエージェント仕様書です。主要な3つのエージェントクラスの設計仕様、インターフェース、実装詳細を定義します。

- **RefinireAgent**: メインの多機能AIエージェント
- **RoutingAgent**: ルーティング判定専用軽量エージェント  
- **EvaluationAgent**: 品質評価専用軽量エージェント

## 1. RefinireAgent 仕様

### 1.1 目的
- 汎用的なAI生成タスクの実行
- オーケストレーションモードによる自動品質改善
- ルーティング機能による動的フロー制御
- 評価機能による品質保証

### 1.2 クラス定義
```python
class RefinireAgent:
    """
    Main AI agent for general-purpose generation tasks
    汎用AI生成タスク用メインエージェント
    
    Features:
    - Multi-provider LLM support (OpenAI, Anthropic, Google, Ollama)
    - Orchestration mode with automatic quality improvement
    - Built-in routing and evaluation capabilities
    - Context providers for conversation history and external data
    - Structured output with Pydantic models
    - Comprehensive tracing and observability
    """
    
    def __init__(
        self,
        name: str,
        generation_instructions: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None,
        
        # Orchestration mode
        orchestration_mode: bool = False,
        evaluation_instructions: Optional[str] = None,
        evaluation_threshold: float = 0.7,
        max_improvement_iterations: int = 3,
        
        # Routing
        routing_instruction: Optional[str] = None,
        
        # Context providers
        context_providers_config: Optional[List[Dict[str, Any]]] = None,
        
        # Structured output
        output_model: Optional[Type[BaseModel]] = None,
        
        # Advanced options
        system_message: Optional[str] = None,
        max_retries: int = 3,
        **kwargs
    ):
        """
        Initialize RefinireAgent
        
        Args:
            name: Agent name for identification and tracing
            generation_instructions: Core instructions for content generation
            model: LLM model identifier
            # provider: Automatically detected from model name patterns and environment variables
            temperature: Generation temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
            timeout: Request timeout in seconds
            
            # Orchestration mode parameters
            orchestration_mode: Enable automatic quality improvement
            evaluation_instructions: Instructions for quality evaluation
            evaluation_threshold: Minimum score for passing evaluation
            max_improvement_iterations: Maximum improvement attempts
            
            # Routing parameters
            routing_instruction: Instructions for next step routing
            
            # Context parameters
            context_providers_config: Configuration for context providers
            
            # Output parameters
            output_model: Pydantic model for structured output
            
            # Advanced parameters
            system_message: Custom system message
            max_retries: Maximum retry attempts for failed requests
        """
```

### 1.3 主要メソッド

#### 1.3.1 run_async メソッド
```python
async def run_async(
    self, 
    input_text: str, 
    context: Optional[Context] = None,
    **kwargs
) -> Context:
    """
    Execute agent asynchronously
    
    Args:
        input_text: Input text for generation
        context: Optional context for conversation history and state
        **kwargs: Additional parameters passed to LLM
        
    Returns:
        Context: Updated context containing generated content, routing/evaluation results, and state
        
    Process:
        1. Initialize or update context
        2. Build prompt with instructions and context providers
        3. Execute LLM generation
        4. Save prompt/generation to context.shared_state
        5. Store LLMResult in context.result
        6. Execute orchestration mode if enabled (store in context.evaluation_result)
        7. Execute routing if configured (store in context.routing_result)
        8. Return updated context
    """
```

#### 1.3.2 run メソッド
```python
def run(
    self, 
    input_text: str, 
    context: Optional[Context] = None,
    **kwargs
) -> Context:
    """Synchronous wrapper for run_async"""
    return asyncio.run(self.run_async(input_text, context, **kwargs))
```

### 1.4 内部メソッド

#### 1.4.1 プロンプト構築
```python
def _build_prompt(
    self, 
    input_text: str, 
    context: Optional[Context] = None,
    include_instructions: bool = True
) -> str:
    """
    Build complete prompt with instructions and context
    
    Template structure:
    ```
    {system_message}
    
    {generation_instructions}
    
    {context_provider_data}
    
    User input: {input_text}
    ```
    """
```

#### 1.4.2 オーケストレーションモード
```python
async def _execute_orchestration_mode(
    self, 
    initial_result: LLMResult, 
    context: Context
) -> LLMResult:
    """
    Execute orchestration mode with evaluation and improvement
    
    Process:
        1. Evaluate initial result using evaluation_instructions
        2. If evaluation passes, return result
        3. If evaluation fails, generate improvement suggestions
        4. Re-generate content with improvement guidance
        5. Repeat up to max_improvement_iterations
        6. Return best result or final attempt
    """
```

#### 1.4.3 shared_state管理
```python
def _save_to_shared_state(self, context: Context, prompt: str, generation: str) -> None:
    """
    Save prompt and generation to context.shared_state
    
    Keys:
        - '_last_prompt': Complete prompt used for generation
        - '_last_generation': Generated content
        
    Note: Does not overwrite if routing/evaluation agents are executing
    """
```

### 1.5 Context Providers

#### 1.5.1 対応プロバイダー
```python
# Conversation history provider
{
    "type": "conversation_history",
    "max_items": 10,
    "include_system": False
}

# Custom data provider
{
    "type": "custom_data",
    "data_source": "external_api",
    "config": {...}
}
```

#### 1.5.2 プロバイダー統合
```python
def _apply_context_providers(
    self, 
    base_prompt: str, 
    context: Optional[Context] = None
) -> str:
    """Apply configured context providers to enhance prompt"""
```

### 1.6 エラーハンドリング
- LLM API呼び出し失敗時のリトライ機能
- Pydantic validation エラーの適切な処理
- Context更新エラーのフォールバック
- タイムアウト処理とグレースフル終了

## 2. RoutingAgent 仕様

### 2.1 目的
- RefinireAgentの生成結果に基づいて次のステップを決定
- Context.shared_state['_last_prompt'] と Context.shared_state['_last_generation'] を活用
- 軽量で高速なルーティング判定に特化

### 2.2 クラス定義
```python
class RoutingAgent:
    """
    Single-purpose routing agent for RefinireAgent workflow routing
    RefinireAgentワークフローのルーティング専用エージェント
    
    Features:
    - Uses Context.shared_state for last_prompt/last_generation access
    - Structured output with RoutingResult
    - Lightweight and fast routing decisions
    - Compatible with RefinireAgent interface
    """
    
    def __init__(
        self,
        name: str,
        routing_instruction: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,  # 低温度でより確実な判定
        max_retries: int = 3,
        timeout: Optional[float] = None,
        **kwargs
    ):
        """
        Initialize RoutingAgent
        
        Args:
            name: Agent name for identification
            routing_instruction: Instructions for routing decision logic
            model: LLM model to use
            temperature: Low temperature for consistent routing
            # provider: Automatically detected from model name patterns and environment variables
            max_retries: Maximum retry attempts
            timeout: Request timeout
        """
```

### 2.3 主要メソッド

#### 2.3.1 run_async メソッド
```python
async def run_async(
    self, 
    input_text: str, 
    context: Context,
    **kwargs
) -> Context:
    """
    Execute routing decision asynchronously
    
    Args:
        input_text: Input text (typically routing instruction)
        context: Context containing shared_state with last_prompt/last_generation
        
    Returns:
        Context: Updated context with routing result stored in context.routing_result
        
    Process:
        1. Extract last_prompt and last_generation from context.shared_state
        2. Build routing prompt with context information
        3. Execute LLM call with structured output (RoutingResult)
        4. Store routing result in context.routing_result
        5. Store LLMResult in context.result
        6. Return updated context
    """
```

#### 2.3.2 run メソッド
```python
def run(self, input_text: str, context: Context, **kwargs) -> Context:
    """Synchronous wrapper for run_async"""
    return asyncio.run(self.run_async(input_text, context, **kwargs))
```

### 2.4 内部メソッド

#### 2.4.1 プロンプト構築
```python
def _build_routing_prompt(self, context: Context, input_text: str) -> str:
    """
    Build routing prompt using context shared_state
    
    Template:
    ```
    直前の生成プロセスを分析し、ルーティング判断を行ってください。
    
    === 直前の生成プロンプト ===
    {context.shared_state.get('_last_prompt', 'N/A')}
    
    === 直前の生成結果 ===
    {context.shared_state.get('_last_generation', 'N/A')}
    
    === ルーティング指示 ===
    {self.routing_instruction}
    
    上記の情報に基づいて、適切なルーティング判断を行い、指定されたJSON形式で出力してください。
    ```
    """
```

### 2.5 出力形式
- **構造化出力**: RoutingResult Pydanticモデル
- **値制限**: next_route は指定された選択肢のみ
- **信頼度**: confidence フィールドで判定の確実性を示す

### 2.6 エラーハンドリング
- LLM呼び出し失敗時のリトライ機能
- 不正なルーティング結果の検出と修正
- Context更新エラーの適切な処理

## 3. EvaluationAgent 仕様

### 3.1 目的
- RefinireAgentの生成結果の品質評価
- Context.shared_state を活用した効率的な評価処理
- 評価基準に基づく合格/不合格判定

### 3.2 クラス定義
```python
class EvaluationAgent:
    """
    Single-purpose evaluation agent for RefinireAgent output quality assessment
    RefinireAgent出力品質評価専用エージェント
    
    Features:
    - Uses Context.shared_state for last_prompt/last_generation access
    - Structured output with EvaluationResult
    - Configurable evaluation criteria and thresholds
    - Compatible with RefinireAgent interface
    """
    
    def __init__(
        self,
        name: str,
        evaluation_instructions: str,
        evaluation_criteria: Optional[Dict[str, Any]] = None,
        pass_threshold: float = 0.7,
        model: str = "gpt-4o-mini",
        temperature: float = 0.2,  # 低温度で一貫した評価
        max_retries: int = 3,
        timeout: Optional[float] = None,
        **kwargs
    ):
        """
        Initialize EvaluationAgent
        
        Args:
            name: Agent name for identification
            evaluation_instructions: Instructions for evaluation logic
            evaluation_criteria: Specific criteria for evaluation
            pass_threshold: Minimum score for passing evaluation
            model: LLM model to use
            temperature: Low temperature for consistent evaluation
            # provider: Automatically detected from model name patterns and environment variables
            max_retries: Maximum retry attempts
            timeout: Request timeout
        """
```

### 3.3 主要メソッド

#### 3.3.1 run_async メソッド
```python
async def run_async(
    self, 
    input_text: str, 
    context: Context,
    **kwargs
) -> Context:
    """
    Execute evaluation asynchronously
    
    Args:
        input_text: Input text (typically evaluation instruction)
        context: Context containing shared_state with last_prompt/last_generation
        
    Returns:
        Context: Updated context with evaluation result stored in context.evaluation_result
        
    Process:
        1. Extract last_prompt and last_generation from context.shared_state
        2. Build evaluation prompt with context and criteria
        3. Execute LLM call with structured output (EvaluationResult)
        4. Apply pass_threshold to determine pass/fail
        5. Store evaluation result in context.evaluation_result
        6. Store LLMResult in context.result
        7. Return updated context
    """
```

#### 3.3.2 run メソッド
```python
def run(self, input_text: str, context: Context, **kwargs) -> Context:
    """Synchronous wrapper for run_async"""
    return asyncio.run(self.run_async(input_text, context, **kwargs))
```

### 3.4 内部メソッド

#### 3.4.1 プロンプト構築
```python
def _build_evaluation_prompt(self, context: Context, input_text: str) -> str:
    """
    Build evaluation prompt using context shared_state
    
    Template:
    ```
    直前の生成プロセスを評価してください。
    
    === 元のプロンプト ===
    {context.shared_state.get('_last_prompt', 'N/A')}
    
    === 生成結果 ===
    {context.shared_state.get('_last_generation', 'N/A')}
    
    === 評価指示 ===
    {self.evaluation_instructions}
    
    === 評価基準 ===
    {self._format_evaluation_criteria()}
    
    上記の内容を評価し、指定されたJSON形式で評価結果を出力してください。
    ```
    """
```

#### 3.4.2 評価基準フォーマット
```python
def _format_evaluation_criteria(self) -> str:
    """Format evaluation criteria for prompt inclusion"""
    if not self.evaluation_criteria:
        return "一般的な品質基準（正確性、関連性、完全性）で評価してください。"
    
    criteria_text = []
    for criterion, details in self.evaluation_criteria.items():
        criteria_text.append(f"- {criterion}: {details}")
    
    return "\n".join(criteria_text)
```

### 3.5 出力形式
- **構造化出力**: EvaluationResult Pydanticモデル
- **評価スコア**: 0.0-1.0 の数値スコア
- **合格判定**: pass_threshold との比較による boolean
- **詳細フィードバック**: 改善点や評価理由

## 4. 共通データモデル

### 4.1 Context拡張仕様

エージェント専用の結果格納フィールドを追加します：

```python
class Context(BaseModel):
    """Extended Context with agent-specific result fields"""
    
    # 既存フィールド（省略）
    # ...
    
    # Agent-specific results / エージェント専用結果フィールド
    routing_result: Optional[Dict[str, Any]] = None  # RoutingAgent実行結果
    evaluation_result: Optional[Dict[str, Any]] = None  # EvaluationAgent実行結果
```

### 4.2 LLMResult
```python
class LLMResult(BaseModel):
    """Common result structure for all agents"""
    content: Any = Field(description="Generated content or structured output")
    success: bool = Field(description="Whether the operation succeeded")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution metadata")
    evaluation_score: Optional[float] = Field(default=None, description="Quality evaluation score")
    attempts: int = Field(default=1, description="Number of attempts made")
```

### 4.2 RoutingResult
```python
class RoutingResult(BaseModel):
    """Routing decision result structure"""
    content: str = Field(description="Generated content (copied from generation)")
    next_route: str = Field(description="Next route to execute")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in routing decision")
    reasoning: str = Field(description="Reasoning for the routing decision")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional routing metadata")
```

### 4.3 EvaluationResult
```python
class EvaluationResult(BaseModel):
    """Evaluation result structure"""
    content: str = Field(description="Generated content (copied from generation)")
    score: float = Field(ge=0.0, le=1.0, description="Overall evaluation score")
    passed: bool = Field(description="Whether evaluation passed threshold")
    criteria_scores: Dict[str, float] = Field(default_factory=dict, description="Individual criteria scores")
    feedback: str = Field(description="Detailed evaluation feedback")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional evaluation metadata")
```

## 5. Agent統合パターン

### 5.1 RefinireAgent内でのRouting/Evaluation統合
```python
class RefinireAgent:
    def __init__(self, ...):
        # 専用エージェント初期化
        if self.routing_instruction:
            self._routing_agent = RoutingAgent(
                name=f"{self.name}_router",
                routing_instruction=self.routing_instruction,
                model=self.model,
                temperature=0.1
            )
        
        if self.evaluation_instructions:
            self._evaluation_agent = EvaluationAgent(
                name=f"{self.name}_evaluator", 
                evaluation_instructions=self.evaluation_instructions,
                pass_threshold=self.evaluation_threshold,
                model=self.model,
                temperature=0.2
            )
    
    async def _execute_routing(self, context: Context) -> Optional[RoutingResult]:
        """Execute routing using dedicated RoutingAgent"""
        if self._routing_agent:
            updated_context = await self._routing_agent.run_async("", context)
            return updated_context.routing_result
        return None
    
    async def _execute_evaluation(self, context: Context) -> Optional[EvaluationResult]:
        """Execute evaluation using dedicated EvaluationAgent"""
        if self._evaluation_agent:
            updated_context = await self._evaluation_agent.run_async("", context)
            return updated_context.evaluation_result
        return None
```

### 5.2 Context.shared_state活用パターン
```python
# RefinireAgent: shared_stateに保存
context.shared_state['_last_prompt'] = full_prompt
context.shared_state['_last_generation'] = llm_result.content

# RoutingAgent: shared_stateから読み取り
last_prompt = context.shared_state.get('_last_prompt', 'N/A')
last_generation = context.shared_state.get('_last_generation', 'N/A')

# EvaluationAgent: shared_stateから読み取り（同様）
```

### 5.3 Flow統合パターン
```python
# FlowでのRoutingAgent使用例
class CustomFlow(Flow):
    def __init__(self):
        # RefinireAgentとRoutingAgentを組み合わせ
        main_agent = RefinireAgent(...)
        routing_agent = RoutingAgent(...)
        
        super().__init__(
            steps={
                "main": main_agent,
                "routing": routing_agent,
                "next_step": ...
            }
        )
```

## 6. 自動プロバイダー検出の詳細

### 6.1 検出優先順位

`get_llm()`関数は以下の優先順位でプロバイダーを自動検出します：

1. **明示的指定**: `provider`パラメータが指定された場合
2. **モデルID解析**: `"provider:model:tag"`形式の場合（例：`"openai:gpt-4o-mini"`）
3. **環境変数検出**: 以下の環境変数の存在確認
   - `OLLAMA_BASE_URL` → "ollama"
   - `LM_STUDIO_BASE_URL` → "lmstudio"
   - `OPENROUTER_API_KEY` → "openrouter"
   - `GROQ_API_KEY` → "groq" 
   - `ANTHROPIC_API_KEY` → "anthropic"
   - `AZURE_OPENAI_ENDPOINT` → "azure"
4. **モデル名パターン判定**: モデル名の文字列マッチング
   - `"gpt"`, `"o3"`, `"o4"` を含む → "openai"
   - `"gemini"` を含む → "google"
   - `"claude"` を含む → "anthropic"
   - その他 → "ollama" (デフォルト)

### 6.2 実用例

```python
# 以下は全て自動でプロバイダーが検出される
get_llm("gpt-4o-mini")           # → openai
get_llm("claude-3-5-sonnet")     # → anthropic  
get_llm("gemini-2.0-flash")      # → google
get_llm("llama3.2")              # → ollama
get_llm("o3-mini")               # → openai

# 環境変数が設定されている場合は優先される
# ANTHROPIC_API_KEY が設定されていれば "anthropic" が選択される
```

### 6.3 環境変数による設定

```bash
# プロバイダー別API設定
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GROQ_API_KEY="your-groq-key"

# デフォルトモデル設定
export REFINIRE_DEFAULT_LLM_MODEL="claude-3-5-sonnet"

# oneenv namespace設定（環境別）
export ONEENV_NAMESPACE="production"
```

## 7. パフォーマンス特性

### 7.1 RefinireAgent
- **柔軟性**: 多様なタスクに対応可能
- **機能性**: オーケストレーション、ルーティング、評価を統合
- **コスト**: 高機能だが相応のリソース消費

### 7.2 RoutingAgent/EvaluationAgent
- **軽量性**: 単機能に特化した高速処理
- **一貫性**: 低温度設定による安定した判定
- **効率性**: Context.shared_state活用による無駄のない処理

### 7.3 使い分けガイドライン

#### RefinireAgentを選ぶべき場合
- 複雑な生成タスクが必要
- オーケストレーションモードによる品質向上が必要
- Context providersによる外部データ統合が必要
- 構造化出力が必要

#### 専用Agentを選ぶべき場合
- 高速なルーティング判定のみが必要
- シンプルな品質評価のみが必要
- パフォーマンスが最優先
- 既存のContext.shared_stateを活用したい

## 8. 実装優先順位

### Phase 1: RoutingAgent実装
1. 基本クラス構造の実装
2. shared_state活用のプロンプト構築
3. RoutingResult構造化出力
4. RefinireAgentとの統合テスト

### Phase 2: EvaluationAgent実装
1. 基本クラス構造の実装
2. 評価基準の動的設定機能
3. EvaluationResult構造化出力
4. pass_threshold判定ロジック

### Phase 3: 統合とテスト
1. 3つのAgentの協調動作テスト
2. Flow統合での動作確認
3. パフォーマンス測定と最適化
4. ドキュメント整備

この仕様書に基づいて、効率的で保守性の高いAgent生態系を構築することができます。各Agentは独立性を保ちながら、Context.shared_stateを通じて効率的に連携し、Refinireプラットフォーム全体の機能性とパフォーマンスを向上させます。