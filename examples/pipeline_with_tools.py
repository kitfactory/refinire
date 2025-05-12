"""
Pipeline example with tools for enhanced generation
ツールを使用した拡張生成のPipelineの例
"""

from agents_sdk_models.pipeline import Pipeline
from agents import function_tool

@function_tool
def search_web(query: str) -> str:
    """
    Search the web for information.
    Webで情報を検索します。

    Args:
        query: The search query / 検索クエリ
    """
    # 実際のWeb検索APIを呼ぶ場合はここを実装
    return f"Search results for: {query}"

@function_tool
def get_weather(location: str) -> str:
    """
    Get current weather for a location.
    指定した場所の現在の天気を取得します。

    Args:
        location: The location to get weather for / 天気を取得する場所
    """
    # 実際の天気APIを呼ぶ場合はここを実装
    return f"Weather in {location}: Sunny, 25°C"

def main():
    # パイプライン用のツールを定義
    tools = [search_web, get_weather]

    pipeline = Pipeline(
        name="tooled_generator",
        generation_template="""
        You are a helpful assistant that can use tools to gather information.
        あなたは情報を収集するためにツールを使用できる役立つアシスタントです。

        You have access to the following tools:
        以下のツールにアクセスできます：

        1. search_web: Search the web for information
           search_web: 情報をWebで検索する
        2. get_weather: Get current weather for a location
           get_weather: 場所の現在の天気を取得する

        Please use these tools when appropriate to provide accurate information.
        適切な場合は、これらのツールを使用して正確な情報を提供してください。
        """,
        evaluation_template=None,  # No evaluation
        model="gpt-3.5-turbo",  # Using GPT-3.5
        generation_tools=tools
    )

    test_inputs = [
        "What's the weather like in Tokyo?",
        "Search for information about the latest AI developments"
    ]

    for user_input in test_inputs:
        print(f"\nInput: {user_input}")
        result = pipeline.run(user_input)
        print("Response:")
        print(result)

if __name__ == "__main__":
    main() 