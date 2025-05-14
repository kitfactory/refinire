# 実装TODO

- [x] AnthropicModel の async テストを作成する
- [x] GeminiModel の async テストを作成する
- [x] OllamaModel のテストを作成する
- [x] AgentPipeline の `_build_generation_prompt` メソッドのテストを作成する
- [x] AgentPipeline の `_build_evaluation_prompt` メソッドのテストを作成する
- [x] 評価が閾値未満の場合の `improvements_callback` の動作テストを作成する
- [x] ガードレール機能（Guardrails）統合テストを作成する
- [x] ツール統合のテストを作成する
- [x] ダイナミックプロンプト機能のテストを作成する
- [x] ルーティング機能のテストを作成する
- [x] コードカバレッジを90%以上に向上させる
- [x] examples フォルダ内のスクリプトを動作検証する
- [x] docs フォルダ内のドキュメントの整合性を確認・更新する

## docs/ APIリファレンス & チュートリアル構築（MkDocs Material）
- [x] MkDocs Material をプロジェクトに開発環境に導入する
- [x] mkdocs.yml 設定ファイルを作成し、サイト構成を設計する
- [x] docs/index.md にプロジェクト概要・導入方法を記載する
- [x] docs/api_reference.md に主要クラス・関数のAPIリファレンスを記載する
- [x] docs/tutorials/ ディレクトリを作成し、チュートリアル記事（例：クイックスタート、応用例）を追加する
- [x] コードブロックや図（PlantUML等）を活用し、分かりやすいドキュメントにする
- [x] mkdocs serve でローカルプレビューし、表示・リンク切れ等を確認する
- [x] 完成したらGitにコミット・プッシュする

## 粒度の確認

- 上記のステップは対象ファイルと対象機能が明確であり、現状の粒度で十分です。 