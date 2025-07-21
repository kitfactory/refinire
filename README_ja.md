# Refinire — Refined Simplicity for Agentic AI
ひらめきを"すぐに動く"へ、直感的エージェント・フレームワーク

## なぜRefinireなのか？

- **シンプルなインストール** — `pip install refinire`だけ
- **LLM固有の設定を簡素化** — 複雑なセットアップは不要
- **プロバイダー間の統一API** — OpenAI / Anthropic / Google / Ollama
- **組み込み評価 & 再生成ループ** — 品質保証が標準装備
- **1行での並列処理** — `{"parallel": [...]}`で複雑な非同期操作
- **包括的な可観測性** — OpenTelemetry統合による自動トレーシング

# 30-Second Quick Start

```bash
> pip install refinire
```

**オプション**: 対話型CLIで環境変数を簡単に設定:

```bash
pip install "refinire[cli]"
refinire-setup
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

## インテリジェントルーティングシステム

**課題**: 複雑なAIワークフローでは、生成されたコンテンツに基づいて次のステップを動的に決定する必要があります。手動での条件分岐は複雑で保守が困難です。

**解決策**: RefinireAgentの新しいルーティング機能は、生成されたコンテンツを自動的に分析し、品質・複雑さ・完了状態に基づいて次のステップを決定します。これにより、フロー内での動的なワークフロー制御が実現できます。

**主な利点**:
- **自動フロー制御**: コンテンツ品質に基づく動的ステップルーティング
- **柔軟な分析モード**: 精度重視またはパフォーマンス重視の実行モード
- **型安全な出力**: Pydanticモデルによる構造化されたルーティング結果
- **シームレス統合**: 既存のFlowアーキテクチャとの完全な統合

### 基本的なルーティング機能

```python
from refinire import RefinireAgent

# ルーティング機能付きエージェント
agent = RefinireAgent(
    name="smart_processor",
    generation_instructions="ユーザーの要求に対して適切なレスポンスを生成してください",
    routing_instruction="コンテンツ品質を評価し、次の処理を決定してください：高品質なら'complete'、改善必要なら'enhance'、不十分なら'regenerate'",
    routing_mode="accurate_routing",  # 精度重視の分析
    model="gpt-4o-mini"
)

result = agent.run("機械学習について説明してください")

# ルーティング結果にアクセス
print(f"生成コンテンツ: {result.content}")
print(f"次のルート: {result.next_route}")
print(f"信頼度: {result.confidence}")
print(f"判断理由: {result.reasoning}")
```

### 構造化出力との組み合わせ

```python
from pydantic import BaseModel, Field

class ArticleOutput(BaseModel):
    title: str = Field(description="記事のタイトル")
    content: str = Field(description="記事本文")
    keywords: list[str] = Field(description="キーワードリスト")

# 構造化出力とルーティングを組み合わせ
agent = RefinireAgent(
    name="article_generator", 
    generation_instructions="指定されたトピックについて詳細な記事を作成してください",
    output_model=ArticleOutput,
    routing_instruction="記事品質を評価し、次の処理を決定：優秀なら'publish'、良好なら'review'、改善必要なら'revise'",
    routing_mode="fast_routing",  # パフォーマンス重視
    model="gpt-4o-mini"
)

result = agent.run("量子コンピューティングについて記事を書いてください")

# 構造化されたコンテンツとルーティング情報の両方にアクセス
article = result.content  # ArticleOutputオブジェクト
print(f"タイトル: {article.title}")
print(f"キーワード: {article.keywords}")
print(f"次のアクション: {result.next_route}")
```

### Flowワークフローでのルーティング統合

```python
from refinire import Flow, FunctionStep, Context

# ルーティング結果を活用する関数
def route_based_processor(ctx: Context):
    routing_result = ctx.routing_result
    if routing_result:
        quality = routing_result['confidence']
        next_route = routing_result['next_route']
        
        # ルーティング結果に基づいて処理を分岐
        if next_route == "complete":
            ctx.goto("finalize")
        elif next_route == "enhance":
            ctx.goto("improvement")
        else:
            ctx.goto("regenerate")
    else:
        ctx.goto("default_process")

# ルーティング統合フロー
flow = Flow({
    "analyze": RefinireAgent(
        name="content_analyzer",
        generation_instructions="コンテンツを分析して品質を判定してください",
        routing_instruction="品質レベルに応じて次の処理を決定：高品質なら'complete'、中品質なら'enhance'、低品質なら'regenerate'",
        routing_mode="accurate_routing"
    ),
    "router": FunctionStep("router", route_based_processor),
    "complete": FunctionStep("complete", finalize_content),
    "enhance": FunctionStep("enhance", improve_content),
    "regenerate": FunctionStep("regenerate", regenerate_content),
    "finalize": FunctionStep("finalize", publish_content)
})

result = await flow.run("技術記事のコンテンツを処理してください")
```

### ルーティングモードの選択

```python
# 精度重視モード - 詳細な分析と高品質なルーティング決定
accurate_agent = RefinireAgent(
    name="quality_analyzer",
    generation_instructions="高品質なコンテンツを生成してください",
    routing_instruction="コンテンツを厳密に評価し、適切な次ステップを決定してください",
    routing_mode="accurate_routing",  # 別エージェントで詳細分析
    model="gpt-4o-mini"
)

# パフォーマンス重視モード - 高速なルーティング決定
fast_agent = RefinireAgent(
    name="speed_processor",
    generation_instructions="効率的にコンテンツを生成してください", 
    routing_instruction="素早くコンテンツを評価し、次ステップを決定してください",
    routing_mode="fast_routing",  # 統合実行で高速処理
    model="gpt-4o-mini"
)
```

**主要ルーティング機能**:
- **動的コンテンツ分析**: 生成されたコンテンツの自動品質評価
- **柔軟なルーティング指示**: カスタムルーティングロジックの定義
- **実行モード選択**: 精度重視 vs パフォーマンス重視
- **構造化出力対応**: カスタムデータ型との完全統合
- **Flow統合**: ワークフロー内での自動ルーティング決定
- **コンテキスト保存**: ルーティング結果のワークフロー間での共有

**📖 詳細ガイド**: [新しいフロー制御コンセプト](docs/new_flow_control_concept.md) - ルーティングシステムの完全解説

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

# 前のエージェントの出力にアクセス（shared_stateに保存）
analyzer_output = summary_ctx.shared_state.get("prev_outputs_analyzer")
summarizer_output = summary_ctx.shared_state.get("prev_outputs_summarizer")

# カスタムデータ保存（artifacts、knowledge等も含む）
result_ctx.shared_state["custom_data"] = {"key": "value"}
result_ctx.shared_state["artifacts"] = {"result": "最終出力"}
result_ctx.shared_state["knowledge"] = {"domain_info": "研究データ"}
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

---

## インストール & クイックスタート

### インストール

```bash
pip install refinire
```

### 環境設定（推奨）

対話型で環境変数を設定:

```bash
# CLI対応でインストール
pip install "refinire[cli]"

# 対話型セットアップウィザードを実行
refinire-setup
```

CLIが以下をガイドします:
- **プロバイダー選択**: OpenAI、Anthropic、Google、OpenRouter、Groq、Ollama、LM Studioから選択
- **機能設定**: トレーシング、エージェント設定、開発機能を有効化
- **テンプレート生成**: カスタマイズされた`.env`ファイルを作成

**手動設定**: 代わりに環境変数を手動で設定:

```bash
export OPENAI_API_KEY="your-api-key-here"
export REFINIRE_DEFAULT_LLM_MODEL="gpt-4o-mini"
```

📖 **完全ガイド**: [環境変数](docs/environment_variables_ja.md) | [CLIツール](docs/cli.md)

### 最初のエージェント（30秒）

```python
from refinire import RefinireAgent

# 作成
agent = RefinireAgent(
    name="hello_world",
    generation_instructions="親切なアシスタントです。",
    model="gpt-4o-mini"
)

# 実行
result = agent.run("こんにちは！")
print(result.content)
```

### プロバイダーの柔軟性

```python
from refinire import get_llm

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
        print(f"✓ {provider}: {model} - Ready")
    except Exception as e:
        print(f"✗ {provider}: {model} - {str(e)}")
```

**対話型セットアップ**: Refinire CLIで簡単設定:

```bash
refinire-setup
```

📖 **完全セットアップガイド**: [環境変数](docs/environment_variables_ja.md) | [CLIドキュメント](docs/cli.md)

## 環境の名前空間管理 - OneEnv 0.4.0対応

**課題**: 開発・本番・テスト環境で異なるAPIキーやモデル設定を管理するのは複雑で、環境の切り替えが困難です。

**解決策**: Refinireはoneenv 0.4.0の名前空間機能に完全対応し、環境ごとに独立した設定を管理できます。同じエージェントコードで異なる環境設定を簡単に切り替えられます。

**主な利点**:
- **環境の完全分離**: 開発・本番・テスト環境を明確に区別
- **設定の集約管理**: 環境ごとの設定を一元管理
- **チーム開発対応**: 各開発者が独自の名前空間を持てる
- **安全な本番運用**: 環境の誤使用を防止

### 基本的な名前空間の使用

```python
from refinire import RefinireAgent

# 開発環境のエージェント
dev_agent = RefinireAgent(
    name="dev_assistant",
    generation_instructions="開発環境用のアシスタントです",
    model="gpt-4o-mini",
    namespace="development"  # 開発環境の名前空間
)

# 本番環境のエージェント
prod_agent = RefinireAgent(
    name="prod_assistant", 
    generation_instructions="本番環境用のアシスタントです",
    model="gpt-4o-mini",
    namespace="production"  # 本番環境の名前空間
)

# テスト環境のエージェント
test_agent = RefinireAgent(
    name="test_assistant",
    generation_instructions="テスト環境用のアシスタントです",
    model="gpt-4o-mini",
    namespace="testing"  # テスト環境の名前空間
)
```

### 環境設定の管理

```bash
# 開発環境の設定
oneenv init refinire:core --namespace development

# 本番環境の設定
oneenv init refinire:core --namespace production

# テスト環境の設定
oneenv init refinire:core --namespace testing
```

### プロバイダー固有の名前空間対応

```python
from refinire import get_llm

# 開発環境では異なるプロバイダーをテスト
dev_llm = get_llm(
    model="gpt-4o-mini",
    namespace="development"
)

# 本番環境では安定したプロバイダーを使用
prod_llm = get_llm(
    model="claude-3-sonnet",
    namespace="production"
)
```

### 名前空間なしのデフォルト動作

```python
# 名前空間を指定しない場合はデフォルト名前空間を使用
agent = RefinireAgent(
    name="default_assistant",
    generation_instructions="デフォルト設定のアシスタントです",
    model="gpt-4o-mini"
    # namespace未指定 = デフォルト名前空間（空文字列）
)
```

**主要な名前空間機能**:
- **環境切り替え**: 同じコードで異なる環境設定を使用
- **設定の分離**: 環境ごとに完全に独立した設定管理
- **チーム協力**: 開発者ごとの個別設定対応
- **本番安全性**: 環境の誤使用防止
- **後方互換性**: 既存コードはそのまま動作（デフォルト名前空間）

**📖 詳細ガイド**: [環境変数ドキュメント](docs/environment_variables_ja.md) - 名前空間機能の完全解説