import io
from agents.tracing import set_tracing_disabled, set_trace_processors, trace, custom_span
from refinire.core.tracing import ConsoleTracingProcessor
import pytest
from refinire import get_llm

# English: Test integration of set_tracing_disabled and custom tracing processor.
# 日本語: set_tracing_disabledと独自TracingProcessorを組み合わせた統合動作をテストします。
def test_integration_with_custom_processor():
    stream = io.StringIO()
    processor = ConsoleTracingProcessor(output_stream=stream)
    # Enable tracing and replace processors with our custom one
    set_tracing_disabled(False)
    set_trace_processors([processor])

    # Run a trace with a custom span
    with trace("wf2", metadata={"m": 1}):
        with custom_span("spanA", data={"foo": "bar"}):
            pass

    # ConsoleTracingProcessor no-ops on trace/span start/end for custom spans
    output = stream.getvalue()
    assert output == ""

# English: Test that disabling tracing suppresses logs.
# 日本語: set_tracing_disabled(True)でログが出力されないことをテストします。
def test_tracing_disabled_suppresses_logs():
    stream = io.StringIO()
    processor = ConsoleTracingProcessor(output_stream=stream)
    set_trace_processors([processor])
    set_tracing_disabled(True)

    with trace("wf3"):  # default disabled=False, but global disabled=True overrides
        with custom_span("spanB", data=None):
            pass

    # No logs should be emitted
    assert stream.getvalue() == ""

def test_get_llm_tracing_disabled():
    """
    English: Ensure get_llm completes without error when tracing is disabled.
    日本語: tracing=False でエラーが発生しないことを確認します。
    """
    model = get_llm(tracing=False)
    assert model is not None


def test_get_llm_tracing_enabled():
    """
    English: Ensure get_llm completes without error when tracing is enabled.
    日本語: tracing=True でエラーが発生しないことを確認します。
    """
    model = get_llm(tracing=True)
    assert model is not None 
