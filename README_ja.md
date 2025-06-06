# 🤖 Agents SDK Models

**複数のLLMプロバイダーに対応した統一インターフェース**

agents-sdk-modelsは、OpenAI、Anthropic、Google、Ollamaなどの様々なLLMプロバイダーを統一インターフェースで利用できるPythonライブラリです。

## ✨ 特徴

- **🔄 統一インターフェース**: すべての主要LLMプロバイダーを同じAPIで利用
- **🛠️ 自動Tool実行**: LLMが必要に応じてツールを自動実行  
- **🔧 簡単設定**: 最小限のコードで強力なAIパイプラインを構築
- **📊 品質評価**: コンテンツの自動評価とスコアリング
- **🛡️ 安全機能**: 入出力のガードレール機能
- **🚀 非同期対応**: 高性能な非同期処理に対応

## 🚀 クイックスタート

### インストール

```bash
uv add agents-sdk-models
# または
pip install agents-sdk-models
```

### 基本的な使用方法

```python
from agents_sdk_models import get_llm

# 任意のプロバイダーのLLMを取得
llm = get_llm(provider="openai", model="gpt-4o-mini")
response = llm.complete("こんにちは！")
print(response)
```

## 🛠️ LLMPipeline: 次世代ツール対応AIパイプライン

**✅ 推奨:** `LLMPipeline`は、OpenAI Python SDKを直接使用した最新の安定実装で、完全なツールサポートと自動関数呼び出し機能を提供します。

### 🚀 主要機能

- **🔧 自動ツール実行**: LLMが必要に応じてツールを自動判断・実行
- **🚀 手動呼び出し不要**: ツールはLLMが必要なときに自動実行
- **🔄 関数呼び出しループ**: 複雑な複数ツールワークフローを自動処理
- **📊 組み込み評価**: オプションのコンテンツ評価とスコアリング
- **🛡️ ガードレール**: 入出力の検証と安全性チェック
- **💾 セッション履歴**: 会話コンテキストの維持
- **🎯 構造化出力**: Pydanticモデルによる型付きレスポンス

### ツール付きクイックスタート

```python
from agents_sdk_models import create_tool_enabled_llm_pipeline

# ツールをシンプルなPython関数として定義
def get_weather(city: str) -> str:
    """都市の現在の天気を取得"""
    # 天気API統合をここに実装
    return f"{city}の天気: 晴れ、22°C"

def calculate(expression: str) -> float:
    """数式を計算"""
    return eval(expression)  # 本番環境ではより安全な評価を使用

# 自動ツール登録でパイプラインを作成
pipeline = create_tool_enabled_llm_pipeline(
    name="スマートアシスタント",
    instructions="ツールにアクセスできる親切なアシスタントです。必要に応じて使用してください。",
    tools=[get_weather, calculate],  # ツールが自動登録される
    model="gpt-4o-mini"
)

# パイプラインを使用 - ツールが自動実行される！ 🎯
result = pipeline.run("東京の天気と15 * 23の計算結果を教えて")
print(result.content)
# LLMが自動的に:
# 1. get_weather("東京")を呼び出し
# 2. calculate("15 * 23")を呼び出し  
# 3. 結果を自然な応答にまとめる
```

### 🏗️ 事前構築されたパイプラインタイプ

```python
from agents_sdk_models import (
    create_calculator_pipeline,
    create_web_search_pipeline,
    create_evaluated_llm_pipeline
)

# 🧮 安全な数学評価付き計算機パイプライン
calc_pipeline = create_calculator_pipeline(
    name="数学アシスタント",
    model="gpt-4o-mini"
)

# 🔍 Web検索パイプライン（検索統合のテンプレート）
search_pipeline = create_web_search_pipeline(
    name="検索アシスタント",
    model="gpt-4o-mini"
)

# ⭐ 評価と品質管理付きパイプライン
quality_pipeline = create_evaluated_llm_pipeline(
    name="品質アシスタント",
    generation_instructions="役立つ正確な情報を提供してください。",
    evaluation_instructions="正確性、有用性、明確性を評価してください（0-100）。",
    threshold=80.0,  # 最小品質スコア
    model="gpt-4o-mini"
)
```

### ⚙️ 手動ツール管理

```python
from agents_sdk_models import LLMPipeline

# パイプラインを作成し、ツールを動的に追加
pipeline = LLMPipeline(
    name="カスタムアシスタント",
    generation_instructions="親切なアシスタントです。",
    model="gpt-4o-mini",
    tools=[]
)

# ツールを一つずつ追加
def greet(name: str) -> str:
    """ユーザーを名前で挨拶"""
    return f"こんにちは、{name}さん！"

pipeline.add_function_tool(greet)

# ツール管理
print(f"利用可能なツール: {pipeline.list_tools()}")
pipeline.remove_tool("greet")
```

### 📊 LLMPipelineが優れている理由

| 機能 | AgentPipeline（非推奨） | LLMPipeline（推奨） |
|------|------------------------|-------------------|
| **API依存** | ❌ OpenAI Agents SDK（非推奨API） | ✅ OpenAI Python SDK（安定） |
| **ツール実行** | ⚠️ 手動実装が必要 | ✅ 自動ツール呼び出しループ |
| **関数呼び出し** | ⚠️ 限定的サポート | ✅ 完全なOpenAI関数呼び出し |
| **将来性** | ❌ v0.1.0で削除予定 | ✅ 安定、積極的に保守 |
| **非同期問題** | ❌ Flow統合の問題 | ✅ クリーンな非同期/同期サポート |
| **ツール登録** | ⚠️ 複雑な設定 | ✅ シンプルな関数装飾 |

---

## 🔄 複数プロバイダー対応

### 利用例: 複数プロバイダーの使用

```python
from agents_sdk_models import get_llm

# 複数のプロバイダーをテスト
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

---

## 🖥️ サポート環境

- Python 3.9+
- OpenAI Agents SDK 0.0.9+
- Windows, Linux, MacOS

---

## 💡 なぜこのライブラリを使うのか？

- **統一性**: すべての主要LLMプロバイダーに対する単一インターフェース
- **柔軟性**: 生成、評価、ツール、ガードレールを自由に組み合わせ
- **簡単**: 最小限のコードで開始、高度なワークフローにも対応
- **安全**: コンプライアンスと安全のためのガードレール
- **自己改善**: 最小設定での自動フィードバックと再試行メカニズム

---

## 📂 使用例

より高度な使用方法については`examples/`ディレクトリを参照してください：
- `llm_pipeline_example.py`: LLMPipelineのツール機能例
- `pipeline_simple_generation.py`: 最小限の生成例
- `pipeline_with_evaluation.py`: 生成 + 評価
- `pipeline_with_tools.py`: ツール拡張生成
- `pipeline_with_guardrails.py`: ガードレール（入力フィルタリング）

---

## 📄 ライセンスとクレジット

MITライセンス。[OpenAI Agents SDK](https://github.com/openai/openai-agents-python)によって支援されています。