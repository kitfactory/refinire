# RefinireAgent Result and Context Implementation

## Overview / 概要

This document describes the implementation details of result handling and Context objects in RefinireAgent.

このドキュメントでは、RefinireAgentでの結果処理とContextオブジェクトの実装詳細について説明します。

## Result Access Pattern / 結果アクセスパターン

### Official Specification / 公式仕様

**RefinireAgent returns Context objects with results accessible via `.content` property**

RefinireAgentは、`.content`プロパティ経由で結果にアクセス可能なContextオブジェクトを返します。

```python
from refinire import RefinireAgent

agent = RefinireAgent(
    name="example_agent",
    generation_instructions="You are a helpful assistant.",
    model="gpt-4o-mini"
)

# Correct usage pattern / 正しい使用パターン
result = agent.run("What is AI?")
print(result.content)    # ✅ Correct
print(result.success)    # ✅ Correct  
print(result.metadata)   # ✅ Correct
```

### Return Type Structure / 返り値タイプ構造

```python
# RefinireAgent.run() returns:
result: Context
├── content: Any          # Generated content only (recommended for users)
├── result: LLMResult     # Complete LLM API response object (recommended for advanced usage)
├── success: bool         # Operation success status
├── metadata: Dict        # Evaluation and execution metadata
├── messages: List        # Conversation history
└── shared_state: Dict    # Shared workflow state
```

## Context Class Implementation / Contextクラス実装

### Core Properties / コアプロパティ

```python
class Context(BaseModel):
    # Core state / コア状態
    last_user_input: Optional[str] = None
    messages: List[Message] = Field(default_factory=list)
    result: LLMResult = None  # Complete LLM API response object / 完全なLLM API応答オブジェクト
    evaluation_result: Optional[Dict[str, Any]] = None
    routing_result: Optional[Dict[str, Any]] = None  # Flow routing control / フロールーティング制御
    
    # Note: Deprecated fields removed for simplification:
    # 注意: 簡素化のため廃止されたフィールドを削除:
    # - knowledge: Use shared_state["knowledge"] instead
    # - prev_outputs: Agent results automatically stored in shared_state["agent_name_result"]
    # - artifacts: Use shared_state["artifacts"] instead  
    # - next_label: Use routing_result["next_route"] instead
    
    # Flow control / フロー制御
    current_step: Optional[str] = None
    
    # Shared state for all workflow data / ワークフロー全データの共有状態
    shared_state: Dict[str, Any] = Field(default_factory=dict)
```

### Compatibility Properties / 互換性プロパティ

For backward compatibility with existing documentation and examples, Context provides these properties:

既存のドキュメントや例との後方互換性のため、Contextは以下のプロパティを提供します：

**Deprecated field compatibility / 廃止フィールドの互換性:**
```python
@property
def artifacts(self) -> Dict[str, Any]:
    """Access artifacts via shared_state (backward compatibility)"""
    return self.shared_state.get("artifacts", {})

@artifacts.setter
def artifacts(self, value: Dict[str, Any]) -> None:
    """Store artifacts in shared_state"""
    self.shared_state["artifacts"] = value

@property
def next_label(self) -> Optional[str]:
    """Access next_label via routing_result (backward compatibility)"""
    if self.routing_result:
        return self.routing_result.get('next_route')
    return None

@next_label.setter
def next_label(self, value: Optional[str]) -> None:
    """Store next_label in routing_result"""
    if not self.routing_result:
        self.routing_result = {}
    self.routing_result['next_route'] = value
```

**Main API properties / メインAPIプロパティ:**

```python
@property
def content(self) -> Any:
    """
    Access to generated content only (recommended for most users)
    生成されたコンテンツのみにアクセス（一般ユーザー推奨）
    
    Returns the actual generated content from LLMResult.content
    LLMResult.contentから実際の生成コンテンツを返す
    """
    return self.result.content if self.result else None

@content.setter
def content(self, value: Any) -> None:
    """
    Setter for content property - updates LLMResult.content
    contentプロパティのセッター - LLMResult.contentを更新
    """
    if self.result:
        self.result.content = value
    else:
        # Create minimal LLMResult if none exists
        from refinire.agents.pipeline.llm_pipeline import LLMResult
        self.result = LLMResult(content=value, success=True)

@property
def success(self) -> bool:
    """
    Indicates if the operation was successful
    操作が成功したかを示す
    
    Success is True when:
    - Result is not None
    - If evaluation_result exists, evaluation passed
    - No error indicators are present
    """
    # Basic check: must have a result
    if self.result is None:
        return False
    
    # Check evaluation result if available
    if self.evaluation_result:
        if not self.evaluation_result.get('passed', True):
            return False
    
    # Check for error indicators in shared state
    if 'error' in self.shared_state:
        return False
        
    # Check routing result for error conditions
    if self.routing_result:
        if self.routing_result.get('next_route') == 'error':
            return False
    
    return True

@property
def metadata(self) -> Dict[str, Any]:
    """
    Metadata information (returns evaluation_result or empty dict)
    メタデータ情報（evaluation_resultまたは空辞書を返す）
    """
    return self.evaluation_result or {}

### Routing Control Properties / ルーティング制御プロパティ

The `routing_result` property provides flow control information for multi-step workflows:

`routing_result`プロパティは、マルチステップワークフローのフロー制御情報を提供します：

```python
# routing_result structure / routing_result構造
routing_result: Optional[Dict[str, Any]] = {
    "next_route": str,          # Next step/agent to execute / 次に実行するステップ/エージェント
    "confidence": float,        # Routing confidence (0.0-1.0) / ルーティング信頼度
    "reasoning": str,           # Routing decision reason / ルーティング判断理由
    "needs_user_input": bool,   # Whether user input is required / ユーザー入力が必要かどうか
    "prompt": str,              # User input prompt / ユーザー入力プロンプト
    "step_name": str            # Current step name / 現在のステップ名
}

# Usage in Flow control / フロー制御での使用
def check_next_step(context: Context) -> str:
    if context.routing_result:
        return context.routing_result.get('next_route', 'end')
    return 'end'
```
```

## Internal Implementation / 内部実装

### RefinireAgent Result Processing / RefinireAgent結果処理

```python
# In RefinireAgent._run_standalone method:
# RefinireAgent._run_standaloneメソッド内：

# LLM execution and result storage
# LLM実行と結果保存
llm_result = await self._execute_llm(input_text, ctx)

if llm_result.success:
    # Store complete LLM result in Context
    # 完全なLLM結果をContextに保存
    ctx.result = llm_result  # Complete LLMResult object
    
    # Store generated content in shared_state for workflow access
    # ワークフローアクセス用にshared_stateに生成コンテンツを保存
    ctx.shared_state[self.store_result_key] = ctx.content  # Custom key storage
    ctx.shared_state[f"{self.name}_result"] = ctx.content  # Agent name-based storage
else:
    ctx.result = llm_result  # Store failed result for debugging
```

### LLMResult vs Context / LLMResult対Context

**LLMResult (Internal):**
```python
@dataclass
class LLMResult:
    content: Any      # Generated content
    success: bool     # Execution success
    metadata: Dict    # Execution metadata
    evaluation_score: Optional[float]
    attempts: int
```

**Context (Public API):**
```python
class Context(BaseModel):
    result: LLMResult    # Complete LLM API response object
    # ... other fields
    
    @property
    def content(self) -> Any:  # Generated content only
        return self.result.content if self.result else None
```

## Migration Notes / 移行注意事項

### From Legacy Patterns / 従来パターンからの移行

```python
# ❌ Legacy incorrect pattern (removed)
# 従来の間違ったパターン（削除済み）
# result.result  # This pattern has been eliminated

# ✅ Current correct pattern
# 現在の正しいパターン
result.content  # Use this for RefinireAgent results
```

### Context vs Flow Results / Context対Flow結果

```python
# RefinireAgent returns Context
# RefinireAgentはContextを返す
agent_result = agent.run("input")
content = agent_result.content        # ✅ Generated content only (recommended)
full_result = agent_result.result     # ✅ Complete LLM response (advanced usage)

# Flow also returns Context
# FlowもContextを返す
flow_result = flow.run("input")
content = flow_result.content         # ✅ Generated content (recommended)
full_result = flow_result.result      # ✅ Complete LLM response (advanced usage)
```

## Error Handling / エラーハンドリング

### Success Status Evaluation / 成功ステータス評価

The `success` property performs comprehensive checks:

`success`プロパティは包括的なチェックを実行します：

1. **Result Existence**: `result is not None`
2. **Evaluation Status**: If evaluation enabled, must pass threshold
3. **Error Indicators**: No errors in shared_state
4. **Routing Status**: No error routing conditions

### Failure Scenarios / 失敗シナリオ

```python
result = agent.run("input")

if not result.success:
    # Check failure reasons
    # 失敗理由をチェック
    if result.content is None:
        print("No result generated")
    elif 'error' in result.shared_state:
        print(f"Error: {result.shared_state['error']}")
    elif result.evaluation_result and not result.evaluation_result.get('passed'):
        print(f"Evaluation failed: {result.evaluation_result}")
```

## Best Practices / ベストプラクティス

### Recommended Usage Patterns / 推奨使用パターン

```python
# 1. Basic result access / 基本的な結果アクセス
result = agent.run("input")
if result.success:
    print(result.content)  # Generated content only

# 2. Advanced usage with full LLM response / 完全なLLM応答での高度な使用
result = agent.run("input")
if result.success:
    llm_result = result.result  # Complete LLMResult object
    print(f"Content: {llm_result.content}")
    print(f"Metadata: {llm_result.metadata}")
    print(f"Attempts: {llm_result.attempts}")

# 3. With error handling / エラーハンドリング付き
result = agent.run("input")
if result.success:
    process_content(result.content)
else:
    handle_error(result.metadata)

# 4. Structured output / 構造化出力
from pydantic import BaseModel

class Response(BaseModel):
    answer: str
    confidence: float

agent = RefinireAgent(
    name="structured_agent",
    generation_instructions="Provide structured responses",
    output_model=Response
)

result = agent.run("What is AI?")
if result.success:
    typed_response: Response = result.content  # Structured content
    print(f"Answer: {typed_response.answer}")
    print(f"Confidence: {typed_response.confidence}")
    
    # Access full LLM response for debugging
    full_result = result.result
    print(f"Model used: {full_result.metadata.get('model')}")
```

### Testing Patterns / テストパターン

```python
def test_agent_execution():
    agent = RefinireAgent(...)
    result = agent.run("test input")
    
    # Test result structure
    # 結果構造をテスト
    assert isinstance(result, Context)
    assert hasattr(result, 'content')
    assert hasattr(result, 'success')
    assert hasattr(result, 'metadata')
    
    # Test success case
    # 成功ケースをテスト
    if result.success:
        assert result.content is not None
        assert isinstance(result.content, (str, dict, list))
```

## Implementation History / 実装履歴

### Changes Made / 実施された変更

1. **Eliminated `result.result` pattern** - Removed all instances of incorrect double-result access
   **`result.result`パターンを排除** - 不正な二重結果アクセスのすべてのインスタンスを削除

2. **Unified on `result.content`** - Standardized all documentation and examples to use `.content`
   **`result.content`で統一** - すべてのドキュメントと例で`.content`使用に標準化

3. **Added compatibility properties** - Added `.content`, `.success`, `.metadata` properties to Context
   **互換性プロパティを追加** - Contextに`.content`、`.success`、`.metadata`プロパティを追加

4. **Enhanced success logic** - Improved success determination with evaluation and error checking
   **成功ロジックを強化** - 評価とエラーチェックによる成功判定を改善

### Files Modified / 修正されたファイル

- **Source Code**: 21 files updated for `result.result` → `result.content`
- **Documentation**: 11 files updated 
- **Examples**: 6 files updated
- **Tests**: 8 files updated
- **Total**: 46+ files modified for consistency

**ソースコード**: 21ファイル、**ドキュメント**: 11ファイル、**例**: 6ファイル、**テスト**: 8ファイル
**合計**: 一貫性のため46+ファイルを修正

## Conclusion / 結論

The RefinireAgent result system now provides a clear, hierarchical API where:

RefinireAgentの結果システムは、以下の明確で階層的なAPIを提供します：

- **Clear separation**: `result.content` for generated content, `result.result` for complete LLM response
- **User-friendly access**: Most users only need `.content` for everyday usage
- **Advanced debugging**: Developers can access complete LLM response via `.result`
- **Type safety**: Context objects with well-defined properties and clear data hierarchy
- **Enhanced error handling**: Comprehensive success status evaluation

**明確な分離**: 生成コンテンツは`result.content`、完全なLLM応答は`result.result`
**ユーザーフレンドリーアクセス**: 日常使用では多くのユーザーは`.content`のみで十分
**高度なデバッグ**: 開発者は`.result`経由で完全なLLM応答にアクセス可能
**型安全性**: 明確に定義されたプロパティと明確なデータ階層を持つContextオブジェクト
**強化されたエラーハンドリング**: 包括的な成功ステータス評価