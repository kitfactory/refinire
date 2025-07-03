# Refinireでのトレーシングと可観測性

Refinireは、AIエージェントワークフローの監視とデバッグを支援する包括的なトレーシング機能を提供します。このチュートリアルでは、組み込みのコンソールトレーシングと高度なOpenTelemetry統合の両方をカバーします。

## 概要

Refinireは2つのレベルのトレーシングを提供します：

1. **組み込みコンソールトレーシング** - 常に利用可能、追加の依存関係不要
2. **OpenTelemetryトレーシング** - OTLP エクスポートによる高度な可観測性（オプションの依存関係が必要）

## 組み込みコンソールトレーシング

デフォルトで、Refinireは色分けされた出力でコンソールに詳細なトレース情報を表示します：

- **🔵 インストラクション** - エージェントの生成指示（青）
- **🟢 ユーザー入力** - ユーザークエリと入力（緑）
- **🟡 LLM出力** - モデルの応答と結果（黄）
- **🔴 エラー** - エラーメッセージと警告（赤）

### コンソール出力の例

```python
from refinire import RefinireAgent
from refinire.agents.flow import Context

agent = RefinireAgent(
    name="example_agent",
    generation_instructions="あなたは役立つアシスタントです。",
    model="gpt-4o-mini"
)

ctx = Context()
result = await agent.run_async("量子コンピューティングとは何ですか？", ctx)
```

コンソール出力：
```
🔵 [Instructions] あなたは役立つアシスタントです。
🟢 [User Input] 量子コンピューティングとは何ですか？
🟡 [LLM Output] 量子コンピューティングは革新的なコンピューティングパラダイム...
✅ [Result] 操作が正常に完了しました
```

## OpenTelemetryトレーシング

本番環境や高度なデバッグでは、RefinireはGrafana Tempo、Jaegerなどの可観測性プラットフォームへのOTLPエクスポートを持つOpenTelemetryをサポートします。

### インストール

オプションのOpenInference instrumentation依存関係をインストール：

```bash
# extrasでインストール
pip install refinire[openinference-instrumentation]

# または手動でインストール
pip install openinference-instrumentation openinference-instrumentation-openai opentelemetry-exporter-otlp
```

### 基本的なOpenTelemetryセットアップ

```python
from refinire import (
    RefinireAgent,
    enable_opentelemetry_tracing,
    disable_opentelemetry_tracing
)
from refinire.agents.flow import Context

# OpenTelemetryトレーシングを有効化
enable_opentelemetry_tracing(
    service_name="my-agent-app",
    otlp_endpoint="http://localhost:4317",  # Grafana Tempoエンドポイント
    console_output=True  # コンソールトレースも表示
)

# エージェント作成 - 自動的にスパンとしてトレースされます
agent = RefinireAgent(
    name="traced_agent",
    generation_instructions="あなたは役立つアシスタントです。",
    model="gpt-4o-mini"
)

# すべてのエージェント実行が自動的にスパンを作成
ctx = Context()
result = await agent.run_async("機械学習とは何ですか？", ctx)

# 以下の情報がスパンに自動的にキャプチャされます：
# - エージェント名: "RefinireAgent(traced_agent)"
# - 入力: ユーザークエリ
# - 指示: 生成指示
# - 出力: エージェントの応答
# - モデル: "gpt-4o-mini"
# - 成功/エラー状態
# - 評価スコア（評価が有効な場合）

# 完了時にトレーシングを無効化
disable_opentelemetry_tracing()
```

### 全トレーシングの無効化

すべてのトレーシング（コンソール + OpenTelemetry）を完全に無効化するには、`disable_tracing()`関数を使用します：

```python
from refinire import disable_tracing

# 全トレーシング出力を無効化
disable_tracing()

# これで全てのエージェント実行がトレース出力なしで静寂に動作
agent = RefinireAgent(
    name="silent_agent",
    generation_instructions="あなたは役立つアシスタントです。",
    model="gpt-4o-mini"
)

result = agent.run("これは静寂に実行されます")
# コンソール出力なし、OpenTelemetryスパンも作成されません
```

### トレーシングの再有効化

無効化後にトレーシングを再度有効化する場合：

```python
from refinire import enable_console_tracing, enable_opentelemetry_tracing

# コンソールトレーシングのみを再有効化
enable_console_tracing()

# またはOpenTelemetryトレーシングを再有効化
enable_opentelemetry_tracing(
    service_name="my-service",
    otlp_endpoint="http://localhost:4317"
)
```

### 環境変数による設定

Refinireは`REFINIRE_TRACE_*`変数を使用した環境ベースの設定をサポートします：

```bash
# 環境変数を設定
export REFINIRE_TRACE_OTLP_ENDPOINT="http://localhost:4317"
export REFINIRE_TRACE_SERVICE_NAME="my-agent-service"
export REFINIRE_TRACE_RESOURCE_ATTRIBUTES="environment=production,team=ai"

# パラメータ不要 - 環境変数を使用
enable_opentelemetry_tracing()
```

### 設定管理にoneenvを使用

Refinireは簡単な環境管理のためのoneenvテンプレートを提供します：

```bash
# トレーシング設定テンプレートを初期化
oneenv init --template refinire.tracing

# これにより以下の内容の.envファイルが作成されます：
# REFINIRE_TRACE_OTLP_ENDPOINT=
# REFINIRE_TRACE_SERVICE_NAME=refinire-agent
# REFINIRE_TRACE_RESOURCE_ATTRIBUTES=

# 設定で.envファイルを編集
# REFINIRE_TRACE_OTLP_ENDPOINT=http://localhost:4317
# REFINIRE_TRACE_SERVICE_NAME=my-application
# REFINIRE_TRACE_RESOURCE_ATTRIBUTES=environment=production,team=ai
```

Pythonコードでは：

```python
from oneenv import load_env

# .envファイルから環境変数を読み込み
load_env()

# トレーシング関数を使用可能
from refinire import enable_opentelemetry_tracing

# 環境変数が自動的に使用されます
enable_opentelemetry_tracing()
```

## 自動エージェントトレーシング

### 自動的にトレースされる内容

OpenTelemetryトレーシングを有効にすると、すべてのRefinireAgent実行が自動的に豊富なメタデータを持つスパンを作成します：

```python
from refinire import RefinireAgent, enable_opentelemetry_tracing
from refinire.agents.flow import Context

# トレーシングを有効化 - これだけで十分です！
enable_opentelemetry_tracing(
    service_name="my-app",
    otlp_endpoint="http://localhost:4317"
)

# 評価付きエージェントを作成
agent = RefinireAgent(
    name="helpful_assistant",
    generation_instructions="あなたは技術分野に特化した役立つアシスタントです。",
    evaluation_instructions="正確性と有用性に基づいて応答品質を0-100で評価してください。",
    threshold=75.0,
    model="gpt-4o-mini"
)

# この単一の呼び出しが以下の情報を含むスパンを自動作成：
# - スパン名: "RefinireAgent(helpful_assistant)"
# - 入力テキスト、指示、出力
# - モデル名とパラメータ
# - 成功/失敗状態
# - 評価スコアと合格/不合格状態
# - 失敗が発生した場合のエラー詳細
ctx = Context()
result = await agent.run_async("量子コンピューティングについて説明してください", ctx)
```

### 自動スパンカバレッジ

Refinireは以下を自動的にスパン化します：

#### **RefinireAgentスパン**
すべてのRefinireAgent実行が詳細なスパンを作成：
- **`input`**: ユーザークエリまたは入力テキスト
- **`instructions`**: エージェントの生成指示
- **`output`**: 生成された応答
- **`model`**: 使用されたLLMモデル（例："gpt-4o-mini"）
- **`success`**: 実行が成功したかを示すブール値
- **`evaluation.score`**: 評価が有効な場合の評価スコア（0-100）
- **`evaluation.passed`**: 評価閾値を満たしたかを示すブール値
- **`error`**: 実行が失敗した場合のエラーメッセージ

#### **ワークフローステップスパン**
すべてのワークフローステップが自動的にスパンを作成：

**ConditionStepスパン：**
- **`condition_result`**: 条件評価のブール結果
- **`if_true`**: true分岐のステップ名
- **`if_false`**: false分岐のステップ名
- **`next_step`**: 実際に取られた次ステップ

**FunctionStepスパン：**
- **`function_name`**: 実行された関数名
- **`next_step`**: 実行後の次ステップ
- **`success`**: 実行成功状態

**ParallelStepスパン：**
- **`parallel_steps`**: 並列ステップ名のリスト
- **`execution_time_seconds`**: 総並列実行時間
- **`successful_steps`**: 正常完了したステップのリスト
- **`failed_steps`**: 失敗した並列ステップ数
- **`total_steps`**: 総並列ステップ数

**すべてのステップタイプに含まれる項目：**
- **`step.name`**: ステップ識別子
- **`step.type`**: ステップクラス名（ConditionStep、FunctionStepなど）
- **`step.category`**: ステップカテゴリ（condition、function、parallelなど）
- **`current_step`**: 現在のワークフロー位置
- **`step_count`**: 実行されたステップ数
- **`recent_messages`**: 最新3つのコンテキストメッセージ

#### **Flowワークフロースパン**
完全なワークフローが自動的にトップレベルスパンを作成：

**Flowスパン：**
- **`flow.name`**: フロー識別名
- **`flow.id`**: 一意のフロー実行ID
- **`flow.start_step`**: 開始ステップ名
- **`flow.step_count`**: 定義された総ステップ数
- **`flow.step_names`**: フロー内の全ステップ名のリスト
- **`flow_input`**: フローに提供された入力データ
- **`flow_completed`**: 正常完了を示すブール値
- **`final_step_count`**: 実際に実行されたステップ数
- **`flow_finished`**: フローが自然な終了に達したか
- **`flow_result`**: フローからの最終結果（500文字に切り詰め）
- **`flow_error`**: フロー実行が失敗した場合のエラーメッセージ

### 高度なワークフロートレーシング（オプション）

複雑なワークフローの場合、エージェント呼び出しのグループの周りにカスタムスパンを追加できます：

```python
from refinire import get_tracer, enable_opentelemetry_tracing
from refinire.agents.flow import Context

# トレーシングを有効化
enable_opentelemetry_tracing(
    service_name="workflow-app",
    otlp_endpoint="http://localhost:4317"
)

# カスタムワークフロースパン用のトレーサーを取得（オプション）
tracer = get_tracer("workflow-tracer")

with tracer.start_as_current_span("multi-agent-workflow") as span:
    span.set_attribute("workflow.type", "analysis-pipeline")
    span.set_attribute("user.id", "user123")
    
    # これらのエージェントはワークフロースパン内で自動的にスパンを作成
    analyzer = RefinireAgent(
        name="content_analyzer",
        generation_instructions="入力を分析して分類してください。",
        model="gpt-4o-mini"
    )
    
    expert = RefinireAgent(
        name="domain_expert",
        generation_instructions="専門的な分析を提供してください。",
        model="gpt-4o-mini"
    )
    
    ctx = Context()
    
    # これらの呼び出しはそれぞれ自動的に詳細なスパンを作成
    analysis = await analyzer.run_async("機械学習について説明してください", ctx)
    response = await expert.run_async("機械学習について説明してください", ctx)
    
    span.set_attribute("workflow.status", "completed")
    span.set_attribute("agents.count", 2)
```

### カスタムスパンとワークフロートレーシング（従来の方法）

```python
from refinire import get_tracer, enable_opentelemetry_tracing
from refinire.agents.flow import Context

# トレーシングを有効化
enable_opentelemetry_tracing(
    service_name="workflow-app",
    otlp_endpoint="http://localhost:4317"
)

# カスタムスパン用のトレーサーを取得
tracer = get_tracer("workflow-tracer")

with tracer.start_as_current_span("user-workflow") as span:
    span.set_attribute("workflow.type", "question-answering")
    span.set_attribute("user.id", "user123")
    
    # エージェントを作成
    analyzer = RefinireAgent(
        name="content_analyzer",
        generation_instructions="入力を分析して分類してください。",
        model="gpt-4o-mini"
    )
    
    expert = RefinireAgent(
        name="domain_expert",
        generation_instructions="専門的な分析を提供してください。",
        model="gpt-4o-mini"
    )
    
    ctx = Context()
    
    # ステップ1: 分析
    with tracer.start_as_current_span("content-analysis") as analysis_span:
        analysis = await analyzer.run_async("機械学習について説明してください", ctx)
        analysis_span.set_attribute("analysis.category", str(analysis.result))
    
    # ステップ2: 専門家の回答
    with tracer.start_as_current_span("expert-response") as expert_span:
        response = await expert.run_async("機械学習について説明してください", ctx)
        expert_span.set_attribute("response.length", len(str(response.result)))
    
    span.set_attribute("workflow.status", "completed")
```

### マルチエージェントパイプライントレーシング

```python
# 異なる役割を持つ特化エージェントを作成
agents = {
    "analyzer": RefinireAgent(
        name="content_analyzer",
        generation_instructions="入力を分析してカテゴリを決定してください。",
        model="gpt-4o-mini"
    ),
    "technical": RefinireAgent(
        name="technical_expert",
        generation_instructions="技術的な説明を提供してください。",
        model="gpt-4o-mini"
    ),
    "business": RefinireAgent(
        name="business_expert", 
        generation_instructions="ビジネス分析を提供してください。",
        model="gpt-4o-mini"
    )
}

tracer = get_tracer("multi-agent-pipeline")

with tracer.start_as_current_span("multi-agent-workflow") as workflow_span:
    user_query = "CI/CDをどのように実装すべきですか？"
    workflow_span.set_attribute("query", user_query)
    
    ctx = Context()
    
    # 分析に基づくルーティング
    with tracer.start_as_current_span("routing") as route_span:
        analysis = await agents["analyzer"].run_async(user_query, ctx)
        category = str(analysis.result).lower()
        route_span.set_attribute("route.category", category)
    
    # 適切な専門家で実行
    expert_key = "technical" if "技術" in category else "business"
    with tracer.start_as_current_span(f"{expert_key}-response") as expert_span:
        result = await agents[expert_key].run_async(user_query, ctx)
        expert_span.set_attribute("expert.type", expert_key)
        expert_span.set_attribute("response.length", len(str(result.result)))
```

## 可観測性プラットフォームとの統合

### 完全なGrafana Tempoセットアップチュートリアル

このセクションでは、Grafana Tempoをセットアップし、Refinireからトレースを送信する手順を詳しく説明します。

#### ステップ1: Grafana Tempoのダウンロードとインストール

**オプションA: バイナリのダウンロード**
```bash
# Tempoをダウンロード（最新バージョンに置き換えてください）
wget https://github.com/grafana/tempo/releases/download/v2.3.0/tempo_2.3.0_linux_amd64.tar.gz
tar -xzf tempo_2.3.0_linux_amd64.tar.gz
```

**オプションB: Dockerを使用**
```bash
# DockerでTempoを実行
docker run -d \
  --name tempo \
  -p 3200:3200 \
  -p 4317:4317 \
  -p 4318:4318 \
  -v $(pwd)/tempo.yaml:/etc/tempo.yaml \
  grafana/tempo:latest \
  -config.file=/etc/tempo.yaml
```

#### ステップ2: Tempo設定の作成

`tempo.yaml`設定ファイルを作成：

```yaml
# tempo.yaml
server:
  http_listen_port: 3200

distributor:
  receivers:
    otlp:
      protocols:
        grpc:
          endpoint: 0.0.0.0:4317
        http:
          endpoint: 0.0.0.0:4318

storage:
  trace:
    backend: local
    local:
      path: /tmp/tempo/traces

# 検索機能を有効化
storage:
  trace:
    backend: local
    local:
      path: /tmp/tempo/traces
    pool:
      max_workers: 100
      queue_depth: 10000
```

#### ステップ3: Tempoサーバーの開始

```bash
# バイナリを使用する場合
./tempo -config.file=tempo.yaml

# Tempoが実行されているか確認
curl http://localhost:3200/ready
# 戻り値: ready
```

#### ステップ4: トレースを送信するRefinireの設定

```python
from refinire import (
    RefinireAgent,
    enable_opentelemetry_tracing,
    disable_opentelemetry_tracing
)

# Tempoエンドポイントでトレーシングを有効化
enable_opentelemetry_tracing(
    service_name="refinire-tempo-demo",
    otlp_endpoint="http://localhost:4317",  # Tempo gRPCエンドポイント
    console_output=True,  # コンソールにもトレースを表示
    resource_attributes={
        "environment": "development",
        "service.version": "1.0.0",
        "demo.type": "tempo-integration"
    }
)

# エージェントを作成して実行
agent = RefinireAgent(
    name="tempo_agent",
    generation_instructions="あなたはトレーシングをデモンストレーションする役立つアシスタントです。",
    model="gpt-4o-mini"
)

from refinire.agents.flow import Context
ctx = Context()

# これによりTempoに送信されるトレースが生成されます
result = await agent.run_async("分散トレーシングの利点について説明してください", ctx)
print(f"応答: {result.result}")

# クリーンアップ
disable_opentelemetry_tracing()
```

#### ステップ5: トレースを表示するためのGrafanaセットアップ

1. **Grafanaのインストール**：
```bash
# Dockerを使用
docker run -d \
  --name grafana \
  -p 3000:3000 \
  grafana/grafana:latest
```

2. **Grafanaへのアクセス**：
   - http://localhost:3000 を開く
   - ログイン: admin/admin（初回ログイン時にパスワードを変更）

3. **Tempoデータソースの追加**：
   - Configuration → Data Sources に移動
   - "Add data source" をクリック
   - "Tempo" を選択
   - URL: `http://localhost:3200` を設定
   - "Save & Test" をクリック

4. **トレースの表示**：
   - Explore に移動
   - Tempoデータソースを選択
   - TraceQLクエリを使用: `{service.name="refinire-tempo-demo"}`
   - またはドロップダウンでサービス名で検索

#### ステップ6: トレースが送信されていることの確認

Grafana Tempoの例を実行して統合をテスト：

```bash
# 例を実行
python examples/grafana_tempo_tracing_example.py
```

期待される出力：
```
=== Grafana Tempo Tracing Example ===

✅ OpenTelemetry tracing enabled with Tempo endpoint: http://localhost:4317

--- Running operations (traces sent to Grafana Tempo) ---

🔍 Query 1: What are the benefits of using Grafana for observability?
📝 Response length: 342 characters
📊 First 100 chars: Grafana offers several key benefits for observability: 1. **Unified Dashboard**...

✅ All traces sent to Grafana Tempo at http://localhost:4317
🔗 Check your Grafana Tempo UI to view the traces!
```

#### ステップ7: Grafanaでのトレース探索

1. **トレースの検索**：
   - Grafana Exploreで、サービス: `refinire-tempo-demo` を検索
   - 最近のトレース（過去15分以内）を探す
   - トレースをクリックして詳細なスパン情報を表示

2. **表示されるトレースの詳細**：
   - サービス名: `refinire-tempo-demo`
   - 操作名: OpenAI API呼び出し、エージェント操作
   - 期間とタイミング情報
   - リソース属性（environment、demo.type など）
   - 失敗が発生した場合のエラー情報

3. **高度なクエリ**：
   ```
   # エラーのあるトレースを検索
   {service.name="refinire-tempo-demo" && status=error}
   
   # 長時間実行されたトレースを検索
   {service.name="refinire-tempo-demo" && duration>5s}
   
   # リソース属性でトレースを検索
   {environment="development"}
   ```

#### ステップ8: 高度なTempo設定

本番環境では、以下の追加設定を検討してください：

```yaml
# tempo-production.yaml
server:
  http_listen_port: 3200

distributor:
  receivers:
    otlp:
      protocols:
        grpc:
          endpoint: 0.0.0.0:4317
        http:
          endpoint: 0.0.0.0:4318

# 本番環境でS3を使用
storage:
  trace:
    backend: s3
    s3:
      bucket: tempo-traces
      endpoint: s3.amazonaws.com

# メトリクス生成を有効化
metrics_generator:
  registry:
    external_labels:
      source: tempo
  storage:
    path: /tmp/tempo/generator/wal
    remote_write:
      - url: http://prometheus:9090/api/v1/write
```

### Jaegerセットアップ

```bash
# Jaeger all-in-oneを実行
docker run -d --name jaeger \
  -p 16686:16686 \
  -p 14250:14250 \
  jaegertracing/all-in-one:latest

# Refinireを設定
enable_opentelemetry_tracing(
    service_name="refinire-app",
    otlp_endpoint="http://localhost:14250"
)
```

## サンプルファイル

Refinireは`examples/`ディレクトリに包括的な例を含んでいます：

- **`opentelemetry_tracing_example.py`** - 基本的なOpenTelemetryセットアップと使用法
- **`grafana_tempo_tracing_example.py`** - Grafana Tempo統合の例
- **`oneenv_tracing_example.py`** - oneenvでの環境設定

### 例の実行

```bash
# 基本的なOpenTelemetryの例
python examples/opentelemetry_tracing_example.py

# Grafana Tempo統合
python examples/grafana_tempo_tracing_example.py

# OneEnv設定デモ
python examples/oneenv_tracing_example.py
```

## ベストプラクティス

### 1. リソース属性
常に意味のあるリソース属性を含める：

```python
enable_opentelemetry_tracing(
    resource_attributes={
        "environment": "production",
        "service.version": "1.2.3",
        "deployment.environment": "kubernetes",
        "team": "ai-research"
    }
)
```

### 2. ビジネスロジック用のカスタムスパン
重要なビジネス操作にスパンを作成：

```python
with tracer.start_as_current_span("document-processing") as span:
    span.set_attribute("document.type", "pdf")
    span.set_attribute("document.size", file_size)
    # 処理ロジックをここに
    span.set_attribute("processing.status", "completed")
```

### 3. エラーハンドリング
常にトレースでエラーをキャプチャ：

```python
try:
    result = await agent.run_async(query, ctx)
    span.set_attribute("operation.success", True)
except Exception as e:
    span.set_attribute("operation.success", False)
    span.set_attribute("error.message", str(e))
    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
    raise
```

### 4. パフォーマンス監視
パフォーマンスメトリクスを追跡：

```python
import time

start_time = time.time()
result = await agent.run_async(query, ctx)
duration = time.time() - start_time

span.set_attribute("operation.duration_ms", duration * 1000)
span.set_attribute("tokens.input", len(query.split()))
span.set_attribute("tokens.output", len(str(result.result).split()))
```

## トラブルシューティング

### よくある問題

1. **トレースが表示されない**: OTLPエンドポイントの接続性を確認
2. **依存関係の不足**: `refinire[openinference-instrumentation]`をインストール
3. **環境変数**: `REFINIRE_TRACE_*`変数が正しく設定されているか確認

### デバッグのヒント

1. **開発時にコンソール出力を有効化**：
```python
enable_opentelemetry_tracing(console_output=True)
```

2. **トレース利用可能性を確認**：
```python
from refinire import is_openinference_available, is_opentelemetry_enabled

print(f"OpenInference利用可能: {is_openinference_available()}")
print(f"トレーシング有効: {is_opentelemetry_enabled()}")
```

3. **接続性をテスト**：
```python
import socket

def test_otlp_connection(host="localhost", port=4317):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

print(f"OTLPエンドポイント到達可能: {test_otlp_connection()}")
```

## 次のステップ

- Grafana + Tempoで本番可観測性スタックをセットアップ
- トレーシングと並行してカスタムメトリクスを実装
- エージェントパフォーマンス監視用のダッシュボードを作成
- トレースデータに基づくアラートをセットアップ

より多くの例と高度な設定については、Refinireリポジトリの`examples/`ディレクトリを確認してください。