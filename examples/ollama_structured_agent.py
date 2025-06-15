"""
Example of using Ollama with structured output
Ollamaで構造化された出力を使用する例
"""

import asyncio
from typing import List
from pydantic import BaseModel
from agents import Agent, Runner
from refinire import OllamaModel

class WeatherInfo(BaseModel):
    """
    Weather information data model
    天気情報データモデル
    """
    location: str
    """Location name / 場所の名前"""
    
    temperature: float
    """Temperature in Celsius / 気温（摂氏）"""
    
    condition: str
    """Weather condition / 天気の状態"""
    
    recommendation: str
    """Activity recommendation / おすすめの活動"""

class WeatherReport(BaseModel):
    """
    Weather report with multiple locations
    複数地点の天気レポート
    """
    report_date: str
    """Report date / レポート日付"""
    
    locations: List[WeatherInfo]
    """Weather information for multiple locations / 複数地点の天気情報"""

async def main():
    """
    Main function to demonstrate structured output with Ollama
    Ollamaでの構造化出力を実演するメイン関数
    """
    # Create an agent with Ollama model
    # OllamaモデルでAgentを作成
    model = OllamaModel(model="phi4-mini:latest")
    agent = Agent(
        name="Weather Reporter",
        model=model,
        instructions="""You are a helpful weather reporter that responds in Japanese.
You will provide weather information and activity recommendations for different locations.
Your recommendations should consider the weather conditions and be practical.

あなたは日本語で応答する天気レポーターです。
異なる場所の天気情報とアクティビティの推奨事項を提供します。
推奨事項は天候を考慮し、実用的なものである必要があります。

Important: Your response must be in the exact JSON format matching the WeatherReport schema:
{
    "report_date": "YYYY-MM-DD",
    "locations": [
        {
            "location": "地名",
            "temperature": 気温（数値）,
            "condition": "天気の状態",
            "recommendation": "おすすめの活動"
        },
        ...
    ]
}""",
        output_type=WeatherReport  # Specify the output type / 出力の型を指定
    )

    # Run the agent and get structured response
    # Agentを実行して構造化されたレスポンスを取得
    response = await Runner.run(
        agent,
        "東京、大阪、札幌の今日の天気と、それぞれの場所でおすすめの活動を教えてください。"
    )

    # Print the structured output
    # 構造化された出力を表示
    weather_report = response.final_output
    print(f"\n=== 天気レポート ({weather_report.report_date}) ===")
    for info in weather_report.locations:
        print(f"\n【{info.location}】")
        print(f"気温: {info.temperature}°C")
        print(f"天気: {info.condition}")
        print(f"おすすめ: {info.recommendation}")

if __name__ == "__main__":
    # Disable tracing since we're not using OpenAI's API
    # OpenAIのAPIを使用しないのでトレースを無効化
    from agents import set_tracing_disabled
    set_tracing_disabled(True)
    
    asyncio.run(main()) 
