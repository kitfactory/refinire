# Agents SDK Models 🤖🔌

[![PyPI Downloads](https://static.pepy.tech/badge/agents-sdk-models)](https://pepy.tech/projects/agents-sdk-models)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI Agents 0.0.9](https://img.shields.io/badge/OpenAI-Agents_0.0.9-green.svg)](https://github.com/openai/openai-agents-python)
[![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)]

OpenAI Agents SDK のためのモデルアダプター＆ワークフロー拡張集です。様々なLLMプロバイダーを統一インターフェースで利用し、実践的なエージェントパイプラインを簡単に構築できます！

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