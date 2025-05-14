# APIリファレンス

本ページでは、主要なクラス・関数の概要・主な引数・戻り値・役割をまとめます。

## クラス・関数一覧

| 名前                | 種別     | 概要                                             |
|---------------------|----------|--------------------------------------------------|
| get_llm             | 関数     | モデル名・プロバイダー名からLLMインスタンスを取得 |
| AgentPipeline       | クラス   | 生成・評価・ツール・ガードレールを統合したパイプライン |
| OpenAIResponsesModel| クラス   | OpenAI用モデルラッパー                           |
| GeminiModel         | クラス   | Google Gemini用モデルラッパー                    |
| ClaudeModel         | クラス   | Anthropic Claude用モデルラッパー                  |
| OllamaModel         | クラス   | Ollama用モデルラッパー                           |

---

## get_llm
- モデル名・プロバイダー名からLLMインスタンスを返すファクトリ関数

- 引数:
    - model (str): モデル名
    - provider (str, optional): プロバイダー名（省略時は自動推論）
- 戻り値: LLMインスタンス

### 引数
| 名前       | 型                 | 必須/オプション | デフォルト | 説明                                 |
|------------|--------------------|----------------|------------|--------------------------------------|
| model      | str                | 必須           | -          | 使用するLLMモデル名                  |
| provider   | str (optional)     | オプション     | None       | モデルのプロバイダー名（自動推論可）|

### 戻り値
`LLMインスタンス`

## AgentPipeline
- 生成・評価・ツール・ガードレールを統合したパイプライン管理クラス
- 主な引数:
    - name (str): パイプライン名
    - generation_instructions (str): 生成用プロンプト
    - evaluation_instructions (str, optional): 評価用プロンプト
    - model (str or LLM): 使用するモデル
    - generation_tools (list, optional): 生成時ツール
    - input_guardrails/output_guardrails (list, optional): 入出力ガードレール
    - threshold (int): 評価閾値
    - retries (int): リトライ回数
    - retry_comment_importance (list[str], optional): 重要度指定
- 主なメソッド:
    - run(input): 入力に対して生成・評価・自己改善を実行
- 戻り値: 生成・評価結果

### 引数
| 名前                    | 型                                    | 必須/オプション | デフォルト        | 説明                                             |
|-------------------------|---------------------------------------|----------------|-------------------|--------------------------------------------------|
| name                    | str                                   | 必須           | -                 | パイプライン名                                    |
| generation_instructions | str                                   | 必須           | -                 | 生成用システムプロンプト                          |
| evaluation_instructions | str (optional)                        | 必須           | None              | 評価用システムプロンプト                          |
| model                   | str or LLM                            | オプション     | None              | 使用するLLMモデル名またはLLMインスタンス          |
| generation_tools        | list (optional)                       | オプション     | []                | 生成時に使用するツールのリスト                    |
| evaluation_tools        | list (optional)                       | オプション     | []                | 評価時に使用するツールのリスト                    |
| input_guardrails        | list (optional)                       | オプション     | []                | 生成時の入力ガードレールリスト                    |
| output_guardrails       | list (optional)                       | オプション     | []                | 評価時の出力ガードレールリスト                    |
| routing_func            | Callable (optional)                   | オプション     | None              | 出力ルーティング用関数                            |
| session_history         | list (optional)                       | オプション     | []                | セッション履歴                                    |
| history_size            | int                                   | オプション     | 10                | 履歴保持数                                        |
| threshold               | int                                   | オプション     | 85                | 評価スコアの閾値                                  |
| retries                 | int                                   | オプション     | 3                 | リトライ試行回数                                  |
| debug                   | bool                                  | オプション     | False             | デバッグモードフラグ                              |
| improvement_callback    | Callable[[Any, EvaluationResult], None] (optional) | オプション | None  | 改善提案用コールバック                            |
| dynamic_prompt          | Callable[[str], str] (optional)      | オプション     | None              | 動的プロンプト生成関数                            |
| retry_comment_importance| list[str] (optional)                 | オプション     | []                | リトライ時にプロンプトに含めるコメント重大度レベル |

### 戻り値
`生成・評価結果（`EvaluationResult` を含むオブジェクト）`

## モデルラッパークラス
| クラス名                | 概要                       |
|------------------------|----------------------------|
| OpenAIResponsesModel   | OpenAI API用               |
| GeminiModel            | Google Gemini API用        |
| ClaudeModel            | Anthropic Claude API用     |
| OllamaModel            | Ollama API用               |

---

## クラス図（mermaid）

```mermaid
classDiagram
    class AgentPipeline {
        +run(input)
        -_build_generation_prompt()
        -_build_evaluation_prompt()
    }
    class OpenAIResponsesModel
    class GeminiModel
    class ClaudeModel
    class OllamaModel

    AgentPipeline --> OpenAIResponsesModel
    AgentPipeline --> GeminiModel
    AgentPipeline --> ClaudeModel
    AgentPipeline --> OllamaModel
```

