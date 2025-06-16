"""
Simple generation example using RefinireAgent without evaluation
評価なしのRefinireAgentを使用したシンプルな生成の例
"""

from refinire import RefinireAgent

def main():
    # Initialize pipeline with generation template only
    # 生成テンプレートのみでパイプラインを初期化
    pipeline = RefinireAgent(
        name="simple_generator",
        generation_instructions="""
        You are a helpful assistant that generates creative stories.
        あなたは創造的な物語を生成する役立つアシスタントです。

        Please generate a short story based on the user's input.
        ユーザーの入力に基づいて短い物語を生成してください。
        """,
        evaluation_instructions=None,  # No evaluation
        model="gpt-3.5-turbo"  # Using GPT-3.5
    )

    # Run the pipeline
    # パイプラインを実行
    user_input = "A story about a robot learning to paint"
    result = pipeline.run(user_input)
    print("\nGenerated Story:")
    print(result)

if __name__ == "__main__":
    main() 
