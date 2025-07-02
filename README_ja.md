# Refinire — Refined Simplicity for Agentic AI
ひらめきを"すぐに動く"へ、直感的エージェント・フレームワーク

## Why Refinire?

- **Simple installation** — Just `pip install refinire`
- **Simplify LLM-specific configuration** — No complex setup required
- **Unified API across providers** — OpenAI / Anthropic / Google / Ollama  
- **Built-in evaluation & regeneration loops** — Quality assurance out of the box
- **One-line parallel processing** — Complex async operations with just `{"parallel": [...]}`

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

**課題**: 複雑なAIワークフローの構築には、複数のエージェント、条件ロジック、並列処理、エラーハンドリングの管理が必要です。従来のアプローチは硬直で保守が困難なコードにつながります。

**解決策**: RefinireのFlow Architectureは、再利用可能なステップからワークフローを構成できます。各ステップは関数、条件、並列実行、AIエージェントのいずれかになります。フローはルーティング、エラー回復、状態管理を自動的に処理します。

**主な利点**:
- **コンポーザブル設計**: シンプルで再利用可能なコンポーネントから複雑なワークフローを構築
- **視覚的ロジック**: ワークフロー構造がコードから即座に明確
- **自動オーケストレーション**: フローエンジンが実行順序とデータ受け渡しを処理
- **組み込み並列化**: シンプルな構文で劇的なパフォーマンス向上

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

## 1. Unified LLM Interface（統一LLMインターフェース）

**課題**: AIプロバイダーの切り替えには、異なるSDK、API、認証方法が必要です。複数のプロバイダー統合の管理は、ベンダーロックインと複雑さを生み出します。

**解決策**: RefinireAgentは、すべての主要LLMプロバイダーに対して単一の一貫したインターフェースを提供します。プロバイダーの選択は環境設定に基づいて自動的に行われ、複数のSDKの管理やプロバイダー切り替え時のコード書き換えが不要になります。

**主な利点**:
- **プロバイダーの自由度**: OpenAI、Anthropic、Google、Ollamaをコード変更なしで切り替え
- **ベンダーロックインゼロ**: エージェントロジックはプロバイダー固有の詳細から独立
- **自動解決**: 環境変数が最適なプロバイダーを自動的に決定
- **一貫したAPI**: すべてのプロバイダーで同じメソッド呼び出しが動作

```python
from refinire import RefinireAgent

# モデル名を指定するだけで自動的にプロバイダーが解決されます
agent = RefinireAgent(
    name="assistant",
    generation_instructions="親切なアシスタントです",
    model="gpt-4o-mini"  # OpenAI
)

# Anthropic, Google, Ollama も同様にモデル名だけでOK
agent2 = RefinireAgent(
    name="anthropic_assistant",
    generation_instructions="Anthropicモデル用",
    model="claude-3-sonnet"  # Anthropic
)

agent3 = RefinireAgent(
    name="google_assistant",
    generation_instructions="Google Gemini用",
    model="gemini-pro"  # Google
)

agent4 = RefinireAgent(
    name="ollama_assistant",
    generation_instructions="Ollamaモデル用",
    model="llama3.1:8b"  # Ollama
)
```

これにより、プロバイダー間の切り替えやAPIキーの管理が非常に簡単になり、開発の柔軟性が大幅に向上します。

**📖 チュートリアル:** [クイックスタートガイド](docs/tutorials/quickstart_ja.md) | **詳細:** [統一LLMインターフェース](docs/unified-llm-interface.md)

## 2. Autonomous Quality Assurance（自律品質保証）

**課題**: AIの出力は一貫性がなく、手動レビューや再生成が必要です。品質管理が本番システムのボトルネックになります。

**解決策**: RefinireAgentには、出力品質を自動評価し、基準を下回った場合にコンテンツを再生成する組み込み評価機能があります。これにより、手動介入なしで一貫した品質を維持する自己改善システムを作成できます。

**主な利点**:
- **自動品質管理**: 閾値を設定してシステムに基準維持を任せる
- **自己改善**: 失敗した出力は改善されたプロンプトで再生成をトリガー
- **本番対応**: 手動監視なしで一貫した品質
- **設定可能な基準**: 独自の評価基準と閾値を定義

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

# ワークフロー統合用のContextを使用
from refinire import Context
ctx = Context()
result_ctx = agent.run("量子コンピューティングを説明して", ctx)
print(f"評価結果: {result_ctx.evaluation_result}")
print(f"スコア: {result_ctx.evaluation_result['score']}")
print(f"合格: {result_ctx.evaluation_result['passed']}")
print(f"フィードバック: {result_ctx.evaluation_result['feedback']}")
```

評価が閾値を下回った場合、自動的に再生成されるため、常に高品質な出力が保証されます。

**📖 チュートリアル:** [高度な機能](docs/tutorials/advanced.md) | **詳細:** [自律品質保証](docs/autonomous-quality-assurance.md)

## 3. Tool Integration - 関数呼び出しの自動化

**課題**: AIエージェントは外部システム、API、計算と相互作用する必要があることが多いです。手動ツール統合は複雑でエラーが発生しやすいです。

**解決策**: RefinireAgentはツールを使用するタイミングを自動検出し、シームレスに実行します。デコレートされた関数を提供するだけで、エージェントがツール選択、パラメータ抽出、実行を自動的に処理します。

**主な利点**:
- **設定ゼロ**: デコレートされた関数が自動的にツールとして利用可能
- **インテリジェント選択**: ユーザーリクエストに基づいて適切なツールを選択
- **エラーハンドリング**: ツール実行の組み込みリトライとエラー回復
- **拡張可能**: 特定のユースケース用のカスタムツールを簡単に追加

RefinireAgentは関数ツールを自動的に実行します。

```python
from refinire import RefinireAgent, tool

@tool
def calculate(expression: str) -> float:
    """数式を計算する"""
    return eval(expression)

@tool
def get_weather(city: str) -> str:
    """都市の天気を取得"""
    return f"{city}の天気: 晴れ、22℃"

# ツール付きエージェント
agent = RefinireAgent(
    name="tool_assistant",
    generation_instructions="ツールを使って質問に答えてください",
    tools=[calculate, get_weather],
    model="gpt-4o-mini"
)

result = agent.run("東京の天気は？あと、15 * 23は？")
print(result.content)  # 両方の質問に自動的に答えます
```

**📖 チュートリアル:** [高度な機能](docs/tutorials/advanced.md) | **詳細:** [組み合わせ可能なフローアーキテクチャ](docs/composable-flow-architecture.md)

## 4. 自動並列処理: 劇的なパフォーマンス向上

**課題**: 独立したタスクの順次処理は不必要なボトルネックを作り出します。手動の非同期実装は複雑でエラーが発生しやすいです。

**解決策**: Refinireの並列処理は、独立した操作を自動的に識別し、同時に実行します。操作を`parallel`ブロックでラップするだけで、システムがすべての非同期調整を処理します。

**主な利点**:
- **自動最適化**: システムが並列化可能な操作を識別
- **劇的な高速化**: 4倍以上のパフォーマンス向上が一般的
- **複雑さゼロ**: async/awaitやスレッド管理が不要
- **スケーラブル**: 設定可能なワーカープールがワークロードに適応

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

# 順次実行: 2.0秒 → 並列実行: 0.5秒（大幅な高速化）
result = await flow.run("この包括的なテキストを分析...")
```

この機能により、複雑な分析タスクを複数同時実行でき、開発者が手動で非同期処理を実装する必要がありません。

**📖 チュートリアル:** [高度な機能](docs/tutorials/advanced.md) | **詳細:** [組み合わせ可能なフローアーキテクチャ](docs/composable-flow-architecture.md)

## 5. コンテキスト管理 - インテリジェントメモリ

**課題**: AIエージェントは会話間でコンテキストを失い、関連ファイルやコードの認識がありません。これは繰り返しの質問や、あまり役に立たない回答につながります。

**解決策**: RefinireAgentのコンテキスト管理は、会話履歴を自動的に維持し、関連ファイルを分析し、関連情報をコードベースから検索します。エージェントはプロジェクトの包括的な理解を構築し、会話を通じてそれを維持します。

**主な利点**:
- **永続的メモリ**: 会話は以前のインタラクションを基盤に構築
- **コード認識**: 関連ソースファイルの自動分析
- **動的コンテキスト**: 現在の会話トピックに基づいてコンテキストが適応
- **インテリジェントフィルタリング**: トークン制限を避けるために関連情報のみが含まれる

RefinireAgentは高度なコンテキスト管理機能を提供し、会話をより豊かにします。

```python
from refinire import RefinireAgent

# 会話履歴とファイルコンテキストを持つエージェント
agent = RefinireAgent(
    name="code_assistant",
    generation_instructions="コード分析と改善を支援します",
    context_providers_config=[
        {
            "type": "conversation_history",
            "max_items": 10
        },
        {
            "type": "fixed_file",
            "file_path": "src/main.py",
            "description": "メインアプリケーションファイル"
        },
        {
            "type": "source_code",
            "base_path": "src/",
            "file_patterns": ["*.py"],
            "max_files": 5
        }
    ],
    model="gpt-4o-mini"
)

# コンテキストは会話全体で自動的に管理されます
result = agent.run("メイン関数は何をしていますか？")
print(result.content)

# コンテキストは保持され、進化します
result = agent.run("エラーハンドリングをどのように改善できますか？")
print(result.content)
```

**📖 チュートリアル:** [コンテキスト管理](docs/tutorials/context_management_ja.md) | **詳細:** [コンテキスト管理](docs/context_management.md)

### コンテキストベース結果アクセス

**課題**: 複数のAIエージェントを連鎖するには、複雑なデータ受け渡しと状態管理が必要です。あるエージェントの結果を次のエージェントにシームレスに流す必要があります。

**解決策**: RefinireのContextシステムは、エージェントの結果、評価データ、共有状態を自動的に追跡します。エージェントは手動状態管理なしで、以前の結果、評価スコア、カスタムデータにアクセスできます。

**主な利点**:
- **自動状態管理**: Contextがエージェント間のデータフローを処理
- **豊富な結果アクセス**: 出力だけでなく評価スコアやメタデータにもアクセス
- **柔軟なデータストレージ**: 複雑なワークフロー要件用のカスタムデータを保存
- **シームレス統合**: エージェント通信用のボイラープレートコードが不要

Contextを通じてエージェントの結果と評価データにアクセスし、シームレスなワークフロー統合を実現：

```python
from refinire import RefinireAgent, Context, create_evaluated_agent

# 評価機能付きエージェント作成
agent = create_evaluated_agent(
    name="analyzer",
    generation_instructions="入力を徹底的に分析してください",
    evaluation_instructions="分析品質を0-100で評価してください",
    threshold=80
)

# Contextで実行
ctx = Context()
result_ctx = agent.run("このデータを分析して", ctx)

# シンプルな結果アクセス
print(f"結果: {result_ctx.result}")

# 評価結果アクセス
if result_ctx.evaluation_result:
    score = result_ctx.evaluation_result["score"]
    passed = result_ctx.evaluation_result["passed"]
    feedback = result_ctx.evaluation_result["feedback"]
    
# エージェント連携でのデータ受け渡し
next_agent = create_simple_agent("summarizer", "要約を作成してください")
summary_ctx = next_agent.run(f"要約: {result_ctx.result}", result_ctx)

# 前のエージェントの出力にアクセス
analyzer_output = summary_ctx.prev_outputs["analyzer"]
summarizer_output = summary_ctx.prev_outputs["summarizer"]

# カスタムデータ保存
result_ctx.shared_state["custom_data"] = {"key": "value"}
```

**自動結果追跡によるエージェント間のシームレスなデータフロー。**

## Architecture Diagram

Learn More
Examples — 充実のレシピ集
API Reference — 型ヒント付きで迷わない
Contributing — 初回PR歓迎！

Refinire は、複雑さを洗練されたシンプルさに変えることで、AIエージェント開発をより直感的で効率的なものにします。

---

## リリースノート - v0.2.8

### 🛠️ 革新的なツール統合
- **新しい @tool デコレータ**: シームレスなツール作成のための直感的な `@tool` デコレータを導入
- **簡素化されたインポート**: 複雑な外部SDK知識に代わるクリーンな `from refinire import tool`
- **デバッグ機能の強化**: より良いツール内省のための `get_tool_info()` と `list_tools()` を追加
- **後方互換性**: 既存の `function_tool` デコレータ関数の完全サポート
- **簡素化されたツール開発**: 直感的なデコレータ構文による合理化されたツール作成プロセス

### 📚 ドキュメントの革新
- **コンセプト駆動の説明**: READMEは課題-解決策-利点構造に焦点
- **チュートリアル統合**: すべての機能セクションがステップバイステップチュートリアルにリンク
- **明確性の向上**: コード例の前に明確な説明で認知負荷を軽減
- **バイリンガル強化**: 英語と日本語の両ドキュメントが大幅に改善
- **ユーザー中心のアプローチ**: 開発者の視点から再設計されたドキュメント

### 🔄 開発者体験の変革
- **統一インポート戦略**: すべてのツール機能が単一の `refinire` パッケージから利用可能
- **将来対応アーキテクチャ**: 外部SDKの変更から分離されたツールシステム
- **強化されたメタデータ**: デバッグと開発のための豊富なツール情報
- **インテリジェントエラーハンドリング**: より良いエラーメッセージとトラブルシューティングガイダンス
- **合理化されたワークフロー**: アイデアから動作するツールまで5分以内

### 🚀 品質とパフォーマンス
- **コンテキストベース評価**: ワークフロー統合のための新しい `ctx.evaluation_result`
- **包括的テスト**: すべての新しいツール機能の100%テストカバレッジ
- **移行例**: 完全な移行ガイドと比較デモンストレーション
- **API一貫性**: すべてのRefinireコンポーネント全体で統一されたパターン
- **破壊的変更ゼロ**: 既存コードは動作し続け、新機能が能力を向上

### 💡 ユーザーにとっての主な利点
- **高速なツール開発**: 合理化されたワークフローによりツール作成時間を大幅短縮
- **学習曲線の軽減**: 外部SDKの複雑さを理解する必要がない
- **より良いデバッグ**: 豊富なメタデータと内省機能
- **将来的な互換性**: 外部SDKの破壊的変更から保護
- **直感的な開発**: すべての開発者に馴染みのある自然なPythonデコレータパターン

**このリリースは、Refinireを最も開発者フレンドリーなAIエージェントプラットフォームにするための大きな前進を表しています。**