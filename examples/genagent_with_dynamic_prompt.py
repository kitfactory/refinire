"""
GenAgent example with dynamic prompt function
動的プロンプト生成関数（dynamic_prompt）を使ったGenAgentの例

This example demonstrates how to use GenAgent with dynamic prompt functionality (Flow/Step architecture).
この例は、動的プロンプト機能付きGenAgent（Flow/Stepアーキテクチャ）の使用方法を示しています。
"""

import asyncio
from refinire import GenAgent, create_simple_flow
from datetime import datetime
import re

def simple_dynamic_prompt(user_input: str) -> str:
    """
    Simple dynamic prompt that modifies user input.
    ユーザー入力を変更するシンプルな動的プロンプト。
    
    Args:
        user_input: The user's input / ユーザーの入力
        
    Returns:
        Modified prompt / 変更されたプロンプト
    """
    # Example: Convert to uppercase and add context
    # 例：大文字化してコンテキストを追加
    return f"[DYNAMIC PROMPT] USER SAID: {user_input.upper()}"

def contextual_dynamic_prompt(user_input: str) -> str:
    """
    Contextual dynamic prompt that adds time and formatting.
    時間と書式を追加するコンテキスト動的プロンプト。
    
    Args:
        user_input: The user's input / ユーザーの入力
        
    Returns:
        Contextualized prompt / コンテキスト化されたプロンプト
    """
    current_time = datetime.now().strftime("%H:%M:%S")
    return f"[{current_time}] Context-aware request: {user_input}"

def intelligent_dynamic_prompt(user_input: str) -> str:
    """
    Intelligent dynamic prompt that adapts based on input content.
    入力内容に基づいて適応するインテリジェント動的プロンプト。
    
    Args:
        user_input: The user's input / ユーザーの入力
        
    Returns:
        Intelligently adapted prompt / インテリジェントに適応されたプロンプト
    """
    # Detect question types and adapt prompt accordingly
    # 質問タイプを検出して適切にプロンプトを適応
    input_lower = user_input.lower()
    
    if any(word in input_lower for word in ['joke', 'funny', 'humor']):
        return f"[HUMOR MODE] Please respond with humor to: {user_input}"
    elif any(word in input_lower for word in ['explain', 'what is', 'how does']):
        return f"[EDUCATIONAL MODE] Please provide a detailed explanation for: {user_input}"
    elif any(word in input_lower for word in ['create', 'write', 'generate']):
        return f"[CREATIVE MODE] Please be creative and generate content for: {user_input}"
    elif re.search(r'\?', user_input):
        return f"[Q&A MODE] Please answer this question: {user_input}"
    else:
        return f"[GENERAL MODE] Please respond to: {user_input}"

async def main():
    """
    Main function demonstrating GenAgent with dynamic prompt functionality
    動的プロンプト機能付きGenAgentをデモンストレーションするメイン関数
    """
    
    print("=== GenAgent with Dynamic Prompt Example ===")

    # Method 1: Simple dynamic prompt
    # 方法1: シンプルな動的プロンプト
    print("\n--- Simple Dynamic Prompt ---")
    
    simple_agent = GenAgent(
        name="simple_dynamic_agent",
        generation_instructions="""
        You are a helpful assistant. Respond to the user's request.
        あなたは親切なアシスタントです。ユーザーのリクエストに答えてください。
        
        Pay attention to any special formatting in the prompt.
        プロンプトの特別な書式に注意を払ってください。
        """,
        model="gpt-4o-mini",
        dynamic_prompt=simple_dynamic_prompt,
        store_result_key="simple_result"
    )

    simple_flow = create_simple_flow(simple_agent)
    
    simple_inputs = [
        "Tell me a joke.",
        "What is the capital of Japan?"
    ]

    for i, user_input in enumerate(simple_inputs, 1):
        print(f"\n[{i}] User: {user_input}")
        print(f"   Dynamic Prompt: {simple_dynamic_prompt(user_input)}")
        try:
            result = await simple_flow.run(input_data=user_input)
            response = result.get_result("simple_result")
            print(f"AI: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")

    # Method 2: Contextual dynamic prompt with time awareness
    # 方法2: 時間認識付きコンテキスト動的プロンプト
    print("\n\n--- Contextual Dynamic Prompt with Time ---")
    
    contextual_agent = GenAgent(
        name="contextual_agent",
        generation_instructions="""
        You are a time-aware assistant. Use the timestamp information in your responses.
        あなたは時間認識アシスタントです。応答でタイムスタンプ情報を使用してください。
        
        Reference the time when it's relevant to the conversation.
        会話に関連する場合は時間を参照してください。
        """,
        model="gpt-4o-mini",
        dynamic_prompt=contextual_dynamic_prompt,
        store_result_key="contextual_result"
    )

    contextual_flow = create_simple_flow(contextual_agent)
    
    contextual_inputs = [
        "What should I have for breakfast?",
        "Is it a good time to call someone in Tokyo?",
        "Plan my evening activities"
    ]

    for i, user_input in enumerate(contextual_inputs, 1):
        print(f"\n[{i}] User: {user_input}")
        print(f"   Dynamic Prompt: {contextual_dynamic_prompt(user_input)}")
        try:
            result = await contextual_flow.run(input_data=user_input)
            response = result.get_result("contextual_result")
            print(f"AI: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")

    # Method 3: Intelligent adaptive dynamic prompt
    # 方法3: インテリジェント適応動的プロンプト
    print("\n\n--- Intelligent Adaptive Dynamic Prompt ---")
    
    intelligent_agent = GenAgent(
        name="intelligent_agent",
        generation_instructions="""
        You are an adaptive assistant that changes behavior based on the mode specified in the prompt.
        あなたはプロンプトで指定されたモードに基づいて動作を変更する適応型アシスタントです。
        
        - HUMOR MODE: Be funny and entertaining
          ユーモアモード：面白く楽しい
        - EDUCATIONAL MODE: Be detailed and informative
          教育モード：詳細で情報豊富
        - CREATIVE MODE: Be imaginative and original
          創造モード：想像力豊かでオリジナル
        - Q&A MODE: Be direct and accurate
          Q&Aモード：直接的で正確
        - GENERAL MODE: Be helpful and balanced
          一般モード：役立つでバランス良く
        """,
        model="gpt-4o",
        dynamic_prompt=intelligent_dynamic_prompt,
        store_result_key="intelligent_result"
    )

    intelligent_flow = create_simple_flow(intelligent_agent)
    
    intelligent_inputs = [
        "Tell me a joke about programming",
        "Explain how machine learning works",
        "Create a short story about a robot",
        "What is the largest planet in our solar system?",
        "Help me with my project"
    ]

    for i, user_input in enumerate(intelligent_inputs, 1):
        print(f"\n[{i}] User: {user_input}")
        adapted_prompt = intelligent_dynamic_prompt(user_input)
        print(f"   Adapted Prompt: {adapted_prompt}")
        try:
            result = await intelligent_flow.run(input_data=user_input)
            response = result.get_result("intelligent_result")
            print(f"AI: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")

    # Method 4: Multi-Agent Flow with different dynamic prompts
    # 方法4: 異なる動的プロンプトを持つマルチエージェントフロー
    print("\n\n--- Multi-Agent Flow with Dynamic Prompts ---")
    
    from refinire import Flow
    
    def analyzer_prompt(user_input: str) -> str:
        return f"[ANALYSIS] Analyze the following request: {user_input}"
    
    def creator_prompt(user_input: str) -> str:
        return f"[CREATION] Based on the analysis, create content for: {user_input}"
    
    # Agent 1: Analyzer with analysis-focused dynamic prompt
    # エージェント1: 分析重視の動的プロンプトを持つ分析者
    analyzer_agent = GenAgent(
        name="analyzer",
        generation_instructions="""
        You are an analytical assistant. Break down requests into components and analyze them.
        あなたは分析アシスタントです。リクエストをコンポーネントに分解して分析してください。
        """,
        model="gpt-4o-mini",
        dynamic_prompt=analyzer_prompt,
        store_result_key="analysis",
        next_step="creator"
    )
    
    # Agent 2: Creator with creation-focused dynamic prompt
    # エージェント2: 創造重視の動的プロンプトを持つ創造者
    creator_agent = GenAgent(
        name="creator",
        generation_instructions="""
        You are a creative assistant. Use the analysis to create engaging content.
        あなたは創造的アシスタントです。分析を使用して魅力的なコンテンツを作成してください。
        
        Reference the previous analysis in your creation.
        創造において前の分析を参照してください。
        """,
        model="gpt-4o-mini",
        dynamic_prompt=creator_prompt,
        store_result_key="creation"
    )
    
    # Create multi-agent flow
    # マルチエージェントフローを作成
    dynamic_flow = Flow("dynamic_prompt_flow")
    dynamic_flow.add_step(analyzer_agent)
    dynamic_flow.add_step(creator_agent)
    
    flow_inputs = [
        "Create a marketing campaign for eco-friendly products",
        "Design a user interface for a mobile app"
    ]
    
    for i, user_input in enumerate(flow_inputs, 1):
        print(f"\n[Flow {i}] User: {user_input}")
        print(f"   Analyzer Prompt: {analyzer_prompt(user_input)}")
        print(f"   Creator Prompt: {creator_prompt(user_input)}")
        try:
            result = await dynamic_flow.run(input_data=user_input)
            
            # Show results from both agents
            # 両エージェントからの結果を表示
            analysis = result.get_result("analysis")
            creation = result.get_result("creation")
            
            print(f"🔍 Analysis: {analysis}")
            print(f"✨ Creation: {creation}")
            
        except Exception as e:
            print(f"❌ Flow Error: {e}")

def sync_main():
    """
    Synchronous wrapper for the async main function
    非同期main関数の同期ラッパー
    """
    asyncio.run(main())

if __name__ == "__main__":
    sync_main() 
