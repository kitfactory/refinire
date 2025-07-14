#!/usr/bin/env python3
"""
OpenRouter Cost Optimization Example
OpenRouterコスト最適化例

This example demonstrates cost optimization strategies when using OpenRouter,
including model selection, token management, and cost-effective workflows.
この例は、OpenRouterを使用する際のコスト最適化戦略を示し、
モデル選択、トークン管理、コスト効率的なワークフローを含みます。

Before running this example, ensure you have:
この例を実行する前に、以下を確認してください：
1. Set OPENROUTER_API_KEY environment variable
   OPENROUTER_API_KEY環境変数を設定
2. Install refinire: pip install -e .
   refinireをインストール: pip install -e .
"""

import os
import asyncio
import time
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from refinire.core.llm import get_llm
from pydantic import BaseModel, Field

# Clear other provider environment variables to ensure OpenRouter is used
# 他のプロバイダーの環境変数をクリアしてOpenRouterが使用されるようにする
os.environ.pop('OLLAMA_API_KEY', None)
os.environ.pop('LMSTUDIO_API_KEY', None)
os.environ.pop('OLLAMA_BASE_URL', None)
os.environ.pop('LMSTUDIO_BASE_URL', None)

@dataclass
class ModelCostInfo:
    """
    Cost information for different models
    異なるモデルのコスト情報
    """
    name: str
    cost_per_1k_tokens: float  # Approximate cost in USD
    speed_tier: str  # fast, medium, slow
    quality_tier: str  # basic, good, excellent
    recommended_for: List[str]

# Cost-optimized model configurations (approximate costs)
# コスト最適化されたモデル設定（概算コスト）
COST_OPTIMIZED_MODELS = {
    "budget": ModelCostInfo(
        name="meta-llama/llama-3-8b-instruct",
        cost_per_1k_tokens=0.0001,
        speed_tier="fast",
        quality_tier="good",
        recommended_for=["simple_tasks", "high_volume", "prototyping"]
    ),
    "balanced": ModelCostInfo(
        name="anthropic/claude-3-haiku",
        cost_per_1k_tokens=0.0005,
        speed_tier="fast",
        quality_tier="good",
        recommended_for=["general_purpose", "balanced_workloads"]
    ),
    "premium": ModelCostInfo(
        name="openai/gpt-4",
        cost_per_1k_tokens=0.003,
        speed_tier="medium",
        quality_tier="excellent",
        recommended_for=["complex_reasoning", "high_quality_output"]
    ),
    "efficient": ModelCostInfo(
        name="mistralai/mixtral-8x7b-instruct",
        cost_per_1k_tokens=0.0002,
        speed_tier="medium",
        quality_tier="good",
        recommended_for=["technical_tasks", "structured_output"]
    )
}

class CostTracker:
    """
    Track and estimate costs for API calls
    API呼び出しのコストを追跡・推定
    """
    
    def __init__(self):
        self.total_cost = 0.0
        self.call_history = []
    
    def estimate_tokens(self, text: str) -> int:
        """
        Rough token estimation (1 token ≈ 4 characters)
        大まかなトークン推定（1トークン≈4文字）
        """
        return len(text) // 4
    
    def calculate_cost(self, prompt: str, response: str, model_cost_info: ModelCostInfo) -> float:
        """
        Calculate cost for a single API call
        単一のAPI呼び出しのコストを計算
        """
        prompt_tokens = self.estimate_tokens(prompt)
        response_tokens = self.estimate_tokens(response)
        total_tokens = prompt_tokens + response_tokens
        
        cost = (total_tokens / 1000) * model_cost_info.cost_per_1k_tokens
        return cost
    
    def track_call(self, prompt: str, response: str, model_name: str, duration: float):
        """
        Track an API call for cost analysis
        コスト分析のためのAPI呼び出しを追跡
        """
        model_info = None
        for info in COST_OPTIMIZED_MODELS.values():
            if info.name == model_name:
                model_info = info
                break
        
        if model_info:
            cost = self.calculate_cost(prompt, response, model_info)
            self.total_cost += cost
            
            call_record = {
                "model": model_name,
                "prompt_length": len(prompt),
                "response_length": len(response),
                "estimated_tokens": self.estimate_tokens(prompt + response),
                "estimated_cost": cost,
                "duration": duration
            }
            self.call_history.append(call_record)
            
            return call_record
        return None
    
    def get_summary(self) -> Dict:
        """
        Get cost summary and statistics
        コスト概要と統計を取得
        """
        if not self.call_history:
            return {"total_cost": 0, "total_calls": 0}
        
        total_calls = len(self.call_history)
        total_tokens = sum(record["estimated_tokens"] for record in self.call_history)
        avg_cost_per_call = self.total_cost / total_calls if total_calls > 0 else 0
        
        return {
            "total_cost": self.total_cost,
            "total_calls": total_calls,
            "total_tokens": total_tokens,
            "avg_cost_per_call": avg_cost_per_call,
            "calls_by_model": {}
        }

class CostOptimizedWorkflow:
    """
    Workflow that optimizes for cost efficiency
    コスト効率を最適化するワークフロー
    """
    
    def __init__(self):
        self.cost_tracker = CostTracker()
        self.models = {}
    
    async def get_cost_effective_model(self, task_complexity: str, quality_requirement: str):
        """
        Select the most cost-effective model for given requirements
        指定された要件に対して最もコスト効率的なモデルを選択
        """
        if task_complexity == "simple" and quality_requirement == "basic":
            return COST_OPTIMIZED_MODELS["budget"]
        elif task_complexity == "medium" and quality_requirement == "good":
            return COST_OPTIMIZED_MODELS["balanced"]
        elif task_complexity == "complex" or quality_requirement == "excellent":
            return COST_OPTIMIZED_MODELS["premium"]
        else:
            return COST_OPTIMIZED_MODELS["efficient"]
    
    async def generate_with_cost_tracking(self, prompt: str, model_info: ModelCostInfo, **kwargs):
        """
        Generate response with cost tracking
        コスト追跡付きで応答を生成
        """
        if model_info.name not in self.models:
            self.models[model_info.name] = get_llm(provider="openrouter", model=model_info.name)
        
        model = self.models[model_info.name]
        
        start_time = time.time()
        response = await model.generate(prompt, **kwargs)
        end_time = time.time()
        
        duration = end_time - start_time
        call_record = self.cost_tracker.track_call(prompt, response, model_info.name, duration)
        
        return response, call_record

async def demonstrate_cost_comparison():
    """
    Compare costs across different models for the same task
    同じタスクで異なるモデルのコストを比較
    """
    print("=== Cost Comparison Example ===")
    print("=== コスト比較例 ===\n")
    
    workflow = CostOptimizedWorkflow()
    
    # Task to compare across models
    # モデル間で比較するタスク
    task_prompt = "Write a professional email to a client explaining a project delay and proposing a solution."
    
    print(f"Task: {task_prompt}")
    print(f"タスク: {task_prompt}")
    print(f"Comparing costs across {len(COST_OPTIMIZED_MODELS)} models...")
    print(f"{len(COST_OPTIMIZED_MODELS)}個のモデルでコストを比較中...")
    print()
    
    results = []
    
    for tier, model_info in COST_OPTIMIZED_MODELS.items():
        print(f"Testing {tier} tier: {model_info.name}")
        print(f"{tier}ティアをテスト中: {model_info.name}")
        
        try:
            response, call_record = await workflow.generate_with_cost_tracking(
                task_prompt, 
                model_info, 
                temperature=0.7
            )
            
            results.append({
                "tier": tier,
                "model": model_info.name,
                "cost": call_record["estimated_cost"],
                "duration": call_record["duration"],
                "response_length": len(response),
                "response_preview": response[:100]
            })
            
            print(f"  Cost: ${call_record['estimated_cost']:.6f}")
            print(f"  コスト: ${call_record['estimated_cost']:.6f}")
            print(f"  Duration: {call_record['duration']:.2f}s")
            print(f"  期間: {call_record['duration']:.2f}秒")
            print(f"  Response length: {len(response)} chars")
            print(f"  応答の長さ: {len(response)} 文字")
            print()
            
        except Exception as e:
            print(f"  Error: {e}")
            print(f"  エラー: {e}")
            print()
    
    # Show cost comparison summary
    # コスト比較概要を表示
    if results:
        print("Cost Comparison Summary:")
        print("コスト比較概要:")
        results.sort(key=lambda x: x["cost"])
        
        cheapest = results[0]
        most_expensive = results[-1]
        
        print(f"  Cheapest: {cheapest['tier']} (${cheapest['cost']:.6f})")
        print(f"  最安値: {cheapest['tier']} (${cheapest['cost']:.6f})")
        print(f"  Most expensive: {most_expensive['tier']} (${most_expensive['cost']:.6f})")
        print(f"  最高値: {most_expensive['tier']} (${most_expensive['cost']:.6f})")
        print(f"  Cost difference: {most_expensive['cost'] / cheapest['cost']:.1f}x")
        print(f"  コスト差: {most_expensive['cost'] / cheapest['cost']:.1f}倍")
        print()

async def demonstrate_batch_processing():
    """
    Demonstrate cost-efficient batch processing
    コスト効率的なバッチ処理を実演
    """
    print("=== Batch Processing Cost Optimization ===")
    print("=== バッチ処理コスト最適化 ===\n")
    
    workflow = CostOptimizedWorkflow()
    
    # Simulate multiple similar tasks that can be batched
    # バッチ処理可能な複数の類似タスクをシミュレート
    individual_tasks = [
        "Summarize: 'The quarterly report shows 15% growth in sales.'",
        "Summarize: 'Customer satisfaction ratings improved by 8% this month.'",
        "Summarize: 'New product launch exceeded initial projections by 20%.'",
        "Summarize: 'Marketing campaign resulted in 300% increase in website traffic.'",
        "Summarize: 'Employee retention rate improved to 94% after policy changes.'"
    ]
    
    # Method 1: Individual processing (less efficient)
    # 方法1: 個別処理（効率が悪い）
    print("Method 1: Individual Processing")
    print("方法1: 個別処理")
    
    model_info = COST_OPTIMIZED_MODELS["budget"]
    individual_cost = 0
    
    for i, task in enumerate(individual_tasks, 1):
        response, call_record = await workflow.generate_with_cost_tracking(
            task, model_info, temperature=0.3
        )
        individual_cost += call_record["estimated_cost"]
        print(f"  Task {i}: ${call_record['estimated_cost']:.6f}")
    
    print(f"  Total individual cost: ${individual_cost:.6f}")
    print(f"  個別処理の総コスト: ${individual_cost:.6f}")
    print()
    
    # Method 2: Batch processing (more efficient)
    # 方法2: バッチ処理（より効率的）
    print("Method 2: Batch Processing")
    print("方法2: バッチ処理")
    
    batch_prompt = "Summarize each of the following business updates in one sentence:\n\n"
    for i, task in enumerate(individual_tasks, 1):
        batch_prompt += f"{i}. {task.replace('Summarize: ', '')}\n"
    
    batch_response, batch_call_record = await workflow.generate_with_cost_tracking(
        batch_prompt, model_info, temperature=0.3
    )
    
    print(f"  Batch cost: ${batch_call_record['estimated_cost']:.6f}")
    print(f"  バッチコスト: ${batch_call_record['estimated_cost']:.6f}")
    print(f"  Cost savings: ${individual_cost - batch_call_record['estimated_cost']:.6f}")
    print(f"  コスト節約: ${individual_cost - batch_call_record['estimated_cost']:.6f}")
    print(f"  Efficiency gain: {individual_cost / batch_call_record['estimated_cost']:.1f}x")
    print(f"  効率改善: {individual_cost / batch_call_record['estimated_cost']:.1f}倍")
    print()

async def demonstrate_smart_caching():
    """
    Demonstrate smart caching to reduce API calls
    API呼び出しを削減するスマートキャッシングを実演
    """
    print("=== Smart Caching Example ===")
    print("=== スマートキャッシング例 ===\n")
    
    class CachedWorkflow(CostOptimizedWorkflow):
        def __init__(self):
            super().__init__()
            self.response_cache = {}
        
        async def generate_with_cache(self, prompt: str, model_info: ModelCostInfo, **kwargs):
            """
            Generate response with caching
            キャッシング付きで応答を生成
            """
            cache_key = f"{model_info.name}:{hash(prompt)}:{kwargs.get('temperature', 0.7)}"
            
            if cache_key in self.response_cache:
                print(f"  ✓ Cache hit for prompt: {prompt[:50]}...")
                print(f"  ✓ プロンプトのキャッシュヒット: {prompt[:50]}...")
                return self.response_cache[cache_key], None
            
            response, call_record = await self.generate_with_cost_tracking(
                prompt, model_info, **kwargs
            )
            
            self.response_cache[cache_key] = response
            print(f"  ✓ Generated and cached: {prompt[:50]}...")
            print(f"  ✓ 生成してキャッシュ: {prompt[:50]}...")
            
            return response, call_record
    
    cached_workflow = CachedWorkflow()
    model_info = COST_OPTIMIZED_MODELS["balanced"]
    
    # Simulate repeated queries
    # 繰り返しクエリをシミュレート
    queries = [
        "What is machine learning?",
        "Explain neural networks briefly.",
        "What is machine learning?",  # Duplicate
        "How does deep learning work?",
        "What is machine learning?",  # Duplicate
        "Explain neural networks briefly.",  # Duplicate
    ]
    
    print(f"Processing {len(queries)} queries (some duplicates)...")
    print(f"{len(queries)}個のクエリを処理中（一部重複）...")
    print()
    
    total_cost = 0
    cache_hits = 0
    
    for i, query in enumerate(queries, 1):
        print(f"Query {i}: {query}")
        print(f"クエリ {i}: {query}")
        
        response, call_record = await cached_workflow.generate_with_cache(
            query, model_info, temperature=0.5
        )
        
        if call_record:
            total_cost += call_record["estimated_cost"]
            print(f"  Cost: ${call_record['estimated_cost']:.6f}")
            print(f"  コスト: ${call_record['estimated_cost']:.6f}")
        else:
            cache_hits += 1
            print(f"  Cost: $0.000000 (cached)")
            print(f"  コスト: $0.000000 (キャッシュ)")
        
        print()
    
    print(f"Total cost: ${total_cost:.6f}")
    print(f"総コスト: ${total_cost:.6f}")
    print(f"Cache hits: {cache_hits}/{len(queries)}")
    print(f"キャッシュヒット: {cache_hits}/{len(queries)}")
    print(f"Cost savings from caching: {cache_hits / len(queries) * 100:.1f}%")
    print(f"キャッシングによるコスト節約: {cache_hits / len(queries) * 100:.1f}%")
    print()

async def cost_optimization_recommendations():
    """
    Provide cost optimization recommendations
    コスト最適化の推奨事項を提供
    """
    print("=== Cost Optimization Recommendations ===")
    print("=== コスト最適化の推奨事項 ===\n")
    
    recommendations = [
        {
            "title": "Model Selection Strategy",
            "title_ja": "モデル選択戦略",
            "tips": [
                "Use budget models for simple tasks (summarization, basic Q&A)",
                "Reserve premium models for complex reasoning and creative tasks",
                "Consider model switching based on task complexity"
            ],
            "tips_ja": [
                "単純なタスク（要約、基本的なQ&A）には予算モデルを使用",
                "複雑な推論や創造的なタスクには高品質モデルを予約",
                "タスクの複雑さに基づいてモデルを切り替えることを検討"
            ]
        },
        {
            "title": "Batch Processing",
            "title_ja": "バッチ処理",
            "tips": [
                "Combine similar tasks into single API calls",
                "Use structured prompts for multiple items",
                "Reduce overhead from multiple API calls"
            ],
            "tips_ja": [
                "類似タスクを単一のAPI呼び出しにまとめる",
                "複数アイテムには構造化プロンプトを使用",
                "複数のAPI呼び出しからのオーバーヘッドを削減"
            ]
        },
        {
            "title": "Smart Caching",
            "title_ja": "スマートキャッシング",
            "tips": [
                "Cache frequently requested responses",
                "Implement TTL for cache entries",
                "Use semantic similarity for cache matching"
            ],
            "tips_ja": [
                "頻繁にリクエストされる応答をキャッシュ",
                "キャッシュエントリにTTLを実装",
                "キャッシュマッチングにセマンティック類似度を使用"
            ]
        },
        {
            "title": "Token Management",
            "title_ja": "トークン管理",
            "tips": [
                "Optimize prompt length and clarity",
                "Use shorter system messages when possible",
                "Consider output length requirements"
            ],
            "tips_ja": [
                "プロンプトの長さと明確性を最適化",
                "可能な場合はより短いシステムメッセージを使用",
                "出力長要件を考慮"
            ]
        }
    ]
    
    for rec in recommendations:
        print(f"📊 {rec['title']} / {rec['title_ja']}")
        for tip, tip_ja in zip(rec['tips'], rec['tips_ja']):
            print(f"  • {tip}")
            print(f"    {tip_ja}")
        print()

async def main():
    """
    Main function to run all cost optimization examples
    すべてのコスト最適化例を実行するメイン関数
    """
    # Check if OpenRouter API key is set
    # OpenRouter APIキーが設定されているかチェック
    if not os.getenv('OPENROUTER_API_KEY'):
        print("ERROR: OPENROUTER_API_KEY environment variable not set")
        print("エラー: OPENROUTER_API_KEY環境変数が設定されていません")
        print("Please set it with: export OPENROUTER_API_KEY=your_api_key")
        print("次のコマンドで設定してください: export OPENROUTER_API_KEY=your_api_key")
        return
    
    print("OpenRouter Cost Optimization Examples")
    print("OpenRouterコスト最適化例")
    print("=" * 50)
    print()
    
    # Run cost optimization examples
    # コスト最適化例を実行
    await demonstrate_cost_comparison()
    await demonstrate_batch_processing()
    await demonstrate_smart_caching()
    await cost_optimization_recommendations()
    
    print("=" * 50)
    print("All cost optimization examples completed!")
    print("すべてのコスト最適化例が完了しました！")
    print("\nRemember: These are estimated costs based on approximate token counts.")
    print("注意: これらは近似トークンカウントに基づく推定コストです。")
    print("Actual costs may vary based on OpenRouter's pricing and model availability.")
    print("実際のコストは、OpenRouterの価格設定とモデルの利用可能性により異なる場合があります。")

if __name__ == "__main__":
    asyncio.run(main())