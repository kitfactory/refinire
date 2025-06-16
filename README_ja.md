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

## リリースノート - v0.2.5

### 🎯 RefinireAgentへの完全移行
- **LLMPipeline廃止**: 非推奨の`LLMPipeline`をモダンな`RefinireAgent`アーキテクチャに完全置換
- **統一エージェントシステム**: すべての専用エージェント（ExtractorAgent、GenAgent、RouterAgent、ClarifyAgent）が内部でRefinireAgentを使用
- **破壊的変更**: `LLMPipeline`と関連ファクトリ関数を完全削除 - 代わりに`RefinireAgent`を使用
- **移行ガイド**: すべての例とドキュメントがRefinireAgent使用法を反映するよう更新

### 🔧 コードモダナイゼーション
- **インポート更新**: 非推奨の`agents.models`インポートを削除し、`agents`パッケージの直接使用に更新
- **例の刷新**: 30以上の例ファイルを`AgentPipeline`から`RefinireAgent`に更新
- **テストスイートクリーンアップ**: 非推奨のAgentPipelineテストを削除し、453のテストをRefinireAgent使用に更新
- **API一貫性**: 関数命名の統一（例：`create_simple_agent` vs `create_simple_llm_pipeline`）

### ✅ 品質 & 互換性
- **100% テスト合格率**: 包括的な移行後、453のテストがすべて合格
- **破壊的変更ゼロ**: 移行はアーキテクチャをモダン化しながら機能を維持
- **安定性向上**: レガシーコード削除により保守負担軽減と信頼性向上
- **将来対応**: 今後の機能のためのモダンアーキテクチャ基盤

### 📖 ドキュメント & 例
- **完全ドキュメント更新**: すべてのガイドがRefinireAgentパターンを使用
- **例のモダン化**: パイプライン例をRefinireAgent機能実証に変換
- **明確な移行パス**: レガシーユーザーがRefinireAgentにシームレスにアップグレード可能
- **明確性向上**: すべてのコンポーネントで一貫した命名とパターン

### 🚀 開発者体験
- **簡素化されたメンタルモデル**: 単一エージェントシステムが認知負荷を軽減
- **一貫したAPI**: すべてのエージェントタイプと使用ケースで統一インターフェース
- **パフォーマンス向上**: レガシーオーバーヘッド削減による最適化アーキテクチャ
- **保守性向上**: よりクリーンなコードベース構造と組織化

---

## 過去のリリースノート

### v0.2.4
- **インポート修正**: `agents.models`インポート問題を解決し、`agents`パッケージの直接使用に更新
- **安定性向上**: より良いエラーハンドリングと互換性修正による信頼性向上
- **テストカバレッジ**: 453テストで100%合格率を維持

### v0.2.1
- **P() 関数**: `PromptStore.get("name")` の便利な短縮形 `P("name")`
- **単一パッケージ構造**: 保守性向上のための統一パッケージアーキテクチャ
- **互換性強化**: Pydantic v2 互換性修正とテストカバレッジ77%向上