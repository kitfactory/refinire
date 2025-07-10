# Refinire Tracing Specifications
# Refinireトレーシング仕様書

This document outlines the complete tracing behavior specifications for Refinire platform.

このドキュメントは、Refinireプラットフォームの完全なトレーシング動作仕様を説明します。

## 🚀 Default Behavior / デフォルト動作

### Automatic Console Tracing / 自動コンソールトレーシング
- **Console tracing is ENABLED by default** when importing refinire
- **ConsoleTracingProcessor automatically registered** during module import
- **Enhanced color-coded output with trace/span IDs**: 
  - Instruction: `\033[93m` (Yellow / 黄色) + `[trace:XXXXXXXX span:YYYYYYYY]`
  - Prompt: `\033[94m` (Blue / 青色) + `[trace:XXXXXXXX span:YYYYYYYY]`
  - Output: `\033[92m` (Green / 緑色) + `[trace:XXXXXXXX span:YYYYYYYY]`
- **Compact ID format**: Last 8 characters of trace_id and span_id for readability
- **No active trace context initially** (`get_current_trace()` returns `None`)

### Implementation Details / 実装詳細
```python
# In src/refinire/core/tracing.py line 141:
enable_console_tracing()  # Called automatically on import
```

## 🤖 RefinireAgent Behavior / RefinireAgentの動作

### WITHOUT `with trace()` Context / `with trace()`コンテキストなし

```python
agent = RefinireAgent(name="test", instructions="...", model="gpt-4o-mini")
context = Context()
result = agent.run("Hello", context)
```

**Behavior / 動作:**
- ✅ Agent executes normally with API calls
- ✅ Console shows colored Instruction/Prompt/Output
- ✅ No shared trace context
- ✅ Independent execution tracking

### WITH `with trace()` Context / `with trace()`コンテキストあり

```python
with trace("agent_test"):
    agent = RefinireAgent(name="test", instructions="...", model="gpt-4o-mini")
    context = Context()
    result = agent.run("Hello", context)
```

**Behavior / 動作:**
- ✅ Agent executes within trace context
- ✅ Console shows colored Instruction/Prompt/Output
- ✅ Participates in unified trace tracking
- ✅ Shares trace context with other components

## 🌊 Flow Behavior / Flowの動作

### WITHOUT `with trace()` Context / `with trace()`コンテキストなし

```python
flow = Flow(name="TestFlow", start="step1", steps={"step1": step})
result = await flow.run("input")
```

**Behavior / 動作:**
- ✅ Generates unique `trace_id`: `{flow_name}_{YYYYMMDD_HHMMSS_microseconds}`
- ✅ Context inherits Flow's `trace_id`
- ✅ Independent trace lifecycle
- ✅ Example: `testflow_20250710_103344_714008`

### WITH `with trace()` Context / `with trace()`コンテキストあり ⭐ **NEW**

```python
with trace("unified_workflow"):
    flow1 = Flow(name="Flow1", start="step1", steps={"step1": step1})
    flow2 = Flow(name="Flow2", start="step2", steps={"step2": step2})
    
    result1 = await flow1.run("input1")
    result2 = await flow2.run("input2")
```

**Behavior / 動作:**
- ✅ **Uses trace context's `trace_id`** (NEW BEHAVIOR)
- ✅ **Multiple Flows share same `trace_id`**
- ✅ **Unified observability across entire workflow**
- ✅ Example: All flows use `trace_c8799b3aedb144608be2153219d0fba6`

## 🎛️ Control Functions / 制御関数

### `enable_console_tracing()`
- Enables `ConsoleTracingProcessor`
- Calls `set_tracing_disabled(False)`
- Registers colored console output processor

### `disable_tracing()`
- Disables all tracing output
- Calls `set_tracing_disabled(True)`
- No console output, clean execution

### `with trace(name)`
- Creates trace context with unique `trace_id`
- Format: `trace_{32_character_hex}`
- All components within context share this `trace_id`

## 🔍 Trace ID Formats / トレースID形式

### Flow Default Format / Flowデフォルト形式
```
{flow_name_lowercase}_{YYYYMMDD_HHMMSS_microseconds}

Examples:
- testflow_20250710_103344_714008
- dataprocessing_20250710_103500_123456
```

### Trace Context Format / トレースコンテキスト形式
```
trace_{32_character_hexadecimal}

Examples:
- trace_c8799b3aedb144608be2153219d0fba6
- trace_3abac18250834d6589163e1648116d80
```

## 🔧 Implementation Details / 実装詳細

### Flow Trace ID Generation / FlowトレースID生成
Location: `src/refinire/agents/flow/flow.py:317-351`

```python
def _generate_trace_id(self) -> str:
    try:
        from agents.tracing import get_current_trace
        current_trace = get_current_trace()
        if current_trace and current_trace.trace_id:
            # Use trace context's trace_id
            return current_trace.trace_id
    except Exception:
        pass
    
    # Fall back to default format
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    if self.name:
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" 
                           for c in self.name.lower())
        return f"{safe_name}_{timestamp}"
    else:
        return f"flow_{timestamp}"
```

### Console Tracing Processor / コンソールトレーシングプロセッサ
Location: `src/refinire/core/tracing.py:49-119`

```python
class ConsoleTracingProcessor(TracingProcessor):
    def on_span_end(self, span):
        # Get trace ID and span ID for enhanced observability
        trace_id = getattr(span, 'trace_id', 'unknown')
        span_id = getattr(span, 'span_id', 'unknown')
        
        # Truncate IDs for better readability (show last 8 characters)
        trace_short = trace_id[-8:] if trace_id != 'unknown' else 'unknown'
        span_short = span_id[-8:] if span_id != 'unknown' else 'unknown'
        id_info = f"[trace:{trace_short} span:{span_short}]"
        
        # Enhanced colored output with ID information
        if instr:
            self.output_stream.write(f"\033[93mInstruction: {id_info} {instr}\033[0m\n")
        if prompt:
            self.output_stream.write(f"\033[94mPrompt: {id_info} {prompt}\033[0m\n")
        if output:
            self.output_stream.write(f"\033[92mOutput: {id_info} {output}\033[0m\n")
```

## 🎨 Enhanced Console Output / 強化されたコンソール出力

### Output Format Comparison / 出力形式比較

**BEFORE Enhancement / 強化前:**
```
Instruction: You are a helpful assistant.
Prompt: Say hello
Output: Hello from AI!
```

**AFTER Enhancement / 強化後:**
```
Instruction: [trace:fba86a73 span:a18e1fa6] You are a helpful assistant.
Prompt: [trace:fba86a73 span:a18e1fa6] Say hello
Output: [trace:fba86a73 span:a18e1fa6] Hello from AI!
```

### Benefits of Enhanced Output / 強化された出力の利点

- ✅ **Easy span correlation** within the same trace / 同一トレース内でのspan相関の簡素化
- ✅ **Enhanced debugging capabilities** with unique identifiers / 一意識別子による強化されたデバッグ機能
- ✅ **Clear identification** of related operations / 関連する操作の明確な識別
- ✅ **Compact format** using last 8 characters for readability / 可読性のための末尾8文字のコンパクト形式

### Trace/Span ID Examples / Trace/Span ID例

```
Full IDs:
- trace_id: trace_bf1cd607979044db8b57ca38fba86a73
- span_id:  span_a18e1fa6b0c3437d803fa1bd

Short format in console:
- [trace:fba86a73 span:a18e1fa6]
```

## 💡 Key Insights / 重要なポイント

### ✅ Unified Tracing / 統一トレーシング
- **Flow trace_id generation respects active trace context**
- **Multiple Flows in same `trace()` share unified trace_id**
- **Enables end-to-end workflow observability**

### ✅ Default Observability / デフォルトオブザーバビリティ
- **Console tracing enabled by default for immediate feedback**
- **Color-coded output for easy identification**
- **No configuration required for basic tracing**

### ✅ Flexible Control / 柔軟な制御
- **`disable_tracing()` provides clean output when needed**
- **`with trace()` enables workflow-level tracking**
- **Backward compatible with existing code**

## 📊 Test Results Summary / テスト結果概要

All core functionality verified:
- ✅ Default Configuration
- ✅ Flow Trace ID Behavior (with/without trace context)
- ✅ RefinireAgent Basic Functionality
- ✅ Flow Execution Behavior
- ✅ Tracing Control Functions

## 🎯 Usage Recommendations / 使用推奨

### For Simple Scripts / シンプルなスクリプト用
```python
from refinire import disable_tracing
disable_tracing()  # Clean output
```

### For Development & Debugging / 開発・デバッグ用
```python
# Default behavior - colored console output
from refinire import RefinireAgent
# Console tracing automatically enabled
```

### For Complex Workflows / 複雑なワークフロー用
```python
from refinire import Flow
from agents.tracing import trace

with trace("workflow_name"):
    # All flows share unified trace_id
    flow1 = Flow(...)
    flow2 = Flow(...)
    # Unified observability
```

---

**Document Version**: 1.1  
**Last Updated**: 2025-01-10  
**Tested Version**: Refinire 0.2.11  
**Latest Enhancement**: Console output now includes trace/span IDs for enhanced observability