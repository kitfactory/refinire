# Agents SDK Models 🤖🔌

[![PyPI Downloads](https://static.pepy.tech/badge/agents-sdk-models)](https://pepy.tech/projects/agents-sdk-models)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI Agents 0.0.9](https://img.shields.io/badge/OpenAI-Agents_0.0.9-green.svg)](https://github.com/openai/openai-agents-python)
[![Coverage](https://img.shields.io/badge/coverage-87%25-brightgreen.svg)]

OpenAI Agents SDK のためのモデルアダプター＆ワークフロー拡張集です。様々なLLMプロバイダーを統一インターフェースで利用し、実践的なエージェントパイプラインを簡単に構築できます！

## ⚡ 推奨: Flow/Step アーキテクチャ - **超簡単！** 

**🎉 v0.0.22の新機能:** **Flow/Step アーキテクチャ**と**GenAgent**の使用を推奨します。信じられないほど簡単で強力です！

### 🚀 **たった3行で開始！**

```python
from agents_sdk_models import create_simple_gen_agent, Context
import asyncio

# ステップ1: GenAgentを作成（AgentPipelineみたいだけど、もっと良い！）
gen_agent = create_simple_gen_agent(
    name="simple_gen",
    instructions="あなたは親切なアシスタントです。ユーザーの質問に簡潔で分かりやすく答えてください。",
    model="gpt-4o-mini"
)

# ステップ2: コンテキストを作成して実行
context = Context()
context.add_user_message("こんにちは！日本の文化について簡潔に教えてください。")

# ステップ3: 実行！（前と同じシンプルなインターフェース）
result = asyncio.run(gen_agent.run("こんにちは！日本の文化について簡潔に教えてください。", context))
print(result.shared_state["simple_gen_result"])  # あなたの回答が完成！
```

### 🚀 **新機能: 超シンプルなFlow作成！**

今や**3つの方法**でフローを作成できます：

```python
# 1. 単一ステップ（新機能！）
flow = Flow(steps=gen_agent)

# 2. シーケンシャルステップ（新機能！）
flow = Flow(steps=[step1, step2, step3])  # 自動接続！

# 3. 従来方式（複雑なフロー用）
flow = Flow(start="step1", steps={"step1": step1, "step2": step2})
```

### 🎯 **なぜこんなに簡単なの？**

| **LangChain/LangGraph (~50-100+行)** | **GenAgent + Flow (3-5行)** |
|---------------------------|----------------------------|
| 🔧 **複雑なインポート**（10+モジュール） | ✨ **1つのインポート** - すべて含まれる |
| 📝 **手動プロンプトテンプレート** | 🎯 **シンプルな指示文字列** |
| 🧩 **グラフ/チェーン構築**（20+行） | 🔄 **自動生成ワークフロー** |
| ⚙️ **カスタムエラーハンドリング** | 🛡️ **内蔵エラー回復機能** |
| 🔁 **手動リトライロジック** | 🔄 **評価付き自動リトライ** |
| 🛠️ **状態管理コード** | 📦 **自動処理** |

### 🌟 **実用例: 評価付きコンテンツ生成器**

```python
from agents_sdk_models import create_evaluated_gen_agent, Context
import asyncio

# 評価付きGenAgentを作成（複雑なAgentPipeline設定を置き換え）
gen_agent = create_evaluated_gen_agent(
    name="eval_gen",
    generation_instructions="人工知能の未来について200文字程度で分かりやすく説明してください。",
    evaluation_instructions="回答が200文字程度で、分かりやすく、正確な内容かを評価してください。",
    model="gpt-4o-mini"
)

# 評価付きで実行
context = Context()
context.add_user_message("人工知能の未来について200文字程度で説明してください。")

result = asyncio.run(gen_agent.run("人工知能の未来について200文字程度で説明してください。", context))
print(result.shared_state["eval_gen_result"])
print("評価:", result.shared_state.get("eval_gen_evaluation"))
# 自動処理: 生成 → 評価 → フィードバック
```

### 🎨 **LangChain/LangGraphとの比較 - 圧倒的な差！**

```python
# LangChain/LangGraph方式 (~80+行、複雑な設定)
"""
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser
from langchain.callbacks import BaseCallbackHandler
from langchain.schema.runnable import RunnablePassthrough
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
# ... (約15行のimport文) ...

class AgentState(TypedDict):
    input: str
    generation: str
    evaluation: dict
    retry_count: int
    # ... (約10行の状態定義) ...

def generation_node(state):
    # ... (約15行の生成ロジック) ...
    
def evaluation_node(state):
    # ... (約20行の評価ロジック) ...
    
def should_retry(state):
    # ... (約10行のリトライ判定) ...

workflow = StateGraph(AgentState)
workflow.add_node("generate", generation_node)
workflow.add_node("evaluate", evaluation_node)
workflow.add_conditional_edges(
    "evaluate", 
    should_retry,
    {"retry": "generate", "end": END}
)
# ... (約10行のグラフ構築) ...
"""

# GenAgent + Flow方式（3行！）
gen_agent = create_simple_gen_agent(
    name="simple_setup",
    instructions="...",
    model="gpt-4o-mini"
)
# GenAgentを直接使用 - 複雑なFlowは不要！
result = asyncio.run(gen_agent.run("あなたの入力", Context()))  # 完了！
```

### 🏗️ **高度な機能もシンプルに**

```python
# シンプルなFlow例
from agents_sdk_models import Context, FunctionStep, create_simple_flow
import asyncio

def process_greeting(user_input, ctx):
    """ユーザーデータで挨拶を処理"""
    name = ctx.shared_state.get("user_name", "名無し")
    task = ctx.shared_state.get("task", "何か")
    greeting = f"こんにちは、{name}さん！{task}について支援いたします。"
    ctx.shared_state["greeting"] = greeting
    ctx.finish()
    return ctx

# シンプルなFlowを作成
context = Context()
context.shared_state["user_name"] = "太郎"
context.shared_state["task"] = "プログラミング学習"

greeting_step = FunctionStep("greeting", process_greeting)
flow = create_simple_flow([("greeting", greeting_step)], context)

result = asyncio.run(flow.run())
print(result.shared_state.get("greeting"))  # "こんにちは、太郎さん！プログラミング学習について支援いたします。"
```

### 条件付きFlow例
```python
from agents_sdk_models import Context, ConditionStep, FunctionStep, Flow
import asyncio

# ユーザーレベル付きコンテキストを作成
context = Context()
context.shared_state["user_level"] = "beginner"

# 条件関数を作成
def is_beginner(ctx):
    return ctx.shared_state.get("user_level") == "beginner"

# アクション関数を作成
def beginner_action(user_input, ctx):
    ctx.shared_state["message"] = "初心者向けのチュートリアルを開始します。"
    ctx.finish()
    return ctx

def advanced_action(user_input, ctx):
    ctx.shared_state["message"] = "上級者向けのコンテンツを表示します。"
    ctx.finish()
    return ctx

# 条件付きFlowを作成
condition_step = ConditionStep("condition", is_beginner, "beginner", "advanced")
beginner_step = FunctionStep("beginner", beginner_action)
advanced_step = FunctionStep("advanced", advanced_action)

flow = Flow(
    start="condition",
    steps={
        "condition": condition_step,
        "beginner": beginner_step,
        "advanced": advanced_step
    },
    context=context
)

result = asyncio.run(flow.run())
print(result.shared_state.get("message"))  # "初心者向けのチュートリアルを開始します。"
```

### ✨ **あなたが気に入る利点:**
- 🔄 **より柔軟**: モジュラーステップで複雑なワークフローを構成
- 🧩 **再利用性向上**: ステップを異なるフロー間で再利用
- 🎯 **クリーンなアーキテクチャ**: 関心の明確な分離
- 🚀 **将来対応**: スケーラビリティと拡張性を考慮した設計
- 💡 **直感的**: AgentPipelineを理解していれば、これも理解できます！

**注意:** LangChain/LangGraphの50-100+行の複雑な設定と比較して、GenAgent + Flowはわずか3-5行で同じ機能を実現！`AgentPipeline`はv0.1.0で削除予定です。

---

## 🌟 特徴

- 🔄 **統一ファクトリ**: `get_llm` 関数で各種プロバイダーのモデルを簡単取得
- 🧩 **複数プロバイダー対応**: OpenAI, Ollama, Google Gemini, Anthropic Claude
- 📊 **構造化出力**: `get_llm` で取得したモデルはPydanticモデルによる構造化出力に対応
- 🏗️ **AgentPipelineクラス**: 生成・評価・ツール・ガードレールを1つのワークフローで簡単統合
- 🛡️ **ガードレール**: 入力・出力ガードレールで安全・コンプライアンス対応
- 🛠️ **シンプルなインターフェース**: 最小限の記述で最大限の柔軟性
- ✨ **ノーコード評価＆自己改善**: モデル名とプロンプトだけで生成・評価を実行し、自動的なフィードバックループで改善可能
- 🔍 **コンソールトレーシング**: 本ライブラリではデフォルトでコンソールトレーシング（`ConsoleTracingProcessor`）が有効化されています。OpenAI Agents SDK はデフォルトで OpenAI のトレーシングサービスを使用します（`OPENAI_API_KEY` が必要）が、本ライブラリでは軽量なコンソールベースのトレーサーを提供しています。不要な場合は `disable_tracing()` で無効化できます。

---

## v0.22 リリースノート
- **🚀 重要: 新しいFlowコンストラクタ** - 3つのモードで超シンプルなFlow作成を追加:
  - 単一ステップ: `Flow(steps=gen_agent)` 
  - シーケンシャルステップ: `Flow(steps=[step1, step2, step3])` (自動接続)
  - 従来方式: `Flow(start="step1", steps={"step1": step1, "step2": step2})`
- **🚀 Flow.run()の機能強化** - `input_data`パラメータを追加（`initial_input`より推奨）
- **✨ GenAgent + Flowアーキテクチャ** - 新規プロジェクトではAgentPipelineより推奨
- **⚠️ AgentPipelineの非推奨化** - AgentPipelineは非推奨となり、v0.1.0で削除予定
- **📚 完全なドキュメント更新** - 全チュートリアルと例を新しいFlow機能に対応して更新

## v0.21 リリースノート
- `get_available_models` 同期関数を修正し、実行中のイベントループがある環境（Jupyter Notebook、IPythonなど）でも正常に動作するよう改善
- Ollama の `/api/tags` エンドポイント経由での動的モデル検出をサポート

## v0.20 リリースノート
- Ollama設定用の `OLLAMA_BASE_URL` 環境変数をサポート
- OpenAI Agents SDK標準のTraceを除去し、コンソール専用トレーシングに変更して互換性を向上

## v0.19 リリースノート
- `get_available_models()` と `get_available_models_async()` 関数を追加し、各プロバイダーの利用可能なモデル名を取得可能にしました
- モデルリストを最新版に更新：Claude-4（Opus/Sonnet）、Gemini 2.5（Pro/Flash）、OpenAI最新モデル（gpt-4.1、o3、o4-mini）

## v0.18 リリースノート
- OpenAI Agents SDK の Trace 機能をサポートし、標準でコンソールトレーシングを有効化しました。
- `evaluation_model` パラメータを追加し、生成モデルと評価モデルを切り替え可能にしました。

## 🛠️ インストール

### PyPI から（推奨）
```bash
pip install agents-sdk-models
```

### ソースから
```bash
git clone https://github.com/kitfactory/agents-sdk-models.git
cd agents-sdk-models
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -e .[dev]
```

## 🧪 テスト & カバレッジ

テストを実行し、カバレッジレポートを表示します:

```bash
pytest --cov=agents_sdk_models --cov-report=term-missing
```
- ✅ すべてのテストは正常にパスしています。
- Coverageバッジは`agents_sdk_models`パッケージの行カバレッジ率（pytest-covによる計測）を示しています。

---

## 🚀 クイックスタート: `get_llm` の使い方

`get_llm` 関数はモデル名・プロバイダー名の指定、またはモデル名だけで（プロバイダー自動推論）利用できます。

```python
from agents_sdk_models import get_llm

# モデル・プロバイダー両方指定
llm = get_llm(model="gpt-4o-mini", provider="openai")
# モデル名だけ指定（プロバイダー自動推論）
llm = get_llm("claude-3-5-sonnet-latest")
```

### 構造化出力例
```python
from agents import Agent, Runner
from agents_sdk_models import get_llm
from pydantic import BaseModel

class WeatherInfo(BaseModel):
    location: str
    temperature: float
    condition: str

llm = get_llm("gpt-4o-mini")
agent = Agent(
    name="天気レポーター",
    model=llm,
    instructions="あなたは役立つ天気レポーターです。",
    output_type=WeatherInfo
)
result = Runner.run_sync(agent, "東京の天気は？")
print(result.final_output)
```

### コンソールトレーシング & インストルメンテーション
開発やデバッグ時にコンソールで軽量トレースを取得できます:
```python
from agents_sdk_models import enable_console_tracing, disable_tracing
from agents_sdk_models.pipeline import AgentPipeline
from agents.tracing import trace

# コンソールトレーシングを有効化 (ConsoleTracingProcessor)
enable_console_tracing()

pipeline = AgentPipeline(
    name="trace_example",
    generation_instructions="あなたは親切なアシスタントです。",
    evaluation_instructions=None,
    model="gpt-4o-mini"
)

# trace コンテキスト内で実行
with trace("MyTrace"):
    result = pipeline.run("こんにちは！")

print(result)
```
コンソール出力例 (色は省略):
```
Instruction: あなたは親切なアシスタントです。
Prompt: こんにちは！
Output: [生成された応答]
```

### ClearifyAgent：曖昧な要求の明確化例
```python
from agents_sdk_models import create_simple_clearify_agent, Context
import asyncio

# 曖昧な要求を処理するClearifyAgentを作成
agent = create_simple_clearify_agent(
    name="clarify_agent",
    instructions="ユーザーの曖昧な要求を明確にするために質問をしてください。要求が十分明確になったら、明確化された要求を出力してください。",
    model="gpt-4o-mini"
)

# 曖昧な要求を処理
ambiguous_request = "APIを作りたいです"
context = Context()
context.add_user_message(ambiguous_request)

result = asyncio.run(agent.run(ambiguous_request, context))
print("元の要求:", ambiguous_request)
print("明確化後:", result.shared_state.get("clarify_agent_result", "明確化中"))
```

### マルチプロバイダーLLMアクセス例
```python
from agents_sdk_models import get_llm

# 異なるプロバイダーを試す
providers = [
    ("openai", "gpt-4o-mini"),
    ("anthropic", "claude-3-haiku-20240307"),
    ("google", "gemini-1.5-flash"),
    ("ollama", "llama3.1:8b")
]

for provider, model in providers:
    try:
        llm = get_llm(provider=provider, model=model)
        print(f"✓ {provider}: {model} - 準備完了")
    except Exception as e:
        print(f"✗ {provider}: {model} - エラー: {str(e)}")
```

### 利用可能なモデルの取得例
```python
from agents_sdk_models import get_available_models, get_available_models_async

# 全プロバイダーからモデルを取得（同期版）
models = get_available_models(["openai", "google", "anthropic", "ollama"])
print("利用可能なモデル:", models)

# 特定のプロバイダーからモデルを取得（非同期版）
import asyncio
async def main():
    models = await get_available_models_async(["openai", "google"])
    for provider, model_list in models.items():
        print(f"{provider}: {model_list}")

asyncio.run(main())

# カスタムOllama URL
models = get_available_models(["ollama"], ollama_base_url="http://custom-host:11434")
```

---

## 🏗️ AgentPipelineクラス: LLMワークフローを簡単構築

`AgentPipeline` クラスは、生成指示・評価指示・ツール・ガードレールを柔軟に組み合わせてLLMエージェントワークフローを簡単に構築できます。

#### 主な初期化パラメータ
- `generation_instructions` (str): 生成用システムプロンプト
- `evaluation_instructions` (str, optional): 評価用システムプロンプト
- `model` (str, optional): 生成に使用するLLMモデル名（例: "gpt-4o"）
- `evaluation_model` (str, optional): 評価に使用するLLMモデル名（省略時は`model`と同じモデルを使用）
- 補足: `evaluation_model` を切り替えることで、生成にOpenAIモデルを、評価にローカルOllamaモデルを使用し、コスト削減やパフォーマンス向上が可能です。
- `generation_tools` (list, optional): 生成時ツールのリスト
- `input_guardrails` (list, optional): 入力ガードレールのリスト
- `output_guardrails` (list, optional): 出力ガードレールのリスト
- `threshold` (int): 評価スコアの閾値
- `retries` (int): リトライ回数
- `retry_comment_importance` (list[str], optional): リトライ時に含めるコメント重大度

### 基本構成
```python
from agents_sdk_models.pipeline import AgentPipeline

pipeline = AgentPipeline(
    name="simple_generator",
    generation_instructions="""
    あなたは創造的な物語を生成する役立つアシスタントです。
    ユーザーの入力に基づいて短い物語を生成してください。
    """,
    evaluation_instructions=None,  # 評価不要
    model="gpt-4o"
)
result = pipeline.run("ロボットが絵を学ぶ物語")
```

### 評価付き
```python
pipeline = AgentPipeline(
    name="evaluated_generator",
    generation_instructions="""
    あなたは創造的な物語を生成する役立つアシスタントです。
    ユーザーの入力に基づいて短い物語を生成してください。
    """,
    evaluation_instructions="""
    あなたは物語の評価者です。以下の基準で生成された物語を評価してください：
    1. 創造性（0-100）
    2. 一貫性（0-100）
    3. 感情的な影響（0-100）
    平均スコアを計算し、各側面について具体的なコメントを提供してください。
    """,
    model="gpt-4o",
    evaluation_model="gpt-4o-mini",  # 評価に使用するモデルを指定
    threshold=70
)
result = pipeline.run("ロボットが絵を学ぶ物語")
```

### ツール連携
```python
from agents import function_tool

@function_tool
def search_web(query: str) -> str:
    # 実際のWeb検索APIを呼ぶ場合はここを実装
    return f"Search results for: {query}"

@function_tool
def get_weather(location: str) -> str:
    # 実際の天気APIを呼ぶ場合はここを実装
    return f"Weather in {location}: Sunny, 25°C"

tools = [search_web, get_weather]

pipeline = AgentPipeline(
    name="tooled_generator",
    generation_instructions="""
    あなたは情報を収集するためにツールを使用できる役立つアシスタントです。
    以下のツールにアクセスできます：
    1. search_web: 情報をWebで検索する
    2. get_weather: 場所の現在の天気を取得する
    適切な場合は、これらのツールを使用して正確な情報を提供してください。
    """,
    evaluation_instructions=None,
    model="gpt-4o",
    generation_tools=tools
)
result = pipeline.run("東京の天気は？")
```

### ガードレール連携（input_guardrails）
```python
from agents import Agent, input_guardrail, GuardrailFunctionOutput, InputGuardrailTripwireTriggered, Runner, RunContextWrapper
from agents_sdk_models.pipeline import AgentPipeline
from pydantic import BaseModel

class MathHomeworkOutput(BaseModel):
    is_math_homework: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="ユーザーが数学の宿題を依頼しているか判定してください。",
    output_type=MathHomeworkOutput,
)

@input_guardrail
async def math_guardrail(ctx: RunContextWrapper, agent: Agent, input: str):
    result = await Runner.run(guardrail_agent, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math_homework,
    )

pipeline = AgentPipeline(
    name="guardrail_pipeline",
    generation_instructions="""
    あなたは役立つアシスタントです。ユーザーの質問に答えてください。
    """,
    evaluation_instructions=None,
    model="gpt-4o",
    input_guardrails=[math_guardrail],
)

try:
    result = pipeline.run("2x + 3 = 11 を解いてください")
    print(result)
except InputGuardrailTripwireTriggered:
    print("[Guardrail Triggered] 数学の宿題依頼を検出し、リクエストをブロックしました。")
```

### dynamic_promptによる動的プロンプト生成
```python
# dynamic_prompt引数にカスタム関数を渡すことで、プロンプト生成を柔軟にカスタマイズできます。
from agents_sdk_models.pipeline import AgentPipeline

def my_dynamic_prompt(user_input: str) -> str:
    # 例: ユーザー入力を大文字化し、接頭辞を付与
    return f"[DYNAMIC PROMPT] USER SAID: {user_input.upper()}"

pipeline = AgentPipeline(
    name="dynamic_prompt_example",
    generation_instructions="""
    あなたは親切なアシスタントです。ユーザーのリクエストに答えてください。
    """,
    evaluation_instructions=None,
    model="gpt-4o",
    dynamic_prompt=my_dynamic_prompt
)
result = pipeline.run("面白いジョークを教えて")
print(result)
```

### リトライ時のコメントフィードバック
```python
from agents_sdk_models.pipeline import AgentPipeline

pipeline = AgentPipeline(
    name="comment_retry",
    generation_instructions="生成プロンプト",  # 生成用システムプロンプト
    evaluation_instructions="評価プロンプト",   # 評価用システムプロンプト
    model="gpt-4o-mini",
    threshold=80,
    retries=2,
    retry_comment_importance=["serious", "normal"]
)
result = pipeline.run("入力テキスト")
print(result)
```
リトライ時に前回の評価コメント（指定した重大度のみ）が生成プロンプトに自動で付与され、改善を促します。

---

## 🖥️ サポート環境

- Python 3.9+
- OpenAI Agents SDK 0.0.9+
- Windows, Linux, MacOS

---

## 💡 このライブラリのメリット

- **統一**: 主要なLLMプロバイダーを1つのインターフェースで
- **柔軟**: 生成・評価・ツール・ガードレールを自由に組み合わせ
- **簡単**: 最小限の記述ですぐ使える、上級用途にも対応
- **自己改善**: 評価指示とリトライ設定だけで、自動的に改善サイクルを実行
- **安全**: コンプライアンス・安全性のためのガードレール

---

## 📂 利用例

`examples/` ディレクトリにより高度な使い方例があります：
- `pipeline_simple_generation.py`: 最小構成の生成
- `pipeline_with_evaluation.py`: 生成＋評価
- `pipeline_with_tools.py`: ツール連携生成
- `pipeline_with_guardrails.py`: ガードレール（入力フィルタリング）

---

## 📄 ライセンス・謝辞

MIT License。 [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) により実現。