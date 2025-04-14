# Agents SDK Models 🤖🔌

[![PyPI Downloads](https://static.pepy.tech/badge/agents-sdk-models)](https://pepy.tech/projects/agents-sdk-models)

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI Agents 0.0.9](https://img.shields.io/badge/OpenAI-Agents_0.0.9-green.svg)](https://github.com/openai/openai-agents-python)

OpenAI Agents SDK のモデルアダプターコレクションで、`get_llm` 関数を通じて様々な LLM プロバイダーを統一されたインターフェースで使用できます！🚀

## 🌟 特徴

- 🔄 **統一ファクトリ**: `get_llm` 関数を使用して、異なるプロバイダーのモデルインスタンスを簡単に取得。
- 🧩 **複数プロバイダー対応**: OpenAI, Ollama, Google Gemini, Anthropic Claude をサポート。
- 📊 **構造化出力**: `get_llm` を介してインスタンス化されたすべてのモデルが Pydantic モデルを使用した構造化出力をサポート。
- 🏭 **シンプルなインターフェース**: プロバイダーを指定し、オプションでモデル名を指定するだけ。

## 🛠️ インストール

### PyPI から（推奨）

```bash
# PyPIからインストール
pip install agents-sdk-models

# 構造化出力を使用する例のために (pydantic を含む)
# オプションの依存関係は以下でインストールできます:
# pip install agents-sdk-models[examples]
# または pydantic を直接インストール:
pip install agents-sdk-models pydantic>=2.10,<3
```

### ソースから

```bash
# リポジトリをクローン
git clone https://github.com/kitfactory/agents-sdk-models.git
cd agents-sdk-models

# 仮想環境を作成して有効化
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 開発モードでパッケージをインストール
pip install -e .[dev] # 開発依存関係 (pytest など) と共にインストール
```

## 🚀 クイックスタート: `get_llm` の使用

`get_llm` 関数は、異なるプロバイダーのモデルインスタンスを取得するための単一のエントリーポイントを提供します。

```python
import asyncio
import os
from agents import Agent, Runner
# ファクトリ関数をインポート
from agents_sdk_models import get_llm

async def main():
    # --- 例: OpenAI ---
    # OPENAI_API_KEY 環境変数が必要
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if openai_api_key:
        print("\nOpenAI の例を実行中...")
        # get_llm を使用してモデルを取得
        model_openai = get_llm(
            provider="openai",      # プロバイダーを指定
            model="gpt-4o-mini",    # モデル名を指定 (オプション、None の場合はデフォルトを使用)
            temperature=0.7,
            api_key=openai_api_key # 必要に応じて API キーを渡す
        )
        agent_openai = Agent(
            name="アシスタント",
            instructions="あなたは役立つアシスタントです。",
            model=model_openai
        )
        response_openai = await Runner.run(agent_openai, "あなたの名前と何ができるか教えてください。")
        print(response_openai.final_output)
    else:
        print("OPENAI_API_KEY が見つかりません。OpenAI の例をスキップします。")

    # --- 例: Ollama ---
    # Ollama サーバーがローカルで実行されていることを想定
    print("\nOllama の例を実行中...")
    try:
        # get_llm を使用してモデルを取得
        model_ollama = get_llm(
            provider="ollama",
            model="llama3", # Ollama インスタンスで利用可能なモデル名を指定
            temperature=0.7
            # base_url="http://localhost:11434" # オプション: デフォルトでない場合に指定
        )
        agent_ollama = Agent(
            name="アシスタント",
            instructions="あなたは役立つアシスタントです。",
            model=model_ollama
        )
        response_ollama = await Runner.run(agent_ollama, "あなたの名前と何ができるか教えてください。")
        print(response_ollama.final_output)
    except Exception as e:
        print(f"Ollama の例を実行できませんでした: {e}")
        print("Ollama サーバーが実行中で、モデル 'llama3' が利用可能であることを確認してください。")


    # --- 例: Google Gemini ---
    # GOOGLE_API_KEY 環境変数が必要
    google_api_key = os.environ.get("GOOGLE_API_KEY")
    if google_api_key:
        print("\nGoogle Gemini の例を実行中...")
        # get_llm を使用してモデルを取得
        model_gemini = get_llm(
            provider="google",
            model="gemini-1.5-flash", # モデル名を指定
            temperature=0.7,
            api_key=google_api_key
        )
        agent_gemini = Agent(
            name="アシスタント",
            instructions="あなたは役立つアシスタントです。",
            model=model_gemini
        )
        response_gemini = await Runner.run(agent_gemini, "あなたの名前と何ができるか教えてください。")
        print(response_gemini.final_output)
    else:
        print("GOOGLE_API_KEY が見つかりません。Google Gemini の例をスキップします。")


    # --- 例: Anthropic Claude ---
    # ANTHROPIC_API_KEY 環境変数が必要
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_api_key:
        print("\nAnthropic Claude の例を実行中...")
        # get_llm を使用してモデルを取得
        model_claude = get_llm(
            provider="anthropic",
            model="claude-3-haiku-20240307", # モデル名を指定
            temperature=0.7,
            api_key=anthropic_api_key,
            thinking=True # Claude のようなプロバイダー固有の引数 'thinking' を渡す
        )
        agent_claude = Agent(
            name="アシスタント",
            instructions="あなたは役立つアシスタントです。",
            model=model_claude
        )
        response_claude = await Runner.run(agent_claude, "あなたの名前と何ができるか教えてください。")
        print(response_claude.final_output)
    else:
        print("ANTHROPIC_API_KEY が見つかりません。Anthropic Claude の例をスキップします。")


if __name__ == "__main__":
    # 必要に応じて OpenAI 以外のプロバイダーのトレースを無効にする
    # import sys
    # provider = sys.argv[1] if len(sys.argv) > 1 else "openai"
    # if provider != "openai":
    #     from agents import set_tracing_disabled
    #     set_tracing_disabled(True)
    asyncio.run(main())
```

## 📊 `get_llm` による構造化出力

`get_llm` を介して取得されたすべてのモデルは、Pydantic モデルを使用した構造化出力をサポートしています:

```python
import asyncio
import os
from agents import Agent, Runner
from agents_sdk_models import get_llm
from pydantic import BaseModel
from typing import List

# --- Pydantic モデルを定義 ---
class WeatherInfo(BaseModel):
    location: str
    temperature: float
    condition: str
    recommendation: str

class WeatherReport(BaseModel):
    report_date: str
    locations: List<WeatherInfo>

# --- モデルインスタンスを取得 (例: OpenAI) ---
async def run_structured_example():
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        print("OPENAI_API_KEY が見つかりません。構造化出力の例をスキップします。")
        return

    model = get_llm(
        provider="openai",
        model="gpt-4o-mini",
        api_key=openai_api_key
    )

    # --- 構造化出力を持つエージェントを作成 ---
    agent = Agent(
        name="天気レポーター",
        model=model,
        instructions="あなたは役立つ天気レポーターです。日付を YYYY-MM-DD 形式で提供してください。",
        output_type=WeatherReport # Pydantic モデルを指定
    )

    # --- エージェントを実行し、構造化レスポンスを取得 ---
    print("\n構造化出力の例を実行中...")
    response = await Runner.run(agent, "今日の東京、大阪、札幌の天気はどうですか？")

    # --- 構造化出力にアクセス ---
    if response.final_output:
        weather_report: WeatherReport = response.final_output
        print(f"レポート日付: {weather_report.report_date}")
        for info in weather_report.locations:
            print(f"- 場所: {info.location}, 気温: {info.temperature}, 状態: {info.condition}")
            print(f"  推奨事項: {info.recommendation}")
    else:
        print("構造化出力の取得に失敗しました。")
        print(f"生出力: {response.raw_output}") # デバッグ用に生出力を表示

if __name__ == "__main__":
    asyncio.run(run_structured_example())

```

## 🔧 サポートされている環境

- **オペレーティングシステム**: Windows、macOS、Linux
- **Pythonバージョン**: 3.9以上
- **依存関係**:
  - **コア依存関係** (`pyproject.toml` で定義):
    - `openai>=1.68.0`
    - `openai-agents>=0.0.6`
  - **プロバイダー固有の依存関係** (必要に応じて自動インストール):
    - `google-generativeai` (Google Gemini に必要)
    - `anthropic` (Anthropic Claude に必要)
    - `httpx` (Ollama に必要)
  - **オプション依存関係** (例、特に構造化出力用):
    - `pydantic>=2.10,<3` (`pip install agents-sdk-models[examples]` または別途インストール可能)

*注意: プロバイダー固有の依存関係 (google, anthropic, httpx) は、それぞれのモデルが必要とする際に自動的にインストールされます。*

## 📝 ライセンス

このプロジェクトはMITライセンスの下で提供されています - 詳細はLICENSEファイルをご覧ください。

## 🙏 謝辞

- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
- [Ollama](https://ollama.ai/)
- [Google Gemini](https://ai.google.dev/)
- [Anthropic Claude](https://www.anthropic.com/claude) 