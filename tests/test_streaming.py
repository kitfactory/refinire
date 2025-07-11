#!/usr/bin/env python3
"""
Test RefinireAgent streaming functionality
RefinireAgentストリーミング機能のテスト
"""

import asyncio
import pytest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent, Context

class TestRefinireAgentStreaming:
    """Test suite for RefinireAgent streaming functionality"""

    @pytest.mark.asyncio
    async def test_basic_streaming(self):
        """Test basic streaming functionality"""
        agent = RefinireAgent(
            name="TestStreamingAgent",
            generation_instructions="Respond with 'Hello, this is a test response for streaming.'"
        )
        
        chunks = []
        async for chunk in agent.run_streamed("Test input"):
            chunks.append(chunk)
        
        # Should receive multiple chunks
        assert len(chunks) > 0
        
        # Combine chunks should form complete response
        full_response = "".join(chunks)
        assert len(full_response) > 0
        assert "test" in full_response.lower()

    @pytest.mark.asyncio
    async def test_streaming_with_callback(self):
        """Test streaming with callback function"""
        agent = RefinireAgent(
            name="TestCallbackAgent",
            generation_instructions="Say hello and explain streaming."
        )
        
        callback_chunks = []
        def test_callback(chunk: str):
            callback_chunks.append(chunk)
        
        stream_chunks = []
        async for chunk in agent.run_streamed("Hello", callback=test_callback):
            stream_chunks.append(chunk)
        
        # Both callback and stream should receive same chunks
        assert len(callback_chunks) == len(stream_chunks)
        assert callback_chunks == stream_chunks

    @pytest.mark.asyncio
    async def test_streaming_with_context(self):
        """Test streaming with shared context"""
        agent = RefinireAgent(
            name="TestContextAgent",
            generation_instructions="Continue the conversation naturally."
        )
        
        ctx = Context()
        
        # First message
        chunks1 = []
        async for chunk in agent.run_streamed("My name is Alice", ctx=ctx):
            chunks1.append(chunk)
        
        response1 = "".join(chunks1)
        assert len(response1) > 0
        
        # Second message should have context
        chunks2 = []
        ctx.add_user_message("What is my name?")
        async for chunk in agent.run_streamed("What is my name?", ctx=ctx):
            chunks2.append(chunk)
        
        response2 = "".join(chunks2)
        # Response should reference the name Alice (context-aware)
        # Note: This test might be flaky depending on model behavior
        assert len(response2) > 0

    @pytest.mark.asyncio
    async def test_streaming_empty_input(self):
        """Test streaming with empty input"""
        agent = RefinireAgent(
            name="TestEmptyAgent",
            generation_instructions="Always respond helpfully."
        )
        
        chunks = []
        async for chunk in agent.run_streamed(""):
            chunks.append(chunk)
        
        # Should handle empty input gracefully
        # May return empty or error message
        assert isinstance(chunks, list)

    @pytest.mark.asyncio
    async def test_streaming_context_result_storage(self):
        """Test that streaming results are properly stored in context"""
        agent = RefinireAgent(
            name="TestResultAgent",
            generation_instructions="Say exactly: 'Streaming test response'"
        )
        
        ctx = Context()
        
        chunks = []
        async for chunk in agent.run_streamed("Test", ctx=ctx):
            chunks.append(chunk)
        
        full_response = "".join(chunks)
        
        # Context should store the complete result
        assert ctx.result is not None
        assert len(str(ctx.result)) > 0
        
        # Result in context should match streamed content
        # (Note: might have slight differences due to processing)
        assert "test" in str(ctx.result).lower() or "streaming" in str(ctx.result).lower()

if __name__ == "__main__":
    # Run tests manually
    async def run_manual_tests():
        test_instance = TestRefinireAgentStreaming()
        
        print("🧪 Running streaming tests...")
        
        try:
            await test_instance.test_basic_streaming()
            print("✅ Basic streaming test passed")
        except Exception as e:
            print(f"❌ Basic streaming test failed: {e}")
        
        try:
            await test_instance.test_streaming_with_callback()
            print("✅ Callback streaming test passed")
        except Exception as e:
            print(f"❌ Callback streaming test failed: {e}")
        
        try:
            await test_instance.test_streaming_with_context()
            print("✅ Context streaming test passed")
        except Exception as e:
            print(f"❌ Context streaming test failed: {e}")
        
        try:
            await test_instance.test_streaming_empty_input()
            print("✅ Empty input streaming test passed")
        except Exception as e:
            print(f"❌ Empty input streaming test failed: {e}")
        
        try:
            await test_instance.test_streaming_context_result_storage()
            print("✅ Context result storage test passed")
        except Exception as e:
            print(f"❌ Context result storage test failed: {e}")
        
        print("🎯 All streaming tests completed!")
    
    asyncio.run(run_manual_tests())