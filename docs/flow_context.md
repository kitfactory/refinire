# コンテキスト管理の比較分析と設計提案

## 1. 概要

Flow/Step ベースへ移行した **agents‑sdk‑models** に最適化したコンテキスト（`Context`）設計を検討するため、下記 3 点を整理する。

1. **OpenAI Agents SDK** における Context の位置づけ
2. **LangChain LCEL** のコンテキスト管理手法
3. それらを踏まえた **agents‑sdk‑models 向け Context 案**

---

## 2. OpenAI Agents SDK の Context

| 項目        | 概要                                                            |
| --------- | ------------------------------------------------------------- |
| **目的**    | 依存性注入/局所状態を格納。LLM へは渡らない。                                     |
| **型**     | 任意のユーザ定義クラス（`@dataclass` や Pydantic 可）。                       |
| **主な内容**  | *DB ハンドラ、ロガー、外部 API* など実行時依存物。<br>*ユーザー ID や権限などセッションスコープ情報*。 |
| **会話履歴**  | Runner が内部管理し Agent へ供給。Context には通常含めない。                     |
| **分岐制御**  | Handoff／複数 Agent 呼び出しロジックをコード側で記述。Context にルーティング値は保持しない。     |
| **メリット**  | *完全自由* で既存 DI パターンに近い。                                        |
| **デメリット** | フィールド定義が散在しやすく、大規模フローで可読性低下。                                  |

---

## 3. LangChain LCEL のコンテキスト管理

| 項目         | 概要                                                                               |
| ---------- | -------------------------------------------------------------------------------- |
| **入力/出力**  | `dict[str, Any]` をチェーン間で受渡し。                                                     |
| **会話履歴**   | `ConversationBufferMemory` など Memory クラスが保持し、入力辞書に展開。                            |
| **ルーティング** | `RunnableConditional` 等でラムダ判定しブランチ。辞書に直接フラグを書く場合も。                               |
| **追加メタ**   | RunManager `metadata/tags` に任意データを添付。v0.2 から `Context`（β）が導入されスコープ型 get/set が可能。 |
| **メリット**   | 学習コストが低く、柔軟性が高い。                                                                 |
| **デメリット**  | キー衝突・型不整合が起きやすく、可読性も低下。                                                          |

---

## 4. 両者比較早見表

| 項目     | Agents SDK    | LangChain LCEL           |
| ------ | ------------- | ------------------------ |
| 型      | 任意クラス         | dict + Memory + metadata |
| 会話履歴   | Runner 内部保持   | Memory クラス               |
| ルーティング | コード内 handoff  | RunnableConditional      |
| 依存性注入  | Context フィールド | dict / metadata          |
| 型安全性   | 高（型付きクラス）     | 低（自由キー）                  |

---

## 5. agents‑sdk‑models 向け Context 設計案

### 5.1 設計方針

1. **型安全で読みやすい** : Pydantic `BaseModel` を採用し IDE 補完を活用。
2. **履歴も保持** : Agents SDK 依存を避け、Flow 内で一貫管理。
3. **ルーティング内包** : `next_label: str | None` をフィールド化し Step 返却で更新。
4. **辞書互換** : `as_dict()/from_dict()` で LCEL とのブリッジを提供。

### 5.2 フィールド例

```python
class Context(BaseModel):
    last_user_input: str | None = None      # 直近ユーザー入力
    messages: list[Message] = []            # 会話履歴
    knowledge: dict[str, Any] = {}          # RAG など外部知識
    prev_outputs: dict[str, Any] = {}       # 前 Step 生成物
    next_label: str | None = None           # ルーティング指示
    artifacts: dict[str, Any] = {}          # Flow 全体成果物
    shared_state: dict[str, Any] = {}       # 任意共有値

    def as_dict(self) -> dict[str, Any]:
        """LCEL 互換辞書へ変換"""
        d = self.dict()
        d["history"] = d.pop("messages")
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Context":
        d = d.copy()
        d["messages"] = d.pop("history", [])
        return cls(**d)
```

### 5.3 利用パターン

```python
async def step_example(ctx: Context) -> Context:
    # 1. ユーザー入力を取得
    user_msg = await ctx.io.ask("入力してください")
    ctx.last_user_input = user_msg
    ctx.messages.append(user_msg)

    # 2. モデル呼び出し
    answer = await model.invoke(ctx.messages)
    ctx.messages.append(answer)

    # 3. ルーティング判定
    ctx.next_label = "done" if is_ok(answer) else "retry"
    return ctx
```

### 5.4 Agents SDK 連携案

* **BridgeStep**: Agents SDK Runner を内部で呼び、Runner.context ↔︎ Context 変換しながら実行。
* **履歴同期**: Runner 側のメッセージを取得し `ctx.messages` にマージ。

### 5.5 メリット & トレードオフ

| 利点                  | 懸念                   |
| ------------------- | -------------------- |
| 型安全・補完が効く           | Pydantic バリデーションコスト増 |
| LCEL との双方向変換で使いまわせる | 二重保持でメモリ消費           |
| ルーティングが明示的          | Agents SDK 的には少し冗長   |

### 5.6 今後の拡張イメージ

1. **ContextPlugin API** : 外部システムと自動同期する拡張ポイント（例: DB/Redis）。
2. **StreamingMessages** : 履歴部のみ遅延ロード/ストリーミング可能に。
3. **TypedArtifacts** : 成果物をクラスごとに型付けして安全性向上。

---

これにより、Agents SDK Models は **型安全・分かりやすさ・他フレームワーク互換** を両立したコンテキスト管理を実現できる。
