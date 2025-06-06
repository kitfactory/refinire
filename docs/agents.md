# Agent パターン一覧

## 概要

このドキュメントでは、Agents SDK Modelsで利用可能な、または実装予定のAgentパターンを整理しています。各AgentはStepクラスとして実装され、Flowワークフロー内で使用できます。

## 実装状況

- ✅ 実装済み
- 🚧 部分実装
- 📋 設計済み
- 💡 検討中

---

## 現在実装済みのAgent

### GenAgent ✅
**目的**: LLMベースの生成と評価を行う汎用エージェント

**主な機能**:
- テキスト生成
- 生成結果の評価
- リトライ機能
- 構造化出力対応

**使用例**:
- 文書作成
- コード生成
- 要約作成

### ClarifyAgent ✅
**目的**: ユーザーとの対話を通じて要件や情報を明確化

**主な機能**:
- 対話的質問生成
- 要件収集
- ターン管理
- 完了条件判定

**使用例**:
- 要件定義
- ユーザー情報収集
- 設定ウィザード

---

## 典型的なAgentパターン（カテゴリ別）

## 1. Processing Agents（処理系）

### TransformerAgent 💡
**目的**: データを一つの形式から別の形式に変換

**主な機能**:
- フォーマット変換（JSON ↔ XML ↔ YAML）
- データ正規化
- エンコーディング変換
- スキーマ変換

**使用例**:
```python
transformer = TransformerAgent(
    name="json_to_xml",
    transformation_type="json_to_xml",
    schema_mapping=mapping_rules
)
```

### ExtractorAgent 💡
**目的**: 非構造化データから特定の情報を抽出し、構造化されたデータとして出力

**責務の明確化**:
- **入力**: テキスト、HTML、PDF、ログファイルなどの非構造化データ
- **処理**: 事前定義されたパターンやルールに基づく情報抽出
- **出力**: 構造化されたデータ（辞書、リスト、Pydanticモデル）

**主な機能**:
- **パターンベース抽出**: 正規表現、XPath、CSSセレクター
- **LLMベース抽出**: 自然言語による抽出指示とスキーマ定義
- **マルチフォーマット対応**: テキスト、HTML、JSON、XML、CSV対応
- **バリデーション**: 抽出結果の検証と品質チェック
- **複数抽出**: 一つの入力から複数の情報を同時抽出
- **エラーハンドリング**: 抽出失敗時のフォールバック処理

**他Agentとの役割分担**:
- **vs ClassifierAgent**: 分類ではなく具体的なデータ値を抽出
- **vs TransformerAgent**: 形式変換ではなく情報の取り出し
- **vs ValidatorAgent**: 検証ではなく抽出が主目的

**具体的な抽出パターン**:
```python
# 構造化されたデータ抽出例
extractor = ExtractorAgent(
    name="contact_extractor",
    extraction_rules=[
        EmailRule(pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        PhoneRule(pattern=r'\b\d{3}-\d{3}-\d{4}\b'),
        NameRule(llm_prompt="Extract person names from the text"),
        DateRule(formats=['%Y-%m-%d', '%m/%d/%Y'])
    ],
    output_schema=ContactInfo  # Pydanticモデル
)
```

**使用例**:
- **文書からメタデータ抽出**: PDF契約書から契約者名、期間、金額
- **メールから構造化情報抽出**: 問い合わせメールから顧客情報、要件
- **ログから診断情報抽出**: エラーログからタイムスタンプ、エラーコード、詳細
- **Webページから商品情報抽出**: ECサイトから価格、仕様、在庫状況
- **帳票からデータ抽出**: 請求書から金額、項目、支払い期限

### ValidatorAgent 💡
**目的**: データや条件の検証を行う

**主な機能**:
- 入力データ検証
- ビジネスルール適用
- スキーマ検証
- カスタム検証ルール

**使用例**:
```python
validator = ValidatorAgent(
    name="email_validator",
    validation_rules=[
        EmailFormatRule(),
        DomainWhitelistRule(allowed_domains)
    ]
)
```

### AggregatorAgent 💡
**目的**: 複数のソースからデータを集約・統合

**主な機能**:
- データ結合
- 重複排除
- 統計計算
- レポート生成

**使用例**:
- 複数API結果統合
- データ分析レポート
- ダッシュボード生成

## 2. Decision Agents（判断系）

### RouterAgent 💡
**目的**: 入力を分析して適切な処理パスに振り分け

**主な機能**:
- 意図検出
- 分類ベースルーティング
- 条件ベースルーティング
- フォールバック処理

**使用例**:
```python
router = RouterAgent(
    name="intent_router",
    routes={
        "question": "qa_flow",
        "complaint": "support_flow",
        "request": "service_flow"
    },
    classifier=IntentClassifier()
)
```

### ClassifierAgent 💡
**目的**: 入力を事前定義されたカテゴリに分類

**主な機能**:
- テキスト分類
- 感情分析
- 優先度判定
- 言語検出

**使用例**:
- サポートチケット分類
- 感情分析
- スパム検出

### DecisionAgent 💡
**目的**: 複数の基準に基づいて複雑な判断を実行

**主な機能**:
- 多基準評価
- 重み付け判定
- リスク評価
- 承認/却下判定

**使用例**:
```python
decision = DecisionAgent(
    name="loan_approval",
    criteria=[
        CreditScoreCriteria(weight=0.4),
        IncomeCriteria(weight=0.3),
        HistoryCriteria(weight=0.3)
    ],
    threshold=0.7
)
```

### PrioritizerAgent 💡
**目的**: タスクやアイテムに優先度を付けて並び替え

**主な機能**:
- 優先度スコア計算
- 複数基準での並び替え
- 動的優先度調整

**使用例**:
- タスク管理
- サポートチケット優先度付け
- リソース配分

## 3. Communication Agents（対話系）

### NotificationAgent 💡
**目的**: 各種チャネルを通じて通知を送信

**主な機能**:
- メール送信
- Slack/Teams通知
- SMS送信
- Webhook呼び出し

**使用例**:
```python
notifier = NotificationAgent(
    name="error_notifier",
    channels=[
        EmailChannel(recipients=admin_emails),
        SlackChannel(webhook_url=slack_webhook)
    ]
)
```

### ChatbotAgent 💡
**目的**: 対話型インターフェースの提供

**主な機能**:
- 自然言語理解
- 対話管理
- コンテキスト保持
- 応答生成

**使用例**:
- カスタマーサポート
- FAQ対応
- 情報検索

### InterviewAgent 💡
**目的**: 構造化されたインタビューや質問票を実行

**主な機能**:
- 動的質問生成
- 回答検証
- 条件分岐
- 結果集約

**使用例**:
- 顧客調査
- 診断質問
- 設定収集

## 4. Data Agents（データ系）

### CollectorAgent 💡
**目的**: 複数のソースからデータを収集

**主な機能**:
- API呼び出し
- ファイル読み込み
- データベース接続
- Webスクレイピング

**使用例**:
```python
collector = CollectorAgent(
    name="weather_collector",
    sources=[
        APISource(url="weather.api.com"),
        DatabaseSource(query="SELECT * FROM weather")
    ]
)
```

### CacheAgent 💡
**目的**: データのキャッシングと高速アクセス

**主な機能**:
- メモリキャッシュ
- 永続化キャッシュ
- TTL管理
- キャッシュ戦略

**使用例**:
- API応答キャッシュ
- 計算結果保存
- セッション管理

### SearchAgent 💡
**目的**: 情報検索と関連データの取得

**主な機能**:
- テキスト検索
- セマンティック検索
- ベクトル検索
- ハイブリッド検索

**使用例**:
- 文書検索
- FAQ検索
- 類似データ発見

## 5. Control Agents（制御系）

### OrchestratorAgent 💡
**目的**: 複数のAgentやタスクの協調実行

**主な機能**:
- タスク調整
- 実行順序制御
- 依存関係管理
- エラー処理

**使用例**:
```python
orchestrator = OrchestratorAgent(
    name="data_pipeline",
    tasks=[
        ("collect", CollectorAgent()),
        ("validate", ValidatorAgent()),
        ("transform", TransformerAgent()),
        ("store", StorageAgent())
    ]
)
```

### MonitorAgent 💡
**目的**: システムやプロセスの監視

**主な機能**:
- ヘルスチェック
- パフォーマンス監視
- アラート生成
- ログ分析

**使用例**:
- システム監視
- APIヘルスチェック
- パフォーマンス追跡

### SchedulerAgent 💡
**目的**: タスクのスケジューリングと時間管理

**主な機能**:
- 定期実行
- 遅延実行
- 条件トリガー
- 依存関係考慮

**使用例**:
- バッチ処理
- 定期レポート
- リマインダー

## 6. Security Agents（セキュリティ系）

### AuthAgent 💡
**目的**: 認証と認可の管理

**主な機能**:
- ユーザー認証
- トークン管理
- 権限チェック
- セッション管理

**使用例**:
- API認証
- ユーザーログイン
- 権限確認

### AuditAgent 💡
**目的**: 操作ログとセキュリティ監査

**主な機能**:
- 操作ログ記録
- セキュリティイベント検出
- コンプライアンス確認
- レポート生成

**使用例**:
- 操作履歴追跡
- セキュリティ監査
- コンプライアンス確認

---

## 実装優先度

### 高優先度（次期リリース候補）
1. **RouterAgent** - 最も汎用的で多くの場面で必要
2. **ValidatorAgent** - データ品質確保に必須
3. **ExtractorAgent** - 情報処理の基本機能
4. **NotificationAgent** - アラートやレポート配信に必要

### 中優先度（将来版での実装）
1. **ClassifierAgent** - ルーティングと組み合わせて強力
2. **TransformerAgent** - データ変換の汎用性
3. **AggregatorAgent** - レポート・分析機能
4. **SearchAgent** - 情報検索機能

### 低優先度（長期的な拡張）
1. **OrchestratorAgent** - 複雑なワークフロー制御
2. **MonitorAgent** - 運用監視機能
3. **AuthAgent** - セキュリティ強化
4. **SchedulerAgent** - 高度なタスク管理

---

## 設計原則

### 1. Stepクラスベース
全てのAgentは`Step`クラスを継承し、Flow内で統一的に使用可能

### 2. 設定駆動
各AgentはPydanticモデルで設定を管理し、型安全性を確保

### 3. LLMPipeline統合
LLMを使用するAgentは`LLMPipeline`または`InteractivePipeline`を活用

### 4. ツール統合
OpenAI Function CallingやMCPサーバーとの統合をサポート

### 5. エラーハンドリング
適切なエラー処理とリトライ機能を標準装備

---

## 使用パターン例

### 1. カスタマーサポートワークフロー
```python
flow = Flow([
    RouterAgent(name="intent_router"),  # 問い合わせ分類
    ClarifyAgent(name="detail_collector"),  # 詳細聞き取り
    ValidatorAgent(name="info_validator"),  # 情報検証
    NotificationAgent(name="ticket_creator")  # チケット作成通知
])
```

### 2. データ処理パイプライン
```python
flow = Flow([
    CollectorAgent(name="data_collector"),  # データ収集
    ValidatorAgent(name="data_validator"),  # データ検証
    TransformerAgent(name="data_transformer"),  # データ変換
    AggregatorAgent(name="report_generator")  # レポート生成
])
```

### 3. 承認ワークフロー
```python
flow = Flow([
    ExtractorAgent(name="request_extractor"),  # 申請内容抽出
    ClassifierAgent(name="urgency_classifier"),  # 緊急度分類
    DecisionAgent(name="auto_approver"),  # 自動承認判定
    NotificationAgent(name="result_notifier")  # 結果通知
])
```

---

## 次のステップ

1. **RouterAgent**の詳細設計と実装
2. 各Agentの共通インターフェース定義
3. Agent間の連携パターンの標準化
4. 包括的なテストスイート作成
5. 使用例とドキュメントの充実 