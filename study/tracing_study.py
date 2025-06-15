from agents.tracing import TracingProcessor, add_trace_processor, trace
from agents.tracing.span_data import GenerationSpanData, ResponseSpanData
from refinire import get_llm
from agents import Agent, Runner
import openai

def _merge_msgs(msgs, role):  # ユーティリティ
    return "\n".join(m["content"] for m in msgs if m["role"] == role)

class UnifiedLogger(TracingProcessor):
    def on_trace_start(self, trace):
        # Called when a trace is started. No-op implementation.
        # トレースが開始されたときに呼び出されます。No-op実装です。
        pass

    def on_span_start(self, span):
        # Called when a span is started. No-op implementation.
        # スパンが開始されたときに呼び出されます。No-op実装です。
        print(f"on_span_start: {span}")

    def on_trace_end(self, trace):
        # Called when a trace is finished. No-op implementation.
        # トレースが終了したときに呼び出されます。No-op実装です。
        pass

    def shutdown(self):
        # Called when the application stops. No-op implementation.
        # アプリケーションが停止したときに呼び出されます。No-op実装です。
        pass

    def force_flush(self):
        # Forces an immediate flush of all queued spans/traces. No-op implementation.
        # キューに入ったすべてのスパン/トレースを即時フラッシュします。No-op実装です。
        pass

    def on_span_end(self, span):
        print(f"on_span_end: {span}")
        data = span.span_data
        if isinstance(data, GenerationSpanData):
            # For generation spans, extract from input/output arrays
            instr = _merge_msgs(data.input, "system")
            prompt = _merge_msgs(data.input, "user")
            output = _merge_msgs(data.output, "assistant")
        elif isinstance(data, ResponseSpanData) and data.response:
            # For response spans, extract instructions, user prompt, and assistant output
            instr = data.response.instructions or ""
            prompt = _merge_msgs(data.input, "user") if data.input else ""
            # Extract assistant-generated text chunks
            output_texts = []
            for msg in data.response.output:
                for item in getattr(msg, 'content', []):
                    # ResponseOutputText has attribute `text`
                    output_texts.append(getattr(item, 'text', str(item)))
            output = "\n".join(output_texts)
        else:
            return  # Irrelevant span
        # Print extracted tracing info
        print(f"▼Instruction\n{instr}\n▼Prompt\n{prompt}\n▼Output\n{output}\n")

add_trace_processor(UnifiedLogger())

if __name__ == "__main__":
    # Wrap the workflow in a trace context
    with trace("Tracing Study"):
        # # Initialize the LLM model with tracing enabled
        # llm = get_llm("gpt-4o-mini", tracing=True)
        # # Create an Agent wrapping the LLM
        # agent = Agent(
        #     name="Assistant",
        #     instructions="You are a helpful assistant.",
        #     model=llm,
        # )
        # # Run the agent synchronously with a user prompt
        # result = Runner.run_sync(agent, "What is the capital of the moon?")
        # # Print the final output from the agent
        # print(result.final_output)

        llm = get_llm("qwen3:8b")
        # Create an Agent wrapping the LLM
        agent = Agent(
            name="Assistant",
            instructions="You are a helpful assistant.",
            model=llm,
        )
        # Run the agent synchronously with a user prompt
        result = Runner.run_sync(agent, "What is the capital of the moon?")
        print(result.final_output)
