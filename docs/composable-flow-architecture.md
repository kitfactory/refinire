# Composable Flow Architecture - 組み合わせ可能なフローアーキテクチャ

Refinireの第三の柱である組み合わせ可能なフローアーキテクチャは、複雑なAIワークフローを柔軟で再利用可能なコンポーネントから構築できる革新的なシステムです。

## 基本概念

従来の線形処理から脱却し、条件分岐、ループ、並列処理を含む複雑なワークフローを直感的に定義・実行できます。

```python
from refinire import Flow, FunctionStep, Context
import asyncio

# シンプルなフロー定義
def analyze_input(user_input, ctx):
    ctx.shared_state["analysis"] = f"分析済み: {user_input}"
    return ctx

def generate_response(user_input, ctx):
    analysis = ctx.shared_state["analysis"]
    ctx.shared_state["response"] = f"{analysis}に基づく回答"
    ctx.finish()
    return ctx

# フロー構築
flow = Flow([
    ("analyze", FunctionStep("analyze", analyze_input)),
    ("respond", FunctionStep("respond", generate_response))
])

# 実行
result = asyncio.run(flow.run(input_data="ユーザーリクエスト"))
```

## 簡単な事例

### 1. 基本的な順次フロー

```python
from refinire import Flow, FunctionStep, Context

def step1(input_data, context):
    context.shared_state["step1_result"] = f"処理1: {input_data}"
    print(f"ステップ1実行: {input_data}")
    return context

def step2(input_data, context):
    previous = context.shared_state["step1_result"]
    context.shared_state["step2_result"] = f"処理2: {previous}"
    print(f"ステップ2実行: {previous}")
    context.finish()  # フロー完了
    return context

# 順次実行フロー
sequential_flow = Flow([
    ("first", FunctionStep("first", step1)),
    ("second", FunctionStep("second", step2))
])

# 実行
result = sequential_flow.run_sync(input_data="開始データ")
print(f"最終結果: {result.shared_state}")
```

### 2. 条件分岐フロー

```python
from refinire import Flow, FunctionStep, ConditionStep

def check_input_length(context):
    """入力の長さで分岐判定"""
    return len(context.user_input) > 10

def simple_process(input_data, context):
    context.shared_state["result"] = f"簡単処理: {input_data}"
    context.finish()
    return context

def complex_process(input_data, context):
    context.shared_state["result"] = f"複雑処理: {input_data[:10]}..."
    context.finish()
    return context

# 条件分岐フロー
conditional_flow = Flow({
    "start": ConditionStep("start", check_input_length, "complex", "simple"),
    "simple": FunctionStep("simple", simple_process),
    "complex": FunctionStep("complex", complex_process)
})

# テスト
short_result = conditional_flow.run_sync("短い")
long_result = conditional_flow.run_sync("これは非常に長い入力データです")

print(f"短い入力: {short_result.shared_state['result']}")
print(f"長い入力: {long_result.shared_state['result']}")
```

## 中級事例

### 3. AIエージェント組み込みフロー

```python
from refinire import Flow, FunctionStep, create_simple_gen_agent

def create_ai_workflow():
    """AIエージェントを組み込んだワークフロー"""
    
    # AIエージェント作成
    analyzer = create_simple_gen_agent(
        "analyzer", 
        "入力を分析して要点を抽出してください",
        "gpt-4o-mini"
    )
    
    responder = create_simple_gen_agent(
        "responder",
        "分析結果に基づいて親切な回答を生成してください", 
        "gpt-4o-mini"
    )
    
    def ai_analysis_step(input_data, context):
        """AI分析ステップ"""
        analysis_result = analyzer.run_sync(input_data, context)
        analysis = analysis_result.shared_state["analyzer_result"]
        context.shared_state["analysis"] = analysis
        print(f"AI分析完了: {analysis}")
        return context
    
    def ai_response_step(input_data, context):
        """AI回答生成ステップ"""
        analysis = context.shared_state["analysis"]
        prompt = f"以下の分析に基づいて回答してください: {analysis}"
        response_result = responder.run_sync(prompt, context)
        response = response_result.shared_state["responder_result"]
        context.shared_state["final_response"] = response
        context.finish()
        return context
    
    # AIワークフロー構築
    ai_flow = Flow([
        ("analyze", FunctionStep("analyze", ai_analysis_step)),
        ("respond", FunctionStep("respond", ai_response_step))
    ])
    
    return ai_flow

# 使用例
ai_workflow = create_ai_workflow()
result = ai_workflow.run_sync("プログラミング学習について相談があります")
print(f"最終回答: {result.shared_state['final_response']}")
```

### 4. DAG並列処理フロー

```python
from refinire import Flow, FunctionStep, create_simple_gen_agent

def create_parallel_analysis_flow():
    """複数の分析を並列実行するフロー"""
    
    # 前処理ステップ
    def preprocess_step(input_data, context):
        context.shared_state["preprocessed_data"] = f"前処理済み: {input_data}"
        print(f"前処理完了: {input_data}")
        return context
    
    # 並列分析ステップ
    def sentiment_analysis(input_data, context):
        data = context.shared_state["preprocessed_data"]
        # 実際にはAIエージェントを使用
        context.shared_state["sentiment"] = f"感情分析結果: ポジティブ ({data})"
        print("感情分析完了")
        return context
    
    def keyword_extraction(input_data, context):
        data = context.shared_state["preprocessed_data"]
        context.shared_state["keywords"] = f"キーワード: AI, 技術, 進歩 ({data})"
        print("キーワード抽出完了")
        return context
    
    def category_classification(input_data, context):
        data = context.shared_state["preprocessed_data"]
        context.shared_state["category"] = f"カテゴリ: 技術 ({data})"
        print("カテゴリ分類完了")
        return context
    
    # 結果統合ステップ
    def aggregate_results(input_data, context):
        sentiment = context.shared_state.get("sentiment", "")
        keywords = context.shared_state.get("keywords", "")
        category = context.shared_state.get("category", "")
        
        final_result = f"""
        分析結果統合:
        - {sentiment}
        - {keywords}
        - {category}
        """
        context.shared_state["final_analysis"] = final_result
        context.finish()
        return context
    
    # DAG構造で並列処理を定義
    parallel_flow = Flow({
        "preprocess": FunctionStep("preprocess", preprocess_step),
        "parallel_analysis": {
            "parallel": [
                FunctionStep("sentiment", sentiment_analysis),
                FunctionStep("keywords", keyword_extraction),
                FunctionStep("category", category_classification)
            ]
        },
        "aggregate": FunctionStep("aggregate", aggregate_results)
    })
    
    return parallel_flow

# 使用例
parallel_analysis = create_parallel_analysis_flow()
result = parallel_analysis.run_sync("AI技術について考えています")
print(result.shared_state["final_analysis"])
```

### 5. 動的フロー生成

```python
class DynamicFlowBuilder:
    """動的にフローを構築するビルダー"""
    
    def __init__(self):
        self.steps = []
        self.step_count = 0
    
    def add_processing_step(self, name: str, process_func):
        """処理ステップを追加"""
        self.steps.append((name, FunctionStep(name, process_func)))
        self.step_count += 1
        return self
    
    def add_validation_step(self, name: str, validation_func):
        """検証ステップを追加"""
        def validation_wrapper(input_data, context):
            if validation_func(input_data, context):
                print(f"✓ 検証成功: {name}")
                return context
            else:
                context.shared_state["error"] = f"検証失敗: {name}"
                context.finish()
                return context
        
        self.steps.append((name, FunctionStep(name, validation_wrapper)))
        return self
    
    def add_ai_agent_step(self, name: str, instructions: str, model: str = "gpt-4o-mini"):
        """AIエージェントステップを追加"""
        agent = create_simple_gen_agent(name, instructions, model)
        
        def ai_step(input_data, context):
            result = agent.run_sync(input_data, context)
            context.shared_state[f"{name}_result"] = result.shared_state[f"{name}_result"]
            return context
        
        self.steps.append((name, FunctionStep(name, ai_step)))
        return self
    
    def build(self) -> Flow:
        """フローを構築"""
        if not self.steps:
            raise ValueError("ステップが定義されていません")
        
        # 最後のステップで finish() を呼ぶように調整
        if self.steps:
            last_step_name, last_step = self.steps[-1]
            original_func = last_step.func
            
            def finishing_wrapper(input_data, context):
                context = original_func(input_data, context)
                if not context.finished:
                    context.finish()
                return context
            
            self.steps[-1] = (last_step_name, FunctionStep(last_step_name, finishing_wrapper))
        
        return Flow(self.steps)

# 使用例
builder = DynamicFlowBuilder()

# フローを動的に構築
complex_flow = (builder
    .add_processing_step("preprocess", lambda data, ctx: ctx.update({"preprocessed": f"前処理済み: {data}"}))
    .add_validation_step("validate", lambda data, ctx: len(data) > 5)
    .add_ai_agent_step("analyze", "入力を詳細に分析してください")
    .add_ai_agent_step("summarize", "分析結果を簡潔にまとめてください")
    .build())

# 実行
result = complex_flow.run_sync("複雑なデータ処理タスク")
print(f"処理結果: {result.shared_state}")
```

## 高度な事例

### 5. エラーハンドリング付き復旧フロー

```python
class ResilientFlowSystem:
    """エラー回復機能付きフローシステム"""
    
    def __init__(self):
        self.error_handlers = {}
        self.retry_configs = {}
    
    def add_error_handler(self, step_name: str, handler_func):
        """ステップ専用エラーハンドラーを追加"""
        self.error_handlers[step_name] = handler_func
        return self
    
    def add_retry_config(self, step_name: str, max_retries: int = 3, delay: float = 1.0):
        """リトライ設定を追加"""
        self.retry_configs[step_name] = {
            "max_retries": max_retries,
            "delay": delay
        }
        return self
    
    def create_resilient_step(self, name: str, step_func):
        """エラー回復機能付きステップ作成"""
        
        def resilient_wrapper(input_data, context):
            """エラー回復ラッパー"""
            retry_config = self.retry_configs.get(name, {"max_retries": 1, "delay": 0})
            max_retries = retry_config["max_retries"]
            delay = retry_config["delay"]
            
            for attempt in range(max_retries):
                try:
                    # ステップ実行
                    result = step_func(input_data, context)
                    if attempt > 0:
                        print(f"✓ {name}: {attempt + 1}回目の試行で成功")
                    return result
                    
                except Exception as e:
                    error_info = {
                        "step": name,
                        "attempt": attempt + 1,
                        "error": str(e),
                        "max_retries": max_retries
                    }
                    
                    # エラーハンドラーの実行
                    if name in self.error_handlers:
                        try:
                            recovery_result = self.error_handlers[name](error_info, context)
                            if recovery_result:
                                print(f"✓ {name}: エラーハンドラーで復旧成功")
                                return recovery_result
                        except Exception as handler_error:
                            print(f"✗ {name}: エラーハンドラーも失敗 - {handler_error}")
                    
                    # 最後の試行でない場合はリトライ
                    if attempt < max_retries - 1:
                        print(f"⚠️ {name}: 試行{attempt + 1}失敗、{delay}秒後にリトライ - {e}")
                        import time
                        time.sleep(delay)
                    else:
                        # 最終的に失敗
                        context.shared_state["error"] = error_info
                        context.shared_state["failed_step"] = name
                        print(f"✗ {name}: 全ての試行が失敗 - {e}")
                        raise e
            
            return context
        
        return FunctionStep(name, resilient_wrapper)
    
    def create_fault_tolerant_flow(self, step_definitions: List[Dict]) -> Flow:
        """フォルトトレラントフロー作成"""
        steps = []
        
        for step_def in step_definitions:
            name = step_def["name"]
            func = step_def["func"]
            
            # エラーハンドラー設定
            if "error_handler" in step_def:
                self.add_error_handler(name, step_def["error_handler"])
            
            # リトライ設定
            if "retry_config" in step_def:
                retry_config = step_def["retry_config"]
                self.add_retry_config(
                    name, 
                    retry_config.get("max_retries", 3),
                    retry_config.get("delay", 1.0)
                )
            
            # エラー回復機能付きステップを作成
            resilient_step = self.create_resilient_step(name, func)
            steps.append((name, resilient_step))
        
        return Flow(steps)

# 使用例
resilient_system = ResilientFlowSystem()

# エラーが発生する可能性のある処理関数
def unreliable_data_fetch(input_data, context):
    """不安定なデータ取得（ランダムに失敗）"""
    import random
    if random.random() < 0.7:  # 70%の確率で失敗
        raise Exception("ネットワークエラー")
    
    context.shared_state["fetched_data"] = f"取得データ: {input_data}"
    return context

def unreliable_ai_processing(input_data, context):
    """不安定なAI処理（ランダムに失敗）"""
    import random
    if random.random() < 0.5:  # 50%の確率で失敗
        raise Exception("AI処理エラー")
    
    data = context.shared_state.get("fetched_data", input_data)
    context.shared_state["ai_result"] = f"AI処理結果: {data}"
    context.finish()
    return context

# エラーハンドラー定義
def data_fetch_error_handler(error_info, context):
    """データ取得エラーのハンドラー"""
    print(f"データ取得エラーハンドラー実行: {error_info['error']}")
    # フォールバックデータを設定
    context.shared_state["fetched_data"] = "フォールバックデータ"
    return context

def ai_processing_error_handler(error_info, context):
    """AI処理エラーのハンドラー"""
    print(f"AI処理エラーハンドラー実行: {error_info['error']}")
    # 簡易処理で代替
    data = context.shared_state.get("fetched_data", "デフォルトデータ")
    context.shared_state["ai_result"] = f"簡易処理結果: {data}"
    context.finish()
    return context

# フォルトトレラントフロー定義
fault_tolerant_steps = [
    {
        "name": "data_fetch",
        "func": unreliable_data_fetch,
        "retry_config": {"max_retries": 3, "delay": 0.5},
        "error_handler": data_fetch_error_handler
    },
    {
        "name": "ai_process", 
        "func": unreliable_ai_processing,
        "retry_config": {"max_retries": 2, "delay": 1.0},
        "error_handler": ai_processing_error_handler
    }
]

# フロー作成・実行
fault_tolerant_flow = resilient_system.create_fault_tolerant_flow(fault_tolerant_steps)

try:
    result = fault_tolerant_flow.run_sync("テストデータ")
    print(f"\n最終結果: {result.shared_state}")
except Exception as e:
    print(f"\nフロー実行失敗: {e}")
```

## メリット

- **柔軟性**: 複雑なワークフローを直感的に定義
- **再利用性**: ステップの組み合わせで多様なフローを構築
- **拡張性**: 新しいステップタイプの簡単な追加
- **デバッグ性**: 各ステップの状態とデータフローが透明

組み合わせ可能なフローアーキテクチャにより、開発者は複雑なAIワークフローを効率的に構築・保守できます。
