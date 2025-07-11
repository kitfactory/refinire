#!/usr/bin/env python3
"""
Streaming + Structured Output Test
ストリーミング + 構造化出力テスト

This test explores what happens when you combine streaming output 
with structured output (Pydantic models).
ストリーミング出力と構造化出力（Pydanticモデル）を組み合わせると
何が起こるかを調査するテストです。
"""

import asyncio
import sys
import os
from typing import List

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent
from pydantic import BaseModel, Field

class TaskResponse(BaseModel):
    """Structured response model for task analysis"""
    title: str = Field(description="Task title")
    steps: List[str] = Field(description="List of steps to complete the task")
    estimated_time: str = Field(description="Estimated time to complete")
    difficulty: str = Field(description="Difficulty level: easy, medium, hard")

class PersonInfo(BaseModel):
    """Simple person information model"""
    name: str = Field(description="Person's name")
    age: int = Field(description="Person's age")
    occupation: str = Field(description="Person's occupation")

async def test_streaming_with_structured_output():
    """
    Test streaming with Pydantic structured output
    Pydantic構造化出力でのストリーミングテスト
    """
    print("🧪 Testing Streaming + Structured Output")
    print("=" * 50)
    
    # Create agent with structured output
    agent = RefinireAgent(
        name="StructuredStreamingAgent",
        generation_instructions="""
        Analyze the given task and provide a structured response with:
        - A clear title
        - Step-by-step breakdown
        - Estimated time
        - Difficulty level
        """,
        output_model=TaskResponse,
        model="gpt-4o-mini"
    )
    
    user_input = "How to bake a chocolate cake"
    
    print(f"User: {user_input}")
    print("Agent (Streaming): ", end="", flush=True)
    
    try:
        chunks = []
        async for chunk in agent.run_streamed(user_input):
            print(chunk, end="", flush=True)
            chunks.append(chunk)
        
        print(f"\n\n📊 Streaming Results:")
        print(f"- Received {len(chunks)} chunks")
        print(f"- Total content: {len(''.join(chunks))} characters")
        print(f"- Raw content: {''.join(chunks)}")
        
        # Now test non-streaming for comparison
        print("\n" + "="*50)
        print("Agent (Non-streaming): ")
        
        ctx = agent.run("How to bake a chocolate cake")
        print(f"Structured result: {ctx.result}")
        print(f"Result type: {type(ctx.result)}")
        
        if hasattr(ctx.result, 'title'):
            print(f"- Title: {ctx.result.title}")
            print(f"- Steps: {ctx.result.steps}")
            print(f"- Time: {ctx.result.estimated_time}")
            print(f"- Difficulty: {ctx.result.difficulty}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_simple_structured_streaming():
    """
    Test with simpler structured output
    よりシンプルな構造化出力でのテスト
    """
    print("\n🧪 Testing Simple Structured Streaming")
    print("=" * 50)
    
    agent = RefinireAgent(
        name="SimpleStructuredAgent",
        generation_instructions="Extract person information from the text.",
        output_model=PersonInfo,
        model="gpt-4o-mini"
    )
    
    user_input = "Alice is a 30-year-old software engineer"
    
    print(f"User: {user_input}")
    print("Agent (Streaming): ", end="", flush=True)
    
    try:
        chunks = []
        async for chunk in agent.run_streamed(user_input):
            print(chunk, end="", flush=True)
            chunks.append(chunk)
        
        print(f"\n\n📊 Simple Streaming Results:")
        print(f"- Received {len(chunks)} chunks")
        print(f"- Raw content: {''.join(chunks)}")
        
        # Non-streaming comparison
        print("\nAgent (Non-streaming): ")
        ctx = agent.run(user_input)
        print(f"Structured result: {ctx.result}")
        print(f"Result type: {type(ctx.result)}")
        
    except Exception as e:
        print(f"\n❌ Simple test failed: {e}")
        import traceback
        traceback.print_exc()

async def test_no_structured_streaming():
    """
    Test streaming without structured output for comparison
    比較用の構造化出力なしストリーミングテスト
    """
    print("\n🧪 Testing Streaming Without Structured Output")
    print("=" * 50)
    
    agent = RefinireAgent(
        name="PlainStreamingAgent",
        generation_instructions="Explain how to bake a chocolate cake step by step.",
        # No output_model - plain text output
        model="gpt-4o-mini"
    )
    
    user_input = "How to bake a chocolate cake"
    
    print(f"User: {user_input}")
    print("Agent (Plain Streaming): ", end="", flush=True)
    
    try:
        chunks = []
        async for chunk in agent.run_streamed(user_input):
            print(chunk, end="", flush=True)
            chunks.append(chunk)
        
        print(f"\n\n📊 Plain Streaming Results:")
        print(f"- Received {len(chunks)} chunks")
        print(f"- Total content: {len(''.join(chunks))} characters")
        
    except Exception as e:
        print(f"\n❌ Plain test failed: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all tests to understand streaming + structured output behavior"""
    print("🔬 Investigating Streaming + Structured Output Behavior")
    print("=" * 60)
    
    try:
        await test_no_structured_streaming()
        await test_simple_structured_streaming()  
        await test_streaming_with_structured_output()
        
        print("\n" + "="*60)
        print("📝 Summary:")
        print("This test helps understand how streaming interacts with")
        print("Pydantic structured output models in RefinireAgent.")
        print("Check the output above to see the behavior patterns.")
        
    except Exception as e:
        print(f"❌ Tests failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())