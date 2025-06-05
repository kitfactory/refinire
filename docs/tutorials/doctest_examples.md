# Doctest の例

このページでは、agents-sdk-modelsで使用されているdoctestの例を紹介します。

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

### 2. 型チェックの例

```python
def create_basic_llm() -> LLM:
    """
    Create a basic LLM instance
    基本的なLLMインスタンスを作成します
    
    Returns:
        LLM: Configured LLM instance
        LLM: 設定されたLLMインスタンス
    
    Examples:
        >>> llm = create_basic_llm()
        >>> isinstance(llm, LLM)
        True
        >>> llm.provider
        'openai'
        >>> llm.model
        'gpt-4o-mini'
    """
    return LLM(provider="openai", model="gpt-4o-mini")
```

### 3. 例外処理の例

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
def generate_text(prompt: str) -> str:
    """
    Generate text using OpenAI API
    OpenAI APIを使用してテキストを生成します
    
    Args:
        prompt: Input prompt / 入力プロンプト
    
    Returns:
        Generated text response / 生成されたテキストレスポンス
    
    Examples:
        >>> result = generate_text("Hello")  # doctest: +SKIP
        >>> isinstance(result, str)  # doctest: +SKIP
        True
        >>> len(result) > 0  # doctest: +SKIP
        True
    """
    # Implementation that calls OpenAI API
    pass
```

## Doctestの実行方法

### 1. 単一ファイルの実行

```bash
python -m doctest -v your_module.py
```

### 2. 複数ファイルの実行

```bash
python -m doctest -v src/agents_sdk_models/*.py
```

### 3. Pytestでの実行

```bash
pytest --doctest-modules src/agents_sdk_models/
```

## Doctestのオプション

### よく使用されるオプション

- `# doctest: +SKIP` - テストをスキップ
- `# doctest: +ELLIPSIS` - `...`で部分的なマッチを許可
- `# doctest: +IGNORE_EXCEPTION_DETAIL` - 例外の詳細を無視
- `# doctest: +NORMALIZE_WHITESPACE` - 空白文字の正規化

### 実用的な例

```python
def process_data(data: list) -> dict:
    """
    Process input data and return summary
    入力データを処理して要約を返します
    
    Args:
        data: List of data items / データ項目のリスト
    
    Returns:
        Summary dictionary / 要約辞書
    
    Examples:
        >>> data = [1, 2, 3, 4, 5]
        >>> result = process_data(data)
        >>> result['count']
        5
        >>> result['sum']
        15
        >>> result['average']  # doctest: +ELLIPSIS
        3.0
        
        空のリストの場合:
        >>> process_data([])
        {'count': 0, 'sum': 0, 'average': 0}
        
        文字列データの場合:
        >>> process_data(['a', 'b', 'c'])  # doctest: +ELLIPSIS
        {'count': 3, 'sum': 0, 'average': 0, 'items': [...]}
    """
    if not data:
        return {'count': 0, 'sum': 0, 'average': 0}
    
    numeric_data = [x for x in data if isinstance(x, (int, float))]
    count = len(data)
    total = sum(numeric_data)
    average = total / len(numeric_data) if numeric_data else 0
    
    result = {
        'count': count,
        'sum': total,
        'average': average
    }
    
    if not all(isinstance(x, (int, float)) for x in data):
        result['items'] = data
    
    return result
```

## CIでの実行

GitHub Actionsでdoctestを自動実行する設定：

```yaml
- name: Run doctests
  run: |
    # Run doctests for all Python files in src/
    uv run python -m doctest -v src/agents_sdk_models/*.py
    
    # Run doctests for minimal example
    uv run python -m doctest -v examples/minimal/minimal_example.py
    
    # Run doctests using pytest
    uv run pytest --doctest-modules src/agents_sdk_models/
```

## ベストプラクティス

1. **実行可能な例を提供** - 実際に動作するコードを書く
2. **エラーケースも含める** - 正常系だけでなく異常系もテスト
3. **型チェックを活用** - `isinstance()`でオブジェクトの型を確認
4. **API呼び出しはスキップ** - 外部APIを使用する場合は`+SKIP`を使用
5. **日本語コメントを併記** - 英語と日本語両方でドキュメント化

これらの例を参考に、あなたのコードにもdoctestを追加してみてください！ 