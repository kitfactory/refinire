```python
from agents.tracing import TracingProcessor, add_trace_processor, set_tracing_disabled
from agents.tracing.span_data import GenerationSpanData

class StdoutTracer(TracingProcessor):
    # ---- trace レベル ----
    def on_trace_start(self, trace): ...
    def on_trace_end(self, trace): ...
    # ---- span レベル ----
    def on_span_start(self, span): ...
    def on_span_end(self, span):
        data = span.span_data
        if isinstance(data, GenerationSpanData):
            # messages は list[dict(role, content)]
            sys_msg   = next((m["content"] for m in data.input if m["role"]=="system"), "")
            user_msg  = next((m["content"] for m in data.input if m["role"]=="user"), "")
            assistant = "\n".join(m["content"] for m in data.output or [])
            print("\n=== Instruction ===\n", sys_msg)
            print("=== Prompt ===\n", user_msg)
            print("=== Output ===\n", assistant, "\n")

    def shutdown(self): ...            # 必要なら flush
    def force_flush(self): ...

# OpenAI へのエクスポートを無効化する場合
set_tracing_disabled(True)             # あるいは set_trace_processors([StdoutTracer()])

# Processor を登録
add_trace_processor(StdoutTracer())

# あとは普通に Agent を実行
# result = await Runner.run(agent, "こんにちは")

```
