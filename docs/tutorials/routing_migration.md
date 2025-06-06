# ルーティング機能移行ガイド

## 概要

このガイドでは、`AgentPipeline`の`routing_func`機能を`Flow/Step`アーキテクチャでどのように実現するかを詳しく説明します。

## AgentPipelineのrouting_funcとは

**AgentPipeline**では、`routing_func`パラメータを使って生成結果に基づいて後続処理を制御できました：

```python
def my_routing_func(output):
    """出力内容に基づいてルーティング"""
    if "緊急" in output:
        return f"🚨 緊急対応: {output}"
    elif "質問" in output:
        return f"❓ Q&A対応: {output}"
    else:
        return f"📝 通常対応: {output}"

pipeline = AgentPipeline(
    name="router",
    generation_instructions="ユーザーの要求を分析してください",
    evaluation_instructions=None,
    routing_func=my_routing_func  # 出力に応じてルーティング
)

result = pipeline.run("システムが停止しています！助けて！")
# 結果: "🚨 緊急対応: システムが停止しており、緊急対応が必要です。"
```

## Flow/Stepアーキテクチャでの実現方法

### 1. 基本的な条件分岐ルーティング

`ConditionStep`を使用した条件分岐でルーティングを実現：

```python
from agents_sdk_models import Flow, ConditionStep, create_simple_gen_agent
import asyncio

# Step 1: 分析エージェント（元のAgentPipelineの生成部分）
analyzer = create_simple_gen_agent(
    name="analyzer",
    instructions="""
    ユーザーの要求を分析し、以下のカテゴリに分類してください：
    - 緊急: システム障害、セキュリティ問題など
    - 質問: 情報を求める問い合わせ
    - 通常: その他の一般的な要求
    
    分類結果を明確に記載してください。
    """,
    model="gpt-4o-mini"
)

# Step 2: 条件関数（元のrouting_funcのロジック）
def is_urgent(ctx):
    """緊急度判定"""
    result = ctx.shared_state.get("analyzer_result", "")
    return "緊急" in result or "障害" in result or "停止" in result

def is_question(ctx):
    """質問タイプ判定"""
    result = ctx.shared_state.get("analyzer_result", "")
    return "質問" in result or "問い合わせ" in result or "教えて" in result

# Step 3: 各種対応エージェント
urgent_agent = create_simple_gen_agent(
    name="urgent_handler",
    instructions="緊急事態に迅速かつ適切に対応します。具体的な解決手順を提示してください。",
    model="gpt-4o"  # 緊急時は高性能モデル
)

qa_agent = create_simple_gen_agent(
    name="qa_handler",
    instructions="質問に詳しく、分かりやすく回答します。関連情報も含めて説明してください。",
    model="gpt-4o-mini"
)

normal_agent = create_simple_gen_agent(
    name="normal_handler",
    instructions="一般的な要求に丁寧に対応します。",
    model="gpt-4o-mini"
)

# Step 4: フロー構築（多段階条件分岐）
flow = Flow(
    start="analyzer",
    steps={
        "analyzer": analyzer,
        "urgent_check": ConditionStep(
            "urgent_check", 
            is_urgent, 
            if_true="urgent_handler",
            if_false="question_check"
        ),
        "question_check": ConditionStep(
            "question_check",
            is_question,
            if_true="qa_handler",
            if_false="normal_handler"
        ),
        "urgent_handler": urgent_agent,
        "qa_handler": qa_agent,
        "normal_handler": normal_agent
    }
)

# 実行例
async def run_routing_example():
    # 緊急事態の例
    result1 = await flow.run("システムが停止しています！助けて！")
    print("緊急対応:", result1.shared_state.get("urgent_handler_result"))
    
    # 質問の例
    result2 = await flow.run("Pythonの使い方を教えてください")
    print("Q&A対応:", result2.shared_state.get("qa_handler_result"))
    
    # 通常要求の例
    result3 = await flow.run("レポートを作成したいです")
    print("通常対応:", result3.shared_state.get("normal_handler_result"))

# 実行
asyncio.run(run_routing_example())
```

### 2. 動的ルーティング関数によるアプローチ

より柔軟なルーティングロジックには`FunctionStep`を使用：

```python
from agents_sdk_models import FunctionStep

def dynamic_router(user_input, ctx):
    """動的ルーティング関数（routing_funcの直接的な置き換え）"""
    analysis_result = ctx.shared_state.get("analyzer_result", "")
    
    # AgentPipelineのrouting_funcと同様のロジック
    if "緊急" in analysis_result or "障害" in analysis_result:
        ctx.goto("urgent_handler")
        ctx.shared_state["route_decision"] = "緊急対応ルート"
        ctx.shared_state["priority"] = "high"
    elif "質問" in analysis_result or "教えて" in analysis_result:
        ctx.goto("qa_handler")
        ctx.shared_state["route_decision"] = "Q&Aルート"
        ctx.shared_state["priority"] = "medium"
    else:
        ctx.goto("normal_handler")
        ctx.shared_state["route_decision"] = "通常対応ルート"
        ctx.shared_state["priority"] = "low"
    
    # ルーティング理由をログ出力
    ctx.add_system_message(f"ルーティング決定: {ctx.shared_state['route_decision']}")
    
    return ctx

# フロー構築（単一のルーティング関数使用）
router_step = FunctionStep("router", dynamic_router)

flow = Flow(
    start="analyzer",
    steps={
        "analyzer": analyzer,
        "router": router_step,  # 動的ルーティング
        "urgent_handler": urgent_agent,
        "qa_handler": qa_agent,
        "normal_handler": normal_agent
    }
)
```

### 3. 複雑な多段階ルーティング

複数の条件を組み合わせた高度なルーティングパターン：

```python
# 多段階条件分岐の例
def check_user_level(ctx):
    """ユーザーレベル確認"""
    return ctx.shared_state.get("user_level", "beginner") == "expert"

def check_complexity(ctx):
    """複雑度判定"""
    result = ctx.shared_state.get("analyzer_result", "")
    return "複雑" in result or "高度" in result

# 専門家向け、初心者向けエージェントを追加
expert_agent = create_simple_gen_agent(
    name="expert_handler",
    instructions="専門的な内容を技術的詳細を含めて説明します。",
    model="gpt-4o"
)

beginner_agent = create_simple_gen_agent(
    name="beginner_handler", 
    instructions="初心者向けに分かりやすく、段階的に説明します。",
    model="gpt-4o-mini"
)

# 複雑なフロー構築
complex_flow = Flow(
    start="analyzer",
    steps={
        "analyzer": analyzer,
        
        # 1段階目：緊急度判定
        "urgent_check": ConditionStep(
            "urgent_check",
            is_urgent,
            if_true="urgent_handler",
            if_false="user_level_check"
        ),
        
        # 2段階目：ユーザーレベル判定
        "user_level_check": ConditionStep(
            "user_level_check",
            check_user_level,
            if_true="expert_complexity_check",
            if_false="beginner_complexity_check"
        ),
        
        # 3段階目：複雑度判定（専門家向け）
        "expert_complexity_check": ConditionStep(
            "expert_complexity_check",
            check_complexity,
            if_true="expert_handler",
            if_false="qa_handler"
        ),
        
        # 3段階目：複雑度判定（初心者向け）
        "beginner_complexity_check": ConditionStep(
            "beginner_complexity_check",
            check_complexity,
            if_true="beginner_handler",
            if_false="normal_handler"
        ),
        
        # 各種対応エージェント
        "urgent_handler": urgent_agent,
        "expert_handler": expert_agent,
        "beginner_handler": beginner_agent,
        "qa_handler": qa_agent,
        "normal_handler": normal_agent
    }
)
```

### 4. 実用的なトリアージシステム例

実際のカスタマーサポートシステムを想定した実装：

```python
from agents_sdk_models import UserInputStep

def analyze_customer_request(user_input, ctx):
    """顧客要求の詳細分析"""
    request = ctx.last_user_input.lower()
    
    # 緊急度スコア計算
    urgency_score = 0
    if any(word in request for word in ["停止", "障害", "エラー", "緊急"]):
        urgency_score += 3
    if any(word in request for word in ["遅い", "問題", "困っている"]):
        urgency_score += 2
    if any(word in request for word in ["質問", "教えて", "方法"]):
        urgency_score += 1
    
    # カテゴリ判定
    if "請求" in request or "料金" in request:
        category = "billing"
    elif "技術" in request or "設定" in request:
        category = "technical"
    elif "解約" in request or "変更" in request:
        category = "account"
    else:
        category = "general"
    
    # 結果をコンテキストに保存
    ctx.shared_state.update({
        "urgency_score": urgency_score,
        "category": category,
        "original_request": ctx.last_user_input
    })
    
    return ctx

# トリアージ条件関数
def is_high_priority(ctx):
    return ctx.shared_state.get("urgency_score", 0) >= 3

def is_billing_issue(ctx):
    return ctx.shared_state.get("category") == "billing"

def is_technical_issue(ctx):
    return ctx.shared_state.get("category") == "technical"

# 専門対応エージェント
billing_agent = create_simple_gen_agent(
    name="billing_specialist",
    instructions="請求・料金に関する専門対応を行います。正確な情報を提供してください。",
    model="gpt-4o"
)

technical_agent = create_simple_gen_agent(
    name="technical_specialist",
    instructions="技術的な問題に対応します。具体的な解決手順を提示してください。",
    model="gpt-4o"
)

# カスタマーサポートフロー
support_flow = Flow(
    start="welcome",
    steps={
        "welcome": UserInputStep(
            "welcome", 
            "お困りの内容を詳しく教えてください：",
            "analyze"
        ),
        "analyze": FunctionStep("analyze", analyze_customer_request, "priority_check"),
        "priority_check": ConditionStep(
            "priority_check",
            is_high_priority,
            if_true="urgent_handler",
            if_false="category_routing"
        ),
        "category_routing": ConditionStep(
            "category_routing",
            is_billing_issue,
            if_true="billing_specialist",
            if_false="tech_check"
        ),
        "tech_check": ConditionStep(
            "tech_check",
            is_technical_issue,
            if_true="technical_specialist",
            if_false="normal_handler"
        ),
        "urgent_handler": urgent_agent,
        "billing_specialist": billing_agent,
        "technical_specialist": technical_agent,
        "normal_handler": normal_agent
    }
)
```

## 移行メリットの比較

| 項目 | AgentPipeline routing_func | Flow/Step アーキテクチャ |
|------|----------------------------|-------------------------|
| **実装方式** | 単一関数内でルーティング | ステップ分離による明確な制御フロー |
| **条件の複雑さ** | 複雑になると保守困難 | 段階的条件分岐で管理しやすい |
| **再利用性** | 関数単位での再利用のみ | ステップ単位で柔軟な再利用 |
| **デバッグ** | ブラックボックス化しやすい | 各ステップで状態確認可能 |
| **拡張性** | 条件追加時に全体修正必要 | 新しいステップ追加で対応 |
| **テスト** | 統合テストが中心 | ステップ単位でユニットテスト可能 |
| **パフォーマンス** | 単一実行で完結 | ステップ間のオーバーヘッドあり |
| **保守性** | 修正時の影響範囲が広い | 変更の影響範囲を限定可能 |

## ベストプラクティス

### 1. 段階的移行

```python
# Step 1: 既存のrouting_funcをFunctionStepに移行
def legacy_router(user_input, ctx):
    """既存のrouting_funcをそのまま移植"""
    result = ctx.shared_state.get("analyzer_result", "")
    
    # 既存のrouting_funcロジックをそのまま使用
    if "緊急" in result:
        routed_result = f"🚨 緊急対応: {result}"
        ctx.shared_state["final_result"] = routed_result
        ctx.finish()  # フロー終了
    elif "質問" in result:
        routed_result = f"❓ Q&A対応: {result}"
        ctx.shared_state["final_result"] = routed_result
        ctx.finish()
    else:
        routed_result = f"📝 通常対応: {result}"
        ctx.shared_state["final_result"] = routed_result
        ctx.finish()
    
    return ctx

# Step 2: 徐々にConditionStepに分割
# Step 3: 最終的に専用エージェントに置き換え
```

### 2. 条件関数の設計指針

```python
# ✅ 良い例：単一責任の条件関数
def is_urgent_request(ctx):
    """緊急要求かどうかを判定する単一目的関数"""
    result = ctx.shared_state.get("analyzer_result", "")
    urgent_keywords = ["緊急", "障害", "停止", "エラー", "問題"]
    return any(keyword in result for keyword in urgent_keywords)

def has_high_priority_user(ctx):
    """高優先度ユーザーかどうかを判定"""
    user_level = ctx.shared_state.get("user_level", "standard")
    return user_level in ["premium", "enterprise"]

# ❌ 避けるべき例：複数の責任を持つ条件関数
def complex_routing_logic(ctx):
    """複雑すぎる条件判定（避けるべき）"""
    result = ctx.shared_state.get("analyzer_result", "")
    user_level = ctx.shared_state.get("user_level", "standard")
    time_of_day = ctx.shared_state.get("current_time", 12)
    
    # 複数の条件が混在しており、保守困難
    if ("緊急" in result and user_level == "premium") or \
       ("質問" in result and 9 <= time_of_day <= 17) or \
       (user_level == "enterprise"):
        return True
    return False
```

### 3. エラーハンドリング

```python
def safe_condition_check(ctx):
    """安全な条件チェック（エラーハンドリング付き）"""
    try:
        result = ctx.shared_state.get("analyzer_result", "")
        if not result:
            # 分析結果がない場合のフォールバック
            ctx.add_system_message("警告: 分析結果が見つかりません")
            return False
        
        return "緊急" in result.lower()
    
    except Exception as e:
        # エラー時は安全側（False）に倒す
        ctx.add_system_message(f"条件チェックエラー: {e}")
        return False

# エラー対応ステップの追加
error_handler = create_simple_gen_agent(
    name="error_handler",
    instructions="システムエラーが発生しました。お客様には丁寧に謝罪し、代替手段を提示してください。",
    model="gpt-4o-mini"
)
```

## まとめ

Flow/Stepアーキテクチャでは、AgentPipelineの`routing_func`よりも：

1. **明確な制御フロー** - 各ステップの責任が明確
2. **段階的な条件分岐** - 複雑なロジックも管理しやすい
3. **高い再利用性** - ステップ単位での組み合わせが可能
4. **優れた保守性** - 変更の影響範囲を限定可能
5. **豊富なデバッグ情報** - 各ステップで状態確認可能

これにより、より堅牢で拡張性の高いワークフローを構築できます。 