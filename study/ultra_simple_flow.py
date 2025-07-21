#!/usr/bin/env python3
"""
Ultra Simple Flow - 最もシンプルなFlowの例
ウルトラシンプルフロー - SimpleFlowを使った最短コード例

This shows the absolute simplest way to create workflows.
これは最も絶対的にシンプルなワークフロー作成方法を示します。
"""

import asyncio
import os
from refinire import RefinireAgent
from refinire.agents.flow import SimpleFlow, simple_step, Context


async def ultra_simple_demo():
    """Ultra simple 2-step workflow"""
    print("⚡ Ultra Simple Flow Demo")
    print("⚡ ウルトラシンプルフローデモ")
    print("=" * 40)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set OPENAI_API_KEY")
        return
    
    # Step 1: Generate summary
    async def summarize(user_input: str, context: Context) -> Context:
        agent = RefinireAgent(
            name="summarizer",
            generation_instructions="Create a brief summary in 2 sentences.",
            model="gpt-4o-mini"
        )
        result = await agent.run_async(f"Summarize: {context.last_user_input}")
        context.shared_state["summary"] = result.content
        return context
    
    # Step 2: Generate questions  
    async def questions(user_input: str, context: Context) -> Context:
        agent = RefinireAgent(
            name="questioner", 
            generation_instructions="Generate 2 interesting questions about the topic.",
            model="gpt-4o-mini"
        )
        summary = context.shared_state.get("summary", "")
        result = await agent.run_async(f"Create questions about: {summary}")
        context.shared_state["questions"] = result.content
        return context
    
    # Create and run workflow - just 3 lines!
    # ワークフロー作成・実行 - たった3行！
    flow = SimpleFlow([simple_step("sum", summarize), simple_step("q", questions)])
    result = await flow.run("artificial intelligence")
    
    # Show results
    print(f"📝 Summary: {result.shared_state.get('summary', '')}")
    print(f"❓ Questions: {result.shared_state.get('questions', '')}")


async def one_liner_demo():
    """Demonstrate ultra-compact workflow creation"""
    print(f"\n🎯 One-Liner Workflow Demo")
    print("🎯 ワンライナーワークフローデモ")
    
    # Define simple processing step
    async def process(user_input: str, context: Context) -> Context:
        agent = RefinireAgent(name="processor", generation_instructions="Be helpful and concise.", model="gpt-4o-mini")
        result = await agent.run_async(context.last_user_input)
        context.shared_state["result"] = result.content
        return context
    
    # One-liner workflow execution!
    # ワンライナーワークフロー実行！
    result = await SimpleFlow([simple_step("process", process)]).run("Hello AI!")
    
    print(f"🤖 Response: {result.shared_state.get('result', '')}")


if __name__ == "__main__":
    async def main():
        await ultra_simple_demo()
        await one_liner_demo()
        
        print(f"\n✨ That's it! SimpleFlow makes workflows incredibly easy.")
        print("✨ これだけ！SimpleFlowでワークフローが信じられないほど簡単に。")
    
    asyncio.run(main())