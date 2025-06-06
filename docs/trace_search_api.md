# トレース検索API

## 概要

Agents SDK Modelsのトレース検索機能は、フロー名やエージェント名でトレースを検索し、実行履歴を追跡・分析するための包括的なAPIを提供します。

## 主要クラス

### TraceRegistry

トレースの保存・検索を管理するメインクラスです。

| メソッド | 説明 | 戻り値 |
|---------|------|--------|
| `register_trace()` | 新しいトレースを登録 | None |
| `search_by_flow_name()` | フロー名でトレースを検索 | List[TraceMetadata] |
| `search_by_agent_name()` | エージェント名でトレースを検索 | List[TraceMetadata] |
| `search_by_tags()` | タグでトレースを検索 | List[TraceMetadata] |
| `search_by_status()` | ステータスでトレースを検索 | List[TraceMetadata] |
| `search_by_time_range()` | 時間範囲でトレースを検索 | List[TraceMetadata] |
| `complex_search()` | 複数条件による複合検索 | List[TraceMetadata] |
| `get_statistics()` | トレース統計を取得 | Dict[str, Any] |
| `export_traces()` | トレースをファイルにエクスポート | None |
| `import_traces()` | ファイルからトレースをインポート | int |

### TraceMetadata

トレースのメタデータを表現するデータクラスです。

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `trace_id` | str | ユニークなトレース識別子 |
| `flow_name` | Optional[str] | フロー名 |
| `flow_id` | Optional[str] | フローインスタンスID |
| `agent_names` | List[str] | 使用されたエージェント名のリスト |
| `start_time` | datetime | トレース開始時刻 |
| `end_time` | Optional[datetime] | トレース終了時刻 |
| `status` | str | トレースステータス (running, completed, error) |
| `total_spans` | int | トレース内のスパン数 |
| `error_count` | int | エラースパン数 |
| `duration_seconds` | Optional[float] | 総実行時間 |
| `tags` | Dict[str, Any] | カスタムタグ |
| `artifacts` | Dict[str, Any] | トレース成果物 |

## 検索メソッド詳細

### フロー名による検索

```python
# 完全一致検索
exact_matches = registry.search_by_flow_name("customer_support_workflow", exact_match=True)

# 部分一致検索
partial_matches = registry.search_by_flow_name("support", exact_match=False)
```

**パラメータ:**
- `flow_name` (str): 検索するフロー名
- `exact_match` (bool): 完全一致を使用するか（デフォルト: False）

### エージェント名による検索

```python
# 特定のエージェントを検索
agent_traces = registry.search_by_agent_name("SupportAgent", exact_match=True)

# エージェントパターンを検索
pattern_traces = registry.search_by_agent_name("Agent", exact_match=False)
```

**パラメータ:**
- `agent_name` (str): 検索するエージェント名
- `exact_match` (bool): 完全一致を使用するか（デフォルト: False）

### タグによる検索

```python
# すべてのタグがマッチする必要がある
all_match = registry.search_by_tags({"env": "prod", "version": "1.0"}, match_all=True)

# いずれかのタグがマッチすればよい
any_match = registry.search_by_tags({"priority": "high"}, match_all=False)
```

**パラメータ:**
- `tags` (Dict[str, Any]): 検索するタグ
- `match_all` (bool): すべてのタグがマッチする必要があるか（デフォルト: True）

### 時間範囲による検索

```python
from datetime import datetime, timedelta

# 過去1時間のトレース
recent = registry.search_by_time_range(
    start_time=datetime.now() - timedelta(hours=1)
)

# 特定の期間のトレース
period = registry.search_by_time_range(
    start_time=datetime(2024, 1, 1),
    end_time=datetime(2024, 1, 31)
)
```

**パラメータ:**
- `start_time` (Optional[datetime]): 検索開始時刻
- `end_time` (Optional[datetime]): 検索終了時刻

### 複合検索

```python
# 複数条件による検索
results = registry.complex_search(
    flow_name="support",           # フロー名に"support"を含む
    agent_name="Agent",            # エージェント名に"Agent"を含む
    status="completed",            # ステータスが"completed"
    tags={"priority": "high"},     # タグに"priority": "high"を含む
    start_time=datetime.now() - timedelta(days=7),  # 過去7日間
    max_results=10                 # 最大10件
)
```

**パラメータ:**
- `flow_name` (Optional[str]): フロー名フィルタ
- `agent_name` (Optional[str]): エージェント名フィルタ
- `tags` (Optional[Dict[str, Any]]): タグフィルタ
- `status` (Optional[str]): ステータスフィルタ
- `start_time` (Optional[datetime]): 開始時刻フィルタ
- `end_time` (Optional[datetime]): 終了時刻フィルタ
- `max_results` (Optional[int]): 最大結果数

## 統計情報

```python
stats = registry.get_statistics()
print(f"総トレース数: {stats['total_traces']}")
print(f"ユニークフロー名数: {stats['unique_flow_names']}")
print(f"ユニークエージェント名数: {stats['unique_agent_names']}")
print(f"総スパン数: {stats['total_spans']}")
print(f"総エラー数: {stats['total_errors']}")
print(f"平均実行時間: {stats['average_duration_seconds']:.2f}秒")
```

**戻り値の構造:**
```python
{
    "total_traces": int,
    "status_distribution": Dict[str, int],
    "unique_flow_names": int,
    "unique_agent_names": int,
    "total_spans": int,
    "total_errors": int,
    "average_duration_seconds": float,
    "flow_names": List[str],
    "agent_names": List[str]
}
```

## エクスポート・インポート

### エクスポート

```python
# JSONファイルにエクスポート
registry.export_traces("traces_backup.json", format="json")
```

### インポート

```python
# JSONファイルからインポート
imported_count = registry.import_traces("traces_backup.json", format="json")
print(f"{imported_count}件のトレースをインポートしました")
```

## グローバルレジストリ

```python
from agents_sdk_models import get_global_registry, set_global_registry

# グローバルレジストリを取得
registry = get_global_registry()

# カスタムレジストリを設定
custom_registry = TraceRegistry(storage_path="custom_traces.json")
set_global_registry(custom_registry)
```

## Flow統合

Flowクラスは自動的にトレースレジストリと統合されます：

```python
# フロー作成時に自動的にトレースが登録される
flow = Flow(
    name="my_workflow",
    steps=my_steps,
    start="first_step"
)

# フロー実行後、トレースが更新される
await flow.run("input_data")

# 検索で見つけることができる
traces = registry.search_by_flow_name("my_workflow")
```

## 使用例

### 1. 特定エージェントを使用したフローの検索

```python
# SupportAgentを使用したすべてのフローを検索
support_traces = registry.search_by_agent_name("SupportAgent")
for trace in support_traces:
    print(f"フロー: {trace.flow_name}, 開始時刻: {trace.start_time}")
```

### 2. エラーが発生したフローの分析

```python
# エラーが発生したトレースを検索
error_traces = registry.search_by_status("error")
for trace in error_traces:
    error_step = trace.tags.get("error_step", "不明")
    error_type = trace.tags.get("error_type", "不明")
    print(f"エラーフロー: {trace.flow_name}, ステップ: {error_step}, エラー: {error_type}")
```

### 3. パフォーマンス分析

```python
# 完了したトレースの実行時間を分析
completed_traces = registry.search_by_status("completed")
durations = [t.duration_seconds for t in completed_traces if t.duration_seconds]
if durations:
    avg_duration = sum(durations) / len(durations)
    print(f"平均実行時間: {avg_duration:.2f}秒")
```

### 4. 最近のアクティビティ監視

```python
# 過去1時間のアクティビティを監視
recent_traces = registry.get_recent_traces(hours=1)
print(f"過去1時間で{len(recent_traces)}件のフローが実行されました")

# ステータス別の分布
status_counts = {}
for trace in recent_traces:
    status_counts[trace.status] = status_counts.get(trace.status, 0) + 1
print("ステータス分布:", status_counts)
```

## ベストプラクティス

1. **フロー名の命名規則**: 検索しやすいように一貫した命名規則を使用する
2. **エージェント名の標準化**: エージェント名に一貫したパターンを使用する
3. **タグの活用**: 環境、バージョン、優先度などの情報をタグで管理する
4. **定期的なクリーンアップ**: 古いトレースを定期的に削除する
5. **エクスポート**: 重要なトレースデータは定期的にエクスポートしてバックアップする

## 注意事項

- トレースレジストリはメモリ内に保存されるため、アプリケーション再起動時にはデータが失われます
- 永続化が必要な場合は、`storage_path`を指定してTraceRegistryを作成してください
- 大量のトレースを扱う場合は、定期的なクリーンアップを実施してください
- 検索結果は開始時刻の降順（新しい順）でソートされます 