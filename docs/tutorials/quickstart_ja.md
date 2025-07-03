# クイックスタート

このチュートリアルでは、Refinireを使った最小限のLLM活用例を紹介します。数分で動作するAIエージェントを作成できます。

## 前提条件

- Python 3.10以上がインストールされていること
- 使用するプロバイダーのAPIキーが設定されていること

```bash
# OpenAI（OpenAIモデルを使用する場合）
export OPENAI_API_KEY=your_api_key_here

# Anthropic（Claudeモデルを使用する場合）
export ANTHROPIC_API_KEY=your_api_key_here

# Google（Geminiモデルを使用する場合）
export GOOGLE_API_KEY=your_api_key_here
```

## インストール

```bash
pip install refinire
```

## 1. シンプルなエージェント作成

RefinireAgentで基本的な対話エージェントを作成します。

```python
from refinire import RefinireAgent

# シンプルなエージェント
agent = RefinireAgent(
    name="assistant",
    generation_instructions="あなたは親切なアシスタントです。明確で理解しやすい回答を提供してください。",
    model="gpt-4o-mini"
)

result = agent.run("こんにちは！何をお手伝いできますか？")
print(result.content)
```

## 2. マルチプロバイダー対応

異なるLLMプロバイダーをシームレスに使用できます。

```python
from refinire import RefinireAgent

# OpenAI
openai_agent = RefinireAgent(
    name="openai_assistant",
    generation_instructions="あなたは親切なアシスタントです。",
    model="gpt-4o-mini"
)

# Anthropic Claude
claude_agent = RefinireAgent(
    name="claude_assistant", 
    generation_instructions="あなたは親切なアシスタントです。",
    model="claude-3-haiku"
)

# Google Gemini
gemini_agent = RefinireAgent(
    name="gemini_assistant",
    generation_instructions="あなたは親切なアシスタントです。",
    model="gemini-1.5-flash"
)

# Ollama（ローカル）
ollama_agent = RefinireAgent(
    name="ollama_assistant",
    generation_instructions="あなたは親切なアシスタントです。",
    model="llama3.1:8b"
)
```

## 3. 自動品質保証

組み込み評価と自動改善機能付きのエージェントを作成します。

```python
from refinire import RefinireAgent

# 自動品質管理付きエージェント
agent = RefinireAgent(
    name="quality_assistant",
    generation_instructions="技術トピックに関して正確で明確なコンテンツを生成してください。",
    evaluation_instructions="""
    生成されたコンテンツを正確性、明確性、完全性で評価してください。
    0-100で評価し、改善のための具体的なフィードバックを提供してください。
    """,
    threshold=80.0,  # スコアが80未満の場合自動的に再試行
    max_retries=2,
    model="gpt-4o-mini"
)

result = agent.run("機械学習を分かりやすく説明してください")
print(f"内容: {result.content}")
print(f"品質スコア: {result.evaluation_score}")
print(f"試行回数: {result.attempts}")
```

## 4. ツール統合

外部機能を使用できるエージェントを作成します。

```python
from refinire import RefinireAgent, tool

@tool
def get_weather(city: str) -> str:
    """都市の現在の天気を取得"""
    # ここに天気APIロジックを実装
    return f"{city}の天気: 晴れ、気温22度"

@tool
def calculate(expression: str) -> float:
    """数式を安全に計算"""
    try:
        # シンプルな計算機 - 本番では適切なパーシングを実装
        return eval(expression.replace("^", "**"))
    except:
        return 0.0

# ツール付きエージェント
agent = RefinireAgent(
    name="tool_assistant",
    generation_instructions="必要に応じて利用可能なツールを使ってユーザーを支援してください。",
    tools=[get_weather, calculate],
    model="gpt-4o-mini"
)

result = agent.run("東京の天気と15 * 23の計算結果を教えて")
print(result.content)
```

## 5. コンテキスト管理とメモリ

ステートフルな会話とデータ共有にコンテキストを使用します。

```python
from refinire import RefinireAgent, Context

# コンテキスト管理付きエージェント
agent = RefinireAgent(
    name="context_assistant",
    generation_instructions="あなたは親切なアシスタントです。以前のコンテキストを使って関連性のある回答を提供してください。",
    context_providers_config=[
        {
            "type": "conversation_history",
            "max_items": 5
        }
    ],
    model="gpt-4o-mini"
)

# 共有コンテキストを作成
ctx = Context()

# 最初のやり取り
result1 = agent.run("私の名前はアリスで、機械学習に興味があります", ctx)
print(f"回答1: {result1.content}")

# 二番目のやり取り（前の会話を記憶）
result2 = agent.run("どのトピックから始めるべきでしょうか？", ctx)
print(f"回答2: {result2.content}")
```

## 6. 動的プロンプトのための変数埋め込み

プロンプトで動的変数置換を使用します。

```python
from refinire import RefinireAgent, Context

# 変数埋め込み対応エージェント
agent = RefinireAgent(
    name="dynamic_assistant",
    generation_instructions="あなたは{{role}}として{{audience}}の{{task_type}}に関する質問を支援します。スタイル: {{response_style}}",
    model="gpt-4o-mini"
)

# 変数付きコンテキストを設定
ctx = Context()
ctx.shared_state = {
    "role": "技術専門家",
    "audience": "初心者開発者",
    "task_type": "プログラミング",
    "response_style": "段階的な説明"
}

result = agent.run("{{task_type}}の学習を始めるにはどうすればよいですか？", ctx)
print(result.content)
```

## 7. Flowを使った高度なワークフロー

複雑な複数ステップのワークフローを作成します。

```python
from refinire import RefinireAgent, Flow, FunctionStep
import asyncio

def preprocess_data(ctx):
    """ユーザー入力の前処理"""
    ctx.shared_state["processed"] = True
    return "データの前処理が正常に完了しました"

# 複数ステップワークフロー
analyzer = RefinireAgent(
    name="analyzer",
    generation_instructions="与えられたトピックを分析し、重要な洞察を提供してください。",
    model="gpt-4o-mini"
)

summarizer = RefinireAgent(
    name="summarizer",
    generation_instructions="分析結果に基づいて簡潔な要約を作成してください: {{RESULT}}",
    model="gpt-4o-mini"
)

# フローを作成
flow = Flow(start="preprocess", steps={
    "preprocess": FunctionStep("preprocess", preprocess_data),
    "analyze": analyzer,
    "summarize": summarizer
})

async def main():
    result = await flow.run("人工知能のトレンド")
    print(f"分析: {result.shared_state.get('analyzer_result', 'N/A')}")
    print(f"要約: {result.shared_state.get('summarizer_result', 'N/A')}")

# 非同期ワークフローを実行
asyncio.run(main())
```

## 8. MCPサーバー統合

高度なツール機能のためのModel Context Protocolサーバーとの統合。

```python
from refinire import RefinireAgent

# MCPサーバー対応エージェント
agent = RefinireAgent(
    name="mcp_assistant",
    generation_instructions="MCPサーバーツールを使用してユーザーのリクエストを支援してください。",
    mcp_servers=[
        "stdio://filesystem-server",
        "http://localhost:8000/mcp"
    ],
    model="gpt-4o-mini"
)

result = agent.run("現在のディレクトリのプロジェクトファイルを分析してください")
print(result.content)
```

---

## 重要なポイント

### ✅ 現在のベストプラクティス
- **RefinireAgent**: すべてのLLMプロバイダーの統一インターフェース
- **組み込み品質保証**: 自動評価と再試行メカニズム
- **ツール統合**: `@tool`デコレータによる簡単な関数呼び出し
- **コンテキスト管理**: インテリジェントなメモリと会話処理
- **変数埋め込み**: `{{variable}}`構文による動的プロンプト生成
- **Flowアーキテクチャ**: シンプルな宣言的構文による複雑なワークフロー
- **MCP統合**: Model Context Protocolによる標準化されたツールアクセス

### 🚀 パフォーマンス機能
- **マルチプロバイダー対応**: OpenAI、Anthropic、Google、Ollama
- **自動並列化**: 組み込み並列処理機能
- **スマートコンテキスト**: 自動コンテキストフィルタリングと最適化
- **構造化出力**: Pydanticモデルによる型安全なレスポンス

### 🔗 次のステップ
- [高度機能](advanced_ja.md) - 複雑なワークフローとパターン
- [コンテキスト管理](context_management_ja.md) - メモリと状態管理
- [Flowガイド](flow_complete_guide.md) - 包括的なワークフロー構築
- [サンプル集](../../examples/) - 実践的な実装例