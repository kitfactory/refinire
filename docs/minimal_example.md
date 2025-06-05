# 最小使用例

このページでは、agents-sdk-modelsの最も基本的な使用方法を紹介します。

## 基本的な使用方法

```python
--8<-- "examples/minimal/minimal_example.py"
```

## 実行方法

### 1. 環境変数の設定

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 2. 実行

```bash
python examples/minimal/minimal_example.py
```

## 主な機能

### シンプルなテキスト生成

```python
from agents_sdk_models import Pipeline, LLM

llm = LLM(provider="openai", model="gpt-4o-mini")
pipeline = Pipeline()
result = pipeline.run("Hello, world!", llm=llm)
print(result.result)
```

### コンテキスト変数を使用した生成

```python
from agents_sdk_models import Pipeline, LLM, Context

llm = LLM(provider="openai", model="gpt-4o-mini")
pipeline = Pipeline()
context = Context()

context.add_variable("user_name", "Alice")
result = pipeline.run("Hello {user_name}!", llm=llm, context=context)
print(result.result)  # "Hello Alice! ..."
```

## Doctest の例

このライブラリでは、コード例としてdoctestを広く活用しています。以下のように、関数のdocstringに実行可能な例を含めています：

```python
def simple_generation(prompt: str, api_key: Optional[str] = None) -> str:
    """
    Perform simple text generation
    
    Examples:
        >>> result = simple_generation("Say hello")  # doctest: +SKIP
        >>> isinstance(result, str)  # doctest: +SKIP
        True
    """
    # ... implementation
```

`# doctest: +SKIP` を使用することで、APIキーが必要なテストを実際のCI実行時にスキップしています。

## 次のステップ

- [APIリファレンス](api_reference.md)で詳細な機能を確認
- [チュートリアル](tutorials/quickstart.md)で応用的な使用方法を学習 