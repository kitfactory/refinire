# Doctest の例

このページでは、Refinireで使用されているdoctestの例を紹介します。

## Doctestとは

Doctestは、Pythonのdocstring内に記述されたインタラクティブなPythonセッションの例をテストとして実行する機能です。

## 基本的な使用方法

### 1. シンプルな例

```python
def add(a: int, b: int) -> int:
    """
    Add two numbers
    二つの数を足し算します
    
    Args:
        a: First number / 最初の数
        b: Second number / 二番目の数
    
    Returns:
        Sum of a and b / aとbの合計
    
    Examples:
        >>> add(2, 3)
        5
        >>> add(-1, 1)
        0
    """
    return a + b
```

### 2. RefinireAgent の例

```python
def create_basic_agent():
    """
    Create a basic RefinireAgent instance
    基本的なRefinireAgentインスタンスを作成します
    
    Returns:
        RefinireAgent: Configured agent instance
        RefinireAgent: 設定されたエージェントインスタンス
    
    Examples:
        >>> from refinire import RefinireAgent
        >>> agent = RefinireAgent(
        ...     name="test_agent",
        ...     generation_instructions="You are a helpful assistant.",
        ...     model="gpt-4o-mini"
        ... )
        >>> agent.name
        'test_agent'
        >>> agent.model
        'gpt-4o-mini'
        >>> isinstance(agent, RefinireAgent)
        True
    """
    from refinire import RefinireAgent
    return RefinireAgent(
        name="test_agent",
        generation_instructions="You are a helpful assistant.",
        model="gpt-4o-mini"
    )
```

### 3. ツール統合の例

```python
def create_tool_enabled_agent():
    """
    Create an agent with tool integration
    ツール統合付きエージェントを作成します
    
    Returns:
        RefinireAgent: Agent with tools / ツール付きエージェント
    
    Examples:
        >>> from refinire import RefinireAgent, tool
        >>> @tool
        ... def sample_tool(text: str) -> str:
        ...     return f"Processed: {text}"
        >>> agent = RefinireAgent(
        ...     name="tool_agent",
        ...     generation_instructions="Use tools to help users.",
        ...     tools=[sample_tool],
        ...     model="gpt-4o-mini"
        ... )
        >>> len(agent.tools) > 0
        True
        >>> agent.list_tools()
        ['sample_tool']
    """
    pass
```

### 4. 例外処理の例

```python
def safe_divide(a: float, b: float) -> float:
    """
    Safely divide two numbers
    安全に二つの数を割り算します
    
    Args:
        a: Dividend / 被除数
        b: Divisor / 除数
    
    Returns:
        Result of a / b / a ÷ b の結果
    
    Raises:
        ValueError: When b is zero / bが0の場合
    
    Examples:
        >>> safe_divide(10, 2)
        5.0
        >>> safe_divide(7, 3)  # doctest: +ELLIPSIS
        2.333...
        >>> safe_divide(1, 0)  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
            ...
        ValueError: Cannot divide by zero
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

## API呼び出しを含む例

APIキーが必要な場合は、`# doctest: +SKIP`を使用します：

```python
def test_agent_execution():
    """
    Test agent execution with API calls
    API呼び出しを含むエージェント実行のテスト
    
    Returns:
        Result from agent execution / エージェント実行結果
    
    Examples:
        >>> from refinire import RefinireAgent
        >>> agent = RefinireAgent(
        ...     name="test_agent",
        ...     generation_instructions="You are a helpful assistant.",
        ...     model="gpt-4o-mini"
        ... )
        >>> result = agent.run("Hello")  # doctest: +SKIP
        >>> hasattr(result, 'content')  # doctest: +SKIP
        True
        >>> isinstance(result.content, str)  # doctest: +SKIP
        True
    """
    pass
```

## Context の使用例

```python
def context_usage_example():
    """
    Demonstrate Context usage patterns
    Contextの使用パターンを示します
    
    Examples:
        >>> from refinire import Context
        >>> ctx = Context()
        >>> ctx.shared_state = {"key": "value"}
        >>> ctx.shared_state["key"]
        'value'
        >>> ctx.result = "test result"
        >>> ctx.result
        'test result'
        >>> len(ctx.messages)
        0
    """
    pass
```

## Flow の基本例

```python
def flow_basic_example():
    """
    Basic Flow usage example
    基本的なFlowの使用例
    
    Examples:
        >>> from refinire import Flow, RefinireAgent
        >>> agent = RefinireAgent(
        ...     name="test_agent",
        ...     generation_instructions="Respond helpfully.",
        ...     model="gpt-4o-mini"
        ... )
        >>> flow = Flow(start="agent", steps={"agent": agent})
        >>> flow.start_step
        'agent'
        >>> "agent" in flow.steps
        True
    """
    pass
```

## Doctestの実行方法

### 1. 単一ファイルの実行

```bash
python -m doctest -v your_module.py
```

### 2. 複数ファイルの実行

```bash
python -m doctest -v src/refinire/*.py
```

### 3. Pytestでの実行

```bash
pytest --doctest-modules src/refinire/
```

## Doctestのオプション

### よく使用されるオプション

- `# doctest: +SKIP` - テストをスキップ
- `# doctest: +ELLIPSIS` - `...`で部分的なマッチを許可
- `# doctest: +IGNORE_EXCEPTION_DETAIL` - 例外の詳細を無視
- `# doctest: +NORMALIZE_WHITESPACE` - 空白文字の正規化

### 実用的な例

```python
def process_agent_result(result) -> dict:
    """
    Process agent result and return summary
    エージェント結果を処理して要約を返します
    
    Args:
        result: Agent execution result / エージェント実行結果
    
    Returns:
        Summary dictionary / 要約辞書
    
    Examples:
        >>> class MockResult:
        ...     def __init__(self, content, success=True):
        ...         self.content = content
        ...         self.success = success
        ...         self.evaluation_score = 85.0
        ...         self.attempts = 1
        >>> result = MockResult("Hello world")
        >>> summary = process_agent_result(result)
        >>> summary['success']
        True
        >>> summary['content_length']
        11
        >>> summary['quality_score']  # doctest: +ELLIPSIS
        85.0
        
        失敗した場合:
        >>> failed_result = MockResult("", False)
        >>> process_agent_result(failed_result)
        {'success': False, 'content_length': 0, 'quality_score': None}
    """
    if not hasattr(result, 'success') or not result.success:
        return {'success': False, 'content_length': 0, 'quality_score': None}
    
    return {
        'success': result.success,
        'content_length': len(result.content) if hasattr(result, 'content') else 0,
        'quality_score': getattr(result, 'evaluation_score', None)
    }
```

## 変数埋め込みの例

```python
def test_variable_embedding():
    """
    Test variable embedding functionality
    変数埋め込み機能のテスト
    
    Examples:
        >>> from refinire import RefinireAgent, Context
        >>> agent = RefinireAgent(
        ...     name="dynamic_agent",
        ...     generation_instructions="You are a {{role}} assistant.",
        ...     model="gpt-4o-mini"
        ... )
        >>> ctx = Context()
        >>> ctx.shared_state = {"role": "helpful"}
        >>> # Variable substitution happens during execution
        >>> "{{role}}" in agent.generation_instructions
        True
    """
    pass
```

## CIでの実行

GitHub Actionsでdoctestを自動実行する設定：

```yaml
- name: Run doctests
  run: |
    # Run doctests for all Python files in src/
    uv run python -m doctest -v src/refinire/*.py
    
    # Run doctests for examples
    uv run python -m doctest -v examples/*.py
    
    # Run doctests using pytest
    uv run pytest --doctest-modules src/refinire/
```

## ベストプラクティス

1. **実行可能な例を提供** - 実際に動作するコードを書く
2. **エラーケースも含める** - 正常系だけでなく異常系もテスト
3. **型チェックを活用** - `isinstance()`でオブジェクトの型を確認
4. **API呼び出しはスキップ** - 外部APIを使用する場合は`+SKIP`を使用
5. **日本語コメントを併記** - 英語と日本語両方でドキュメント化
6. **モックオブジェクトを活用** - 複雑な依存関係にはモックを使用
7. **簡潔で分かりやすく** - 例は理解しやすく、要点を明確に

これらの例を参考に、あなたのコードにもdoctestを追加してみてください！