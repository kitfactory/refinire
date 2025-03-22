# Agents SDK Models 🤖🔌

[![PyPI Downloads](https://static.pepy.tech/badge/agents-sdk-models)](https://pepy.tech/projects/agents-sdk-models)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI Agents](https://img.shields.io/badge/OpenAI-Agents-green.svg)](https://github.com/openai/openai-agents-python)

OpenAI Agents SDKのモデルアダプターコレクションで、様々なLLMプロバイダーを統一されたインターフェースで使用できます！🚀

## 🌟 特徴

- 🔄 **統一インターフェース**: 複数のモデルプロバイダーで同じOpenAI Agents SDKインターフェースを使用
- 🧩 **複数モデル対応**: Ollama、Google Gemini、Anthropic Claudeをサポート
- 📊 **構造化出力**: すべてのモデルがPydanticモデルを使用した構造化出力をサポート

## 🛠️ インストール

### PyPIから（推奨）

```bash
# PyPIからインストール
pip install agents-sdk-models

# 構造化出力を使用する例のために
pip install agents-sdk-models[examples]
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
pip install -e .
```

## 🚀 クイックスタート

### Ollama

```python
import asyncio
from agents import Agent, Runner
from agents_sdk_models import OllamaModel

async def main():
    # Ollamaモデルを初期化
    model = OllamaModel(
        model="llama3",  # または他のOllamaインスタンスで利用可能なモデル
        temperature=0.7
    )
    
    # モデルを使用してエージェントを作成
    agent = Agent(
        name="アシスタント",
        instructions="あなたは役立つアシスタントです。",
        model=model
    )
    
    # エージェントを実行
    response = await Runner.run(agent, "あなたの名前と何ができるか教えてください。")
    print(response.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

### Google Gemini

```python
import asyncio
import os
from agents import Agent, Runner
from agents_sdk_models import GeminiModel

async def main():
    # 環境変数からAPIキーを取得
    api_key = os.environ.get("GOOGLE_API_KEY")
    
    # Geminiモデルを初期化
    model = GeminiModel(
        model="gemini-1.5-pro",
        temperature=0.7,
        api_key=api_key
    )
    
    # モデルを使用してエージェントを作成
    agent = Agent(
        name="アシスタント",
        instructions="あなたは役立つアシスタントです。",
        model=model
    )
    
    # エージェントを実行
    response = await Runner.run(agent, "あなたの名前と何ができるか教えてください。")
    print(response.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

### Anthropic Claude

```python
import asyncio
import os
from agents import Agent, Runner
from agents_sdk_models import ClaudeModel

async def main():
    # 環境変数からAPIキーを取得
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    # Claudeモデルを初期化
    model = ClaudeModel(
        model="claude-3-sonnet-20240229",
        temperature=0.7,
        api_key=api_key,
        thinking=True  # 複雑な推論のための思考機能を有効化
    )
    
    # モデルを使用してエージェントを作成
    agent = Agent(
        name="アシスタント",
        instructions="あなたは役立つアシスタントです。",
        model=model
    )
    
    # エージェントを実行
    response = await Runner.run(agent, "あなたの名前と何ができるか教えてください。")
    print(response.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

## 📊 構造化出力

すべてのモデルがPydanticモデルを使用した構造化出力をサポートしています：

```python
from pydantic import BaseModel
from typing import List

class WeatherInfo(BaseModel):
    location: str
    temperature: float
    condition: str
    recommendation: str

class WeatherReport(BaseModel):
    report_date: str
    locations: List[WeatherInfo]

# 構造化出力を持つエージェントを作成
agent = Agent(
    name="天気レポーター",
    model=model,
    instructions="あなたは役立つ天気レポーターです。",
    output_type=WeatherReport
)

# 構造化レスポンスを取得
response = await Runner.run(agent, "東京、大阪、札幌の天気はどうですか？")
weather_report = response.final_output  # これはWeatherReportオブジェクト
```

## 🔧 サポートされている環境

- **オペレーティングシステム**: Windows、macOS、Linux
- **Pythonバージョン**: 3.11以上
- **依存関係**: 
  - openai>=1.66.2
  - openai-agents==0.0.4
  - pydantic>=2.10, <3 (構造化出力を使用する例のため)

## 📝 ライセンス

このプロジェクトはMITライセンスの下で提供されています - 詳細はLICENSEファイルをご覧ください。

## 🙏 謝辞

- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
- [Ollama](https://ollama.ai/)
- [Google Gemini](https://ai.google.dev/)
- [Anthropic Claude](https://www.anthropic.com/claude) 