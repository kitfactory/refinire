# Refinire — Refined Simplicity for Agentic AI
ひらめきを“すぐに動く”へ変える、洗練されたエージェント・フレームワーク

# Why Refinire?
- 設定沼からの解放 — 2行でLLMエージェントが起動
- プロバイダーの壁を溶かす — OpenAI / Anthropic / Google / Ollama を同一APIで
- 品質はコードに埋め込む — 自動評価&再生成ループで常に≥85点
- 並列処理を一行で実現 — 複雑な非同期処理が `{"parallel": [...]}` だけ

# 30-Second Quick Start

```bash
> pip install refinire
```

```python
from refinire import create_simple_gen_agent, Context
agent = create_simple_gen_agent("assistant", "親切なアシスタントです", model="gpt-4o-mini")
print(agent.run_sync("こんにちは", Context()).text)
```

## The Four Pillars

Refinire は、AI エージェント開発を支える四つの柱を提供します。これらは、開発者が効率的かつ柔軟にエージェントを構築するための基盤です。

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
エージェントの出力品質を自動的に評価し、必要に応じて再生成を行います。

```python
from refinire import create_evaluated_gen_agent, Context
import asyncio

agent = create_evaluated_gen_agent(
    name="quality_assistant",
    generation_instructions="役立つ回答を生成してください",
    evaluation_instructions="正確性と有用性を評価してください",
    threshold=85.0,
    model="gpt-4o-mini"
)

result = asyncio.run(agent.run("量子コンピューティングを説明して", Context()))
print(result.shared_state["quality_assistant_result"])
```

この機能により、エージェントの品質を維持しながら、開発者の手間を削減できます。

**📖 詳細:** [自律品質保証](docs/autonomous-quality-assurance.md)

## 3. Composable Flow Architecture
エージェントの処理フローを柔軟に構築できます。

```python
from refinire import Flow, FunctionStep
import asyncio

flow = Flow([
    ("analyze", FunctionStep("analyze", analyze_input)),
    ("respond", FunctionStep("respond", generate_response))
])

result = asyncio.run(flow.run(input_data="ユーザーリクエスト"))
print(result.shared_state["response"])
```

このアーキテクチャにより、処理の再利用性と拡張性が向上し、複雑なワークフローの構築が容易になります。

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