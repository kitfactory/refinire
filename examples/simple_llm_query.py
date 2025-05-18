#!/usr/bin/env python3
"""
Simple LLM Query Example

English: A simple example demonstrating how to query an LLM with tracing enabled using DialogProcessor.
日本語: DialogProcessor を使ってトレーシングを有効化した上で LLM に問い合わせる簡単な例。
"""
import sys
try:
    # English: Initialize colorama for Windows ANSI support.
    # 日本語: Windows の ANSI サポートのため colorama を初期化します。
    import colorama
    colorama.init()
except ImportError:
    pass
import asyncio
from agents.tracing import set_tracing_disabled, set_trace_processors, trace
from agents_sdk_models.llm import get_llm
from agents.model_settings import ModelSettings
from agents.models.interface import ModelTracing
from agents_sdk_models import AgentPipeline

async def main() -> None:
    """
    English: Main entrypoint for direct LLM query with tracing.
    日本語: 直接 LLM 呼び出しでトレーシングを行うエントリポイント。
    """

    # Create LLM model instance with tracing enabled
    llm = get_llm(model="gpt-3.5-turbo", temperature=0.5, tracing=True)

    # Prepare messages including system and user prompts
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Translate 'Hello, world!' into French."},
    ]
    # Use a trace context for the workflow
    with trace("simple_query", metadata={"example": "true"}):
        # Perform the LLM query using list of messages
        response = await llm.get_response(
            system_instructions=None,
            input=messages,
            model_settings=ModelSettings(temperature=0.5),
            tools=[],
            output_schema=None,
            handoffs=[],
            tracing=ModelTracing.ENABLED,
        )
        # Print the response output
        print("Response:", response.output)

if __name__ == '__main__':
    asyncio.run(main()) 