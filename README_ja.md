# Refinire — Refined Simplicity for Agentic AI
ひらめきを"すぐに動く"へ、直感的エージェント・フレームワーク

## Why Refinire?

- **Simple installation** — Just `pip install refinire`
- **Simplify LLM-specific configuration** — No complex setup required
- **Unified API across providers** — OpenAI / Anthropic / Google / Ollama  
- **Built-in evaluation & regeneration loops** — Quality assurance out of the box
- **One-line parallel processing** — Complex async operations with just `{"parallel": [...]}`
- **Comprehensive observability** — Automatic tracing with OpenTelemetry integration

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
    generation_instructions="明確な構成と魅力的な文体で、高品質で情報豊富なコンテンツを生成してください",
    evaluation_instructions="""以下の基準でコンテンツ品質を0-100点で評価してください：
    - 明確性と読みやすさ（0-25点）
    - 正確性と事実の正しさ（0-25点）
    - 構成と組織化（0-25点）
    - 魅力的な文体とエンゲージメント（0-25点）
    
    評価結果は以下の形式で提供してください：
    スコア: [0-100]
    コメント:
    - [強みに関する具体的なフィードバック]
    - [改善点]
    - [向上のための提案]""",
    threshold=85.0,  # 85点未満は自動的に再生成
    max_retries=3,
    model="gpt-4o-mini"
)

result = agent.run("AIについての記事を書いて")
print(f"品質スコア: {result.evaluation_score}点")
print(f"生成内容: {result.content}")
```

## ストリーミング出力 - リアルタイム応答表示

**リアルタイムでレスポンスをストリーミング**することで、ユーザー体験の向上と即座のフィードバックを実現します。RefinireAgentとFlowの両方がストリーミング出力をサポートし、チャットインターフェース、ライブダッシュボード、インタラクティブアプリケーションに最適です。

### 基本的なRefinireAgentストリーミング

```python
from refinire import RefinireAgent

agent = RefinireAgent(
    name="streaming_assistant",
    generation_instructions="詳細で役立つ回答を提供してください",
    model="gpt-4o-mini"
)

# レスポンスチャンクを到着と同時にストリーミング
async for chunk in agent.run_streamed("量子コンピューティングを説明してください"):
    print(chunk, end="", flush=True)  # リアルタイム表示
```

### コールバック処理付きストリーミング

```python
# 各チャンクをカスタム処理
chunks_received = []
def process_chunk(chunk: str):
    chunks_received.append(chunk)
    # WebSocketに送信、UIを更新、ファイルに保存等

async for chunk in agent.run_streamed(
    "Pythonチュートリアルを書いて", 
    callback=process_chunk
):
    print(chunk, end="", flush=True)

print(f"\n{len(chunks_received)}個のチャンクを受信")
```

### コンテキスト対応ストリーミング

```python
from refinire import Context

# ストリーミング応答全体で会話コンテキストを維持
ctx = Context()

# 最初のメッセージ
async for chunk in agent.run_streamed("こんにちは、Pythonを学習中です", ctx=ctx):
    print(chunk, end="", flush=True)

# コンテキスト対応のフォローアップ
ctx.add_user_message("非同期プログラミングについてはどうですか？")
async for chunk in agent.run_streamed("非同期プログラミングについてはどうですか？", ctx=ctx):
    print(chunk, end="", flush=True)
```

### Flowストリーミング

**Flowも複雑な多段階ワークフローのストリーミングをサポート**：

```python
from refinire import Flow, FunctionStep

flow = Flow({
    "analyze": FunctionStep("analyze", analyze_input),
    "generate": RefinireAgent(
        name="writer", 
        generation_instructions="詳細なコンテンツを書いてください"
    )
})

# フロー全体の出力をストリーミング
async for chunk in flow.run_streamed("技術記事を作成してください"):
    print(chunk, end="", flush=True)
```

### 構造化出力ストリーミング

**重要**: 構造化出力（Pydanticモデル）をストリーミングで使用すると、レスポンスは解析されたオブジェクトではなく**JSONチャンク**としてストリーミングされます：

```python
from pydantic import BaseModel

class Article(BaseModel):
    title: str
    content: str
    tags: list[str]

agent = RefinireAgent(
    name="structured_writer",
    generation_instructions="記事を生成してください",
    output_model=Article  # 構造化出力
)

# JSONチャンクをストリーミング: {"title": "...", "content": "...", "tags": [...]}
async for json_chunk in agent.run_streamed("AIについて書いてください"):
    print(json_chunk, end="", flush=True)
    
# 解析されたオブジェクトが必要な場合は、通常のrun()メソッドを使用：
result = await agent.run_async("AIについて書いてください")
article = result.content  # Articleオブジェクトを返す
```

**主要ストリーミング機能**:
- **リアルタイム出力**: コンテンツ生成と同時の即座の応答
- **コールバックサポート**: 各チャンクのカスタム処理
- **コンテキスト継続性**: 会話コンテキストと連携するストリーミング
- **Flow統合**: 複雑な多段階ワークフローのストリーミング
- **JSONストリーミング**: 構造化出力はJSONチャンクとしてストリーミング
- **エラーハンドリング**: ストリーミング中断の適切な処理

## Flow Architecture - 複雑なワークフローの構築

**課題**: 複雑なAIワークフローの構築には、複数のエージェント、条件ロジック、並列処理、エラーハンドリングの管理が必要です。従来のアプローチは硬直で保守が困難なコードにつながります。

**解決策**: RefinireのFlow Architectureは、再利用可能なステップからワークフローを構成できます。各ステップは関数、条件、並列実行、AIエージェントのいずれかになります。フローはルーティング、エラー回復、状態管理を自動的に処理します。

**主な利点**:
- **コンポーザブル設計**: シンプルで再利用可能なコンポーネントから複雑なワークフローを構築
- **視覚的ロジック**: ワークフロー構造がコードから即座に明確
- **自動オーケストレーション**: フローエンジンが実行順序とデータ受け渡しを処理
- **組み込み並列化**: シンプルな構文で劇的なパフォーマンス向上

```python
from refinire import Flow, FunctionStep, ConditionStep

# 条件分岐と並列処理を含むフロー
flow = Flow({
    "analyze": FunctionStep("analyze", analyze_input),
    "route": ConditionStep("route", check_complexity, "simple", "complex"),
    "simple": RefinireAgent(name="simple", generation_instructions="簡潔に回答"),
    "complex": {
        "parallel": [
            RefinireAgent(name="expert1", generation_instructions="詳細な分析"),
            RefinireAgent(name="expert2", generation_instructions="別の視点から分析")
        ],
        "next_step": "combine"
    },
    "combine": FunctionStep("combine", aggregate_results)
})

result = await flow.run("複雑なユーザーリクエスト")
```

**🎯 Flow完全ガイド**: ワークフロー構築の包括的な学習には、詳細なステップバイステップガイドをご覧ください：

**📖 日本語**: [Flow完全ガイド](docs/tutorials/flow_complete_guide_ja.md) - 基本から高度な並列処理まで完全解説  
**📖 English**: [Complete Flow Guide](docs/tutorials/flow_complete_guide_en.md) - Comprehensive workflow construction

### Flow設計パターン

**シンプルなルーティング**:
```python
# ユーザーの言語に基づく自動ルーティング
def detect_language(ctx):
    return "japanese" if any(char in ctx.user_input for char in "あいうえお") else "english"

flow = Flow({
    "detect": ConditionStep("detect", detect_language, "jp_agent", "en_agent"),
    "jp_agent": RefinireAgent(name="jp", generation_instructions="日本語で丁寧に回答"),
    "en_agent": RefinireAgent(name="en", generation_instructions="Respond in English professionally")
})
```

**高性能並列分析**:
```python
# 複数の分析を同時実行
flow = Flow(start="preprocess", steps={
    "preprocess": FunctionStep("preprocess", clean_data),
    "analysis": {
        "parallel": [
            RefinireAgent(name="sentiment", generation_instructions="感情分析を実行"),
            RefinireAgent(name="keywords", generation_instructions="キーワード抽出"),
            RefinireAgent(name="summary", generation_instructions="要約作成"),
            RefinireAgent(name="classification", generation_instructions="カテゴリ分類")
        ],
        "next_step": "report",
        "max_workers": 4
    },
    "report": FunctionStep("report", generate_final_report)
})
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

**📖 チュートリアル:** [クイックスタートガイド](docs/tutorials/quickstart_ja.md) | **詳細:** [統一LLMインターフェース](docs/unified-llm-interface_ja.md)

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

**📖 チュートリアル:** [高度な機能](docs/tutorials/advanced.md) | **詳細:** [自律品質保証](docs/autonomous-quality-assurance_ja.md)

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

### MCPサーバー統合 - Model Context Protocol

RefinireAgentは**MCP（Model Context Protocol）サーバー**をネイティブサポートし、外部データソースやツールへの標準化されたアクセスを提供します：

```python
from refinire import RefinireAgent

# MCPサーバー統合エージェント
agent = RefinireAgent(
    name="mcp_agent",
    generation_instructions="MCPサーバーのツールを活用してタスクを実行してください",
    mcp_servers=[
        "stdio://filesystem-server",  # ローカルファイルシステムアクセス
        "http://localhost:8000/mcp",  # リモートAPIサーバー
        "stdio://database-server --config db.json"  # データベースアクセス
    ],
    model="gpt-4o-mini"
)

# MCPツールが自動的に利用可能になります
result = agent.run("プロジェクトファイルを分析して、データベースの情報も含めて報告してください")
```

**MCPサーバータイプ:**
- **stdio servers**: ローカルサブプロセスとして実行
- **HTTP servers**: リモートHTTPエンドポイント  
- **WebSocket servers**: リアルタイム通信対応

**自動機能:**
- MCPサーバーからのツール自動検出
- ツールの動的登録と実行
- エラーハンドリングと再試行
- 複数サーバーの並列管理

**📖 チュートリアル:** [高度な機能](docs/tutorials/advanced.md) | **詳細:** [組み合わせ可能なフローアーキテクチャ](docs/composable-flow-architecture_ja.md)

## 4. 包括的可観測性 - 自動トレーシング

**課題**: AIワークフローのデバッグと本番環境でのエージェント動作の理解には、実行フロー、パフォーマンスメトリクス、障害パターンの可視性が必要です。手動ログは複雑なマルチエージェントシステムには不十分です。

**解決策**: Refinireは設定ゼロの包括的なトレーシング機能を提供します。すべてのエージェント実行、ワークフローステップ、評価が自動的にキャプチャされ、Grafana TempoやJaegerなどの業界標準可観測性プラットフォームにエクスポートできます。

**主な利点**:
- **設定ゼロ**: 組み込みコンソールトレーシングが即座に動作
- **本番対応**: OpenTelemetry統合とOTLPエクスポート
- **自動スパン作成**: すべてのエージェントとワークフローステップが自動的にトレース
- **豊富なメタデータ**: 入力、出力、評価スコア、パフォーマンスメトリクスをキャプチャ

### 組み込みコンソールトレーシング

```python
from refinire import RefinireAgent

agent = RefinireAgent(
    name="traced_agent",
    generation_instructions="あなたは役立つアシスタントです。",
    model="gpt-4o-mini"
)

result = agent.run("量子コンピューティングとは？")
# コンソールに自動表示:
# 🔵 [Instructions] あなたは役立つアシスタントです。
# 🟢 [User Input] 量子コンピューティングとは？
# 🟡 [LLM Output] 量子コンピューティングは革新的な...
# ✅ [Result] 操作が正常に完了しました
```

### 本番OpenTelemetry統合

```python
from refinire import enable_opentelemetry_tracing, disable_opentelemetry_tracing

# 包括的トレーシングを有効化
enable_opentelemetry_tracing(
    service_name="my-agent-app",
    otlp_endpoint="http://localhost:4317"  # Grafana Tempoエンドポイント
)

# すべてのエージェント実行が自動的にスパンを作成
agent = RefinireAgent(name="production_agent", model="gpt-4o-mini")
result = agent.run("機械学習の概念を説明してください")

# 完了時にクリーンアップ
disable_opentelemetry_tracing()
```

### 全トレーシングの無効化

すべてのトレーシング（コンソール + OpenTelemetry）を完全に無効化：

```python
from refinire import disable_tracing

# 全トレーシング出力を無効化
disable_tracing()

# これで全てのエージェント実行がトレース出力なしで動作
agent = RefinireAgent(name="silent_agent", model="gpt-4o-mini")
result = agent.run("これは静寂に実行されます")  # トレース出力なし
```

**📖 完全ガイド:** [トレーシングと可観測性チュートリアル](docs/tutorials/tracing_ja.md) - 包括的なセットアップと使用方法

**🔗 統合例:**
- [OpenTelemetry例](examples/opentelemetry_tracing_example.py) - 基本的なOpenTelemetryセットアップ
- [Grafana Tempo例](examples/grafana_tempo_tracing_example.py) - 完全なTempo統合
- [環境設定](examples/oneenv_tracing_example.py) - oneenv設定管理

---

## 5. 自動並列処理: 劇的なパフォーマンス向上

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

**📖 チュートリアル:** [高度な機能](docs/tutorials/advanced.md) | **詳細:** [組み合わせ可能なフローアーキテクチャ](docs/composable-flow-architecture_ja.md)

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

**📖 チュートリアル:** [コンテキスト管理](docs/tutorials/context_management_ja.md) | **詳細:** [コンテキスト管理設計書](docs/context_management.md)

### 動的プロンプト生成 - 変数埋め込み機能

RefinireAgentの新しい変数埋め込み機能により、コンテキストに基づいた動的なプロンプト生成が可能になりました：

```python
from refinire import RefinireAgent, Context

# 変数埋め込み対応エージェント
agent = RefinireAgent(
    name="dynamic_responder",
    generation_instructions="あなたは{{agent_role}}として、{{user_type}}ユーザーに{{response_style}}で対応してください。前回の結果: {{RESULT}}",
    model="gpt-4o-mini"
)

# コンテキスト設定
ctx = Context()
ctx.shared_state = {
    "agent_role": "カスタマーサポート専門家",
    "user_type": "プレミアム",
    "response_style": "迅速かつ詳細"
}
ctx.result = "問い合わせ内容を確認済み"

# 動的プロンプトで実行
result = agent.run("{{user_type}}ユーザーからの{{priority_level}}要求への対応をお願いします", ctx)
```

**主な変数埋め込み機能:**
- **`{{RESULT}}`**: 前のステップの実行結果
- **`{{EVAL_RESULT}}`**: 評価結果の詳細情報
- **`{{カスタム変数}}`**: `ctx.shared_state`からの任意の値
- **リアルタイム置換**: 実行時の動的プロンプト生成

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

## リリースノート

### v0.2.10 - MCPサーバー対応とプロトコル統合

### 🔌 Model Context Protocol（MCP）完全対応
- **ネイティブMCPサポート**: OpenAI Agents SDKのMCP機能をRefinireAgentで完全統合
- **多様なサーバータイプ**: stdio、HTTP、WebSocketサーバーに対応
- **自動ツール検出**: MCPサーバーからツールを自動的に発見・登録
- **シームレス統合**: 既存のtoolsパラメータと併用可能
- **エラーハンドリング**: MCPサーバー接続の堅牢な管理

```python
# MCPサーバー統合の例
agent = RefinireAgent(
    name="mcp_integrated_agent",
    generation_instructions="MCPサーバーとローカルツールを活用してタスクを実行",
    mcp_servers=[
        "stdio://filesystem-server",
        "http://localhost:8000/mcp",
        "stdio://database-server --config db.json"
    ],
    tools=[local_calculator, weather_tool],  # ローカルツールとMCPツールの併用
    model="gpt-4o-mini"
)
```

### 🌐 外部システム連携の標準化
- **統一プロトコル**: MCPによる外部データソース・ツールへの標準化されたアクセス
- **業界標準採用**: OpenAI、Anthropic、Block、Replit等が採用するMCP準拠
- **ベンダーロックイン回避**: 標準プロトコルによる柔軟なツール選択
- **拡張性**: 新しいMCPサーバーを簡単に追加・統合

**MCPサーバータイプの完全サポート:**
- **stdio servers**: `stdio://server-name --args` 形式でローカルサブプロセス
- **HTTP servers**: `http://localhost:port/mcp` 形式でリモートAPI
- **WebSocket servers**: `ws://host:port/mcp` 形式でリアルタイム通信

### 🔧 実装とテストの強化
- **包括的テストスイート**: MCP統合の全シナリオをカバー
- **実例の提供**: `examples/mcp_server_example.py`で詳細な使用例
- **後方互換性**: 既存のRefinireAgentとClarifyAgentで追加設定なしで利用可能
- **エラー処理**: MCPサーバー接続失敗時の適切なフォールバック

### 📚 ドキュメント整備
- **MCPガイド**: README日英両言語でMCP統合の完全解説
- **設定パターン**: 様々なMCPサーバー設定の実例
- **ベストプラクティス**: 効率的なMCPサーバー管理のガイドライン

### 💡 開発者への利益
- **開発効率向上**: 外部システム統合の大幅な簡素化
- **保守性向上**: 標準プロトコルによる一貫した統合パターン
- **柔軟性向上**: ツールとMCPサーバーの自由な組み合わせ
- **将来対応**: 新しいMCPサーバーへの即座な対応

**📖 詳細ガイド:**
- [MCP統合例](examples/mcp_server_example.py) - 包括的なMCPサーバー統合デモ
- [高度な機能](docs/tutorials/advanced.md) - MCPとツール統合の詳細

---

### v0.2.9 - 変数埋め込みと高度なFlow機能

### 🎯 動的変数埋め込みシステム
- **`{{変数名}}` 構文**: ユーザー入力とgeneration_instructionsで動的変数置換をサポート
- **予約変数**: `{{RESULT}}`と`{{EVAL_RESULT}}`で前のステップの結果と評価にアクセス
- **コンテキストベース**: `ctx.shared_state`から任意の変数を動的に参照
- **リアルタイム置換**: 実行時にプロンプトを動的に生成・カスタマイズ
- **エージェント柔軟性**: 同一エージェントでコンテキストに応じた異なる動作が可能

```python
# 動的プロンプト生成の例
agent = RefinireAgent(
    name="dynamic_agent",
    generation_instructions="あなたは{{agent_role}}として{{target_audience}}向けに{{response_style}}で回答してください。前の結果: {{RESULT}}",
    model="gpt-4o-mini"
)

ctx = Context()
ctx.shared_state = {
    "agent_role": "技術専門家",
    "target_audience": "開発者",
    "response_style": "詳細な技術説明"
}
result = agent.run("{{user_type}}ユーザーからの{{service_level}}要求に{{response_time}}対応してください", ctx)
```

### 📚 Flow完全ガイドの提供
- **ステップバイステップガイド**: [Flow完全ガイド](docs/tutorials/flow_complete_guide_ja.md)で包括的なワークフロー構築
- **日英両言語対応**: [English Guide](docs/tutorials/flow_complete_guide_en.md)も提供
- **実践的例**: 基本的なフローから複雑な並列処理まで段階的に学習
- **ベストプラクティス**: 効率的なフロー設計とパフォーマンス最適化のガイドライン
- **トラブルシューティング**: よくある問題とその解決方法

### 🔧 コンテキスト管理の強化
- **変数埋め込み統合**: [コンテキスト管理ガイド](docs/tutorials/context_management_ja.md)に変数埋め込み例を追加
- **動的プロンプト生成**: コンテキストの状態に基づいてエージェントの動作を変更
- **ワークフロー統合**: Flowとコンテキストプロバイダーの連携パターン
- **メモリ管理**: 効率的なコンテキスト使用のためのベストプラクティス

### 🛠️ 開発者体験の向上
- **Step互換性修正**: `run()`から`run_async()`への移行に伴うテスト環境の整備
- **テスト組織化**: プロジェクトルートのテストファイルをtests/ディレクトリに整理
- **パフォーマンス検証**: 変数埋め込み機能の包括的テストとパフォーマンス最適化
- **エラーハンドリング**: 変数置換における堅牢なエラー処理とフォールバック

### 🚀 技術的改善
- **正規表現最適化**: 効率的な変数パターンマッチングとコンテキスト置換
- **型安全性**: 変数埋め込みでの適切な型変換と例外処理
- **メモリ効率**: 大規模コンテキストでの最適化された変数処理
- **後方互換性**: 既存のRefinireAgentとFlowの完全な互換性維持

### 💡 実用的な利点
- **開発効率向上**: 動的プロンプト生成により同一エージェントで複数の役割を実現
- **保守性向上**: 変数を使ったテンプレート化により、プロンプトの管理と更新が容易
- **柔軟性向上**: 実行時の状態に応じたエージェントの動作カスタマイズ
- **再利用性向上**: 汎用的なプロンプトテンプレートの作成と共有

**📖 詳細ガイド:**
- [Flow完全ガイド](docs/tutorials/flow_complete_guide_ja.md) - ワークフロー構築の完全ガイド
- [コンテキスト管理](docs/tutorials/context_management_ja.md) - 変数埋め込みを含む包括的なコンテキスト管理

---

### v0.2.8 - 革新的なツール統合

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