"""
Console tracing utilities for agents_sdk_models.

English: Provides ConsoleTracingProcessor for color-coded output of span data and utility functions to enable/disable tracing.
日本語: Spanデータの色分け出力を行う ConsoleTracingProcessor とトレーシングの有効化/無効化ユーティリティを提供します。
"""
from agents.tracing import TracingProcessor, set_trace_processors
from agents.tracing.span_data import GenerationSpanData, ResponseSpanData
from agents import set_tracing_disabled
from .message import get_message, DEFAULT_LANGUAGE  # Import for localized trace labels
import sys


def _merge_msgs(msgs, role):
    """
    English: Merge message contents by role from a list of message dicts.
    日本語: メッセージのリストから指定したroleに一致するcontentを結合します。
    """
    return "\n".join(m.get("content", "") for m in (msgs or []) if m.get("role") == role)


def extract_output_texts(obj):
    """
    English: Recursively extract all text contents from output message objects or dicts.
    日本語: 出力メッセージのオブジェクトや辞書からtextフィールドを再帰的に抽出します。
    """
    results = []
    if isinstance(obj, list):
        for item in obj:
            results.extend(extract_output_texts(item))
    elif isinstance(obj, dict):
        if "content" in obj and isinstance(obj["content"], list):
            results.extend(extract_output_texts(obj["content"]))
        elif "text" in obj and isinstance(obj["text"], str):
            results.append(obj["text"])
        elif "content" in obj and isinstance(obj["content"], str):
            results.append(obj["content"])
    else:
        content = getattr(obj, "content", None)
        if isinstance(content, list):
            results.extend(extract_output_texts(content))
        elif hasattr(obj, "text") and isinstance(obj.text, str):
            results.append(obj.text)
        elif isinstance(content, str):
            results.append(content)
    return results


class ConsoleTracingProcessor(TracingProcessor):
    """
    English: A tracing processor that outputs Instruction, Prompt, and Output with colors to the console.
    日本語: Instruction、Prompt、Outputを色分けしてコンソールに出力するトレーシングプロセッサ。
    """
    def __init__(self, output_stream=sys.stdout):
        # English: Initialize with an output stream for logs.
        # 日本語: ログ出力用の出力ストリームで初期化します。
        self.output_stream = output_stream

    def on_trace_start(self, trace):
        # No-op for trace start
        pass

    def on_trace_end(self, trace):
        # No-op for trace end
        pass

    def on_span_start(self, span):
        # No-op for span start
        pass

    def on_span_end(self, span):
        # Called at the end of each span; outputs color-coded Instruction/Prompt/Output and logs span end
        if span is None:
            return
        data = span.span_data
        instr = ""
        prompt = ""
        output = ""
        if isinstance(data, GenerationSpanData):
            instr = _merge_msgs(data.input, "system")
            prompt = _merge_msgs(data.input, "user")
            output = "\n".join(extract_output_texts(data.output))
        elif isinstance(data, ResponseSpanData) and getattr(data, 'response', None):
            instr = data.response.instructions or ""
            prompt = _merge_msgs(data.input, "user")
            output = "\n".join(extract_output_texts(data.response.output))
        else:
            # Irrelevant span type
            return
        
        # Get trace ID and span ID for enhanced observability
        # オブザーバビリティ向上のためtrace IDとspan IDを取得
        trace_id = getattr(span, 'trace_id', 'unknown')
        span_id = getattr(span, 'span_id', 'unknown')
        
        # Truncate IDs for better readability (show last 8 characters)
        # 可読性向上のためIDを短縮（末尾8文字を表示）
        trace_short = trace_id[-8:] if trace_id != 'unknown' else 'unknown'
        span_short = span_id[-8:] if span_id != 'unknown' else 'unknown'
        id_info = f"[trace:{trace_short} span:{span_short}]"
        
        # Color-coded output with localized labels and ID information
        # ローカライズされたラベルとID情報付きの色分け出力
        if self.output_stream is None:
            return
        if instr:
            instr_label = get_message("trace_instruction", DEFAULT_LANGUAGE)
            self.output_stream.write(f"\033[93m{instr_label} {id_info} {instr}\033[0m\n")
        if prompt:
            prompt_label = get_message("trace_prompt", DEFAULT_LANGUAGE)
            self.output_stream.write(f"\033[94m{prompt_label} {id_info} {prompt}\033[0m\n")
        if output:
            output_label = get_message("trace_output", DEFAULT_LANGUAGE)
            self.output_stream.write(f"\033[92m{output_label} {id_info} {output}\033[0m\n")
        self.output_stream.flush()
        # # Log span end marker with error info
        # info = span.export() or {}
        # span_data = info.get('span_data') or span.span_data.export()
        # name = span_data.get('name') if isinstance(span_data, dict) else None
        # error = info.get('error', None)
        # self.output_stream.write(f"[SPAN END] name={name}, error={error}\n")
        # self.output_stream.flush()

    def shutdown(self):
        # No-op for shutdown
        pass

    def force_flush(self):
        # Forces flush of the output stream
        if hasattr(self, 'output_stream') and self.output_stream is not None:
            self.output_stream.flush()


def enable_console_tracing():
    """
    English: Enable console tracing by registering ConsoleTracingProcessor and enabling tracing.
    日本語: ConsoleTracingProcessorを登録してトレーシングを有効化します。
    """
    # Enable tracing in Agents SDK
    set_tracing_disabled(False)
    # Register console tracing processor
    set_trace_processors([ConsoleTracingProcessor()])


def disable_tracing():
    """
    English: Disable all tracing.
    日本語: トレーシング機能をすべて無効化します。
    """
    set_tracing_disabled(True)


# Automatically enable console tracing when this module is imported
enable_console_tracing() 
