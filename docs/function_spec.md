# 機能仕様書

## 1. シンプルな生成
- ユースケース手順
  1. ユーザーが入力文を与える
  2. AgentPipelineが生成指示をもとにLLMで生成
  3. 結果を返す
- ユースケースフロー図
```plantuml
@startuml
actor User
participant AgentPipeline
participant Agent
User -> AgentPipeline: 入力文
AgentPipeline -> Agent: 生成指示+入力
Agent -> AgentPipeline: 生成結果
AgentPipeline -> User: 結果返却
@enduml
```

## 2. 生成物の評価付き生成
- ユースケース手順
  1. ユーザーが入力文を与える
  2. AgentPipelineが生成指示で生成
  3. AgentPipelineが評価指示で評価
  4. 評価スコアが閾値以上なら結果返却、未満ならリトライor失敗
- ユースケースフロー図
```plantuml
@startuml
actor User
participant AgentPipeline
participant Agent as Generator
participant Agent as Evaluator
User -> AgentPipeline: 入力文
AgentPipeline -> Generator: 生成指示+入力
Generator -> AgentPipeline: 生成結果
AgentPipeline -> Evaluator: 評価指示+生成結果
Evaluator -> AgentPipeline: 評価スコア
alt スコア>=閾値
  AgentPipeline -> User: 結果返却
else スコア<閾値
  AgentPipeline -> User: 失敗通知
end
@enduml
```

## 3. ツール連携
- ユースケース手順
  1. ユーザーが入力文を与える
  2. AgentPipelineがツール付きで生成
  3. 必要に応じてツール関数が呼ばれる
  4. 結果を返す
- ユースケースフロー図
```plantuml
@startuml
actor User
participant AgentPipeline
participant Agent
participant Tool
User -> AgentPipeline: 入力文
AgentPipeline -> Agent: 生成指示+入力+ツール
Agent -> Tool: ツール呼び出し
Tool -> Agent: ツール結果
Agent -> AgentPipeline: 生成結果
AgentPipeline -> User: 結果返却
@enduml
```

## 4. ガードレール（入力ガードレール）
- ユースケース手順
  1. ユーザーが入力文を与える
  2. AgentPipelineがガードレール関数で入力検査
  3. 問題なければ生成、問題あればブロック
- ユースケースフロー図
```plantuml
@startuml
actor User
participant AgentPipeline
participant Guardrail
participant Agent
User -> AgentPipeline: 入力文
AgentPipeline -> Guardrail: 入力検査
alt 問題なし
  AgentPipeline -> Agent: 生成
  Agent -> AgentPipeline: 生成結果
  AgentPipeline -> User: 結果返却
else 問題あり
  AgentPipeline -> User: ブロック通知
end
@enduml
```

---

## 参考
- 詳細なコード例は [docs/pipeline_examples.md](pipeline_examples.md) を参照。 