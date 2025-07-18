# 環境変数リファレンス

このドキュメントは、Refinireがサポートするすべての環境変数の包括的なリファレンスです。

## 概要

Refinireは設定に環境変数を使用し、[oneenv](https://github.com/kitfactory/oneenv)と統合して簡単にセットアップできるテンプレートを提供します。変数は4つのテンプレートに整理されています：

- **core**: コアLLMプロバイダー設定
- **tracing**: OpenTelemetryトレーシング設定
- **agents**: AIエージェントとパイプライン設定
- **development**: 開発とデバッグ設定

## oneenvでの使用方法

Refinireは[OneEnv](https://github.com/kitfactory/oneenv)と統合して環境変数管理を効率化します。

### インストールと基本的な使用方法

```bash
pip install oneenv
oneenv init refinire:core
oneenv init refinire:tracing
oneenv init refinire:agents
oneenv init refinire:development
```

### テンプレート登録

Refinireはエントリーポイントを通じてOneEnvにテンプレートを自動登録します：

```toml
[project.entry-points."oneenv.templates"]
core = "refinire.templates:core_template"
tracing = "refinire.templates:tracing_template"
agents = "refinire.templates:agents_template" 
development = "refinire.templates:development_template"
```

### 対話型CLIセットアップ

最良の体験のために、Refinire CLIウィザードを使用してください：

```bash
# CLI対応でインストール
pip install "refinire[cli]"

# 対話型セットアップを実行
refinire-setup
```

CLIの提供機能：
- **対話型プロバイダー選択** - リッチなターミナルインターフェース
- **スマートテンプレート生成** - 選択に基づいた最適化
- **OneEnv API統合** - 最適なテンプレート作成
- **フォールバック対応** - OneEnvが利用できない場合の代替機能

## コアLLMプロバイダー設定
**テンプレート**: `core`

### OPENAI_API_KEY
- **タイプ**: オプション
- **説明**: GPTモデルのためのOpenAI APIキー
- **取得先**: https://platform.openai.com/api-keys
- **例**: `sk-proj-...`

### ANTHROPIC_API_KEY
- **タイプ**: オプション
- **説明**: ClaudeモデルのためのAnthropic APIキー
- **取得先**: https://console.anthropic.com/
- **例**: `sk-ant-api03-...`

### GOOGLE_API_KEY
- **タイプ**: オプション
- **説明**: GeminiモデルのためのGoogle APIキー
- **取得先**: https://aistudio.google.com/app/apikey
- **例**: `AIzaSy...`

### OPENROUTER_API_KEY
- **タイプ**: オプション
- **説明**: 複数のモデルプロバイダーにアクセスするためのOpenRouter APIキー
- **取得先**: https://openrouter.ai/keys
- **例**: `sk-or-v1-...`

### GROQ_API_KEY
- **タイプ**: オプション
- **説明**: 高速推論モデルのためのGroq APIキー
- **取得先**: https://console.groq.com/keys
- **例**: `gsk_...`

### OLLAMA_BASE_URL
- **タイプ**: オプション
- **デフォルト**: `http://localhost:11434`
- **説明**: ローカルモデルのOllamaサーバーベースURL
- **例**: `http://192.168.1.100:11434`

### LMSTUDIO_BASE_URL
- **タイプ**: オプション
- **デフォルト**: `http://localhost:1234/v1`
- **説明**: ローカルモデルのLM StudioサーバーベースURL
- **例**: `http://192.168.1.100:1234/v1`

## OpenTelemetryトレーシング設定
**テンプレート**: `tracing`

### REFINIRE_TRACE_OTLP_ENDPOINT
- **タイプ**: オプション
- **説明**: OpenTelemetryトレースエクスポート用OTLPエンドポイントURL
- **例**: 
  - `http://localhost:4317` (Grafana Tempo)
  - `http://jaeger:4317` (Jaeger)
  - `https://api.honeycomb.io:443` (Honeycomb)

### REFINIRE_TRACE_SERVICE_NAME
- **タイプ**: オプション
- **デフォルト**: `refinire-agent`
- **説明**: OpenTelemetryトレースのサービス名。トレースデータでアプリケーションを識別するために使用
- **例**: `my-ai-app`, `customer-support-bot`

### REFINIRE_TRACE_RESOURCE_ATTRIBUTES
- **タイプ**: オプション
- **説明**: トレースの追加リソース属性
- **形式**: `key1=value1,key2=value2`
- **例**: `environment=production,team=ai,version=1.0.0`

## AIエージェントとパイプライン設定
**テンプレート**: `agents`

### REFINIRE_DEFAULT_LLM_MODEL
- **タイプ**: オプション
- **デフォルト**: `gpt-4o-mini`
- **説明**: 指定されていない場合に使用するデフォルトLLMモデル
- **例**: `gpt-4o`, `claude-3-sonnet-20240229`, `gemini-pro`

### REFINIRE_DEFAULT_TEMPERATURE
- **タイプ**: オプション
- **デフォルト**: `0.7`
- **説明**: LLM生成のデフォルト温度 (0.0-2.0)
- **範囲**: 0.0 (決定論的) から 2.0 (非常に創造的)

### REFINIRE_DEFAULT_MAX_TOKENS
- **タイプ**: オプション
- **デフォルト**: `2048`
- **説明**: LLM応答のデフォルト最大トークン数
- **例**: `1024`, `4096`, `8192`

## 開発とデバッグ設定
**テンプレート**: `development`

### REFINIRE_DEBUG
- **タイプ**: オプション
- **デフォルト**: `false`
- **説明**: 詳細出力のためのデバッグモードを有効にする
- **値**: `true`, `false`

### REFINIRE_LOG_LEVEL
- **タイプ**: オプション
- **デフォルト**: `INFO`
- **説明**: デバッグ用ログレベル（**非推奨** - Refinireはログ出力の代わりに例外を使用）
- **値**: `DEBUG`, `INFO`, `WARNING`, `ERROR`

### REFINIRE_CACHE_DIR
- **タイプ**: オプション
- **デフォルト**: `~/.cache/refinire`
- **説明**: エージェント応答とモデルのキャッシュディレクトリ
- **例**: `/tmp/refinire-cache`, `./cache`

## プロバイダー固有の環境変数

### Azure OpenAI
```bash
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
```

### OpenRouter
```bash
OPENROUTER_API_KEY=sk-or-v1-...
```

### Groq
```bash
GROQ_API_KEY=gsk_...
```

### LM Studio
```bash
# LM Studioは通常ローカルで実行され、APIキーは不要
LMSTUDIO_BASE_URL=http://localhost:1234/v1
```

## 簡単セットアップ例

### 基本OpenAI設定
```bash
export OPENAI_API_KEY="sk-proj-..."
export REFINIRE_DEFAULT_LLM_MODEL="gpt-4o-mini"
```

### マルチプロバイダー設定
```bash
export OPENAI_API_KEY="sk-proj-..."
export ANTHROPIC_API_KEY="sk-ant-api03-..."
export GOOGLE_API_KEY="AIzaSy..."
export REFINIRE_DEFAULT_LLM_MODEL="gpt-4o-mini"
```

### トレーシング付きローカル開発
```bash
export REFINIRE_DEBUG="true"
export REFINIRE_TRACE_OTLP_ENDPOINT="http://localhost:4317"
export REFINIRE_TRACE_SERVICE_NAME="my-local-app"
```

### プロダクション設定
```bash
export OPENAI_API_KEY="sk-proj-..."
export REFINIRE_TRACE_OTLP_ENDPOINT="https://your-tempo-endpoint:443"
export REFINIRE_TRACE_SERVICE_NAME="production-ai-service"
export REFINIRE_TRACE_RESOURCE_ATTRIBUTES="environment=production,version=1.2.3,team=ai"
```

## 環境変数の優先順位

Refinireは設定で以下の優先順位に従います：

1. **コード内の明示的パラメータ** (最高優先度)
2. **環境変数**
3. **デフォルト値** (最低優先度)

例：
```python
# パラメータからAPIキーを使用し、OPENAI_API_KEYは無視される
llm = get_llm(model="gpt-4o", api_key="explicit-key")

# OPENAI_API_KEY環境変数を使用
llm = get_llm(model="gpt-4o")
```

## セキュリティのベストプラクティス

1. **APIキーをバージョン管理にコミットしない**
2. **ローカル開発では環境ファイル** (`.env`) を使用
3. **プロダクションでは安全なシークレット管理を使用** (AWS Secrets Manager、Azure Key Vaultなど)
4. **APIキーを定期的にローテート**
5. **APIキーには最小権限アクセスを使用**

## トラブルシューティング

### よくある問題

**APIキー不足エラー**:
```
RefinireConfigurationError: OpenAI API key is required
```
解決策: `OPENAI_API_KEY` 環境変数を設定

**接続エラー**:
```
RefinireConnectionError: Failed to connect to Ollama at http://localhost:11434
```
解決策: `OLLAMA_BASE_URL` を確認し、Ollamaが実行されていることを確認

**無効なモデルエラー**:
```
RefinireModelError: Model 'invalid-model' not found
```
解決策: `REFINIRE_DEFAULT_LLM_MODEL` の値と利用可能なモデルを確認

詳細なトラブルシューティング情報については、[メインドキュメント](https://kitfactory.github.io/refinire/)を参照してください。