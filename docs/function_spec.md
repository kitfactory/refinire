# 機能仕様書

## 1. シンプルな生成
- ユースケース手順
  1. ユーザーが入力文を与える
  2. Pipelineが生成テンプレートをもとにLLMで生成
  3. 結果を返す
- ユースケースフロー図
```plantuml
@startuml
actor User
participant Pipeline
participant Agent
User -> Pipeline: 入力文
Pipeline -> Agent: 生成テンプレート+入力
Agent -> Pipeline: 生成結果
Pipeline -> User: 結果返却
@enduml
```

## 2. 生成物の評価付き生成
- ユースケース手順
  1. ユーザーが入力文を与える
  2. Pipelineが生成テンプレートで生成
  3. Pipelineが評価テンプレートで評価
  4. 評価スコアが閾値以上なら結果返却、未満ならリトライor失敗
- ユースケースフロー図
```plantuml
@startuml
actor User
participant Pipeline
participant Agent as Generator
participant Agent as Evaluator
User -> Pipeline: 入力文
Pipeline -> Generator: 生成テンプレート+入力
Generator -> Pipeline: 生成結果
Pipeline -> Evaluator: 評価テンプレート+生成結果
Evaluator -> Pipeline: 評価スコア
alt スコア>=閾値
  Pipeline -> User: 結果返却
else スコア<閾値
  Pipeline -> User: 失敗通知
end
@enduml
```

## 3. ツール連携
- ユースケース手順
  1. ユーザーが入力文を与える
  2. Pipelineがツール付きで生成
  3. 必要に応じてツール関数が呼ばれる
  4. 結果を返す
- ユースケースフロー図
```plantuml
@startuml
actor User
participant Pipeline
participant Agent
participant Tool
User -> Pipeline: 入力文
Pipeline -> Agent: 生成テンプレート+入力+ツール
Agent -> Tool: ツール呼び出し
Tool -> Agent: ツール結果
Agent -> Pipeline: 生成結果
Pipeline -> User: 結果返却
@enduml
```

## 4. ガードレール（入力ガードレール）
- ユースケース手順
  1. ユーザーが入力文を与える
  2. Pipelineがガードレール関数で入力検査
  3. 問題なければ生成、問題あればブロック
- ユースケースフロー図
```plantuml
@startuml
actor User
participant Pipeline
participant Guardrail
participant Agent
User -> Pipeline: 入力文
Pipeline -> Guardrail: 入力検査
alt 問題なし
  Pipeline -> Agent: 生成
  Agent -> Pipeline: 生成結果
  Pipeline -> User: 結果返却
else 問題あり
  Pipeline -> User: ブロック通知
end
@enduml
```

---

## 参考
- 詳細なコード例は [docs/pipeline_examples.md](pipeline_examples.md) を参照。 