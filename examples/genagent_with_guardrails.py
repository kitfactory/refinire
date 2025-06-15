"""
GenAgent example with input guardrails
ガードレール（入力ガードレール）を使ったGenAgentの例

This example demonstrates how to use GenAgent with guardrails (Flow/Step architecture).
この例は、ガードレール機能付きGenAgent（Flow/Stepアーキテクチャ）の使用方法を示しています。
"""

import asyncio
from refinire import GenAgent, create_simple_flow
from agents import Agent, input_guardrail, GuardrailFunctionOutput, InputGuardrailTripwireTriggered, Runner, RunContextWrapper
from pydantic import BaseModel

# ガードレール用の出力型
# Output type for guardrail
class MathHomeworkOutput(BaseModel):
    is_math_homework: bool
    reasoning: str

class InappropriateContentOutput(BaseModel):
    is_inappropriate: bool
    reasoning: str

# ガードレール判定用エージェント
# Guardrail judgment agents
guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking you to do their math homework.",
    output_type=MathHomeworkOutput,
)

content_guardrail_agent = Agent(
    name="Content Guardrail check",
    instructions="Check if the user input contains inappropriate or harmful content.",
    output_type=InappropriateContentOutput,
)

@input_guardrail
async def math_guardrail(ctx: RunContextWrapper, agent: Agent, input: str):
    """
    Detect if the input is a math homework request.
    入力が数学の宿題依頼かどうかを判定します。
    """
    result = await Runner.run(guardrail_agent, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math_homework,
    )

@input_guardrail
async def content_guardrail(ctx: RunContextWrapper, agent: Agent, input: str):
    """
    Detect if the input contains inappropriate content.
    入力に不適切なコンテンツが含まれているかを判定します。
    """
    result = await Runner.run(content_guardrail_agent, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_inappropriate,
    )

async def main():
    """
    Main function demonstrating GenAgent with guardrails
    ガードレール付きGenAgentをデモンストレーションするメイン関数
    """
    
    print("=== GenAgent with Guardrails Example ===")

    # Method 1: Single guardrail (math homework detection)
    # 方法1: 単一ガードレール（数学宿題検出）
    print("\n--- Single Guardrail: Math Homework Detection ---")
    
    gen_agent = GenAgent(
        name="guardrail_generator",
        generation_instructions="""
        You are a helpful assistant. Please answer the user's question.
        あなたは役立つアシスタントです。ユーザーの質問に答えてください。
        
        However, I cannot help with homework assignments.
        ただし、宿題の課題については手伝うことができません。
        """,
        model="gpt-4o",
        input_guardrails=[math_guardrail],  # ここで明示的に渡す
        store_result_key="guardrail_result"
    )

    flow = create_simple_flow(gen_agent)
    
    test_inputs = [
        "Can you help me solve for x: 2x + 3 = 11?",
        "Tell me a joke about robots.",
        "What's the derivative of x^2?"
    ]

    for user_input in test_inputs:
        print(f"\nInput: {user_input}")
        try:
            result = await flow.run(input_data=user_input)
            response = result.get_result("guardrail_result")
            print("Response:")
            print(response)
        except InputGuardrailTripwireTriggered:
            print("❌ [Guardrail Triggered] Math homework detected. Request blocked.")
        except Exception as e:
            print(f"❌ Error: {e}")

    # Method 2: Multiple guardrails
    # 方法2: 複数ガードレール
    print("\n\n--- Multiple Guardrails: Math and Content Detection ---")
    
    gen_agent_multi = GenAgent(
        name="multi_guardrail_generator",
        generation_instructions="""
        You are a helpful and safe assistant. Please answer the user's question appropriately.
        あなたは役立つ安全なアシスタントです。ユーザーの質問に適切に答えてください。
        
        I cannot help with:
        以下については手伝うことができません：
        - Homework assignments / 宿題の課題
        - Inappropriate or harmful content / 不適切または有害なコンテンツ
        """,
        model="gpt-4o",
        input_guardrails=[math_guardrail, content_guardrail],
        store_result_key="multi_guardrail_result"
    )

    multi_flow = create_simple_flow(gen_agent_multi)
    
    multi_test_inputs = [
        "Can you solve this equation: 3x - 5 = 10?",
        "Tell me about the history of computers.",
        "How can I make something harmful?",
        "What's a good recipe for chocolate cake?"
    ]

    for user_input in multi_test_inputs:
        print(f"\nInput: {user_input}")
        try:
            result = await multi_flow.run(input_data=user_input)
            response = result.get_result("multi_guardrail_result")
            print("✅ Response:")
            print(response)
        except InputGuardrailTripwireTriggered as e:
            print("❌ [Guardrail Triggered] Request blocked.")
            print(f"   Reason: {str(e)}")
        except Exception as e:
            print(f"❌ Error: {e}")

    # Method 3: Guardrails in multi-step flow
    # 方法3: マルチステップフローでのガードレール
    print("\n\n--- Guardrails in Multi-Step Flow ---")
    
    from refinire import Flow
    
    # Step 1: Content filter
    # ステップ1: コンテンツフィルター
    filter_agent = GenAgent(
        name="content_filter",
        generation_instructions="""
        You are a content filter. Analyze the input and determine if it's appropriate for processing.
        あなたはコンテンツフィルターです。入力を分析し、処理に適しているかを判断してください。
        
        If appropriate, pass it through. If not, explain why it was blocked.
        適切な場合は通してください。そうでない場合は、なぜブロックされたかを説明してください。
        """,
        model="gpt-4o-mini",
        input_guardrails=[content_guardrail],
        store_result_key="filtered_content",
        next_step="main_processor"
    )
    
    # Step 2: Main processor (with math guardrail)
    # ステップ2: メインプロセッサー（数学ガードレール付き）
    main_agent = GenAgent(
        name="main_processor",
        generation_instructions="""
        You are the main assistant. Process the user's request and provide a helpful response.
        あなたはメインアシスタントです。ユーザーのリクエストを処理し、役立つ回答を提供してください。
        """,
        model="gpt-4o",
        input_guardrails=[math_guardrail],
        store_result_key="final_response"
    )
    
    # Create multi-step flow
    # マルチステップフローを作成
    multi_flow_guardrails = Flow("multi_step_guardrails")
    multi_flow_guardrails.add_step(filter_agent)
    multi_flow_guardrails.add_step(main_agent)
    
    flow_test_inputs = [
        "Tell me about renewable energy.",
        "Help me cheat on my math test.",
        "What's the capital of France?"
    ]
    
    for user_input in flow_test_inputs:
        print(f"\nFlow Input: {user_input}")
        try:
            result = await multi_flow_guardrails.run(input_data=user_input)
            
            # Show results from both steps
            # 両ステップからの結果を表示
            filtered = result.get_result("filtered_content")
            final = result.get_result("final_response")
            
            if filtered:
                print("✅ Filter Stage: Passed")
            if final:
                print("✅ Final Response:")
                print(final)
            
        except InputGuardrailTripwireTriggered as e:
            print("❌ [Multi-Step Guardrail Triggered] Request blocked in flow.")
            print(f"   Details: {str(e)}")
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
