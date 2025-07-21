#!/usr/bin/env python3
"""
Code Generation with Routing Sample - コード生成とrouting_instructionによる複雑度分類
コード生成ルーティングサンプル - 生成されたコードの複雑度を自動評価

This demonstrates generating code and using routing_instruction to classify code complexity.
コードを生成し、routing_instructionでコードの複雑度を分類する方法を実演します。
"""

import asyncio
import os
from refinire import RefinireAgent


async def code_generation_routing_demo():
    """
    Demonstrate code generation with complexity assessment routing
    複雑度評価ルーティング付きコード生成のデモ
    """
    print("💻🔀 Code Generation with Routing Sample")
    print("💻🔀 コード生成・ルーティングサンプル")
    print("=" * 60)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY environment variable.")
        print("❌ OPENAI_API_KEY環境変数を設定してください。")
        return
    
    # Create code generator agent / コード生成エージェントを作成
    code_generator = RefinireAgent(
        name="code_generator",
        generation_instructions="""
You are a Python code generator. Generate working Python code based on the user's request.
Write clean, functional code that solves the given problem.
At the end of your response, add a complexity assessment using exactly this format:
COMPLEXITY: [basic|intermediate|advanced]

あなたはPythonコード生成者です。ユーザーの要求に基づいて動作するPythonコードを生成してください。
与えられた問題を解決するクリーンで機能的なコードを書いてください。
レスポンスの最後に、正確にこの形式で複雑度評価を追加してください:
COMPLEXITY: [basic|intermediate|advanced]
        """,
        routing_instruction="After generating the code, assess its complexity and end with: COMPLEXITY: basic, COMPLEXITY: intermediate, or COMPLEXITY: advanced",
        model="gpt-4o-mini",
        timeout=60
    )
    
    # Test programming tasks / プログラミングタスクのテスト
    programming_tasks = [
        # Basic task / 基本タスク
        "Write a function that adds two numbers",
        
        # # Intermediate task / 中級タスク
        # "Create a class that implements a simple calculator with basic operations (add, subtract, multiply, divide)",
        
        # # Advanced task / 上級タスク
        # "Implement a binary search tree with insert, search, and delete operations, including proper balancing"
    ]
    
    print("🚀 Starting code generation with complexity routing...")
    print("🚀 複雑度ルーティング付きコード生成開始...")
    
    for i, task in enumerate(programming_tasks, 1):
        print(f"\n{'='*60}")
        print(f"💻 Task {i}: {task}")
        print(f"💻 タスク{i}: {task}")
        print("-" * 40)
        
        try:
            print(f"🔧 Generating code...")
            print(f"🔧 コード生成中...")
            
            start_time = asyncio.get_event_loop().time()
            result = await code_generator.run_async(task)
            
            # Display result in JSON format for debugging
            # デバッグ用にresultをJSON形式で表示
            import json
            print("\n📋 Result JSON:")
            print("📋 結果JSON:")
            try:
                # Get all attributes of the result object
                # resultオブジェクトの全ての属性を取得
                result_dict = {
                }                
                # Add all public attributes (not starting with _)
                # 全てのパブリック属性を追加（_で始まらないもの）
                for attr_name in dir(result):
                    print( attr_name )
                #     result_dict[attr_name] = result[attr_name]

                # print(json.dumps(result_dict, indent=2, ensure_ascii=False, default=str))
            except Exception as e:
                print(f"Error formatting result as JSON: {e}")
                print(f"Raw result: {result}")
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            if result.success:
                print(f"\n✅ Code generation completed!")
                print(f"✅ コード生成完了！")
                print(f"⏱️  Execution time: {execution_time:.2f} seconds")
                print(f"⏱️  実行時間: {execution_time:.2f} 秒")
                
                # Extract complexity assessment from response
                # レスポンスから複雑度評価を抽出
                response = result.content
                complexity = extract_complexity(response)
                
                print(f"\n📊 Results:")
                print(f"📊 結果:")
                print(f"   🔀 Complexity Level: {complexity}")
                
                # Show code preview / コードプレビューを表示
                code_lines = response.split('\n')
                code_section = []
                in_code = False
                
                for line in code_lines:
                    if '```python' in line.lower() or '```' in line and 'python' in line.lower():
                        in_code = True
                        continue
                    elif '```' in line and in_code:
                        break
                    elif in_code:
                        code_section.append(line)
                    elif line.strip().startswith('def ') or line.strip().startswith('class '):
                        code_section.append(line)
                        in_code = True
                
                if code_section:
                    code_preview = '\n'.join(code_section[:10])  # First 10 lines
                    print(f"   💻 Code preview:")
                    print(f"   💻 コードプレビュー:")
                    for line in code_preview.split('\n')[:5]:  # Show first 5 lines
                        print(f"      {line}")
                    if len(code_section) > 5:
                        print(f"      ... ({len(code_section)} total lines)")
                else:
                    print(f"   💻 Generated response: {response[:200]}...")
                
                # Handle complexity routing / 複雑度ルーティングを処理
                await handle_complexity_routing(complexity, task)
                
            else:
                print(f"❌ Code generation failed: {result.content}")
                print(f"❌ コード生成失敗: {result.content}")
                
        except Exception as e:
            print(f"💥 Error during code generation: {e}")
            print(f"💥 コード生成中エラー: {e}")
    
    print(f"\n{'='*60}")
    print("🎉 Code generation with routing demo completed!")
    print("🎉 コード生成・ルーティングデモ完了！")
    
    print(f"\n💡 What was demonstrated:")
    print(f"💡 実演された内容:")
    print(f"   • Python code generation from natural language")
    print(f"   • Complexity assessment via routing_instruction")
    print(f"   • Different handling based on complexity levels")
    print(f"   • Single agent performing both generation and evaluation")


def extract_complexity(response: str) -> str:
    """
    Extract complexity level from the response
    レスポンスから複雑度レベルを抽出
    """
    response_lower = response.lower()
    
    if "complexity: basic" in response_lower:
        return "basic"
    elif "complexity: intermediate" in response_lower:
        return "intermediate"
    elif "complexity: advanced" in response_lower:
        return "advanced"
    else:
        # Fallback: try to guess from content
        # フォールバック: 内容から推測
        if any(keyword in response_lower for keyword in ['class', 'inheritance', 'algorithm', 'tree', 'graph']):
            return "advanced (inferred)"
        elif any(keyword in response_lower for keyword in ['function', 'loop', 'condition', 'list']):
            return "intermediate (inferred)"
        else:
            return "basic (inferred)"


async def handle_complexity_routing(complexity: str, task: str):
    """
    Handle different actions based on complexity assessment
    複雑度評価に基づいて異なるアクションを実行
    """
    print(f"\n🎯 Handling complexity level: {complexity}")
    print(f"🎯 複雑度レベル処理: {complexity}")
    
    base_complexity = complexity.split(' ')[0]  # Remove "(inferred)" if present
    
    if base_complexity == "basic":
        print(f"   🟢 BASIC: Simple code ready for immediate use")
        print(f"   🟢 基本: シンプルなコードでそのまま使用可能")
        print(f"   📤 Action: Deploy to beginner-friendly environments")
        
    elif base_complexity == "intermediate":
        print(f"   🟡 INTERMEDIATE: Moderate complexity, requires some review")
        print(f"   🟡 中級: 中程度の複雑度、レビューが必要")
        print(f"   🔍 Action: Schedule for code review and testing")
        
    elif base_complexity == "advanced":
        print(f"   🔴 ADVANCED: Complex code requiring thorough review")
        print(f"   🔴 上級: 複雑なコードで徹底的なレビューが必要")
        print(f"   ⚠️  Action: Assign to senior developer for review")
        
    else:
        print(f"   ❓ UNKNOWN: Could not determine complexity level")
        print(f"   ❓ 不明: 複雑度レベルを判定できませんでした")
        print(f"   🔍 Action: Manual complexity assessment required")


if __name__ == "__main__":
    asyncio.run(code_generation_routing_demo())