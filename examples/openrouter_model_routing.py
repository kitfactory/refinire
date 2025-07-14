#!/usr/bin/env python3
"""
OpenRouter Model Routing Example
OpenRouterモデルルーティング例

This example demonstrates how to use multiple models through OpenRouter
for different tasks, showcasing model selection strategies.
この例は、異なるタスクに対してOpenRouter経由で複数のモデルを使用する方法を示し、
モデル選択戦略を紹介します。

Before running this example, ensure you have:
この例を実行する前に、以下を確認してください：
1. Set OPENROUTER_API_KEY environment variable
   OPENROUTER_API_KEY環境変数を設定
2. Install refinire: pip install -e .
   refinireをインストール: pip install -e .
"""

import os
import asyncio
from dataclasses import dataclass
from typing import List, Dict, Any
from refinire.core.llm import get_llm
from pydantic import BaseModel, Field

# Clear other provider environment variables to ensure OpenRouter is used
# 他のプロバイダーの環境変数をクリアしてOpenRouterが使用されるようにする
os.environ.pop('OLLAMA_API_KEY', None)
os.environ.pop('LMSTUDIO_API_KEY', None)
os.environ.pop('OLLAMA_BASE_URL', None)
os.environ.pop('LMSTUDIO_BASE_URL', None)

@dataclass
class ModelConfig:
    """
    Configuration for different models with their optimal use cases
    異なるモデルの最適な使用例での設定
    """
    name: str
    description: str
    use_cases: List[str]
    cost_tier: str  # low, medium, high
    speed_tier: str  # fast, medium, slow

# Model configurations for different tasks
# 異なるタスクに対するモデル設定
MODEL_CONFIGS = {
    "llama-3-8b": ModelConfig(
        name="meta-llama/llama-3-8b-instruct",
        description="Fast and cost-effective for general tasks",
        use_cases=["general_chat", "simple_analysis", "brainstorming"],
        cost_tier="low",
        speed_tier="fast"
    ),
    "gpt-4": ModelConfig(
        name="openai/gpt-4",
        description="High-quality reasoning and complex tasks",
        use_cases=["complex_reasoning", "code_review", "detailed_analysis"],
        cost_tier="high",
        speed_tier="medium"
    ),
    "claude-3-haiku": ModelConfig(
        name="anthropic/claude-3-haiku",
        description="Balanced performance for most tasks",
        use_cases=["writing", "summarization", "general_assistance"],
        cost_tier="medium",
        speed_tier="fast"
    ),
    "claude-3-sonnet": ModelConfig(
        name="anthropic/claude-3.5-sonnet",
        description="Advanced reasoning and creative tasks",
        use_cases=["creative_writing", "advanced_analysis", "problem_solving"],
        cost_tier="medium",
        speed_tier="medium"
    ),
    "mixtral-8x7b": ModelConfig(
        name="mistralai/mixtral-8x7b-instruct",
        description="Good balance of performance and cost",
        use_cases=["technical_tasks", "code_generation", "structured_output"],
        cost_tier="low",
        speed_tier="medium"
    )
}

class TaskRouter:
    """
    Routes tasks to appropriate models based on requirements
    要件に基づいてタスクを適切なモデルにルーティング
    """
    
    def __init__(self):
        self.models = {}
        
    async def get_model_for_task(self, task_type: str, complexity: str = "medium") -> str:
        """
        Select optimal model based on task type and complexity
        タスクタイプと複雑さに基づいて最適なモデルを選択
        """
        routing_rules = {
            "general_chat": "llama-3-8b",
            "code_review": "gpt-4",
            "creative_writing": "claude-3-sonnet",
            "summarization": "claude-3-haiku",
            "technical_analysis": "mixtral-8x7b",
            "complex_reasoning": "gpt-4",
            "simple_analysis": "llama-3-8b",
            "structured_output": "mixtral-8x7b"
        }
        
        model_key = routing_rules.get(task_type, "llama-3-8b")
        
        # Upgrade model for high complexity tasks
        # 高複雑度タスクではモデルをアップグレード
        if complexity == "high":
            if model_key in ["llama-3-8b", "claude-3-haiku"]:
                model_key = "gpt-4"
        
        return MODEL_CONFIGS[model_key].name
    
    async def get_model_instance(self, model_name: str):
        """
        Get or create model instance
        モデルインスタンスを取得または作成
        """
        if model_name not in self.models:
            self.models[model_name] = get_llm(provider="openrouter", model=model_name)
        return self.models[model_name]

async def demonstrate_task_routing():
    """
    Demonstrate routing different tasks to appropriate models
    異なるタスクを適切なモデルにルーティングすることを実演
    """
    print("=== Task Routing Example ===")
    print("=== タスクルーティング例 ===\n")
    
    router = TaskRouter()
    
    # Define various tasks with different requirements
    # 異なる要件を持つ様々なタスクを定義
    tasks = [
        {
            "type": "general_chat",
            "complexity": "low",
            "prompt": "Hello! How are you today?",
            "description": "Simple greeting"
        },
        {
            "type": "code_review",
            "complexity": "high",
            "prompt": "Review this Python function for bugs and improvements:\n\ndef calculate_fibonacci(n):\n    if n <= 1:\n        return n\n    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)",
            "description": "Code review task"
        },
        {
            "type": "creative_writing",
            "complexity": "medium",
            "prompt": "Write a short story about a robot learning to paint",
            "description": "Creative writing task"
        },
        {
            "type": "technical_analysis",
            "complexity": "medium",
            "prompt": "Explain the differences between REST and GraphQL APIs",
            "description": "Technical analysis"
        }
    ]
    
    for i, task in enumerate(tasks, 1):
        print(f"{i}. {task['description']} ({task['type']}, {task['complexity']} complexity)")
        print(f"{i}. {task['description']} ({task['type']}, {task['complexity']} 複雑度)")
        
        try:
            # Route task to appropriate model
            # タスクを適切なモデルにルーティング
            model_name = await router.get_model_for_task(task['type'], task['complexity'])
            model = await router.get_model_instance(model_name)
            
            print(f"   Selected model: {model_name}")
            print(f"   選択されたモデル: {model_name}")
            
            # Generate response
            # 応答を生成
            response = await model.generate(task['prompt'], temperature=0.7)
            print(f"   Response: {response[:200]}...")
            print(f"   応答: {response[:200]}...")
            print()
            
        except Exception as e:
            print(f"   Error: {e}")
            print(f"   エラー: {e}")
            print()

class ComparisonResult(BaseModel):
    """
    Structure for model comparison results
    モデル比較結果の構造
    """
    model_name: str = Field(description="Name of the model")
    response_quality: int = Field(description="Response quality score (1-10)")
    response_time: float = Field(description="Response time in seconds")
    cost_estimate: str = Field(description="Estimated cost tier")
    best_for: List[str] = Field(description="Best use cases for this model")

async def compare_models_on_same_task():
    """
    Compare different models on the same task
    同じタスクで異なるモデルを比較
    """
    print("=== Model Comparison Example ===")
    print("=== モデル比較例 ===\n")
    
    task_prompt = "Explain the concept of machine learning in simple terms suitable for a beginner."
    
    # Models to compare
    # 比較するモデル
    models_to_compare = [
        "meta-llama/llama-3-8b-instruct",
        "anthropic/claude-3-haiku",
        "mistralai/mixtral-8x7b-instruct"
    ]
    
    print(f"Task: {task_prompt}")
    print(f"タスク: {task_prompt}")
    print(f"Comparing {len(models_to_compare)} models...")
    print(f"{len(models_to_compare)}個のモデルを比較中...")
    print()
    
    for i, model_name in enumerate(models_to_compare, 1):
        print(f"{i}. Testing {model_name}:")
        print(f"{i}. {model_name}をテスト中:")
        
        try:
            model = get_llm(provider="openrouter", model=model_name)
            
            import time
            start_time = time.time()
            response = await model.generate(task_prompt, temperature=0.5)
            end_time = time.time()
            
            response_time = end_time - start_time
            
            print(f"   Response time: {response_time:.2f}s")
            print(f"   応答時間: {response_time:.2f}秒")
            print(f"   Response length: {len(response)} characters")
            print(f"   応答の長さ: {len(response)} 文字")
            print(f"   Response preview: {response[:150]}...")
            print(f"   応答プレビュー: {response[:150]}...")
            print()
            
        except Exception as e:
            print(f"   Error: {e}")
            print(f"   エラー: {e}")
            print()

async def fallback_model_example():
    """
    Demonstrate fallback model strategy
    フォールバックモデル戦略を実演
    """
    print("=== Fallback Model Strategy ===")
    print("=== フォールバックモデル戦略 ===\n")
    
    # Define model hierarchy: primary -> secondary -> fallback
    # モデル階層を定義: プライマリ -> セカンダリ -> フォールバック
    model_hierarchy = [
        "openai/gpt-4",           # Primary (expensive, high quality)
        "anthropic/claude-3-haiku", # Secondary (balanced)
        "meta-llama/llama-3-8b-instruct"  # Fallback (cheap, fast)
    ]
    
    task_prompt = "Write a detailed technical specification for a REST API endpoint that handles user authentication."
    
    print(f"Task: {task_prompt}")
    print(f"タスク: {task_prompt}")
    print(f"Trying models in order: {' -> '.join(model_hierarchy)}")
    print(f"モデルを順番に試行: {' -> '.join(model_hierarchy)}")
    print()
    
    for i, model_name in enumerate(model_hierarchy, 1):
        print(f"Attempt {i}: {model_name}")
        print(f"試行 {i}: {model_name}")
        
        try:
            model = get_llm(provider="openrouter", model=model_name)
            response = await model.generate(task_prompt, temperature=0.3)
            
            print(f"   ✓ Success with {model_name}")
            print(f"   ✓ {model_name}で成功")
            print(f"   Response: {response[:200]}...")
            print(f"   応答: {response[:200]}...")
            break
            
        except Exception as e:
            print(f"   ✗ Failed with {model_name}: {e}")
            print(f"   ✗ {model_name}で失敗: {e}")
            
            if i < len(model_hierarchy):
                print(f"   Trying fallback model...")
                print(f"   フォールバックモデルを試行中...")
            else:
                print(f"   All models failed!")
                print(f"   すべてのモデルが失敗しました！")
            print()

async def main():
    """
    Main function to run all model routing examples
    すべてのモデルルーティング例を実行するメイン関数
    """
    # Check if OpenRouter API key is set
    # OpenRouter APIキーが設定されているかチェック
    if not os.getenv('OPENROUTER_API_KEY'):
        print("ERROR: OPENROUTER_API_KEY environment variable not set")
        print("エラー: OPENROUTER_API_KEY環境変数が設定されていません")
        print("Please set it with: export OPENROUTER_API_KEY=your_api_key")
        print("次のコマンドで設定してください: export OPENROUTER_API_KEY=your_api_key")
        return
    
    print("OpenRouter Model Routing Examples")
    print("OpenRouterモデルルーティング例")
    print("=" * 50)
    print()
    
    # Run examples
    # 例を実行
    await demonstrate_task_routing()
    await compare_models_on_same_task()
    await fallback_model_example()
    
    print("=" * 50)
    print("All model routing examples completed!")
    print("すべてのモデルルーティング例が完了しました！")

if __name__ == "__main__":
    asyncio.run(main())