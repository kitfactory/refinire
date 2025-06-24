"""
RefinireAgent example with input guardrails
ガードレール（入力ガードレール）を使ったRefinireAgentの例
"""

from refinire import RefinireAgent
import re

def math_homework_guardrail(user_input: str) -> bool:
    """
    Detect if the input is a math homework request.
    入力が数学の宿題依頼かどうかを判定します。
    """
    # 数学の宿題に関連するキーワードをチェック
    math_keywords = [
        'solve for', 'equation', 'solve', 'calculate', 'find x', 'find y',
        'solve for x', 'solve for y', 'math homework', 'homework help'
    ]
    
    user_input_lower = user_input.lower()
    for keyword in math_keywords:
        if keyword in user_input_lower:
            return False  # ガードレールに引っかかる場合はFalseを返す
    
    return True  # ガードレールを通過する場合はTrueを返す

def main():
    # パイプラインのエージェントにガードレールを設定
    pipeline = RefinireAgent(
        name="guardrail_pipeline",
        generation_instructions="""
        You are a helpful assistant. Please answer the user's question.
        あなたは役立つアシスタントです。ユーザーの質問に答えてください。
        """,
        evaluation_instructions=None,
        model="gpt-4o",
        input_guardrails=[math_homework_guardrail],  # シンプルな関数ベースのガードレール
    )

    user_inputs = [
        "Can you help me solve for x: 2x + 3 = 11?",
        "Tell me a joke about robots.",
    ]

    for user_input in user_inputs:
        print(f"\nInput: {user_input}")
        try:
            result = pipeline.run(user_input)
            print("Response:")
            print(result)
        except Exception as e:
            if "Input validation failed" in str(e):
                print("[Guardrail Triggered] Math homework detected. Request blocked.")
            else:
                print(f"Error: {e}")

if __name__ == "__main__":
    main() 
