# Streaming Guide - Real-time Response Display

This comprehensive guide covers Refinire's streaming functionality, allowing you to build responsive, real-time AI applications with immediate user feedback.

## Overview

Refinire provides powerful streaming capabilities through both `RefinireAgent` and `Flow`, enabling:
- **Real-time response display** as content is generated
- **Custom chunk processing** via callback functions
- **Context-aware streaming** for conversational applications
- **Flow-level streaming** for complex multi-step workflows
- **Structured output streaming** with JSON chunk delivery

## Table of Contents

1. [Basic RefinireAgent Streaming](#basic-refinireagent-streaming)
2. [Streaming with Callbacks](#streaming-with-callbacks)
3. [Context-Aware Streaming](#context-aware-streaming)
4. [Flow Streaming](#flow-streaming)
5. [Structured Output Streaming](#structured-output-streaming)
6. [Error Handling](#error-handling)
7. [Performance Considerations](#performance-considerations)
8. [Integration Patterns](#integration-patterns)
9. [Best Practices](#best-practices)

## Basic RefinireAgent Streaming

The simplest way to enable streaming is using the `run_streamed()` method:

```python
import asyncio
from refinire import RefinireAgent

async def basic_streaming_example():
    agent = RefinireAgent(
        name="streaming_assistant",
        generation_instructions="Provide detailed, helpful responses",
        model="gpt-4o-mini"
    )
    
    print("User: Explain quantum computing")
    print("Assistant: ", end="", flush=True)
    
    # Stream response chunks as they arrive
    async for chunk in agent.run_streamed("Explain quantum computing"):
        print(chunk, end="", flush=True)
    
    print()  # New line when complete

# Run the example
asyncio.run(basic_streaming_example())
```

### Key Features
- **Immediate response**: Chunks appear as soon as they're generated
- **Non-blocking**: Your application remains responsive
- **Simple integration**: Drop-in replacement for `run()` method

## Streaming with Callbacks

For advanced processing, use callback functions to handle each chunk:

```python
import asyncio
from refinire import RefinireAgent

async def callback_streaming_example():
    agent = RefinireAgent(
        name="callback_agent",
        generation_instructions="Write detailed technical explanations",
        model="gpt-4o-mini"
    )
    
    # Track streaming metrics
    chunks_received = []
    total_characters = 0
    
    def chunk_processor(chunk: str):
        """Process each chunk as it arrives"""
        nonlocal total_characters
        chunks_received.append(chunk)
        total_characters += len(chunk)
        
        # Custom processing examples:
        # - Send to WebSocket clients
        # - Update real-time UI
        # - Save to file/database
        # - Trigger notifications
        
        print(f"[Chunk {len(chunks_received)}]: {len(chunk)} chars")
    
    print("Streaming with callback processing...")
    full_response = ""
    
    async for chunk in agent.run_streamed(
        "Explain machine learning algorithms", 
        callback=chunk_processor
    ):
        full_response += chunk
        print(chunk, end="", flush=True)
    
    print(f"\n\nStreaming complete!")
    print(f"📊 Total chunks: {len(chunks_received)}")
    print(f"📏 Total characters: {total_characters}")
    print(f"💾 Complete response: {len(full_response)} chars")

asyncio.run(callback_streaming_example())
```

### Use Cases for Callbacks
- **WebSocket broadcasting**: Send chunks to multiple clients
- **Real-time UI updates**: Update progress bars, character counts
- **Data persistence**: Save streaming data to databases
- **Analytics**: Track performance metrics and user engagement

## Context-Aware Streaming

Maintain conversation context across streaming interactions:

```python
import asyncio
from refinire import RefinireAgent, Context

async def context_streaming_example():
    agent = RefinireAgent(
        name="context_agent",
        generation_instructions="Continue conversations naturally, referencing previous messages",
        model="gpt-4o-mini"
    )
    
    # Create shared context for the conversation
    ctx = Context()
    
    conversation = [
        "Hello, can you help me learn Python?",
        "What about async/await in Python?", 
        "Can you show me a practical example?",
        "How would I use this in a web application?"
    ]
    
    for i, user_input in enumerate(conversation):
        print(f"\n--- Message {i + 1} ---")
        print(f"User: {user_input}")
        print("Assistant: ", end="", flush=True)
        
        # Add user message to context before streaming
        ctx.add_user_message(user_input)
        
        # Stream response with shared context
        response = ""
        async for chunk in agent.run_streamed(user_input, ctx=ctx):
            response += chunk
            print(chunk, end="", flush=True)
        
        # Context automatically stores the response for future reference
        print()  # New line for readability

asyncio.run(context_streaming_example())
```

### Context Benefits
- **Conversation continuity**: Agent remembers previous exchanges
- **Personalized responses**: Adapt to user preferences and history
- **Session management**: Maintain state across multiple interactions
- **Automatic storage**: Responses are automatically saved to context

## Flow Streaming

Stream complex multi-step workflows:

```python
import asyncio
from refinire import Flow, FunctionStep, RefinireAgent

def analyze_input(user_input, context):
    """Analyze the complexity of the user request"""
    context.shared_state["analysis"] = {
        "complexity": "high" if len(user_input) > 50 else "low",
        "topic": "detected_topic"
    }
    return "Analysis complete"

def format_results(user_input, context):
    """Format the final results"""
    return f"Formatted output based on: {context.result}"

async def flow_streaming_example():
    # Create a flow with streaming-enabled agents
    flow = Flow({
        "analyze": FunctionStep("analyze", analyze_input),
        "generate": RefinireAgent(
            name="content_generator",
            generation_instructions="Generate comprehensive, detailed content based on the analysis",
            model="gpt-4o-mini"
        ),
        "format": FunctionStep("format", format_results)
    })
    
    print("User: Create a comprehensive guide on Python decorators")
    print("Flow Output: ", end="", flush=True)
    
    # Stream the entire flow execution
    async for chunk in flow.run_streamed("Create a comprehensive guide on Python decorators"):
        print(chunk, end="", flush=True)
    
    print("\n\nFlow streaming complete!")

asyncio.run(flow_streaming_example())
```

### Flow Streaming Features
- **Mixed streaming/non-streaming**: Only streaming steps produce chunks
- **Sequential execution**: Steps execute in order with streaming output
- **Context preservation**: Shared state maintained throughout streaming
- **Error propagation**: Streaming errors are handled gracefully

## Structured Output Streaming

**Important**: When using structured output (Pydantic models) with streaming, responses are streamed as **JSON chunks**, not parsed objects:

```python
import asyncio
from pydantic import BaseModel
from refinire import RefinireAgent

class BlogPost(BaseModel):
    title: str
    content: str
    tags: list[str]
    word_count: int

async def structured_streaming_example():
    agent = RefinireAgent(
        name="structured_writer",
        generation_instructions="Generate a well-structured blog post",
        output_model=BlogPost,  # Enable structured output
        model="gpt-4o-mini"
    )
    
    print("Streaming structured output as JSON chunks:")
    print("Raw JSON: ", end="", flush=True)
    
    json_content = ""
    async for json_chunk in agent.run_streamed("Write a blog post about AI ethics"):
        json_content += json_chunk
        print(json_chunk, end="", flush=True)
    
    print(f"\n\nComplete JSON: {json_content}")
    
    # For parsed objects, use regular run() method:
    print("\nParsed object example:")
    result = await agent.run_async("Write a blog post about AI ethics")
    blog_post = result.content  # Returns BlogPost object
    print(f"Title: {blog_post.title}")
    print(f"Tags: {blog_post.tags}")
    print(f"Word count: {blog_post.word_count}")

asyncio.run(structured_streaming_example())
```

### Structured Streaming Behavior
- **JSON chunks**: Structured output streams as raw JSON, not parsed objects
- **Progressive parsing**: You can parse JSON as it becomes complete
- **Mixed usage**: Use streaming for real-time display, regular methods for parsed objects
- **Client-side parsing**: Frontend applications can parse JSON chunks as needed

## Error Handling

Implement robust error handling for streaming scenarios:

```python
import asyncio
from refinire import RefinireAgent

async def error_handling_example():
    agent = RefinireAgent(
        name="error_test_agent",
        generation_instructions="Respond helpfully to user input",
        model="gpt-4o-mini"
    )
    
    test_cases = [
        "",  # Empty input
        "Normal request about Python",
        "A" * 10000,  # Very long input
    ]
    
    for i, test_input in enumerate(test_cases):
        print(f"\n--- Test Case {i + 1}: {len(test_input)} chars ---")
        
        try:
            chunks_received = 0
            async for chunk in agent.run_streamed(test_input):
                chunks_received += 1
                print(chunk, end="", flush=True)
                
                # Simulate processing errors
                if chunks_received > 100:  # Too many chunks
                    print("\n[WARNING] Too many chunks, stopping...")
                    break
            
            print(f"\n✅ Successfully processed {chunks_received} chunks")
            
        except Exception as e:
            print(f"\n❌ Streaming error: {e}")
            # Implement fallback logic here
            print("🔄 Falling back to non-streaming...")
            try:
                result = await agent.run_async(test_input)
                print(f"Fallback result: {result.content[:100]}...")
            except Exception as fallback_error:
                print(f"❌ Fallback also failed: {fallback_error}")

asyncio.run(error_handling_example())
```

### Error Handling Best Practices
- **Graceful degradation**: Fall back to non-streaming when streaming fails
- **Timeout handling**: Set reasonable timeouts for streaming operations
- **Chunk validation**: Validate chunks before processing
- **Resource cleanup**: Properly clean up streaming resources

## Performance Considerations

### Streaming Performance Tips

1. **Buffer Management**:
```python
async def optimized_streaming():
    buffer = []
    buffer_size = 10  # Process every 10 chunks
    
    async for chunk in agent.run_streamed("Long content request"):
        buffer.append(chunk)
        
        if len(buffer) >= buffer_size:
            # Process batch of chunks
            process_chunk_batch(buffer)
            buffer.clear()
    
    # Process remaining chunks
    if buffer:
        process_chunk_batch(buffer)
```

2. **Memory Management**:
```python
async def memory_efficient_streaming():
    total_chars = 0
    max_memory = 10000  # 10KB limit
    
    async for chunk in agent.run_streamed("Generate large content"):
        total_chars += len(chunk)
        
        if total_chars > max_memory:
            print("\n[INFO] Memory limit reached, truncating...")
            break
        
        process_chunk(chunk)
```

3. **Concurrent Streaming**:
```python
async def concurrent_streaming():
    agents = [
        RefinireAgent(name=f"agent_{i}", generation_instructions="Generate content", model="gpt-4o-mini")
        for i in range(3)
    ]
    
    tasks = [
        agent.run_streamed(f"Topic {i}")
        for i, agent in enumerate(agents)
    ]
    
    # Process multiple streams concurrently
    async for chunk_data in asyncio.as_completed(tasks):
        async for chunk in chunk_data:
            print(f"[{time.time()}] {chunk}", end="", flush=True)
```

## Integration Patterns

### WebSocket Integration

```python
import asyncio
import websockets
from refinire import RefinireAgent

async def websocket_streaming_handler(websocket, path):
    agent = RefinireAgent(
        name="websocket_agent",
        generation_instructions="Provide real-time responses",
        model="gpt-4o-mini"
    )
    
    try:
        async for message in websocket:
            # Stream response back to client
            async for chunk in agent.run_streamed(message):
                await websocket.send(chunk)
            
            # Send completion signal
            await websocket.send("[COMPLETE]")
            
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

# Start WebSocket server
start_server = websockets.serve(websocket_streaming_handler, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
```

### FastAPI Integration

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from refinire import RefinireAgent
import json

app = FastAPI()
agent = RefinireAgent(
    name="api_agent",
    generation_instructions="Provide helpful API responses",
    model="gpt-4o-mini"
)

@app.post("/stream")
async def stream_response(request: dict):
    async def generate():
        async for chunk in agent.run_streamed(request["message"]):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        yield f"data: {json.dumps({'complete': True})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/plain")
```

## Best Practices

### 1. **Choose the Right Streaming Method**
- Use `run_streamed()` for real-time user interfaces
- Use callbacks for complex processing pipelines
- Use Flow streaming for multi-step workflows
- Use regular `run()` when streaming isn't needed

### 2. **Handle Network Issues**
- Implement reconnection logic for WebSocket streaming
- Use timeouts to prevent hanging connections
- Buffer chunks for unreliable network conditions

### 3. **Optimize User Experience**
- Show typing indicators during streaming
- Display chunk counts or progress information
- Implement "stop streaming" functionality
- Handle empty or error responses gracefully

### 4. **Resource Management**
- Set memory limits for long-running streams
- Clean up streaming resources properly
- Monitor streaming performance metrics
- Implement rate limiting for high-traffic scenarios

### 5. **Testing Strategies**
- Test with various input sizes and types
- Simulate network interruptions
- Test concurrent streaming scenarios
- Validate chunk integrity and ordering

## Conclusion

Refinire's streaming capabilities enable you to build responsive, real-time AI applications with minimal complexity. Whether you're building chat interfaces, live dashboards, or complex workflow systems, streaming provides the immediate feedback users expect in modern applications.

For more examples, see:
- [`examples/streaming_example.py`](../../examples/streaming_example.py) - Comprehensive streaming examples
- [`examples/flow_streaming_example.py`](../../examples/flow_streaming_example.py) - Flow streaming demonstrations  
- [`tests/test_streaming.py`](../../tests/test_streaming.py) - Complete test suite

**Next Steps**: Explore [Flow Architecture](flow_complete_guide_en.md) to learn how to build complex streaming workflows.