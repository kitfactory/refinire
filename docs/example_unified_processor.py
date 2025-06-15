from agents.tracing import TracingProcessor, add_trace_processor
from agents.tracing.span_data import GenerationSpanData, ResponseSpanData

def _merge_msgs(msgs, role):  # ユーティリティ
    return "\n".join(m["content"] for m in msgs if m["role"] == role)

class UnifiedLogger(TracingProcessor):
    def on_span_end(self, span):
        data = span.span_data
        if isinstance(data, GenerationSpanData):
            instr  = _merge_msgs(data.input,  "system")
            prompt = _merge_msgs(data.input,  "user")
            output = _merge_msgs(data.output, "assistant")
        elif isinstance(data, ResponseSpanData) and data.response:
            instr  = (data.input or {}).get("instructions", "")
            prompt = (data.input or {}).get("prompt", "")
            output = data.response.choices[0].message.content
        else:
            return  # 関係ない span
        print(f"▼Instruction\n{instr}\n▼Prompt\n{prompt}\n▼Output\n{output}\n")

add_trace_processor(UnifiedLogger())

from refinire import get_llm

if __name__ == "__main__":
    llm = get_llm("gpt-4o-mini")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of the moon?"},
    ]
    result = llm.invoke(messages)
    print(result)

