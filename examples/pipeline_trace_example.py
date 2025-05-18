#!/usr/bin/env python3
"""
Pipeline Trace Example

English: An example demonstrating how to run an AgentPipeline with tracing enabled using ConsoleTracingProcessor.
日本語: ConsoleTracingProcessor を使ってトレースを有効化した上で AgentPipeline を実行する例。
"""

import sys
try:
    # English: Initialize colorama for Windows ANSI support.
    # 日本語: Windows の ANSI サポートのため colorama を初期化します。
    import colorama
    colorama.init()
except ImportError:
    pass

from agents.tracing import set_tracing_disabled, set_trace_processors, trace
from agents_sdk_models.tracing import ConsoleTracingProcessor
from agents_sdk_models import AgentPipeline


def main() -> None:
    """
    English: Main entrypoint for pipeline trace example.
    日本語: パイプライン実行のトレース例のエントリポイント。
    """
    # Create a pipeline: simple English-to-French translation
    pipeline = AgentPipeline(
        name="translate_pipeline",
        generation_instructions="You are a helpful assistant that translates English text into French.",
        evaluation_instructions="Evaluate the translation quality and return a JSON object with keys 'score' (0-100) and 'comment' (list of comments).",
        model="gpt-3.5-turbo",
        threshold=0,  # Always pass evaluation
        debug=False,  # Disable pipeline debug prints to rely on trace processor
    )
    # Initialize pipeline tracing processor using ConsoleTracingProcessor
    processor = ConsoleTracingProcessor()
    set_tracing_disabled(False)
    set_trace_processors([processor])

    # Input for the pipeline
    user_input = "Translate 'Good morning' into French."

    # Run pipeline under a trace context
    with trace("pipeline_trace", metadata={"example": "pipeline"}):
        result = pipeline.run(user_input)
        # Print pipeline result as Output within span
        print(f"\033[96mOutput: {result}\033[0m")


if __name__ == '__main__':
    main() 