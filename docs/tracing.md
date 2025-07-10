# トレーシング

Refinireは包括的なトレーシング機能を提供し、AIエージェントのワークフローの監視とデバッグを支援します。

## 📚 ドキュメント構成

### 🔧 基本仕様 - [トレーシング仕様書](tracing_specifications.md)
現在のトレーシング動作の完全な仕様：
- **デフォルトのConsoleトレーシング動作**
- **RefinireAgentとFlowのトレーシング動作**
- **trace ID / span IDの表示機能** ⭐ **新機能**
- **`with trace()`によるFlow統一トレーシング** ⭐ **新機能**
- **制御関数の詳細**

### 📖 詳細ガイド - [トレーシングチュートリアル](tutorials/tracing.md)
実用的な設定とプロダクション利用：
- **OpenTelemetryとの統合**
- **Grafana Tempo / Jaeger設定**
- **環境変数設定**
- **高度なワークフロートレーシング**

## 🚀 クイックスタート

### デフォルト動作（設定不要）
```python
from refinire import RefinireAgent

# デフォルトで色付きコンソールトレーシングが有効
agent = RefinireAgent(name="test", ...)
result = agent.run("Hello")
# 出力: [trace:XXXXXXXX span:YYYYYYYY] とともに色付き表示
```

### シンプルな出力が必要な場合
```python
from refinire import disable_tracing

disable_tracing()  # クリーンな出力
```

### 統一ワークフロートレーシング
```python
from agents.tracing import trace

with trace("workflow"):
    flow1 = Flow(...)
    flow2 = Flow(...)
    # 同一trace_idで統一追跡
```

## 🎯 主な機能

- ✅ **デフォルトで有効** - 設定不要で色付きコンソール出力
- ✅ **trace/span ID表示** - デバッグとオブザーバビリティ向上
- ✅ **Flow統一トレーシング** - `with trace()`で複数Flow統一追跡
- ✅ **柔軟な制御** - 必要に応じて無効化・カスタマイズ可能
- ✅ **OpenTelemetry統合** - プロダクション環境での高度な観測性

## 📋 関連ドキュメント

- **[tracing_specifications.md](tracing_specifications.md)** - 完全な動作仕様とAPI詳細
- **[tutorials/tracing.md](tutorials/tracing.md)** - OpenTelemetry設定とプロダクション利用
- **[tutorials/tracing_ja.md](tutorials/tracing_ja.md)** - 日本語版チュートリアル 