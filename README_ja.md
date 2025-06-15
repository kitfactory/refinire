# Refinire — Refined Simplicity for Agentic AI
ひらめきを“すぐに動く”へ、直感的エージェント・フレームワーク

# Why Refinire?

- 簡単インストール pip install refinireだけ
- LLM特有の設定、複雑な手順を簡単に
- プロバイダー — OpenAI / Anthropic / Google / Ollama を共通APIで
- 自動評価&再生成ループが既に構築済み
- 並列処理を一行で実現 — 複雑な非同期処理も `{"parallel": [...]}` だけ

# 30-Second Quick Start

```bash
> pip install refinire
```

```python
from refinire import RefinireAgent

# シンプルなAIエージェント
agent = RefinireAgent(
    name="assistant",
    generation_instructions="親切なアシスタントです",
    model="gpt-4o-mini"
)

result = agent.run("こんにちは")
print(result.content)
```

## The Core Components

Refinire は、AI エージェント開発を支える主要コンポーネントを提供します。

## RefinireAgent - 生成と評価の統合

```python
from refinire import RefinireAgent

# 自動評価付きエージェント
agent = RefinireAgent(
    name="quality_writer",
    generation_instructions="高品質なコンテンツを生成してください",
    evaluation_instructions="品質を0-100で評価してください",
    threshold=85.0,  # 85点未満は自動的に再生成
    max_retries=3,
    model="gpt-4o-mini"
)

result = agent.run("AIについての記事を書いて")
print(f"品質スコア: {result.evaluation_score}点")
print(f"生成内容: {result.content}")
```

## Flow Architecture - 複雑なワークフローの構築

```python
from refinire import Flow, FunctionStep, ConditionStep, ParallelStep

# 条件分岐と並列処理を含むフロー
flow = Flow({
    "analyze": FunctionStep("analyze", analyze_input),
    "route": ConditionStep("route", check_complexity, "simple", "complex"),
    "simple": RefinireAgent(name="simple", generation_instructions="簡潔に回答"),
    "complex": ParallelStep("experts", [
        RefinireAgent(name="expert1", generation_instructions="詳細な分析"),
        RefinireAgent(name="expert2", generation_instructions="別の視点から分析")
    ]),
    "combine": FunctionStep("combine", aggregate_results)
})

result = await flow.run("複雑なユーザーリクエスト")
```

## 1. Unified LLM Interface
複数の LLM プロバイダーを統一されたインターフェースで扱うことができます。

```python
from refinire import get_llm

llm = get_llm("gpt-4o-mini")      # OpenAI
llm = get_llm("claude-3-sonnet")  # Anthropic
llm = get_llm("gemini-pro")       # Google
llm = get_llm("llama3.1:8b")      # Ollama
```

これにより、プロバイダー間の切り替えが容易になり、開発の柔軟性が向上します。

**📖 詳細:** [統一LLMインターフェース](docs/unified-llm-interface.md)

## 2. Autonomous Quality Assurance
RefinireAgentに組み込まれた自動評価機能により、出力品質を保証します。

```python
from refinire import RefinireAgent

# 評価ループ付きエージェント
agent = RefinireAgent(
    name="quality_assistant",
    generation_instructions="役立つ回答を生成してください",
    evaluation_instructions="正確性と有用性を0-100で評価してください",
    threshold=85.0,
    max_retries=3,
    model="gpt-4o-mini"
)

result = agent.run("量子コンピューティングを説明して")
print(f"評価スコア: {result.evaluation_score}点")
print(f"生成内容: {result.content}")
```

評価が閾値を下回った場合、自動的に再生成されるため、常に高品質な出力が保証されます。

**📖 詳細:** [自律品質保証](docs/autonomous-quality-assurance.md)

## 3. Tool Integration - 関数呼び出しの自動化
RefinireAgentは関数ツールを自動的に実行します。

```python
from refinire import RefinireAgent

def calculate(expression: str) -> float:
    """数式を計算する"""
    return eval(expression)

def get_weather(city: str) -> str:
    """都市の天気を取得"""
    return f"{city}の天気: 晴れ、22℃"

# ツール付きエージェント
agent = RefinireAgent(
    name="tool_assistant",
    generation_instructions="ツールを使って質問に答えてください",
    model="gpt-4o-mini"
)

agent.add_function_tool(calculate)
agent.add_function_tool(get_weather)

result = agent.run("東京の天気は？あと、15 * 23は？")
print(result.content)  # 両方の質問に自動的に答えます
```

**📖 詳細:** [組み合わせ可能なフローアーキテクチャ](docs/composable-flow-architecture.md)

## 4. 自動並列処理: 3.9倍高速化
複雑な処理を並列実行して劇的にパフォーマンスを向上させます。

```python
from refinire import Flow, FunctionStep
import asyncio

# DAG構造で並列処理を定義
flow = Flow(start="preprocess", steps={
    "preprocess": FunctionStep("preprocess", preprocess_text),
    "parallel_analysis": {
        "parallel": [
            FunctionStep("sentiment", analyze_sentiment),
            FunctionStep("keywords", extract_keywords), 
            FunctionStep("topic", classify_topic),
            FunctionStep("readability", calculate_readability)
        ],
        "next_step": "aggregate",
        "max_workers": 4
    },
    "aggregate": FunctionStep("aggregate", combine_results)
})

# 順次実行: 2.0秒 → 並列実行: 0.5秒（3.9倍高速化）
result = await flow.run("この包括的なテキストを分析...")
```

この機能により、複雑な分析タスクを複数同時実行でき、開発者が手動で非同期処理を実装する必要がありません。

**📖 詳細:** [組み合わせ可能なフローアーキテクチャ](docs/composable-flow-architecture.md)

## Architecture Diagram

Learn More
Examples — 充実のレシピ集
API Reference — 型ヒント付きで迷わない
Contributing — 初回PR歓迎！

Refinire は、複雑さを洗練されたシンプルさに変えることで、AIエージェント開発をより直感的で効率的なものにします。

---

## リリースノート - v0.2.1

### 新機能
- **P() 関数**: `PromptStore.get()` の便利な短縮エイリアス - `PromptStore.get("name")` の代わりに `P("name")` でプロンプトにアクセス可能

### アーキテクチャの改善
- **単一パッケージ構造**: マルチパッケージ構造から統一パッケージ構造に統合し、保守性を向上
- **階層の再編成**: flow と pipeline モジュールを `agents` サブパッケージ下に移動してより清潔な構造に
- **依存関係の更新**: Python 3.10+ 要件と OpenAI Agents SDK 0.0.17+ にアップグレード

### 品質 & テスト
- **100% テスト合格率**: 包括的な移行修正により、408個のテストがすべて合格
- **72% テストカバレッジ**: 70% から 72% にコードカバレッジが向上し、テスト品質も改善
- **互換性の強化**: Pydantic v2 互換性と Context API の改善を修正

### 開発者体験
- **シンプルなインポート**: すべての機能が単一の `refinire` パッケージ経由でアクセス可能
- **より良い構造**: core、agents、flow、pipeline モジュール間の明確な分離
- **後方互換性の維持**: 既存のコードは新しい構造でも継続して動作