# APIリファレンス

このページでは、Refinire パッケージの主要APIの詳細なリファレンスを提供します。

## クラス・関数一覧

| 名前                     | 種別     | 概要                                                        |
|--------------------------|----------|-------------------------------------------------------------|
| get_llm                  | 関数     | モデル名・プロバイダー名からLLMインスタンスを取得           |
| create_simple_gen_agent  | 関数     | シンプルな生成エージェントを作成                           |
| create_evaluated_gen_agent| 関数    | 評価機能付き生成エージェントを作成                         |
| Flow                     | クラス   | ワークフロー管理の中心クラス                               |
| GenAgent                 | クラス   | 生成・評価機能を持つエージェントクラス                     |
| ClarifyAgent             | クラス   | 対話型タスク明確化エージェント                             |
| Context                  | クラス   | ステップ間での状態共有用コンテキスト                       |
| ConsoleTracingProcessor  | クラス   | コンソール色分けトレース出力用プロセッサ                   |
| enable_console_tracing   | 関数     | コンソールトレーシングを有効化                             |
| disable_tracing          | 関数     | トレーシング機能をすべて無効化                             |
| AgentPipeline            | クラス   | 【非推奨】生成・評価・ツール・ガードレールを統合したパイプライン |

---

## 統一LLMインターフェース

### get_llm

複数のLLMプロバイダーを統一インターフェースで扱うためのファクトリ関数です。

```python
from refinire import get_llm

# OpenAI
llm = get_llm("gpt-4o-mini")

# Anthropic Claude
llm = get_llm("claude-3-sonnet")

# Google Gemini
llm = get_llm("gemini-pro")

# Ollama（ローカル）
llm = get_llm("llama3.1:8b")
```

#### 引数

| 名前       | 型                 | 必須/オプション | デフォルト | 説明                                          |
|------------|--------------------|----------------|------------|-----------------------------------------------|
| model      | str                | 必須           | -          | 使用するLLMモデル名                           |
| provider   | str                | オプション     | None       | モデルのプロバイダー名（自動推論可）          |
| temperature| float              | オプション     | 0.3        | サンプリング温度（0.0-2.0）                  |
| api_key    | str                | オプション     | None       | プロバイダーAPIキー                          |
| base_url   | str                | オプション     | None       | プロバイダーAPIベースURL                     |
| thinking   | bool               | オプション     | False      | Claudeモデルの思考モード                      |
| tracing    | bool               | オプション     | False      | Agents SDKのトレーシングを有効化するか        |

#### 戻り値
- **LLMインスタンス**: 指定されたプロバイダーのLLMオブジェクト

#### サポートされるモデル

**OpenAI**
- gpt-4o, gpt-4o-mini
- gpt-4-turbo, gpt-4
- gpt-3.5-turbo

**Anthropic Claude**
- claude-3-5-sonnet-20241022
- claude-3-sonnet, claude-3-haiku
- claude-3-opus

**Google Gemini**
- gemini-pro, gemini-pro-vision
- gemini-1.5-pro, gemini-1.5-flash

**Ollama**
- llama3.1:8b, llama3.1:70b
- mistral:7b
- codellama:7b

---

## エージェント作成関数

### create_simple_gen_agent

シンプルな生成エージェントを作成します。

```python
from refinire import create_simple_gen_agent

agent = create_simple_gen_agent(
    name="assistant",
    instructions="あなたは親切なアシスタントです。",
    model="gpt-4o-mini"
)
```

#### 引数

| 名前         | 型    | 必須/オプション | デフォルト | 説明                           |
|--------------|-------|----------------|------------|--------------------------------|
| name         | str   | 必須           | -          | エージェント名                 |
| instructions | str   | 必須           | -          | システムプロンプト             |
| model        | str   | 必須           | -          | 使用するモデル名               |
| tools        | list  | オプション     | None       | 使用可能なツールのリスト       |

### create_evaluated_gen_agent

評価機能付きの生成エージェントを作成します。

```python
from refinire import create_evaluated_gen_agent

agent = create_evaluated_gen_agent(
    name="quality_assistant",
    generation_instructions="役立つ回答を生成してください。",
    evaluation_instructions="正確性と有用性を評価してください。",
    threshold=80.0,
    model="gpt-4o-mini"
)
```

#### 引数

| 名前                      | 型    | 必須/オプション | デフォルト | 説明                           |
|---------------------------|-------|----------------|------------|--------------------------------|
| name                      | str   | 必須           | -          | エージェント名                 |
| generation_instructions   | str   | 必須           | -          | 生成用システムプロンプト       |
| evaluation_instructions   | str   | 必須           | -          | 評価用システムプロンプト       |
| threshold                 | float | 必須           | -          | 品質閾値（0-100）              |
| model                     | str   | 必須           | -          | 使用するモデル名               |
| tools                     | list  | オプション     | None       | 使用可能なツールのリスト       |

---

## Flow/Stepアーキテクチャ

### Flow

ワークフロー管理の中心クラスです。複数のステップを組み合わせて複雑な処理フローを作成できます。

```python
from refinire import Flow, FunctionStep
import asyncio

# シンプルなFlow
flow = Flow(steps=gen_agent)

# 複数ステップのFlow
flow = Flow([
    ("step1", FunctionStep("step1", func1)),
    ("step2", FunctionStep("step2", func2))
])

# 実行
result = asyncio.run(flow.run(input_data="入力データ"))
```

#### 主要メソッド

| メソッド名     | 引数                                        | 戻り値              | 説明                            |
|----------------|---------------------------------------------|---------------------|---------------------------------|
| run            | input_data: Any                             | Context            | ワークフローを非同期実行        |
| run_sync       | input_data: Any                             | Context            | ワークフローを同期実行          |
| run_streamed   | input_data: Any, callback: Callable = None | AsyncIterator[str] | ワークフロー出力をリアルタイムストリーミング |
| show           | -                                           | None               | ワークフロー構造を可視化        |

#### Flowストリーミング

Flowはストリーミングコンテンツを生成するステップ（RefinireAgentなど）からのストリーミング出力をサポートします：

```python
from refinire import Flow, FunctionStep, RefinireAgent

# ストリーミング対応エージェントを含むフローを作成
flow = Flow({
    "analyze": FunctionStep("analyze", analyze_function),
    "generate": RefinireAgent(
        name="generator",
        generation_instructions="詳細なコンテンツを生成してください",
        model="gpt-4o-mini"
    )
})

# フロー全体の出力をストリーミング
async for chunk in flow.run_streamed("技術文書を作成してください"):
    print(chunk, end="", flush=True)
```

**Flowストリーミングの動作:**
- ストリーミング対応ステップ（RefinireAgentなど）のみがチャンクを生成
- 非ストリーミングステップはチャンクなしで通常通り実行
- コンテキストと状態はストリーミング全体で保持
- 混合ストリーミング/非ストリーミングワークフローをサポート

### Context

ステップ間での状態共有に使用するコンテキストクラスです。

```python
from refinire import Context

ctx = Context()
ctx.shared_state["key"] = "value"
ctx.finish()  # ワークフロー終了
```

#### 主要属性・メソッド

| 名前           | 型           | 説明                           |
|----------------|--------------|--------------------------------|
| shared_state   | dict         | ステップ間で共有される状態     |
| user_input     | Any          | ユーザー入力データ             |
| finish()       | メソッド     | ワークフロー終了を指示         |

---

## エージェントクラス

### GenAgent

生成・評価機能を持つエージェントクラスです。Flow内でのステップとして使用できます。

```python
from refinire.agents import GenAgent

agent = GenAgent(
    name="generator",
    generation_instructions="文章を生成してください。",
    evaluation_instructions="品質を評価してください。",
    model="gpt-4o-mini",
    threshold=75.0
)
```

#### 主要メソッド

| メソッド名 | 引数                        | 戻り値        | 説明                           |
|------------|----------------------------|---------------|--------------------------------|
| run        | user_input: str, ctx: Context | Context    | エージェントを非同期実行       |
| run_sync   | user_input: str, ctx: Context | Context    | エージェントを同期実行         |

### RefinireAgent

組み込み評価、ツール統合、ストリーミング機能を備えた高度なAIエージェントです。本番利用に最適な主要エージェントクラスです。

```python
from refinire import RefinireAgent

agent = RefinireAgent(
    name="assistant",
    generation_instructions="明確で正確な情報を提供する親切なアシスタントです。",
    evaluation_instructions="""以下の基準で応答品質を0-100点で評価してください：
    - 正確性と事実の正しさ（0-25点）
    - 明確性と理解しやすさ（0-25点）
    - 有用性と関連性（0-25点）
    - 完全性と徹底性（0-25点）
    
    評価結果は以下の形式で提供してください：
    スコア: [0-100]
    コメント:
    - [応答の具体的な強み]
    - [改善が必要な領域]
    - [向上のための提案]""",
    model="gpt-4o-mini",
    threshold=85.0,
    max_retries=3
)
```

#### 主要メソッド

| メソッド名     | 引数                                         | 戻り値              | 説明                            |
|----------------|----------------------------------------------|---------------------|---------------------------------|
| run            | user_input: str, ctx: Context = None        | LLMResult          | エージェントを同期実行          |
| run_async      | user_input: str, ctx: Context = None        | LLMResult          | エージェントを非同期実行        |
| run_streamed   | user_input: str, ctx: Context = None, callback: Callable = None | AsyncIterator[str] | 応答チャンクをリアルタイムストリーミング |

#### ストリーミング引数

| 引数      | 型                    | 必須/オプション | デフォルト | 説明                              |
|-----------|-----------------------|-----------------|------------|-----------------------------------|
| user_input| str                   | 必須            | -          | 処理する入力テキスト              |
| ctx       | Context               | オプション      | None       | 会話状態用コンテキスト            |
| callback  | Callable[[str], None] | オプション      | None       | 各チャンクを処理する関数          |

#### ストリーミング使用例

**基本ストリーミング:**
```python
async for chunk in agent.run_streamed("量子コンピューティングを説明してください"):
    print(chunk, end="", flush=True)
```

**コールバック付きストリーミング:**
```python
def process_chunk(chunk: str):
    # カスタム処理: ファイル保存、WebSocket送信など
    print(f"受信: {chunk}")

async for chunk in agent.run_streamed("コンテンツを生成", callback=process_chunk):
    print(chunk, end="", flush=True)
```

**コンテキスト対応ストリーミング:**
```python
from refinire import Context

ctx = Context()
async for chunk in agent.run_streamed("こんにちは", ctx=ctx):
    print(chunk, end="", flush=True)

# コンテキストを維持して会話を継続
async for chunk in agent.run_streamed("前の話を続けましょう", ctx=ctx):
    print(chunk, end="", flush=True)
```

#### 構造化出力ストリーミング

構造化出力（Pydanticモデル）をストリーミングで使用すると、応答は解析されたオブジェクトではなく**JSONチャンク**として配信されます：

```python
from pydantic import BaseModel

class Article(BaseModel):
    title: str
    content: str

agent = RefinireAgent(
    name="writer",
    generation_instructions="記事を書いてください",
    output_model=Article
)

# JSONチャンクをストリーミング: {"title": "...", "content": "..."}
async for json_chunk in agent.run_streamed("AIについて書いて"):
    print(json_chunk, end="", flush=True)

# 解析されたオブジェクトが必要な場合は通常のメソッドを使用:
result = await agent.run_async("AIについて書いて")
article = result.content  # Articleオブジェクトを返す
```

#### 評価システム

RefinireAgentには、コンテンツ品質を自動評価し、品質閾値に達しない場合に再生成をトリガーする組み込み評価システムが含まれています。

**評価出力形式:**

評価システムは、この正確な形式での応答を期待します：
```
スコア: 87
コメント:
- 技術的正確性が優れており包括的なカバレッジ
- 論理的な流れを持つ明確な構造
- 実践的な例の効果的な使用
- 視覚的な図解があるとより良い
- トラブルシューティングセクションの追加を検討
```

**評価パラメータ:**

| パラメータ | 型 | デフォルト | 説明 |
|-----------|-----|-----------|------|
| evaluation_instructions | str | None | 品質評価のための指示 |
| threshold | float | 70.0 | 必要な最小スコア（0-100） |
| max_retries | int | 3 | 最大再生成試行回数 |

**評価結果へのアクセス:**

```python
# 基本評価アクセス
result = agent.run("技術コンテンツを作成")
score = result.evaluation_score  # 0-100の整数

# Contextによる詳細評価
from refinire import Context
ctx = Context()
result = agent.run("技術コンテンツを作成", ctx)

eval_data = ctx.evaluation_result
score = eval_data["score"]           # 87
passed = eval_data["passed"]         # True/False
feedback = eval_data["feedback"]     # 完全な評価テキスト
comments = eval_data["comments"]     # 解析されたコメントリスト
```

**評価指示のベストプラクティス:**

1. **明確なポイント配分を含む100点満点スケール**を使用
2. **各スコア次元の具体的基準**を提供
3. **コメントリストによる構造化フィードバック**を要求
4. **改善のための実行可能な提案**を含める

包括的評価指示の例:
```python
evaluation_instructions="""コンテンツ品質を評価してください（0-100点）：
- 技術的正確性（0-30点）: 事実の正確性と精密性
- 明確性（0-30点）: 明確なコミュニケーションと理解
- 構造（0-25点）: 論理的組織と流れ
- 完全性（0-15点）: 包括的なカバレッジ

スコア: [0-100]
コメント:
- [具体例を含む強み]
- [提案を含む改善領域]
- [向上推奨事項]"""
```

### ClarifyAgent

対話型タスク明確化エージェントです。不明確な要求を明確化するための質問を行います。

```python
from refinire.agents import ClarifyAgent

agent = ClarifyAgent(
    name="clarifier",
    instructions="ユーザーの要求を明確化してください。",
    model="gpt-4o-mini"
)
```

---

## トレーシング機能

### enable_console_tracing

コンソールでの色分けトレーシングを有効化します。

```python
from refinire import enable_console_tracing

enable_console_tracing()
```

### disable_tracing

全てのトレーシング機能を無効化します。

```python
from refinire import disable_tracing

disable_tracing()
```

### ConsoleTracingProcessor

カスタムトレース処理用のクラスです。

```python
from refinire.tracing import ConsoleTracingProcessor

processor = ConsoleTracingProcessor(
    output_stream="console",
    simple_mode=True
)
```

---

## 非推奨API

### AgentPipeline（非推奨）

⚠️ **重要**: `AgentPipeline`は v0.1.0 で削除される予定です。新しいコードでは `GenAgent + Flow` を使用してください。

```python
# 非推奨 - 新しいコードでは使用しないでください
from refinire import AgentPipeline

pipeline = AgentPipeline(
    name="example",
    generation_instructions="文章を生成してください。",
    evaluation_instructions="品質を評価してください。",
    model="gpt-4o-mini",
    threshold=80
)
```

---

## アーキテクチャ図

```mermaid
classDiagram
    class Flow {
        +run(input_data)
        +run_sync(input_data)
        +show()
    }
    
    class GenAgent {
        +run(user_input, ctx)
        +run_sync(user_input, ctx)
    }
    
    class ClarifyAgent {
        +run(user_input, ctx)
        +clarify_task(task)
    }
    
    class Context {
        +shared_state: dict
        +user_input: Any
        +finish()
    }
    
    Flow --> GenAgent
    Flow --> ClarifyAgent
    Flow --> Context
    GenAgent --> Context
    ClarifyAgent --> Context
```

## 使用例

### 基本的な使用パターン

```python
from refinire import create_simple_gen_agent, Flow, Context
import asyncio

# 1. エージェント作成
agent = create_simple_gen_agent(
    name="assistant",
    instructions="親切なアシスタントとして回答してください。",
    model="gpt-4o-mini"
)

# 2. フロー作成
flow = Flow(steps=agent)

# 3. 実行
async def main():
    result = await flow.run(input_data="こんにちは")
    print(result.shared_state["assistant_result"])

asyncio.run(main())
```

### 複雑なワークフローの例

```python
from refinire import Flow, FunctionStep, create_evaluated_gen_agent
import asyncio

def preprocess(user_input: str, ctx: Context) -> Context:
    ctx.shared_state["processed_input"] = user_input.strip().lower()
    return ctx

agent = create_evaluated_gen_agent(
    name="analyzer",
    generation_instructions="入力を分析してください。",
    evaluation_instructions="分析の正確性を評価してください。",
    threshold=80.0,
    model="gpt-4o-mini"
)

def postprocess(user_input: str, ctx: Context) -> Context:
    result = ctx.shared_state.get("analyzer_result", "")
    ctx.shared_state["final_result"] = f"最終結果: {result}"
    ctx.finish()
    return ctx

flow = Flow([
    ("preprocess", FunctionStep("preprocess", preprocess)),
    ("analyze", agent),
    ("postprocess", FunctionStep("postprocess", postprocess))
])

async def main():
    result = await flow.run(input_data="  テキストを分析して  ")
    print(result.shared_state["final_result"])

asyncio.run(main())
```

## ContextProviderインターフェース

| クラス/メソッド         | 説明                                                                 | 引数 / 戻り値                |
|---------------------|--------------------------------------------------------------------|------------------------------|
| `ContextProvider`   | すべてのコンテキストプロバイダーの抽象基底クラス。                  |                              |
| `provider_name`     | プロバイダー名（クラス変数）。                                      | `str`                        |
| `get_config_schema` | プロバイダーの設定スキーマを返す。                                  | `classmethod` → `Dict[str, Any]` |
| `from_config`       | 設定辞書からプロバイダーを生成。                                     | `classmethod` → インスタンス |
| `get_context`       | クエリに対するコンテキスト文字列を返す。                            | `query: str, previous_context: Optional[str], **kwargs` → `str` |
| `update`            | 新しい対話でプロバイダー状態を更新。                                 | `interaction: Dict[str, Any]`|
| `clear`             | プロバイダー状態をクリア。                                          |                              |

---

## 標準プロバイダー

### ConversationHistoryProvider

会話履歴を管理するプロバイダーです。

**設定例:**
```python
{
    "type": "conversation_history",
    "max_items": 10
}
```

**パラメータ:**
- `max_items` (int): 保持する最大メッセージ数（デフォルト: 10）

### FixedFileProvider

指定されたファイルの内容を常に提供するプロバイダーです。

**設定例:**
```python
{
    "type": "fixed_file",
    "file_path": "config.yaml",
    "encoding": "utf-8",
    "check_updates": True
}
```

**パラメータ:**
- `file_path` (str, 必須): 読み取るファイルのパス
- `encoding` (str): ファイルエンコーディング（デフォルト: "utf-8"）
- `check_updates` (bool): ファイル更新をチェックするか（デフォルト: True）

### SourceCodeProvider

ユーザーの質問に関連するソースコードを自動検索するプロバイダーです。

**設定例:**
```python
{
    "type": "source_code",
    "base_path": ".",
    "max_files": 5,
    "max_file_size": 1000,
    "file_extensions": [".py", ".js", ".ts"],
    "include_patterns": ["src/**/*"],
    "exclude_patterns": ["tests/**/*"]
}
```

**パラメータ:**
- `base_path` (str): コードベース分析のベースディレクトリ（デフォルト: "."）
- `max_files` (int): コンテキストに含める最大ファイル数（デフォルト: 50）
- `max_file_size` (int): 読み込む最大ファイルサイズ（バイト）（デフォルト: 10000）
- `file_extensions` (list): 含めるファイル拡張子のリスト
- `include_patterns` (list): 含めるファイルパターンのリスト
- `exclude_patterns` (list): 除外するファイルパターンのリスト

### CutContextProvider

コンテキストを指定された長さに圧縮するプロバイダーです。

**設定例:**
```python
{
    "type": "cut_context",
    "provider": {
        "type": "source_code",
        "max_files": 10,
        "max_file_size": 2000
    },
    "max_chars": 3000,
    "max_tokens": None,
    "cut_strategy": "middle",
    "preserve_sections": True
}
```

**パラメータ:**
- `provider` (dict, 必須): ラップするコンテキストプロバイダーの設定
- `max_chars` (int): 最大文字数（Noneで制限なし）
- `max_tokens` (int): 最大トークン数（Noneで制限なし）
- `cut_strategy` (str): カット戦略（"start", "end", "middle"）（デフォルト: "end"）
- `preserve_sections` (bool): カット時に完全なセクションを保持するか（デフォルト: True）

---

## RefinireAgent拡張

| クラス/メソッド         | 説明                                                                 | 引数 / 戻り値                |
|---------------------|--------------------------------------------------------------------|------------------------------|
| `context_providers_config` | コンテキストプロバイダー設定（リスト/辞書/YAML文字列）。 | `List[dict]`/`str`           |
| `get_context_provider_schemas` | 利用可能な全プロバイダーのスキーマを返す。             | `classmethod` → `Dict[str, Any]` |
| `clear_context`     | すべてのコンテキストプロバイダーをクリア。                          |                              |

---

## 使用例: SourceCodeProviderの利用

```python
from refinire.agents.context_provider_factory import ContextProviderFactory

config = {
    "type": "source_code",
    "base_path": "src",
    "max_files": 5
}
provider = ContextProviderFactory.create_provider(config)
context = provider.get_context("パイプラインの仕組みは？")
print(context)
```

---

## 使用例: YAMLライクな複数プロバイダー

```yaml
- conversation_history:
    max_items: 5
- source_code:
    base_path: src
    max_files: 3
- cut_context:
    provider:
      type: conversation_history
      max_items: 10
    max_chars: 4000
    cut_strategy: end
```

---

## 関連ドキュメント
- `docs/api_reference.md`（英語）
- `docs/context_management.md`（設計）
- `examples/context_management_example.py`（使用例） 