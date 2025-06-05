# 型チェック

このページでは、agents-sdk-modelsの型チェック機能について説明します。

## 概要

agents-sdk-modelsでは以下の型チェック機能を提供しています：

- **mypy** による厳密な静的型チェック
- **py.typed** による型情報の提供
- **型ヒント** による開発者体験の向上

## 設定

### pyproject.toml の設定

厳密な型チェックが有効になっています：

```toml
[tool.mypy]
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
disallow_subclassing_any = true
disallow_untyped_calls = true
disallow_untyped_decorators = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_any_unimported = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
```

### py.typed ファイル

`src/agents_sdk_models/py.typed` ファイルにより、このパッケージが型情報を提供することを宣言しています。

## 実行方法

### 基本的なチェック

```bash
# 全体のチェック
uv run mypy src/

# 特定のモジュールのチェック
uv run mypy src/agents_sdk_models/pipeline.py

# より詳細な出力
uv run mypy --verbose src/agents_sdk_models/
```

### CIでのチェック

```bash
# GitHub Actionsで実行
uv run mypy src/ --junit-xml=mypy-results.xml
```

## 型ヒントの例

### 基本的な型ヒント

```python
from typing import Optional, List, Dict, Any, Union
from pathlib import Path

def process_prompt(
    prompt: str,
    max_tokens: Optional[int] = None,
    temperature: float = 0.7
) -> str:
    """
    Process a prompt with type hints
    型ヒント付きでプロンプトを処理します
    
    Args:
        prompt: Input prompt
               入力プロンプト
        max_tokens: Maximum number of tokens to generate
                   生成する最大トークン数
        temperature: Sampling temperature
                    サンプリング温度
    
    Returns:
        Processed result
        処理結果
    """
    # Implementation
    return f"Processed: {prompt}"
```

### クラスの型ヒント

```python
from typing import Generic, TypeVar, Protocol
from abc import ABC, abstractmethod

T = TypeVar('T')

class Processor(Protocol):
    """
    Processor protocol defining the interface
    プロセッサープロトコルでインターフェースを定義
    """
    def process(self, data: str) -> str:
        """Process data / データを処理"""
        ...

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers
    LLMプロバイダーの抽象基底クラス
    """
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        **kwargs: Any
    ) -> str:
        """
        Generate text from prompt
        プロンプトからテキストを生成
        
        Args:
            prompt: Input prompt / 入力プロンプト
            **kwargs: Additional parameters / 追加パラメータ
        
        Returns:
            Generated text / 生成されたテキスト
        """
        pass

class OpenAIProvider(LLMProvider):
    """
    OpenAI provider implementation
    OpenAIプロバイダーの実装
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        self.api_key = api_key
        self.model = model
    
    async def generate(
        self,
        prompt: str,
        **kwargs: Any
    ) -> str:
        # Implementation
        return f"Generated response for: {prompt}"
```

### ジェネリクスの使用

```python
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')
R = TypeVar('R')

class Pipeline(Generic[T, R]):
    """
    Generic pipeline class
    ジェネリックパイプラインクラス
    
    Type Parameters:
        T: Input type / 入力型
        R: Output type / 出力型
    """
    
    def __init__(self) -> None:
        self._steps: List[Callable[[T], T]] = []
    
    def add_step(self, step: Callable[[T], T]) -> 'Pipeline[T, R]':
        """
        Add a processing step
        処理ステップを追加
        
        Args:
            step: Processing function / 処理関数
        
        Returns:
            Self for method chaining / メソッドチェーン用の自分自身
        """
        self._steps.append(step)
        return self
    
    def run(self, input_data: T) -> R:
        """
        Run the pipeline
        パイプラインを実行
        
        Args:
            input_data: Input data / 入力データ
        
        Returns:
            Processed result / 処理結果
        """
        result = input_data
        for step in self._steps:
            result = step(result)
        return result  # type: ignore
```

### Union型と Literal型

```python
from typing import Union, Literal, overload
from typing_extensions import TypedDict

Provider = Literal["openai", "anthropic", "gemini", "ollama"]
Model = Union[str, None]

class LLMConfig(TypedDict):
    """
    LLM configuration type
    LLM設定の型
    """
    provider: Provider
    model: str
    api_key: Optional[str]
    temperature: float
    max_tokens: Optional[int]

@overload
def create_llm(provider: Literal["openai"], model: str) -> OpenAIProvider:
    ...

@overload  
def create_llm(provider: Literal["anthropic"], model: str) -> AnthropicProvider:
    ...

@overload
def create_llm(provider: Provider, model: str) -> LLMProvider:
    ...

def create_llm(provider: Provider, model: str) -> LLMProvider:
    """
    Create LLM instance with proper typing
    適切な型付きでLLMインスタンスを作成
    
    Args:
        provider: LLM provider name / LLMプロバイダー名
        model: Model name / モデル名
    
    Returns:
        LLM provider instance / LLMプロバイダーインスタンス
    """
    if provider == "openai":
        return OpenAIProvider(model=model)
    elif provider == "anthropic":
        return AnthropicProvider(model=model)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
```

## 型チェックの無効化

### 特定の行を無視

```python
# 型チェックを無視
result = some_untyped_function()  # type: ignore

# 特定のエラーのみ無視
result = some_function()  # type: ignore[return-value]
```

### ファイル全体を無視

```python
# mypy: ignore-errors

# このファイル全体で型チェックを無視
```

## よくある型エラーと解決方法

### 1. Any型の使用

```python
# 問題のあるコード
def process(data: Any) -> Any:
    return data

# 改善されたコード
from typing import TypeVar

T = TypeVar('T')

def process(data: T) -> T:
    """
    Process data preserving type
    型を保持してデータを処理
    """
    return data
```

### 2. Optional型の処理

```python
from typing import Optional

def get_value() -> Optional[str]:
    """Get optional value / オプショナル値を取得"""
    return None

# 問題のあるコード
value = get_value()
length = len(value)  # Error: value might be None

# 改善されたコード
value = get_value()
if value is not None:
    length = len(value)  # OK

# または
length = len(value) if value else 0
```

### 3. 辞書の型ヒント

```python
from typing import Dict, Any, TypedDict

# 緩い型付け
config: Dict[str, Any] = {"key": "value"}

# 厳密な型付け
class Config(TypedDict):
    api_key: str
    model: str
    temperature: float

config: Config = {
    "api_key": "sk-...",
    "model": "gpt-4o-mini", 
    "temperature": 0.7
}
```

## IDE統合

### VS Code

`.vscode/settings.json`:

```json
{
  "python.linting.mypyEnabled": true,
  "python.linting.enabled": true,
  "python.linting.mypyArgs": [
    "--strict",
    "--show-error-codes"
  ]
}
```

### PyCharm

1. Settings → Editor → Inspections → Python
2. "Type checker" で "Mypy" を選択
3. "Arguments" に `--strict` を追加

## ベストプラクティス

1. **すべての関数に型ヒントを追加**
2. **Genericクラスを適切に使用**
3. **Protocol を使用してインターフェースを定義**
4. **TypedDict を使用して辞書の構造を定義**
5. **Any型の使用を最小限に抑制**
6. **Optional型を明示的に処理**

## トラブルシューティング

### よくあるエラー

```bash
# エラー: Function is missing a type annotation
def function(x):  # 型ヒントが不足
    return x

# 解決策
def function(x: str) -> str:
    return x
```

```bash
# エラー: Incompatible return value type
def get_number() -> int:
    return "string"  # intが期待されているのにstrを返している

# 解決策
def get_number() -> int:
    return 42
```

このガイドに従って、型安全なコードを書いてください！ 