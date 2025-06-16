"""
RefinireAgent example with dynamic_prompt function
動的プロンプト生成関数（dynamic_prompt）を使ったRefinireAgentの例
"""

from refinire import RefinireAgent

def my_dynamic_prompt(user_input: str) -> str:
    # 例: ユーザー入力を大文字化し、履歴やセッションは含めないシンプルなカスタムプロンプト
    return f"[DYNAMIC PROMPT] USER SAID: {user_input.upper()}"

def main():
    pipeline = RefinireAgent(
        name="dynamic_prompt_example",
        generation_instructions="""
        You are a helpful assistant. Respond to the user's request.
        あなたは親切なアシスタントです。ユーザーのリクエストに答えてください。
        """,
        evaluation_instructions=None,
        model="gpt-4o",
        dynamic_prompt=my_dynamic_prompt
    )

    user_inputs = [
        "Tell me a joke.",
        "What is the capital of Japan?"
    ]

    for i, user_input in enumerate(user_inputs, 1):
        print(f"\n[{i}] User: {user_input}")
        result = pipeline.run(user_input)
        print(f"AI: {result}")

if __name__ == "__main__":
    main() 
