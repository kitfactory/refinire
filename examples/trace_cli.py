#!/usr/bin/env python3
"""
Simple Trace CLI
---
English: A simple command-line interface to run traces and spans with the custom ConsoleTracingProcessor.
日本語: 独自の ConsoleTracingProcessor を使ってトレースとスパンを実行するシンプルなコマンドラインインターフェイスです。
"""

import sys
try:
    # English: Initialize colorama for Windows ANSI support.
    # 日本語: Windows の ANSI サポートのため colorama を初期化します。
    import colorama
    colorama.init()
except ImportError:
    pass

import argparse
from agents.tracing import set_tracing_disabled, set_trace_processors, trace, custom_span
from refinire.core.processor import DialogProcessor


def parse_metadata(items: list[str]) -> dict[str, str]:
    """
    English: Parse metadata items in key=value format into a dictionary.
    日本語: key=value 形式のメタデータアイテムを辞書に変換します。

    Args:
        items (list[str]): List of strings in key=value format.

    Returns:
        dict[str, str]: Parsed metadata dictionary.
    """
    metadata: dict[str, str] = {}
    for item in items:
        if "=" in item:
            key, value = item.split("=", 1)
            metadata[key] = value
    return metadata


def main() -> None:
    """
    English: Entry point for the CLI. Parses arguments and executes trace/span commands.
    日本語: CLI のエントリポイント。引数をパースしてトレース/スパンコマンドを実行します。
    """
    parser = argparse.ArgumentParser(description="Simple Trace CLI")
    parser.add_argument("--trace-name", "-t", required=True, help="Trace name")
    parser.add_argument("--span-name", "-s", help="Span name (optional)")
    parser.add_argument("--disable-trace", action="store_true", help="Disable tracing")
    parser.add_argument("--metadata", "-m", nargs="*", default=[], help="Metadata key=value pairs")
    args = parser.parse_args()

    # Initialize custom tracing processor using DialogProcessor
    processor = DialogProcessor()
    set_tracing_disabled(args.disable_trace)
    set_trace_processors([processor])

    metadata = parse_metadata(args.metadata)
    if args.span_name:
        with trace(args.trace_name, metadata=metadata):
            with custom_span(args.span_name, data={}):
                pass
    else:
        with trace(args.trace_name, metadata=metadata):
            pass


if __name__ == '__main__':
    main() 
