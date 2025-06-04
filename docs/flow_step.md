# Agents SDK Models: Flow/DAG 機能評価と拡張設計 (v3)


# Step / Flow API リファレンス

本ドキュメントでは **agents‑sdk‑models** における `Step` と `Flow` が提供する主要メソッド・属性を一覧表で整理する。CLI でも GUI でも利用しやすいよう **同期ユーティリティ** と **非同期タスク** の両系統を含める。

## 1. Step インターフェース

| メンバー   | 種別          | シグネチャ / 型                                               | 説明                                                           |
| ------ | ----------- | ------------------------------------------------------- | ------------------------------------------------------------ |
| `name` | 属性          | `str`                                                   | ステップ識別名（DSL で参照）                                             |
| `run`  | `async def` | `run(user_input: str \| None, ctx: Context) -> Context` | ステップを 1 回実行し、新しい `Context` を返す。必要に応じ `ctx.next_label` を更新する。 |

> **実装例**: `UserInputStep`, `ConditionStep`, `AgentPipeline` など。

---

## 2. Flow クラス

### 🚀 **新機能：拡張されたコンストラクタ**

Flowクラスは**3つの方法**で作成できるようになりました：

```python
# 1. 単一ステップ（最もシンプル！）
flow = Flow(steps=gen_agent)

# 2. シーケンシャルステップ（自動接続！）
flow = Flow(steps=[step1, step2, step3])

# 3. 従来方式（複雑なフロー用）
flow = Flow(start="step1", steps={"step1": step1, "step2": step2})
```

| メソッド / 属性     | 同期 / 非同期     | シグネチャ                                      | 役割・備考                                                                      |
| ------------- | ------------ | ------------------------------------------ | -------------------------------------------------------------------------- |
| `__init__`    | sync         | `Flow(start=None, steps=Dict[str,Step]|List[Step]|Step)` | **拡張！** 辞書・リスト・単一ステップに対応。リストは自動接続、単一は直接実行。                                                    |
| `context`     | 属性           | `Context`                                  | 現在の共有状態・履歴などを保持。                                                           |                                               |
| `finished`    | 属性           | `bool`                                     | `ctx.next_label is None` で `True`。                                         |                                               |
| `run`         | **async**    | \`run(initial\_input: str                  | None = None) -> Context\`                                                  | 対話を含まない “一発実行” 用高レベル API。ユーザー入力が不要なフロー向け。     |
| `run_loop`    | **async**    | `run_loop() -> None`                       | 非同期タスクとして常駐。`UserInputStep` に当たると一時停止し、`feed()` 待ち。GUI / WebSocket と相性が良い。 |                                               |
| `next_prompt` | sync         | \`next\_prompt() -> str                    | None\`                                                                     | `ctx.awaiting_prompt` を取得しクリア。ポーリング式 CLI で利用。 |
| `feed`        | sync / async | `feed(user_input: str) -> None`            | ユーザー入力を `ctx.last_user_input` に格納し、`run_loop` を再開させる。                      |                                               |
| `step`        | sync         | `step() -> None`                           | 非同期を使わず 1 ステップだけ同期的に進める。LLM 呼び出し中はブロック。                                    |                                               |

### ライフサイクル図（概要）

1. `flow.run_loop()` をタスク起動
2. Flow が `UserInputStep` に到達 ⇒ `ctx.awaiting_prompt` に質問文設定 & `return`
3. アプリ側 → `next_prompt()` で取得 → ユーザーに提示
4. `feed()` で回答注入 → `ctx.waiter.set()` ⇒ `run_loop` 再開
5. `ctx.next_label is None` になったらフロー終了、`flow.finished == True`。

---

## 3. 🎯 新しい超シンプル使用例

新しいFlowコンストラクタを使った超シンプルな例：

```python
from agents_sdk_models import create_simple_gen_agent, Flow, DebugStep

# 1. 単一ステップ（たった1行！）
gen_agent = create_simple_gen_agent("assistant", "親切に回答します", "gpt-4o-mini")
flow = Flow(steps=gen_agent)
result = await flow.run(input_data="こんにちは")
print(result.shared_state["assistant_result"])

# 2. シーケンシャルステップ（自動接続！）
reviewer = create_simple_gen_agent("reviewer", "回答をレビューします", "gpt-4o")
flow = Flow(steps=[gen_agent, reviewer, DebugStep("done", "完了")])
result = await flow.run(input_data="AIについて教えて")

# 3. 複数GenAgent（マルチエージェント）
idea_gen = create_simple_gen_agent("idea", "アイデア生成", "gpt-4o-mini")
writer = create_simple_gen_agent("writer", "記事執筆", "gpt-4o")
editor = create_simple_gen_agent("editor", "編集・校正", "claude-3-5-sonnet-latest")

flow = Flow(steps=[idea_gen, writer, editor])  # 自動でアイデア→執筆→編集
result = await flow.run(input_data="AI技術について")
```

## 4. 同期 vs 非同期 利用例

### 非同期 GUI / WebSocket

```python
flow = Flow(...)
asyncio.create_task(flow.run_loop())
...
prompt = await flow.context.awaiting_prompt_event.wait()
await websocket.send_json({"prompt": prompt})
...
await flow.feed(user_input_from_client)
```

### 同期 CLI

```python
flow = Flow(...)
while not flow.finished:
    if (prompt := flow.next_prompt()):
        user = input(prompt + "> ")
        flow.feed(user)
    else:
        flow.step()  # LLM 呼び出しなど
print(flow.context.artifacts)
```

---

これで Step / Flow の API 一覧と運用パターンが俯瞰できる。詳しい `Context` フィールド定義や型変換ユーティリティは **Agents Sdk Context Design** キャンバスを参照。


---

## 4. Flow/Step 機能の評価

### 4.1 強み

* **宣言的 StepによるDAG 定義** — 学習コストが低い
* **Pipeline 再利用性** — 既存資産をそのままステップとして活用
* **暗黙の END** — ゴールステップ省略で最短構成
* **動的ルーティング** — `router_fn` による条件分岐が容易

### 4.2 課題

* **大規模化で可読性低下** — 辞書定義が肥大
* **共有状態ガイド不足** — Context 設計が必須
* **ユーザー入力ステップ未整備** — 標準型を追加すべき
* **並列実行未対応** — Fork/Join 構文の拡充が必要

### 4.3 総評

80% ユースケースを最短コードで解決するライト級だが、課題克服で大規模・対話ワークフローへ拡張可能。

---

## 5. Flow 拡張設計提案

### 5.1 設計目標

1. **宣言的 DSL** × 可視性
2. **ユーザー入力ステップ** の標準化
3. **型安全 Context** 共有
4. **非同期・並列** サポート
5. **オブザーバビリティ** 組み込み

### 5.2 共通インターフェース `Step`

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Step(Protocol):
    name: str
    async def run(self, user_input: str | None, ctx: "Context") -> "Context":
        ...
```

`AgentPipeline` も同シグネチャで適合。

### 5.3 代表的 Step 実装
`UserInputStep`, `ConditionStep`, `ForkStep`, `JoinStep` など（詳細は前版と同等）。

### 5.4 DSL 使用例

```python
flow = Flow(
    start="welcome",
    steps={
        "welcome": UserInputStep("welcome", prompt="ご用件を入力してください"),
        "triage": triage_agent_pipeline,   # Step 実装済み
        "need_approval": ConditionStep(
            "need_approval",
            cond=lambda ctx: ctx.shared_state.get("need_approval", False),
            if_true="ask_ok", if_false="final"
        ),
        "ask_ok": UserInputStep("ask_ok", prompt="実行してもよろしいですか？(y/n)"),
        "final": response_agent_pipeline,
    },
)

# ---------------- 非同期 GUI / API サーバ ----------------
asyncio.create_task(flow.async_run_loop())
...
prompt = await flow.context.awaiting_prompt_event.wait()
await websocket.send_json({"prompt": prompt})
...
flow.feed(user_answer)

# ---------------- 同期 CLI ----------------
while not flow.finished:
    if (p := flow.next_prompt()):
        flow.feed(input(p + "> "))
    else:
        flow.step()
print(flow.context.artifacts)
```

### 5.5 Context
**→ 詳細は “Agents Sdk Context Design” キャンバスを参照。**

---

### 5.6 並列実行サポート

| 構文                              | 説明                             |                                |
| ------------------------------- | ------------------------------ | ------------------------------ |
| `ForkStep(branches: list[str])` | 指定ステップを **async gather** で並列起動 |                                |
| \`JoinStep(join\_type="all"     | "any")\`                       | `Context` マージ後 `next_label` 設定 |

### 5.7 GUI / チャット統合

* `flow.async_run_loop()` をバックグラウンドタスク化
* `ctx.io` 抽象で CLI / Web / Bot を統一
* ストリーミング応答は `Step` 内でトークン逐次送信

### 5.8 オブザーバビリティ

* `before_run` / `after_run` フック → OpenTelemetry Span
* `ctx.trace_id` で全 Step 横断の相関 ID

### 5.9 ロードマップ

| バージョン    | 主要機能                                                                        |
| -------- | --------------------------------------------------------------------------- |
| **v0.1** | `Step`, `UserInputStep`, `Context`, 直列 Flow, `async_run` / `async_run_loop` |
| **v0.2** | `ConditionStep`, `ForkStep`, `JoinStep`, 並列実行                               |
| **v0.3** | GUI/チャット I/O アダプタ、OpenTelemetry 連携                                          |
| **v0.4** | Step テンプレート登録、AutoDocs 生成                                                   |
| **v1.0** | 安定版リリース、セマンティックバージョニング                                                      |

---
