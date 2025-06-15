# Composable Flow Architecture - 組み合わせ可能なフローアーキテクチャ

Refinireの第三の柱である組み合わせ可能なフローアーキテクチャは、複雑なAIワークフローを柔軟で再利用可能なコンポーネントから構築できる革新的なシステムです。

## 基本概念

従来の線形処理から脱却し、条件分岐、ループ、並列処理を含む複雑なワークフローを直感的に定義・実行できます。

```python
from refinire import Flow, FunctionStep, create_simple_gen_agent
import asyncio

# 超シンプルなFlow - エージェント1つだけ
flow = Flow(steps=gen_agent)

# 複数ステップのFlow - 自動シーケンシャル実行
flow = Flow([
    ("preprocess", FunctionStep("preprocess", preprocess_func)),
    ("generate", gen_agent),
    ("postprocess", FunctionStep("postprocess", postprocess_func))
])

# 複雑な条件分岐Flow
flow = Flow({
    "input_analysis": FunctionStep("analyze", analyze_input),
    "simple_case": {
        "condition": lambda ctx: len(ctx.user_input) < 50,
        "step": simple_agent,
        "next_step": "output"
    },
    "complex_case": {
        "condition": lambda ctx: len(ctx.user_input) >= 50,
        "step": complex_agent, 
        "next_step": "output"
    },
    "output": FunctionStep("format", format_output)
})
```

## 核となる設計原則

### 1. 組み合わせ可能性 (Composability)

各ステップは独立したコンポーネントとして設計され、自由に組み合わせできます。

```python
# 基本ステップを定義
preprocess_step = FunctionStep("preprocess", preprocess_data)
analysis_step = create_simple_gen_agent("analyzer", "データを分析してください", "gpt-4o-mini")
format_step = FunctionStep("format", format_results)

# 異なる組み合わせで再利用
quick_flow = Flow([("analyze", analysis_step)])
detailed_flow = Flow([
    ("preprocess", preprocess_step),
    ("analyze", analysis_step), 
    ("format", format_step)
])
```

### 2. 宣言的設定 (Declarative Configuration)

処理の「手順」ではなく「構造」を宣言的に定義します。

```python
# 命令的な書き方（従来）
def process_text(input_text):
    if len(input_text) < 100:
        return simple_processor(input_text)
    else:
        preprocessed = preprocess(input_text)
        analyzed = complex_analysis(preprocessed)
        return postprocess(analyzed)

# 宣言的な書き方（Refinire）
flow = Flow({
    "route": ConditionStep("router", 
        condition=lambda ctx: "simple" if len(ctx.user_input) < 100 else "complex",
        branches={"simple": simple_agent, "complex": complex_pipeline}
    )
})
```

### 3. 状態管理の分離 (Separated State Management)

ステップ間の状態共有は `Context` オブジェクトによって明示的に管理されます。

```python
def step1(user_input: str, ctx: Context) -> Context:
    """最初のステップ - データを処理して次ステップに渡す"""
    # English: First step - process data and pass to next step
    processed_data = preprocess(user_input)
    ctx.shared_state["processed"] = processed_data
    ctx.shared_state["timestamp"] = datetime.now()
    return ctx

def step2(user_input: str, ctx: Context) -> Context:
    """2番目のステップ - 前ステップの結果を使用"""
    # English: Second step - use results from previous step
    previous_result = ctx.shared_state["processed"]
    result = analyze(previous_result)
    ctx.shared_state["analysis"] = result
    return ctx
```

## Flow作成パターン

### パターン1: 単一エージェントFlow（最もシンプル）

```python
from refinire import create_simple_gen_agent, Flow

# エージェント作成
agent = create_simple_gen_agent(
    name="assistant",
    instructions="ユーザーの質問に親切に回答してください。",
    model="gpt-4o-mini"
)

# 超シンプルなFlow - 1行で完成
flow = Flow(steps=agent)

# 実行
result = await flow.run(input_data="AIについて教えて")
print(result.shared_state["assistant_result"])
```

### パターン2: シーケンシャルFlow（自動順次実行）

```python
from refinire import Flow, FunctionStep, create_simple_gen_agent

def validate_input(user_input: str, ctx: Context) -> Context:
    """入力データの検証を行う"""
    # English: Validate input data
    if not user_input.strip():
        raise ValueError("空の入力は許可されていません")
    ctx.shared_state["validated_input"] = user_input.strip()
    return ctx

def preprocess_text(user_input: str, ctx: Context) -> Context:
    """テキストの前処理を実行"""
    # English: Execute text preprocessing
    validated = ctx.shared_state["validated_input"]
    processed = validated.lower().replace('\n', ' ')
    ctx.shared_state["preprocessed"] = processed
    return ctx

# 生成エージェント
generator = create_simple_gen_agent(
    name="content_gen",
    instructions="前処理されたテキストに基づいて、有用な内容を生成してください。",
    model="gpt-4o-mini"
)

def format_output(user_input: str, ctx: Context) -> Context:
    """出力フォーマットを整える"""
    # English: Format the output
    generated = ctx.shared_state["content_gen_result"]
    formatted = f"=== 生成結果 ===\n{generated}\n=== 終了 ==="
    ctx.shared_state["final_output"] = formatted
    ctx.finish()  # フロー終了を明示
    return ctx

# シーケンシャルFlow（自動で順次実行）
flow = Flow([
    ("validate", FunctionStep("validate", validate_input)),
    ("preprocess", FunctionStep("preprocess", preprocess_text)),
    ("generate", generator),
    ("format", FunctionStep("format", format_output))
])

# 実行
result = await flow.run(input_data="AIの未来について")
print(result.shared_state["final_output"])
```

### パターン3: 条件分岐Flow

```python
from refinire import Flow, ConditionStep, FunctionStep

def analyze_complexity(user_input: str, ctx: Context) -> Context:
    """入力の複雑さを分析"""
    # English: Analyze input complexity
    word_count = len(user_input.split())
    ctx.shared_state["word_count"] = word_count
    ctx.shared_state["complexity"] = "simple" if word_count < 20 else "complex"
    return ctx

def route_by_complexity(ctx: Context) -> str:
    """複雑さに基づいてルーティング"""
    # English: Route based on complexity
    return ctx.shared_state["complexity"]

# 単純な処理用エージェント
simple_agent = create_simple_gen_agent(
    name="simple_processor",
    instructions="簡潔に回答してください。",
    model="gpt-4o-mini"
)

# 複雑な処理用エージェント
complex_agent = create_simple_gen_agent(
    name="complex_processor", 
    instructions="詳細で包括的な分析を行い、段階的に説明してください。",
    model="gpt-4o-mini"
)

# 条件分岐Flow
flow = Flow({
    "analyze": FunctionStep("analyze", analyze_complexity),
    "router": ConditionStep("router", route_by_complexity, "simple", "complex"),
    "simple": simple_agent,
    "complex": complex_agent
})

# 実行
result = await flow.run(input_data="こんにちは")  # → simple_agent
result = await flow.run(input_data="人工知能の倫理的問題について詳しく教えて")  # → complex_agent
```

### パターン4: 並列処理Flow（3.9倍高速化）

```python
from refinire import Flow, FunctionStep
import asyncio

def preprocess_text(user_input: str, ctx: Context) -> Context:
    """テキストの前処理"""
    # English: Text preprocessing
    ctx.shared_state["processed_text"] = user_input.strip().lower()
    return ctx

def sentiment_analysis(user_input: str, ctx: Context) -> Context:
    """感情分析"""
    # English: Sentiment analysis
    # 実際の分析処理をシミュレート
    import time
    time.sleep(0.5)  # 0.5秒の処理時間をシミュレート
    ctx.shared_state["sentiment"] = "positive"
    return ctx

def keyword_extraction(user_input: str, ctx: Context) -> Context:
    """キーワード抽出"""
    # English: Keyword extraction
    import time
    time.sleep(0.5)  # 0.5秒の処理時間をシミュレート
    text = ctx.shared_state["processed_text"]
    ctx.shared_state["keywords"] = text.split()[:5]
    return ctx

def topic_classification(user_input: str, ctx: Context) -> Context:
    """トピック分類"""
    # English: Topic classification
    import time
    time.sleep(0.5)  # 0.5秒の処理時間をシミュレート
    ctx.shared_state["topic"] = "technology"
    return ctx

def readability_check(user_input: str, ctx: Context) -> Context:
    """可読性チェック"""
    # English: Readability check
    import time
    time.sleep(0.5)  # 0.5秒の処理時間をシミュレート
    ctx.shared_state["readability_score"] = 85
    return ctx

def aggregate_results(user_input: str, ctx: Context) -> Context:
    """結果を統合"""
    # English: Aggregate results
    sentiment = ctx.shared_state.get("sentiment", "unknown")
    keywords = ctx.shared_state.get("keywords", [])
    topic = ctx.shared_state.get("topic", "unknown")
    readability = ctx.shared_state.get("readability_score", 0)
    
    summary = {
        "sentiment": sentiment,
        "keywords": keywords,
        "topic": topic,
        "readability": readability
    }
    ctx.shared_state["analysis_summary"] = summary
    ctx.finish()
    return ctx

# 並列処理Flow
flow = Flow({
    "preprocess": FunctionStep("preprocess", preprocess_text),
    "parallel_analysis": {
        "parallel": [
            FunctionStep("sentiment", sentiment_analysis),
            FunctionStep("keywords", keyword_extraction),
            FunctionStep("topic", topic_classification),
            FunctionStep("readability", readability_check)
        ],
        "next_step": "aggregate",
        "max_workers": 4  # 最大4つの並列実行
    },
    "aggregate": FunctionStep("aggregate", aggregate_results)
})

# パフォーマンス比較
import time

# 順次実行: 約2.0秒（0.5 × 4）
start_time = time.time()
result_sequential = await flow.run(input_data="This is a comprehensive analysis test.")
sequential_time = time.time() - start_time

# 並列実行: 約0.5秒（3.9倍高速化）
start_time = time.time()
result_parallel = await flow.run(input_data="This is a comprehensive analysis test.")
parallel_time = time.time() - start_time

print(f"順次実行: {sequential_time:.2f}秒")
print(f"並列実行: {parallel_time:.2f}秒")
print(f"速度向上: {sequential_time/parallel_time:.1f}倍")
```

### パターン5: 複合Flow（エージェント+関数+条件分岐）

```python
from refinire import Flow, FunctionStep, ConditionStep, create_evaluated_gen_agent

# 入力分析
def analyze_request(user_input: str, ctx: Context) -> Context:
    """リクエストの種類を分析"""
    # English: Analyze request type
    if "コード" in user_input or "プログラム" in user_input:
        ctx.shared_state["request_type"] = "coding"
    elif "説明" in user_input or "教えて" in user_input:
        ctx.shared_state["request_type"] = "explanation"
    else:
        ctx.shared_state["request_type"] = "general"
    return ctx

# ルーティング関数
def route_request(ctx: Context) -> str:
    """リクエストタイプに基づくルーティング"""
    # English: Route based on request type
    return ctx.shared_state["request_type"]

# 専門エージェント（評価機能付き）
coding_agent = create_evaluated_gen_agent(
    name="coding_expert",
    generation_instructions="""
    あなたはプログラミングの専門家です。
    実行可能で品質の高いコードを生成し、詳細な説明を付けてください。
    """,
    evaluation_instructions="""
    生成されたコードを以下の観点で評価してください：
    - 正確性（40点）
    - 可読性（30点）
    - 効率性（30点）
    """,
    threshold=80.0,
    model="gpt-4o-mini"
)

explanation_agent = create_evaluated_gen_agent(
    name="explanation_expert",
    generation_instructions="""
    あなたは教育の専門家です。
    分かりやすく段階的に説明し、具体例を含めてください。
    """,
    evaluation_instructions="""
    説明の品質を以下の観点で評価してください：
    - 分かりやすさ（50点）
    - 正確性（30点）
    - 完全性（20点）
    """,
    threshold=75.0,
    model="gpt-4o-mini"
)

general_agent = create_simple_gen_agent(
    name="general_assistant",
    instructions="親切で丁寧な一般的なアシスタントとして回答してください。",
    model="gpt-4o-mini"
)

# 後処理
def format_response(user_input: str, ctx: Context) -> Context:
    """レスポンスをフォーマット"""
    # English: Format response
    request_type = ctx.shared_state["request_type"]
    
    if request_type == "coding":
        result = ctx.shared_state.get("coding_expert_result", "")
        evaluation = ctx.shared_state.get("coding_expert_evaluation", {})
    elif request_type == "explanation":
        result = ctx.shared_state.get("explanation_expert_result", "")
        evaluation = ctx.shared_state.get("explanation_expert_evaluation", {})
    else:
        result = ctx.shared_state.get("general_assistant_result", "")
        evaluation = None
    
    formatted = f"""
=== {request_type.upper()} レスポンス ===
{result}

{f"品質スコア: {evaluation.get('score', 'N/A')}" if evaluation else ""}
=== 終了 ===
    """.strip()
    
    ctx.shared_state["final_response"] = formatted
    ctx.finish()
    return ctx

# 複合Flow
flow = Flow({
    "analyze": FunctionStep("analyze", analyze_request),
    "router": ConditionStep("router", route_request, "coding", "explanation", "general"),
    "coding": coding_agent,
    "explanation": explanation_agent,
    "general": general_agent,
    "format": FunctionStep("format", format_response)
})

# 実行例
examples = [
    "Pythonでフィボナッチ数列を生成するコードを書いて",
    "機械学習とは何か詳しく説明して",
    "今日の天気はどうですか？"
]

for example in examples:
    result = await flow.run(input_data=example)
    print(f"入力: {example}")
    print(result.shared_state["final_response"])
    print("-" * 50)
```

## 状態管理とコンテキスト

### Context クラスの活用

```python
from refinire import Context

def step_with_state(user_input: str, ctx: Context) -> Context:
    """ステップ間でのデータ共有例"""
    # English: Example of data sharing between steps
    
    # 前のステップの結果を取得
    previous_data = ctx.shared_state.get("previous_result", None)
    
    # 現在のステップで処理
    current_result = process_data(user_input, previous_data)
    
    # 次のステップに結果を渡す
    ctx.shared_state["current_result"] = current_result
    
    # ユーザー入力も保持
    ctx.shared_state["original_input"] = ctx.user_input
    
    # メタデータの追加
    ctx.shared_state["processing_time"] = time.time()
    
    return ctx
```

### エラーハンドリング

```python
def safe_processing_step(user_input: str, ctx: Context) -> Context:
    """エラーハンドリングを含むステップ"""
    # English: Step with error handling
    try:
        result = risky_operation(user_input)
        ctx.shared_state["result"] = result
        ctx.shared_state["status"] = "success"
    except Exception as e:
        ctx.shared_state["error"] = str(e)
        ctx.shared_state["status"] = "error"
        # エラーが発生してもフローを継続
    
    return ctx

def error_recovery_step(user_input: str, ctx: Context) -> Context:
    """エラー回復処理"""
    # English: Error recovery processing
    if ctx.shared_state.get("status") == "error":
        # フォールバック処理
        ctx.shared_state["result"] = "デフォルトの回答を使用します"
        ctx.shared_state["status"] = "recovered"
    
    return ctx
```

## パフォーマンス最適化

### 並列処理による高速化

並列処理を使うことで、独立したタスクを同時実行し、大幅な性能向上を実現できます。

```python
# 順次実行（従来）: 4つのタスク × 0.5秒 = 2.0秒
# 並列実行（Refinire）: max(0.5秒) = 0.5秒（3.9倍高速化）

flow = Flow({
    "preprocess": FunctionStep("prep", preprocess_data),
    "parallel_tasks": {
        "parallel": [
            FunctionStep("task1", time_consuming_task1),  # 0.5秒
            FunctionStep("task2", time_consuming_task2),  # 0.5秒  
            FunctionStep("task3", time_consuming_task3),  # 0.5秒
            FunctionStep("task4", time_consuming_task4),  # 0.5秒
        ],
        "max_workers": 4,
        "next_step": "aggregate"
    },
    "aggregate": FunctionStep("agg", combine_results)
})
```

### メモリ効率的な処理

```python
def memory_efficient_step(user_input: str, ctx: Context) -> Context:
    """メモリ効率を考慮したステップ"""
    # English: Memory-efficient step
    
    # 大きなデータは適切に管理
    large_data = process_large_dataset(user_input)
    
    # 必要な部分のみ保持
    ctx.shared_state["summary"] = summarize(large_data)
    
    # 大きなデータはクリーンアップ
    del large_data
    
    return ctx
```

## ベストプラクティス

### 1. ステップの単一責務原則

各ステップは一つの明確な責務を持つべきです。

```python
# 良い例：責務が明確
def validate_input(user_input: str, ctx: Context) -> Context:
    """入力検証のみを行う"""
    # English: Only perform input validation
    if not user_input.strip():
        raise ValueError("入力が空です")
    ctx.shared_state["validated"] = True
    return ctx

def process_data(user_input: str, ctx: Context) -> Context:
    """データ処理のみを行う"""
    # English: Only perform data processing
    processed = user_input.lower().strip()
    ctx.shared_state["processed_data"] = processed
    return ctx

# 悪い例：複数の責務を持つ
def validate_and_process(user_input: str, ctx: Context) -> Context:
    # 検証と処理を一つのステップで行う（推奨されない）
    if not user_input.strip():
        raise ValueError("入力が空です")
    processed = user_input.lower().strip()
    ctx.shared_state["result"] = processed
    return ctx
```

### 2. 明示的なフロー終了

フローの終了は明示的に示すべきです。

```python
def final_step(user_input: str, ctx: Context) -> Context:
    """最終ステップでは明示的に終了"""
    # English: Explicitly end in final step
    ctx.shared_state["final_result"] = "処理完了"
    ctx.finish()  # 明示的な終了
    return ctx
```

### 3. 再利用可能なコンポーネント設計

```python
# 再利用可能な検証ステップ
def create_validation_step(validation_func, error_message):
    """検証ステップのファクトリ関数"""
    # English: Factory function for validation steps
    def validate(user_input: str, ctx: Context) -> Context:
        if not validation_func(user_input):
            raise ValueError(error_message)
        ctx.shared_state["validated"] = True
        return ctx
    return FunctionStep("validate", validate)

# 使用例
email_validator = create_validation_step(
    lambda x: "@" in x, 
    "有効なメールアドレスを入力してください"
)

phone_validator = create_validation_step(
    lambda x: x.replace("-", "").isdigit(),
    "有効な電話番号を入力してください"
)
```

## 実世界での応用例

### カスタマーサポートシステム

```python
# 顧客問い合わせ処理フロー
customer_support_flow = Flow({
    "classify": FunctionStep("classify", classify_inquiry),
    "router": ConditionStep("route", route_by_category, 
                          "technical", "billing", "general"),
    "technical": technical_support_agent,
    "billing": billing_support_agent,
    "general": general_support_agent,
    "quality_check": quality_assurance_step,
    "escalate": ConditionStep("escalate", 
                            lambda ctx: "manager" if ctx.shared_state["quality_score"] < 80 else "complete",
                            "manager", "complete"),
    "manager": manager_review_agent,
    "complete": finalize_response
})
```

### コンテンツ生成パイプライン

```python
# ブログ記事生成フロー
content_generation_flow = Flow({
    "research": research_agent,
    "outline": outline_generator_agent,
    "parallel_writing": {
        "parallel": [
            FunctionStep("intro", write_introduction),
            FunctionStep("body", write_body),
            FunctionStep("conclusion", write_conclusion)
        ],
        "next_step": "assemble"
    },
    "assemble": FunctionStep("assemble", combine_sections),
    "review": editorial_review_agent,
    "publish": FunctionStep("publish", publish_content)
})
```

### データ分析パイプライン

```python
# データ分析フロー
data_analysis_flow = Flow({
    "validate": data_validation_step,
    "clean": data_cleaning_step,
    "parallel_analysis": {
        "parallel": [
            FunctionStep("stats", statistical_analysis),
            FunctionStep("trends", trend_analysis),
            FunctionStep("patterns", pattern_recognition),
            FunctionStep("anomalies", anomaly_detection)
        ],
        "max_workers": 4,
        "next_step": "correlate"
    },
    "correlate": correlation_analysis_step,
    "visualize": visualization_step,
    "report": report_generation_agent
})
```

## まとめ

Refinireの組み合わせ可能なフローアーキテクチャは：

1. **シンプルさ**: `Flow(steps=agent)` で始まり、必要に応じて複雑化
2. **柔軟性**: 条件分岐、並列処理、ループなど豊富な制御構造
3. **再利用性**: コンポーネントベースの設計で高い再利用性
4. **パフォーマンス**: 並列処理で3.9倍の高速化を実現
5. **保守性**: 宣言的設定と明確な状態管理

従来の複雑なワークフロー構築から、直感的で保守可能な設計へのパラダイムシフトを提供します。 