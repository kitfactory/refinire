# コンテキスト管理とルーティング - 完全ガイド

このガイドでは、RefinireのContext機能とRefinireAgentの結果に基づくルーティング設定について詳しく説明します。

## 目次

1. [Contextの基本概念](#contextの基本概念)
2. [RefinireAgentでのルーティング設定](#refinireagentでのルーティング設定)
3. [ContextProviderシステム](#contextproviderシステム)
4. [高度なルーティングパターン](#高度なルーティングパターン)
5. [実践的な例](#実践的な例)
6. [ベストプラクティス](#ベストプラクティス)

## Contextの基本概念

### Contextオブジェクトとは

Contextは、Flow実行中にステップ間でデータを共有し、状態を管理するための中核的なオブジェクトです。

```python
from refinire import Context, Flow, RefinireAgent

# Contextの基本構造
ctx = Context()

# 主要なプロパティ
ctx.result              # 現在のステップの実行結果
ctx.shared_state        # ステップ間で共有される辞書型データ
ctx.evaluation_result   # RefinireAgentの評価結果（評価機能使用時）
ctx.prev_outputs        # 過去のエージェント出力の履歴
```

### Contextのライフサイクル

1. **Flow開始**: 新しいContextオブジェクトが作成
2. **ステップ実行**: 各ステップの結果がContextに格納
3. **データ共有**: 後続ステップがContextから前の結果を参照
4. **Flow終了**: 最終結果がContextから取得

## RefinireAgentでのルーティング設定

### 基本的なルーティングパターン

RefinireAgentの出力結果に基づいて条件分岐を行う基本的な方法：

```python
from refinire import Flow, ConditionStep, RefinireAgent

# 1. 分類エージェント
classifier = RefinireAgent(
    name="content_classifier",
    generation_instructions="""
    入力内容を分析して、以下のカテゴリのいずれかで分類してください：
    - technical: 技術的な内容
    - business: ビジネス関連
    - support: サポート・質問
    
    カテゴリ名のみを返してください。
    """,
    model="gpt-4o-mini"
)

# 2. ルーティング判定関数
def route_by_category(ctx):
    """Contextの結果に基づいてルーティング"""
    result = str(ctx.result).lower().strip()
    
    if "technical" in result:
        return "tech_handler"
    elif "business" in result:
        return "business_handler"
    elif "support" in result:
        return "support_handler"
    else:
        return "general_handler"

# 3. 専門エージェント定義
tech_agent = RefinireAgent(
    name="tech_specialist",
    generation_instructions="技術的な専門知識を活用して詳細に回答してください",
    model="gpt-4o-mini"
)

business_agent = RefinireAgent(
    name="business_specialist",
    generation_instructions="ビジネス観点から実践的なアドバイスを提供してください",
    model="gpt-4o-mini"
)

support_agent = RefinireAgent(
    name="support_specialist",
    generation_instructions="親切で分かりやすいサポートを提供してください",
    model="gpt-4o-mini"
)

# 4. ルーティングFlow
routing_flow = Flow({
    "classify": classifier,
    "route": ConditionStep("route", route_by_category, {
        "tech_handler": "technical",
        "business_handler": "business", 
        "support_handler": "support",
        "general_handler": "general"
    }),
    "technical": tech_agent,
    "business": business_agent,
    "support": support_agent,
    "general": RefinireAgent(
        name="general_assistant",
        generation_instructions="一般的な質問に丁寧に回答してください",
        model="gpt-4o-mini"
    )
})

# 実行例
async def run_routing_example():
    result1 = await routing_flow.run("Pythonでのマルチスレッド処理について教えて")
    print(f"技術的質問の結果: {result1}")
    
    result2 = await routing_flow.run("新規事業の収益モデルを検討したい")
    print(f"ビジネス質問の結果: {result2}")
```

### 評価スコアを使ったルーティング

RefinireAgentの評価機能を活用したより高度なルーティング：

```python
# 評価機能付きエージェント
evaluator = RefinireAgent(
    name="content_evaluator",
    generation_instructions="入力内容を詳しく分析してください",
    evaluation_instructions="分析の完全性と有用性を0-100で評価してください",
    threshold=70.0,
    model="gpt-4o-mini"
)

# 評価スコアに基づくルーティング
def route_by_evaluation_score(ctx):
    """評価スコアに基づく品質ルーティング"""
    if hasattr(ctx, 'evaluation_result') and ctx.evaluation_result:
        score = ctx.evaluation_result.get('score', 0)
        passed = ctx.evaluation_result.get('passed', False)
        
        if score >= 90:
            return "premium_handler"
        elif score >= 70:
            return "standard_handler"
        else:
            return "basic_handler"
    return "basic_handler"

# 品質別対応Flow
quality_flow = Flow({
    "evaluate": evaluator,
    "quality_route": ConditionStep("quality_route", route_by_evaluation_score, {
        "premium_handler": "premium",
        "standard_handler": "standard", 
        "basic_handler": "basic"
    }),
    "premium": RefinireAgent(
        name="premium_service",
        generation_instructions="最高品質の詳細で包括的な回答を提供してください",
        model="gpt-4o-mini"
    ),
    "standard": RefinireAgent(
        name="standard_service", 
        generation_instructions="標準的な品質で丁寧に回答してください",
        model="gpt-4o-mini"
    ),
    "basic": RefinireAgent(
        name="basic_service",
        generation_instructions="基本的なレベルで簡潔に回答してください",
        model="gpt-4o-mini"
    )
})
```

### 複合条件でのルーティング

複数の条件を組み合わせた高度なルーティング：

```python
def complex_routing_logic(ctx):
    """複合条件による高度なルーティング"""
    # 基本結果の取得
    result = str(ctx.result).lower()
    
    # 評価結果の取得
    evaluation_score = 0
    if hasattr(ctx, 'evaluation_result') and ctx.evaluation_result:
        evaluation_score = ctx.evaluation_result.get('score', 0)
    
    # shared_stateからの情報取得
    user_type = ctx.shared_state.get('user_type', 'standard')
    urgency = ctx.shared_state.get('urgency', 'normal')
    
    # 複合判定ロジック
    if urgency == 'urgent':
        return "urgent_handler"
    elif "error" in result or "問題" in result:
        if evaluation_score > 80:
            return "expert_troubleshoot"
        else:
            return "basic_troubleshoot"
    elif user_type == 'premium' and evaluation_score > 85:
        return "premium_service"
    elif "技術" in result or "technical" in result:
        return "technical_specialist"
    else:
        return "general_service"

# ユーザー情報設定関数
def set_user_context(data, ctx):
    """ユーザーコンテキストを設定"""
    # 実際の実装では、ユーザーIDから情報を取得
    ctx.shared_state['user_type'] = 'premium'  # 例: premium, standard, basic
    ctx.shared_state['urgency'] = 'normal'     # 例: urgent, normal, low
    return data

# 複合ルーティングFlow
complex_flow = Flow({
    "setup_context": FunctionStep("setup", set_user_context),
    "analyze": evaluator,
    "complex_route": ConditionStep("complex_route", complex_routing_logic, {
        "urgent_handler": "urgent",
        "expert_troubleshoot": "expert_trouble",
        "basic_troubleshoot": "basic_trouble", 
        "premium_service": "premium",
        "technical_specialist": "tech_spec",
        "general_service": "general"
    }),
    # 各ハンドラーの定義...
})
```

## ContextProviderシステム

### ContextProviderの概要

ContextProviderは、RefinireAgentが実行時に適切なコンテキスト情報を自動的に収集・提供するシステムです。これにより、エージェントは会話履歴、関連ファイル、ソースコードなどの情報を効率的に活用できます。

### 基本的な使用方法

#### 1. シンプルな設定

```python
from refinire.agents.pipeline import RefinireAgent

# 基本的なコンテキスト設定
context_config = [
    {
        "type": "conversation_history",
        "max_items": 5,
        "max_tokens": 1000
    }
]

agent = RefinireAgent(
    name="assistant",
    generation_instructions="過去の会話を参考にして適切に回答してください",
    model="gpt-4o-mini",
    context_providers_config=context_config
)
```

#### 2. 複数のプロバイダーを使用

```python
context_config = [
    {
        "type": "conversation_history",
        "max_items": 5
    },
    {
        "type": "fixed_file",
        "file_path": "README.md"
    },
    {
        "type": "source_code",
        "max_files": 3,
        "max_file_size": 500
    }
]

agent = RefinireAgent(
    name="comprehensive_assistant",
    generation_instructions="提供された全ての情報を活用して回答してください",
    model="gpt-4o-mini",
    context_providers_config=context_config
)
```

## ContextProviderの種類と詳細設定

### 1. ConversationHistoryProvider

会話履歴を管理し、エージェントに過去のやり取りを提供します。

```python
# 基本的な会話履歴の設定
conversation_config = {
    "type": "conversation_history",
    "max_items": 10,        # 保持するメッセージ数
    "max_tokens": 2000      # 最大トークン数（オプション）
}

agent = RefinireAgent(
    name="chat_agent",
    generation_instructions="過去の会話を参考にして適切に回答してください",
    model="gpt-4o-mini",
    context_providers_config=[conversation_config]
)

# 会話の実行例
async def conversation_example():
    agent = RefinireAgent(
        name="assistant",
        generation_instructions="親切なアシスタントとして回答してください",
        model="gpt-4o-mini",
        context_providers_config=[{
            "type": "conversation_history",
            "max_items": 5
        }]
    )
    
    # 複数回の対話
    response1 = await agent.run_async("私の名前は田中です")
    print(f"1回目: {response1}")
    
    response2 = await agent.run_async("私の名前を覚えていますか？")
    print(f"2回目: {response2}")  # 「田中」さんを覚えている
```

### 2. FixedFileProvider

指定されたファイルの内容を常にコンテキストに含めます。

```python
# 設定ファイルを常に参照
fixed_file_config = {
    "type": "fixed_file",
    "file_path": "config/system_config.yaml"
}

# READMEファイルを参照する例
readme_config = {
    "type": "fixed_file", 
    "file_path": "README.md"
}

agent = RefinireAgent(
    name="config_assistant",
    generation_instructions="システム設定に関する質問に答えてください",
    model="gpt-4o-mini",
    context_providers_config=[fixed_file_config, readme_config]
)

# 実行例
async def fixed_file_example():
    result = await agent.run_async("このシステムの主な機能は何ですか？")
    # README.mdの内容を参照した回答が得られる
    print(result)
```

### 3. SourceCodeProvider

ユーザーの質問に関連するソースコードファイルを自動検索・提供します。

```python
# ソースコード検索の設定
source_code_config = {
    "type": "source_code",
    "max_files": 5,                    # 最大ファイル数
    "max_file_size": 1000,             # ファイルあたりの最大サイズ（バイト）
    "file_extensions": [".py", ".js"],  # 対象拡張子（オプション）
    "exclude_dirs": ["node_modules", "__pycache__"]  # 除外ディレクトリ（オプション）
}

agent = RefinireAgent(
    name="code_assistant",
    generation_instructions="提供されたソースコードを参考にして技術的な質問に答えてください",
    model="gpt-4o-mini",
    context_providers_config=[source_code_config]
)

# 実行例
async def source_code_example():
    result = await agent.run_async("RefinireAgentクラスの実装について教えてください")
    # 関連するPythonファイルが自動的に検索され、コンテキストに含まれる
    print(result)
```

### 4. CutContextProvider

他のプロバイダーのコンテキストを指定された長さに圧縮します。

```python
# コンテキストの圧縮設定
cut_context_config = {
    "type": "cut_context",
    "provider": {
        "type": "source_code",
        "max_files": 10,
        "max_file_size": 2000
    },
    "max_chars": 3000,           # 最大文字数
    "cut_strategy": "middle",    # 圧縮戦略: start/end/middle
    "preserve_sections": True    # セクション構造を保持
}

agent = RefinireAgent(
    name="efficient_assistant",
    generation_instructions="提供された情報を効率的に活用して回答してください",
    model="gpt-4o-mini", 
    context_providers_config=[cut_context_config]
)

# 実行例
async def cut_context_example():
    result = await agent.run_async("このプロジェクトの全体的なアーキテクチャを説明してください")
    # 大量のソースコードが適切なサイズに圧縮されてコンテキストに含まれる
    print(result)
```

## 複数ContextProviderの組み合わせ

### 高度な組み合わせ例

```python
# 複合的なコンテキスト設定
comprehensive_config = [
    {
        "type": "conversation_history",
        "max_items": 5
    },
    {
        "type": "fixed_file",
        "file_path": "docs/architecture.md"
    },
    {
        "type": "source_code",
        "max_files": 3,
        "max_file_size": 800
    },
    {
        "type": "cut_context",
        "provider": {
            "type": "source_code",
            "max_files": 8,
            "max_file_size": 1500
        },
        "max_chars": 2500,
        "cut_strategy": "middle"
    }
]

agent = RefinireAgent(
    name="expert_assistant",
    generation_instructions="包括的な情報を活用して専門的な回答を提供してください",
    model="gpt-4o-mini",
    context_providers_config=comprehensive_config
)
```

### FlowでのContextProvider活用

```python
# Flowと組み合わせたContextProvider利用
analyzer_agent = RefinireAgent(
    name="code_analyzer",
    generation_instructions="提供されたコードを詳細に分析してください",
    model="gpt-4o-mini",
    context_providers_config=[{
        "type": "source_code",
        "max_files": 5,
        "max_file_size": 1000
    }]
)

documenter_agent = RefinireAgent(
    name="documenter", 
    generation_instructions="分析結果に基づいてドキュメントを生成してください",
    model="gpt-4o-mini",
    context_providers_config=[{
        "type": "conversation_history",
        "max_items": 3
    }]
)

# Context管理Flow
context_flow = Flow({
    "analyze": analyzer_agent,
    "document": documenter_agent
})

async def context_flow_example():
    result = await context_flow.run("認証システムの実装について説明してください")
    print(f"分析・ドキュメント化結果: {result}")
```

## 高度な設定

### 1. 文字列ベース設定

YAMLライクな文字列で設定を記述できます。

```python
string_config = """
- type: conversation_history
  max_items: 8
- type: source_code
  max_files: 4
  max_file_size: 1200
  file_extensions: [".py", ".md"]
- type: fixed_file
  file_path: "docs/guidelines.md"
"""

agent = RefinireAgent(
    name="custom_agent",
    generation_instructions="カスタム設定に基づいて回答してください",
    model="gpt-4o-mini",
    context_providers_config=string_config
)
```

### 2. 連鎖的処理

プロバイダーは前のプロバイダーのコンテキストを受け取って処理できます。

```python
context_config = [
    {
        "type": "source_code",
        "max_files": 10,
        "max_file_size": 2000
    },
    {
        "type": "cut_context",
        "provider": {
            "type": "source_code",
            "max_files": 10,
            "max_file_size": 2000
        },
        "max_chars": 3000,
        "cut_strategy": "middle"
    }
]
```

## 前段Agentのコンテキストを活用したプロンプト変更

### 基本的なコンテキスト活用パターン

前段のAgentが出力したコンテキストを利用して、後続のAgentのプロンプトを動的に変更することができます。

```python
from refinire import Flow, RefinireAgent, ConditionStep, FunctionStep

# 1. 分析段階：ユーザーの専門レベルを判定
analyzer = RefinireAgent(
    name="level_analyzer",
    generation_instructions="""
    ユーザーの質問内容から専門レベルを判定してください。
    以下のいずれかで回答してください：
    - beginner: 初心者レベル
    - intermediate: 中級者レベル  
    - expert: 上級者レベル
    """,
    model="gpt-4o-mini"
)

# 2. プロンプト調整関数
def adjust_prompt_by_level(data, ctx):
    """前段の分析結果に基づいてプロンプトを調整"""
    level = str(ctx.result).lower().strip()
    
    if "beginner" in level:
        ctx.shared_state["adjusted_prompt"] = "初心者にも分かりやすく、基本的な概念から丁寧に説明してください。専門用語は避けて、具体例を多く使ってください。"
    elif "intermediate" in level:
        ctx.shared_state["adjusted_prompt"] = "中級者向けに、適度な技術的詳細を含めて説明してください。実用的な例とベストプラクティスを含めてください。"
    elif "expert" in level:
        ctx.shared_state["adjusted_prompt"] = "上級者向けに、高度な技術的詳細、パフォーマンス考慮事項、エッジケースについて深く説明してください。"
    else:
        ctx.shared_state["adjusted_prompt"] = "一般的なレベルで説明してください。"
    
    return data

# 3. 動的プロンプト生成Agent
class DynamicRefinireAgent(RefinireAgent):
    def __init__(self, base_instructions, **kwargs):
        self.base_instructions = base_instructions
        super().__init__(**kwargs)
    
    async def run_async(self, data, ctx=None):
        # コンテキストから調整されたプロンプトを取得
        adjusted_prompt = ctx.shared_state.get("adjusted_prompt", "")
        
        # 元の指示と調整されたプロンプトを組み合わせ
        combined_instructions = f"{self.base_instructions}\n\n追加指示: {adjusted_prompt}"
        
        # 一時的にプロンプトを変更
        original_instructions = self.generation_instructions
        self.generation_instructions = combined_instructions
        
        try:
            result = await super().run_async(data, ctx)
            return result
        finally:
            # 元のプロンプトに戻す
            self.generation_instructions = original_instructions

# 4. 適応型回答Agent
adaptive_responder = DynamicRefinireAgent(
    name="adaptive_responder",
    base_instructions="ユーザーの質問に対して技術的に正確な回答を提供してください。",
    model="gpt-4o-mini"
)

# 5. 適応型Flowの構築
adaptive_flow = Flow({
    "analyze_level": analyzer,
    "adjust_prompt": FunctionStep("adjust_prompt", adjust_prompt_by_level),
    "respond": adaptive_responder
})

# 実行例
async def adaptive_flow_example():
    # 初心者の質問
    beginner_result = await adaptive_flow.run("Pythonって何ですか？")
    print(f"初心者向け回答: {beginner_result}")
    
    # 上級者の質問
    expert_result = await adaptive_flow.run("Pythonのメタクラスの実装パターンとパフォーマンス最適化について")
    print(f"上級者向け回答: {expert_result}")
```

### 感情分析に基づくトーン調整

```python
# 感情分析Agent
emotion_analyzer = RefinireAgent(
    name="emotion_analyzer",
    generation_instructions="""
    ユーザーの質問から感情状態を分析してください。
    以下のいずれかで回答してください：
    - frustrated: イライラしている
    - confused: 混乱している
    - excited: 興奮している
    - neutral: 中立的
    """,
    model="gpt-4o-mini"
)

# トーン調整関数
def adjust_tone_by_emotion(data, ctx):
    """感情分析結果に基づいてトーンを調整"""
    emotion = str(ctx.result).lower().strip()
    
    if "frustrated" in emotion:
        ctx.shared_state["tone_adjustment"] = "落ち着いた、共感的なトーンで回答してください。問題解決に焦点を当て、ステップバイステップで説明してください。"
    elif "confused" in emotion:
        ctx.shared_state["tone_adjustment"] = "分かりやすく、丁寧に説明してください。混乱を解消するために、基本から順序立てて説明してください。"
    elif "excited" in emotion:
        ctx.shared_state["tone_adjustment"] = "エネルギッシュで前向きなトーンで回答してください。ユーザーの興奮を維持しながら有用な情報を提供してください。"
    else:
        ctx.shared_state["tone_adjustment"] = "プロフェッショナルで親切なトーンで回答してください。"
    
    return data

# 感情適応型Agent
class EmotionAdaptiveAgent(RefinireAgent):
    async def run_async(self, data, ctx=None):
        tone_adjustment = ctx.shared_state.get("tone_adjustment", "")
        
        enhanced_instructions = f"""
        {self.generation_instructions}
        
        コミュニケーションスタイル: {tone_adjustment}
        """
        
        original_instructions = self.generation_instructions
        self.generation_instructions = enhanced_instructions
        
        try:
            return await super().run_async(data, ctx)
        finally:
            self.generation_instructions = original_instructions

emotion_responder = EmotionAdaptiveAgent(
    name="emotion_responder",
    generation_instructions="ユーザーの質問に対して適切なサポートを提供してください。",
    model="gpt-4o-mini"
)

# 感情適応Flow
emotion_flow = Flow({
    "analyze_emotion": emotion_analyzer,
    "adjust_tone": FunctionStep("adjust_tone", adjust_tone_by_emotion),
    "respond": emotion_responder
})
```

### 複雑なコンテキスト連鎖の例

```python
# 多段階のコンテキスト活用例
class MultiContextAgent(RefinireAgent):
    def __init__(self, context_keys, **kwargs):
        self.context_keys = context_keys
        super().__init__(**kwargs)
    
    async def run_async(self, data, ctx=None):
        # 複数のコンテキスト情報を収集
        context_info = []
        for key in self.context_keys:
            if key in ctx.shared_state:
                context_info.append(f"{key}: {ctx.shared_state[key]}")
        
        # 動的にプロンプトを構成
        context_prompt = "\n".join(context_info)
        enhanced_instructions = f"""
        {self.generation_instructions}
        
        以下のコンテキスト情報を考慮して回答してください：
        {context_prompt}
        """
        
        original_instructions = self.generation_instructions
        self.generation_instructions = enhanced_instructions
        
        try:
            return await super().run_async(data, ctx)
        finally:
            self.generation_instructions = original_instructions

# 専門分野判定Agent
domain_classifier = RefinireAgent(
    name="domain_classifier",
    generation_instructions="質問の専門分野を特定してください（例：機械学習、ウェブ開発、データベース等）",
    model="gpt-4o-mini"
)

# 難易度判定Agent  
difficulty_assessor = RefinireAgent(
    name="difficulty_assessor",
    generation_instructions="質問の技術的難易度を1-10で評価してください",
    model="gpt-4o-mini"
)

# コンテキスト統合関数
def integrate_analysis_context(data, ctx):
    """複数の分析結果を統合"""
    # 前の分析結果を保存
    ctx.shared_state["domain"] = ctx.prev_outputs.get("domain_classifier", "一般")
    ctx.shared_state["difficulty"] = ctx.prev_outputs.get("difficulty_assessor", "5")
    ctx.shared_state["user_level"] = ctx.prev_outputs.get("level_analyzer", "intermediate")
    
    return data

# 統合型回答Agent
integrated_responder = MultiContextAgent(
    context_keys=["domain", "difficulty", "user_level"],
    name="integrated_responder", 
    generation_instructions="提供されたコンテキスト情報に基づいて、最適化された回答を生成してください。",
    model="gpt-4o-mini"
)

# 複合分析Flow
complex_flow = Flow({
    "classify_domain": domain_classifier,
    "assess_difficulty": difficulty_assessor,
    "analyze_level": analyzer,
    "integrate_context": FunctionStep("integrate", integrate_analysis_context),
    "respond": integrated_responder
})

# 実行例
async def complex_flow_example():
    result = await complex_flow.run("React HooksのuseEffectの依存配列の最適化方法について教えてください")
    print(f"統合分析による回答: {result}")
```

### 条件付きプロンプト変更

```python
# 条件に基づく複雑なプロンプト調整
def conditional_prompt_adjustment(data, ctx):
    """複数の条件に基づいてプロンプトを動的に調整"""
    
    # 前段の結果を取得
    domain = ctx.shared_state.get("domain", "").lower()
    difficulty = int(ctx.shared_state.get("difficulty", "5"))
    user_level = ctx.shared_state.get("user_level", "").lower()
    
    # 条件に基づくプロンプト構築
    prompt_parts = []
    
    # ドメイン固有の指示
    if "機械学習" in domain or "ai" in domain:
        prompt_parts.append("数学的な基礎理論と実装例の両方を含めてください。")
    elif "ウェブ開発" in domain:
        prompt_parts.append("ブラウザ互換性とパフォーマンスを考慮してください。")
    elif "データベース" in domain:
        prompt_parts.append("データ整合性とパフォーマンス最適化を重視してください。")
    
    # 難易度に基づく調整
    if difficulty >= 8:
        prompt_parts.append("高度な実装詳細とエッジケースについて説明してください。")
    elif difficulty <= 3:
        prompt_parts.append("基本概念を重視し、シンプルな例を使用してください。")
    
    # ユーザーレベルに基づく調整
    if "beginner" in user_level and difficulty >= 6:
        prompt_parts.append("複雑な内容ですが、段階的に分解して説明してください。")
    elif "expert" in user_level and difficulty <= 4:
        prompt_parts.append("基本的な内容ですが、より深い洞察や応用例を含めてください。")
    
    # 最終的なプロンプト調整
    ctx.shared_state["conditional_prompt"] = " ".join(prompt_parts)
    return data

# 条件適応型Agent
conditional_agent = MultiContextAgent(
    context_keys=["conditional_prompt"],
    name="conditional_agent",
    generation_instructions="技術的に正確で実用的な回答を提供してください。",
    model="gpt-4o-mini"
)

# 条件適応Flow
conditional_flow = Flow({
    "classify_domain": domain_classifier,
    "assess_difficulty": difficulty_assessor, 
    "analyze_level": analyzer,
    "integrate_context": FunctionStep("integrate", integrate_analysis_context),
    "conditional_adjust": FunctionStep("conditional", conditional_prompt_adjustment),
    "respond": conditional_agent
})
```

これらの例では、前段のAgentの出力を活用して：
1. **専門レベルに応じたプロンプト調整**
2. **感情状態に基づくトーン変更**
3. **複数のコンテキスト情報の統合**
4. **条件付きの動的プロンプト生成**

を実現しています。

## RefinireAgentの結果保存場所の制御

### store_result_keyパラメータによる結果保存制御

RefinireAgentでは`store_result_key`パラメータを使用して、生成結果をコンテキストのどこに保存するかを制御できます。

```python
from refinire import Flow, RefinireAgent

# 1. デフォルトの保存場所
default_agent = RefinireAgent(
    name="analyzer",
    generation_instructions="入力内容を分析してください",
    model="gpt-4o-mini"
)
# 結果は ctx.shared_state["analyzer_result"] に自動保存

# 2. カスタム保存場所の指定
custom_agent = RefinireAgent(
    name="processor",
    generation_instructions="データを処理してください", 
    model="gpt-4o-mini",
    store_result_key="processing_output"  # カスタムキーを指定
)
# 結果は ctx.shared_state["processing_output"] に保存

# 3. 結果の取得と活用
async def result_storage_example():
    flow = Flow({
        "analyze": default_agent,
        "process": custom_agent
    })
    
    result = await flow.run("サンプルデータ")
    
    # 各エージェントの結果を取得
    analysis_result = result.shared_state["analyzer_result"]
    processing_result = result.shared_state["processing_output"]
    
    print(f"分析結果: {analysis_result}")
    print(f"処理結果: {processing_result}")
```

### 複数の保存場所での結果アクセス

RefinireAgentは結果を複数の場所に自動保存するため、様々な方法でアクセスできます：

```python
# エージェント実行後のコンテキスト状態
async def context_access_example():
    agent = RefinireAgent(
        name="multi_access_agent",
        generation_instructions="テストメッセージを生成",
        model="gpt-4o-mini",
        store_result_key="custom_output"
    )
    
    ctx = Context()
    result = await agent.run_async("テスト入力", ctx)
    
    # 結果へのアクセス方法（すべて同じ内容）
    print(f"ctx.result: {ctx.result}")                           # 最新結果
    print(f"shared_state: {ctx.shared_state['custom_output']}")  # カスタムキー
    print(f"prev_outputs: {ctx.prev_outputs['multi_access_agent']}")  # エージェント名キー
```

### Flow内での戦略的な結果管理

```python
# 複雑なFlowでの結果管理例
async def strategic_result_management():
    # ステップ1: 初期分析
    initial_analyzer = RefinireAgent(
        name="initial_analyzer",
        generation_instructions="入力データの基本分析を実行",
        model="gpt-4o-mini",
        store_result_key="initial_analysis"
    )
    
    # ステップ2: 詳細分析
    detailed_analyzer = RefinireAgent(
        name="detailed_analyzer", 
        generation_instructions="詳細な技術分析を実行",
        model="gpt-4o-mini",
        store_result_key="detailed_analysis"
    )
    
    # ステップ3: 統合レポート生成
    report_generator = RefinireAgent(
        name="report_generator",
        generation_instructions="""
        前段の分析結果を統合して包括的なレポートを生成してください。
        初期分析と詳細分析の両方を考慮してください。
        """,
        model="gpt-4o-mini",
        store_result_key="final_report"
    )
    
    # カスタム統合関数
    def integrate_analysis_results(data, ctx):
        """複数の分析結果を統合"""
        initial = ctx.shared_state.get("initial_analysis", "")
        detailed = ctx.shared_state.get("detailed_analysis", "")
        
        # 統合されたコンテキストを作成
        integrated_context = f"""
        初期分析結果:
        {initial}
        
        詳細分析結果:
        {detailed}
        
        以上の情報を基に最終レポートを生成してください。
        """
        
        ctx.shared_state["integrated_context"] = integrated_context
        return integrated_context
    
    # 統合Flow
    analysis_flow = Flow({
        "initial": initial_analyzer,
        "detailed": detailed_analyzer,
        "integrate": FunctionStep("integrate", integrate_analysis_results),
        "report": report_generator
    })
    
    result = await analysis_flow.run("複雑なデータセット")
    
    # 各段階の結果にアクセス
    print("初期分析:", result.shared_state["initial_analysis"])
    print("詳細分析:", result.shared_state["detailed_analysis"])
    print("最終レポート:", result.shared_state["final_report"])
    
    return result
```

### 条件分岐でのコンテキスト管理

```python
# 条件分岐における結果管理
def route_by_analysis_type(ctx):
    """分析タイプに基づくルーティング"""
    analysis = ctx.shared_state.get("type_analysis", "").lower()
    
    if "technical" in analysis:
        return "technical_processor"
    elif "business" in analysis:
        return "business_processor"
    else:
        return "general_processor"

# タイプ判定エージェント
type_analyzer = RefinireAgent(
    name="type_analyzer",
    generation_instructions="入力の種類を判定してください（technical/business/general）",
    model="gpt-4o-mini",
    store_result_key="type_analysis"  # 判定結果をこのキーに保存
)

# 専門処理エージェント
technical_processor = RefinireAgent(
    name="technical_processor",
    generation_instructions="技術的な観点から詳細に処理してください",
    model="gpt-4o-mini",
    store_result_key="technical_result"
)

business_processor = RefinireAgent(
    name="business_processor", 
    generation_instructions="ビジネス観点から実用的に処理してください",
    model="gpt-4o-mini",
    store_result_key="business_result"
)

general_processor = RefinireAgent(
    name="general_processor",
    generation_instructions="一般的な観点から処理してください",
    model="gpt-4o-mini",
    store_result_key="general_result"
)

# 条件分岐Flow
conditional_flow = Flow({
    "analyze_type": type_analyzer,
    "route": ConditionStep("route", route_by_analysis_type, {
        "technical_processor": "technical",
        "business_processor": "business", 
        "general_processor": "general"
    }),
    "technical": technical_processor,
    "business": business_processor,
    "general": general_processor
})

# 実行と結果取得
async def conditional_result_example():
    result = await conditional_flow.run("Pythonのパフォーマンス最適化について")
    
    # どのルートが実行されたかを確認
    analysis_type = result.shared_state.get("type_analysis", "")
    print(f"判定されたタイプ: {analysis_type}")
    
    # 実行されたプロセッサーの結果を取得
    if "technical_result" in result.shared_state:
        print(f"技術処理結果: {result.shared_state['technical_result']}")
    elif "business_result" in result.shared_state:
        print(f"ビジネス処理結果: {result.shared_state['business_result']}")
    elif "general_result" in result.shared_state:
        print(f"一般処理結果: {result.shared_state['general_result']}")
```

### 評価結果も含めた包括的なコンテキスト管理

```python
# 評価機能付きエージェントでのコンテキスト管理
quality_agent = RefinireAgent(
    name="quality_content_generator",
    generation_instructions="高品質なコンテンツを生成してください",
    evaluation_instructions="生成されたコンテンツの品質を0-100で評価してください",
    threshold=80.0,
    max_retries=2,
    model="gpt-4o-mini",
    store_result_key="quality_content"
)

async def evaluation_context_example():
    ctx = Context()
    result = await quality_agent.run_async("AIの未来について説明してください", ctx)
    
    # 生成結果
    content = ctx.shared_state["quality_content"]
    print(f"生成コンテンツ: {content}")
    
    # 評価結果
    if hasattr(ctx, 'evaluation_result') and ctx.evaluation_result:
        eval_score = ctx.evaluation_result.get('score', 0)
        eval_passed = ctx.evaluation_result.get('passed', False)
        eval_feedback = ctx.evaluation_result.get('feedback', '')
        
        print(f"評価スコア: {eval_score}")
        print(f"合格判定: {eval_passed}")
        print(f"評価フィードバック: {eval_feedback}")
    
    return ctx
```

この機能により、Flow内でのデータフローを明確に制御し、各エージェントの結果を適切な場所に保存して後続の処理で活用できます。

## ユーザーインプットでの変数埋め込み機能

### {{変数名}}構文による動的コンテキスト参照

RefinireAgentでは、ユーザーインプットと`generation_instructions`の両方で`{{変数名}}`構文を使用して、コンテキストの内容を動的に埋め込むことができます。

#### 予約変数

以下の特殊文字列が予約されています：

- `{{RESULT}}`: 前段の実行結果（`ctx.result`）
- `{{EVAL_RESULT}}`: 評価結果の詳細情報（スコア、合格判定、フィードバック）

#### カスタム変数

その他の変数名は`ctx.shared_state`から値を取得します。

```python
from refinire import Flow, RefinireAgent, FunctionStep

# 1. 基本的な変数埋め込みの例
def store_user_info(data, ctx):
    """ユーザー情報をコンテキストに保存"""
    ctx.shared_state["user_name"] = "田中さん"
    ctx.shared_state["user_department"] = "開発部"
    ctx.shared_state["project_name"] = "新システム開発"
    return data

# 2. 変数を参照するエージェント
greeting_agent = RefinireAgent(
    name="personalized_greeter",
    generation_instructions="丁寧で親しみやすい挨拶をしてください",
    model="gpt-4o-mini",
    store_result_key="greeting_result"
)

report_agent = RefinireAgent(
    name="report_generator",
    generation_instructions="前の結果を踏まえて、プロフェッショナルなレポートを生成してください",
    model="gpt-4o-mini",
    store_result_key="final_report"
)

# 3. 変数埋め込みを使用するFlow
variable_flow = Flow({
    "setup": FunctionStep("setup", store_user_info),
    "greet": greeting_agent,
    "report": report_agent
})

# 実行例
async def variable_embedding_example():
    # {{変数名}}を使ってコンテキスト情報を埋め込み
    result = await variable_flow.run(
        "{{user_name}}、{{user_department}}の{{project_name}}について挨拶してください。"
    )
    
    print(f"挨拶: {result.shared_state['greeting_result']}")
    
    # 前の結果を参照する例
    final_result = await report_agent.run_async(
        "{{RESULT}}の内容を基に、{{project_name}}の進捗レポートを作成してください。",
        result  # コンテキストを引き継ぎ
    )
    
    print(f"最終レポート: {final_result.result}")
```

### generation_instructionsでの変数活用

エージェントの指示文自体にも変数を埋め込むことができ、実行時に動的にプロンプトを生成できます。

```python
# 前段で役割とスタイルを決定する関数
def determine_role_and_style(data, ctx):
    """役割とスタイルをコンテキストに設定"""
    if "技術" in data:
        ctx.shared_state["agent_role"] = "技術専門家"
        ctx.shared_state["response_style"] = "技術的で詳細"
        ctx.shared_state["target_audience"] = "開発者"
    elif "ビジネス" in data:
        ctx.shared_state["agent_role"] = "ビジネスアナリスト"
        ctx.shared_state["response_style"] = "実践的で戦略的"
        ctx.shared_state["target_audience"] = "経営陣"
    else:
        ctx.shared_state["agent_role"] = "一般的なアシスタント"
        ctx.shared_state["response_style"] = "分かりやすく親しみやすい"
        ctx.shared_state["target_audience"] = "一般ユーザー"
    
    return data

# 動的プロンプトを使用するエージェント
dynamic_agent = RefinireAgent(
    name="adaptive_specialist",
    generation_instructions="""
あなたは{{agent_role}}として行動してください。
{{response_style}}なスタイルで、{{target_audience}}向けに回答してください。

前段の結果: {{RESULT}}

上記の情報を考慮して、専門知識を活用した高品質な回答を提供してください。
    """,
    model="gpt-4o-mini",
    store_result_key="specialized_response"
)

# 動的プロンプトFlow
dynamic_prompt_flow = Flow({
    "determine_role": FunctionStep("determine_role", determine_role_and_style),
    "respond": dynamic_agent
})

async def dynamic_prompt_example():
    # 技術的な質問
    tech_result = await dynamic_prompt_flow.run("技術的なPythonの最適化手法について教えてください")
    print(f"技術専門家として: {tech_result.shared_state['specialized_response']}")
    
    # ビジネス的な質問
    business_result = await dynamic_prompt_flow.run("ビジネス戦略における競合分析手法を説明してください")
    print(f"ビジネスアナリストとして: {business_result.shared_state['specialized_response']}")
```

### 複数段階での動的プロンプト構築

```python
# 段階的な情報収集とプロンプト構築
def collect_user_preferences(data, ctx):
    """ユーザー設定を収集"""
    ctx.shared_state["user_level"] = "上級者"
    ctx.shared_state["preferred_format"] = "具体例付き"
    ctx.shared_state["industry"] = "金融"
    return data

def analyze_complexity(data, ctx):
    """複雑度を分析"""
    # 実際の実装では自然言語処理等で分析
    if len(data) > 100:
        ctx.shared_state["complexity"] = "高"
        ctx.shared_state["estimated_time"] = "15分"
    else:
        ctx.shared_state["complexity"] = "中"
        ctx.shared_state["estimated_time"] = "5分"
    return data

# 段階1: 初期分析エージェント
initial_analyzer = RefinireAgent(
    name="initial_analyzer",
    generation_instructions="""
あなたは{{industry}}業界の専門家です。
複雑度: {{complexity}}
推定回答時間: {{estimated_time}}

{{user_level}}レベルのユーザー向けに、{{preferred_format}}の形式で初期分析を行ってください。
    """,
    model="gpt-4o-mini",
    store_result_key="initial_analysis"
)

# 段階2: 詳細説明エージェント
detailed_explainer = RefinireAgent(
    name="detailed_explainer",
    generation_instructions="""
あなたは{{industry}}業界の{{user_level}}向け教育専門家です。

前段の分析結果: {{RESULT}}

上記の分析を基に、{{preferred_format}}の形式で詳細な説明を提供してください。
対象レベル: {{user_level}}
業界特化: {{industry}}
    """,
    model="gpt-4o-mini",
    store_result_key="detailed_explanation"
)

# 段階3: 実装支援エージェント  
implementation_supporter = RefinireAgent(
    name="implementation_supporter",
    generation_instructions="""
あなたは{{industry}}業界の実装サポート専門家です。

分析結果: {{initial_analysis}}
詳細説明: {{RESULT}}

{{user_level}}レベルのユーザーが実際に活用できるよう、
{{preferred_format}}の形式で実装支援情報を提供してください。
    """,
    model="gpt-4o-mini",
    store_result_key="implementation_guide"
)

# 多段階動的プロンプトFlow
multi_stage_flow = Flow({
    "collect_prefs": FunctionStep("collect_prefs", collect_user_preferences),
    "analyze_complexity": FunctionStep("analyze_complexity", analyze_complexity),
    "initial_analysis": initial_analyzer,
    "detailed_explanation": detailed_explainer,
    "implementation_support": implementation_supporter
})

async def multi_stage_example():
    result = await multi_stage_flow.run(
        "金融業界でのリスク管理システムを導入したいのですが、どのような点に注意すべきでしょうか？"
    )
    
    print("=== 多段階分析結果 ===")
    print(f"初期分析: {result.shared_state['initial_analysis']}")
    print(f"詳細説明: {result.shared_state['detailed_explanation']}")
    print(f"実装ガイド: {result.shared_state['implementation_guide']}")
```

### 条件分岐と動的プロンプトの組み合わせ

```python
# ユーザータイプ判定
def determine_user_type(data, ctx):
    """ユーザータイプを判定"""
    if "初心者" in data or "初めて" in data:
        ctx.shared_state["user_type"] = "beginner"
        ctx.shared_state["explanation_depth"] = "基本から丁寧に"
        ctx.shared_state["example_complexity"] = "シンプルな例"
    elif "経験者" in data or "詳しく" in data:
        ctx.shared_state["user_type"] = "expert"
        ctx.shared_state["explanation_depth"] = "高度で専門的に"
        ctx.shared_state["example_complexity"] = "複雑で実用的な例"
    else:
        ctx.shared_state["user_type"] = "intermediate"
        ctx.shared_state["explanation_depth"] = "適度な詳細で"
        ctx.shared_state["example_complexity"] = "実践的な例"
    return data

def route_by_user_type(ctx):
    """ユーザータイプに基づくルーティング"""
    return ctx.shared_state.get("user_type", "intermediate")

# 初心者向けエージェント
beginner_agent = RefinireAgent(
    name="beginner_tutor",
    generation_instructions="""
あなたは初心者向けの親切な講師です。

{{explanation_depth}}説明し、{{example_complexity}}を使って教えてください。
専門用語は最小限に抑え、分からない場合は質問を促してください。

前段の情報: {{RESULT}}
    """,
    model="gpt-4o-mini",
    store_result_key="beginner_response"
)

# 上級者向けエージェント
expert_agent = RefinireAgent(
    name="expert_consultant",
    generation_instructions="""
あなたは経験豊富な専門コンサルタントです。

{{explanation_depth}}解説し、{{example_complexity}}を提供してください。
技術的な詳細、エッジケース、ベストプラクティスを含めてください。

前段の情報: {{RESULT}}
    """,
    model="gpt-4o-mini",
    store_result_key="expert_response"
)

# 中級者向けエージェント
intermediate_agent = RefinireAgent(
    name="practical_advisor",
    generation_instructions="""
あなたは実践的なアドバイザーです。

{{explanation_depth}}説明し、{{example_complexity}}を交えて指導してください。
理論と実践のバランスを取り、すぐに活用できる情報を提供してください。

前段の情報: {{RESULT}}
    """,
    model="gpt-4o-mini",
    store_result_key="intermediate_response"
)

# 適応型教育Flow
adaptive_education_flow = Flow({
    "determine_type": FunctionStep("determine_type", determine_user_type),
    "route": ConditionStep("route", route_by_user_type, {
        "beginner": "beginner_teach",
        "expert": "expert_consult", 
        "intermediate": "intermediate_advise"
    }),
    "beginner_teach": beginner_agent,
    "expert_consult": expert_agent,
    "intermediate_advise": intermediate_agent
})

async def adaptive_education_example():
    # 初心者の質問
    beginner_result = await adaptive_education_flow.run(
        "初心者ですが、Pythonでのデータ分析について教えてください"
    )
    
    # 上級者の質問
    expert_result = await adaptive_education_flow.run(
        "経験者です。Pythonでの大規模データ処理の最適化手法を詳しく知りたいです"
    )
    
    print("初心者向け回答:", beginner_result.shared_state.get("beginner_response"))
    print("上級者向け回答:", expert_result.shared_state.get("expert_response"))
```

### 評価結果を活用した動的プロンプト

```python
# 評価機能付きエージェント
content_creator = RefinireAgent(
    name="content_creator",
    generation_instructions="魅力的なマーケティングコンテンツを作成してください",
    evaluation_instructions="コンテンツの魅力度と説得力を0-100で評価してください",
    threshold=75.0,
    model="gpt-4o-mini",
    store_result_key="initial_content"
)

# 評価結果に基づく改善エージェント
content_improver = RefinireAgent(
    name="content_improver", 
    generation_instructions="評価結果を基にコンテンツを改善してください",
    model="gpt-4o-mini",
    store_result_key="improved_content"
)

# 評価連携Flow
evaluation_flow = Flow({
    "create": content_creator,
    "improve": content_improver
})

async def evaluation_variable_example():
    # 初期コンテンツ作成
    result = await evaluation_flow.run("新しいAIツールの紹介文を作成してください")
    
    # 評価結果を参照して改善
    improved_result = await content_improver.run_async(
        """
        前回のコンテンツ: {{RESULT}}
        評価結果: {{EVAL_RESULT}}
        
        評価を踏まえて、より魅力的なコンテンツに改善してください。
        """,
        result
    )
    
    print(f"改善されたコンテンツ: {improved_result.result}")
```

### 複雑なワークフローでの変数活用

```python
# 多段階分析ワークフロー
def analyze_market_data(data, ctx):
    """市場データ分析結果をシミュレート"""
    ctx.shared_state["market_trend"] = "上昇傾向"
    ctx.shared_state["competition_level"] = "中程度"
    ctx.shared_state["target_audience"] = "若年層"
    return "市場分析完了"

def set_business_goals(data, ctx):
    """ビジネス目標を設定"""
    ctx.shared_state["revenue_target"] = "10億円"
    ctx.shared_state["timeline"] = "6ヶ月"
    return "目標設定完了"

# 戦略立案エージェント
strategy_agent = RefinireAgent(
    name="strategy_planner",
    generation_instructions="市場分析とビジネス目標に基づいて戦略を立案してください",
    model="gpt-4o-mini",
    store_result_key="strategy_plan"
)

# 実行計画エージェント
execution_agent = RefinireAgent(
    name="execution_planner",
    generation_instructions="戦略に基づいて具体的な実行計画を作成してください",
    model="gpt-4o-mini",
    store_result_key="execution_plan"
)

# リスク評価エージェント
risk_agent = RefinireAgent(
    name="risk_assessor",
    generation_instructions="計画に対するリスク評価を行い、対策を提案してください",
    model="gpt-4o-mini",
    store_result_key="risk_assessment"
)

# 包括的戦略Flow
comprehensive_flow = Flow({
    "market_analysis": FunctionStep("market_analysis", analyze_market_data),
    "goal_setting": FunctionStep("goal_setting", set_business_goals),
    "strategy": strategy_agent,
    "execution": execution_agent,
    "risk": risk_agent
})

async def comprehensive_variable_example():
    result = await comprehensive_flow.run(
        """
        市場トレンド: {{market_trend}}
        競争レベル: {{competition_level}}
        ターゲット: {{target_audience}}
        売上目標: {{revenue_target}}
        期間: {{timeline}}
        
        これらの条件で事業戦略を立案してください。
        """
    )
    
    # 実行計画の指示
    execution_input = """
    戦略案: {{RESULT}}
    市場状況: {{market_trend}}, 競争: {{competition_level}}
    目標: {{revenue_target}}を{{timeline}}で達成
    
    上記戦略に基づく詳細な実行計画を策定してください。
    """
    
    execution_result = await execution_agent.run_async(execution_input, result)
    
    # リスク評価の指示
    risk_input = """
    戦略: {{strategy_plan}}
    実行計画: {{RESULT}}
    目標期間: {{timeline}}
    
    この計画のリスクを評価し、対策を提案してください。
    """
    
    risk_result = await risk_agent.run_async(risk_input, execution_result)
    
    print("=== 戦略計画結果 ===")
    print(f"戦略案: {result.shared_state['strategy_plan']}")
    print(f"実行計画: {execution_result.shared_state['execution_plan']}")
    print(f"リスク評価: {risk_result.shared_state['risk_assessment']}")
```

### 条件分岐での変数活用

```python
# 条件分岐と変数の組み合わせ
def analyze_user_request(data, ctx):
    """ユーザーリクエストを分析"""
    # 実際の実装ではNLP等で分析
    if "緊急" in data:
        ctx.shared_state["priority"] = "高"
        ctx.shared_state["response_time"] = "即座"
    elif "重要" in data:
        ctx.shared_state["priority"] = "中"
        ctx.shared_state["response_time"] = "1時間以内"
    else:
        ctx.shared_state["priority"] = "低"
        ctx.shared_state["response_time"] = "24時間以内"
    
    ctx.shared_state["request_type"] = "サポート"
    return data

def route_by_priority(ctx):
    """優先度に基づくルーティング"""
    priority = ctx.shared_state.get("priority", "低")
    return f"{priority}_priority_handler"

# 優先度別対応エージェント
high_priority_agent = RefinireAgent(
    name="urgent_support",
    generation_instructions="緊急サポートとして迅速に対応してください",
    model="gpt-4o-mini",
    store_result_key="urgent_response"
)

medium_priority_agent = RefinireAgent(
    name="important_support",
    generation_instructions="重要案件として丁寧に対応してください",
    model="gpt-4o-mini",
    store_result_key="important_response"
)

low_priority_agent = RefinireAgent(
    name="standard_support",
    generation_instructions="標準的なサポートを提供してください",
    model="gpt-4o-mini",
    store_result_key="standard_response"
)

# 優先度対応Flow
priority_flow = Flow({
    "analyze": FunctionStep("analyze", analyze_user_request),
    "route": ConditionStep("route", route_by_priority, {
        "高_priority_handler": "高_priority",
        "中_priority_handler": "中_priority",
        "低_priority_handler": "低_priority"
    }),
    "高_priority": high_priority_agent,
    "中_priority": medium_priority_agent,
    "低_priority": low_priority_agent
})

async def priority_variable_example():
    result = await priority_flow.run(
        """
        緊急サポートが必要です。
        優先度: {{priority}}
        対応時間: {{response_time}}
        種別: {{request_type}}
        
        システムがダウンしています。すぐに対応してください。
        """
    )
    
    # 結果の確認
    priority = result.shared_state.get("priority")
    if priority == "高":
        response = result.shared_state.get("urgent_response")
    elif priority == "中":
        response = result.shared_state.get("important_response")
    else:
        response = result.shared_state.get("standard_response")
    
    print(f"優先度: {priority}")
    print(f"対応結果: {response}")
```

### 変数埋め込みのベストプラクティス

1. **明確な変数名を使用**: `{{user_name}}`、`{{project_status}}`など
2. **存在チェック**: 存在しない変数は空文字列として扱われます
3. **予約変数の活用**: `{{RESULT}}`、`{{EVAL_RESULT}}`で前段の結果を参照
4. **デバッグ時の確認**: `ctx.shared_state`の内容を確認して変数が正しく設定されているかチェック

```python
# デバッグ用の変数確認
def debug_context_variables(data, ctx):
    """コンテキスト変数の状態をデバッグ出力"""
    print("=== Context Variables ===")
    print(f"ctx.result: {ctx.result}")
    print(f"ctx.shared_state: {ctx.shared_state}")
    if hasattr(ctx, 'evaluation_result'):
        print(f"ctx.evaluation_result: {ctx.evaluation_result}")
    return data
```

この変数埋め込み機能により、動的で柔軟なワークフローの構築が可能になり、コンテキスト情報を効率的に活用できます。

## 実用的な例

### 1. コードレビュー支援

```python
context_config = [
    {
        "type": "source_code",
        "max_files": 10,
        "max_file_size": 2000
    },
    {
        "type": "fixed_file",
        "file_path": "CONTRIBUTING.md"
    },
    {
        "type": "conversation_history",
        "max_items": 5
    }
]

agent = RefinireAgent(
    name="CodeReviewAgent",
    generation_instructions="コードレビューを行い、品質、ベストプラクティス、エラーハンドリング、パフォーマンス、ドキュメントの完全性を評価してください。",
    model="gpt-4o-mini",
    context_providers_config=context_config
)

async def code_review_example():
    response = await agent.run_async("このコードの品質をレビューしてください")
    print(f"レビュー結果: {response}")
```

### 2. ドキュメント生成

```python
context_config = [
    {
        "type": "source_code",
        "max_files": 15,
        "max_file_size": 1500
    },
    {
        "type": "cut_context",
        "provider": {
            "type": "source_code",
            "max_files": 15,
            "max_file_size": 1500
        },
        "max_chars": 4000,
        "cut_strategy": "start"
    }
]

agent = RefinireAgent(
    name="DocRefinireAgent",
    generation_instructions="提供されたソースコードと既存のドキュメントに基づいて、包括的で構造化されたドキュメントを生成してください。",
    model="gpt-4o-mini",
    context_providers_config=context_config
)

async def doc_generation_example():
    response = await agent.run_async("APIドキュメントを生成してください")
    print(f"生成されたドキュメント: {response}")
```

### 3. デバッグ支援

```python
context_config = [
    {
        "type": "source_code",
        "max_files": 8,
        "max_file_size": 1000
    },
    {
        "type": "conversation_history",
        "max_items": 10
    }
]

agent = RefinireAgent(
    name="DebugAgent",
    generation_instructions="エラーの原因を調査し、解決策を提供してください。",
    model="gpt-4o-mini",
    context_providers_config=context_config
)

async def debug_example():
    response = await agent.run_async("このエラーの原因を調べてください")
    print(f"デバッグ結果: {response}")
```

## ContextProviderのベストプラクティス

### 1. プロバイダーの順序を考慮

```python
# 推奨順序: 情報収集 → 処理 → 履歴
optimized_config = [
    # 1. 情報収集プロバイダー
    {"type": "source_code", "max_files": 3, "max_file_size": 800},
    {"type": "fixed_file", "file_path": "README.md"},
    
    # 2. 処理プロバイダー 
    {
        "type": "cut_context",
        "provider": {"type": "source_code", "max_files": 6, "max_file_size": 1000},
        "max_chars": 2000,
        "cut_strategy": "middle"
    },
    
    # 3. 履歴プロバイダー
    {"type": "conversation_history", "max_items": 5}
]
```

### 2. 適切なサイズ制限

```python
# タスクに応じたサイズ調整
quick_response_config = [
    {
        "type": "source_code",
        "max_files": 2,        # 少ないファイル数
        "max_file_size": 500   # 小さいファイルサイズ
    }
]

detailed_analysis_config = [
    {
        "type": "source_code", 
        "max_files": 10,       # 多いファイル数
        "max_file_size": 2000  # 大きいファイルサイズ
    },
    {
        "type": "cut_context",
        "max_chars": 5000      # 大きいコンテキスト
    }
]
```

### 3. エラーハンドリング

```python
async def safe_context_execution():
    try:
        agent = RefinireAgent(
            name="safe_agent",
            generation_instructions="安全にタスクを実行してください",
            model="gpt-4o-mini",
            context_providers_config=[{
                "type": "source_code",
                "max_files": 5,
                "max_file_size": 1000
            }]
        )
        
        result = await agent.run_async("プロジェクトの概要を教えてください")
        return result
        
    except Exception as e:
        print(f"コンテキスト実行エラー: {e}")
        # フォールバック処理
        fallback_agent = RefinireAgent(
            name="fallback_agent",
            generation_instructions="基本的な情報で回答してください",
            model="gpt-4o-mini"
            # ContextProviderなし
        )
        return await fallback_agent.run_async("一般的な情報で回答してください")
```

### 4. パフォーマンス最適化

```python
# パフォーマンス重視の設定
performance_config = [
    {
        "type": "conversation_history",
        "max_items": 3  # 最小限の履歴
    },
    {
        "type": "cut_context",
        "provider": {
            "type": "source_code",
            "max_files": 3,
            "max_file_size": 800
        },
        "max_chars": 1500,  # 小さなコンテキスト
        "cut_strategy": "middle"
    }
]
```

## トラブルシューティング

### よくある問題

1. **ファイルが見つからない**
   - ファイルパスが正しいか確認
   - 相対パスと絶対パスの使い分け

2. **コンテキストが長すぎる**
   - CutContextProviderを使用
   - サイズ制限を調整

3. **関連ファイルが検索されない**
   - SourceCodeProviderの設定を確認
   - ファイル名の類似性を調整

### デバッグ方法

```python
# 利用可能なプロバイダーのスキーマを確認
schemas = agent.get_context_provider_schemas()
for schema in schemas:
    print(f"- {schema['name']}: {schema['description']}")

# コンテキストをクリア
agent.clear_context()
```

### コンテキスト管理のデバッグ

```python
# 詳細なログ出力
import logging
logging.basicConfig(level=logging.DEBUG)

# エージェントのコンテキスト状態確認
async def debug_context_state():
    agent = RefinireAgent(
        name="debug_agent",
        generation_instructions="デバッグ用テスト",
        model="gpt-4o-mini",
        context_providers_config=[{
            "type": "conversation_history",
            "max_items": 3
        }]
    )
    
    # 実行前のコンテキスト状態
    print("実行前コンテキスト:", agent.get_context_summary())
    
    result = await agent.run_async("テスト質問")
    
    # 実行後のコンテキスト状態
    print("実行後コンテキスト:", agent.get_context_summary())
    print("結果:", result)
```

## 次のステップ

- [APIリファレンス](../api_reference_ja.md)で詳細な仕様を確認
- [使用例](../../examples/)で実際のコードを参考
- [アーキテクチャ設計書](../architecture.md)でシステム全体を理解
- [Flow完全ガイド](flow_complete_guide.md)でFlowとの連携を学習 