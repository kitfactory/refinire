#!/usr/bin/env python3
"""
Tests for improved Flow lock management
改善されたFlowロック管理のテスト

This test file verifies that the Flow lock management prevents deadlocks
and handles concurrent execution properly.
このテストファイルは、Flowロック管理がデッドロックを防止し、
並行実行を適切に処理することを検証します。
"""

import asyncio
import sys
import unittest
from unittest.mock import patch
import pytest
import time

from src.refinire.agents.flow.flow import Flow, FlowExecutionError
from src.refinire.agents.flow.context import Context
from src.refinire.agents.flow.step import FunctionStep


class TestFlowLockManagement(unittest.TestCase):
    """Test Flow lock management improvements"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.execution_count = 0
        
    def simple_test_function(self, user_input, context):
        """Simple test function for Flow steps"""
        self.execution_count += 1
        context.result = f"Processed {self.execution_count}: {user_input}"
        return context
        
    async def slow_test_function(self, user_input, context):
        """Slow test function to test concurrency"""
        await asyncio.sleep(0.2)  # Simulate slow operation
        self.execution_count += 1
        context.result = f"Slow processed {self.execution_count}: {user_input}"
        return context
    
    def test_flow_prevent_reentry(self):
        """Test Flow prevents re-entry from same instance"""
        flow = Flow(
            start="test_step",
            steps={
                "test_step": FunctionStep("test_step", self.slow_test_function)
            },
            name="test_flow"
        )
        
        async def test_reentry():
            # Start first execution
            task1 = asyncio.create_task(flow.run("input1"))
            
            # Give first task time to start
            await asyncio.sleep(0.05)
            
            # Try to start second execution immediately (should fail)
            with self.assertRaises(FlowExecutionError) as cm:
                await flow.run("input2")
            
            self.assertIn("already running", str(cm.exception))
            
            # Wait for first execution to complete
            result1 = await task1
            self.assertIsNotNone(result1.result)
            
            # Now second execution should work
            result2 = await flow.run("input2")
            self.assertIsNotNone(result2.result)
        
        asyncio.run(test_reentry())
    
    def test_flow_lock_timeout_protection(self):
        """Test Flow lock acquisition timeout protection"""
        flow = Flow(
            start="test_step",
            steps={
                "test_step": FunctionStep("test_step", self.simple_test_function)
            },
            name="test_flow"
        )
        
        async def test_timeout():
            # Create a proper async mock that never completes
            async def never_complete():
                await asyncio.sleep(60)  # Never completes within test timeout
            
            # Mock the lock to never be acquired
            with patch.object(flow._execution_lock, 'acquire', side_effect=never_complete):
                with self.assertRaises(FlowExecutionError) as cm:
                    await flow.run("test_input")
                
                self.assertIn("failed to acquire execution lock", str(cm.exception))
                self.assertIn("30 seconds", str(cm.exception))
        
        asyncio.run(test_timeout())
    
    def test_flow_proper_lock_release_on_success(self):
        """Test Flow properly releases lock on successful execution"""
        flow = Flow(
            start="test_step",
            steps={
                "test_step": FunctionStep("test_step", self.simple_test_function)
            },
            name="test_flow"
        )
        
        async def test_lock_release():
            # Verify lock is not held initially
            self.assertFalse(flow._execution_lock.locked())
            
            # Execute flow
            result = await flow.run("test_input")
            self.assertIsNotNone(result.result)
            
            # Verify lock is released after execution
            self.assertFalse(flow._execution_lock.locked())
            self.assertFalse(flow._running)
            
            # Should be able to run again
            result2 = await flow.run("test_input2")
            self.assertIsNotNone(result2.result)
            self.assertFalse(flow._execution_lock.locked())
        
        asyncio.run(test_lock_release())
    
    def test_flow_proper_lock_release_on_exception(self):
        """Test Flow properly releases lock when exception occurs"""
        def failing_function(user_input, context):
            raise ValueError("Test exception")
        
        flow = Flow(
            start="test_step",
            steps={
                "test_step": FunctionStep("test_step", failing_function)
            },
            name="test_flow"
        )
        
        async def test_exception_lock_release():
            # Verify lock is not held initially
            self.assertFalse(flow._execution_lock.locked())
            
            # Execute flow (should fail)
            result = await flow.run("test_input")
            
            # Even after exception, lock should be released
            self.assertFalse(flow._execution_lock.locked())
            self.assertFalse(flow._running)
            
            # Should be able to run again
            result2 = await flow.run("test_input2")
            self.assertFalse(flow._execution_lock.locked())
        
        asyncio.run(test_exception_lock_release())
    
    def test_run_loop_prevent_reentry(self):
        """Test run_loop prevents re-entry from same instance"""
        flow = Flow(
            start="test_step",
            steps={
                "test_step": FunctionStep("test_step", self.slow_test_function)
            },
            name="test_flow"
        )
        
        async def test_run_loop_reentry():
            # Start run_loop
            task1 = asyncio.create_task(flow.run_loop())
            
            # Give it a moment to start
            await asyncio.sleep(0.05)
            
            # Try to start another run_loop (should fail)
            with self.assertRaises(FlowExecutionError) as cm:
                await flow.run_loop()
            
            self.assertIn("already running in loop mode", str(cm.exception))
            
            # Cancel the first task
            task1.cancel()
            try:
                await task1
            except asyncio.CancelledError:
                pass
            
            # Give it a moment to clean up
            await asyncio.sleep(0.01)
            
            # Now run_loop should work again
            task2 = asyncio.create_task(flow.run_loop())
            await asyncio.sleep(0.01)  # Let it start
            task2.cancel()
            try:
                await task2
            except asyncio.CancelledError:
                pass
        
        asyncio.run(test_run_loop_reentry())
    
    def test_concurrent_different_flows(self):
        """Test that different Flow instances can run concurrently"""
        flow1 = Flow(
            start="test_step",
            steps={
                "test_step": FunctionStep("test_step", self.simple_test_function)
            },
            name="flow1"
        )
        
        flow2 = Flow(
            start="test_step",
            steps={
                "test_step": FunctionStep("test_step", self.simple_test_function)
            },
            name="flow2"
        )
        
        async def test_different_flows():
            # Both flows should be able to run concurrently
            task1 = asyncio.create_task(flow1.run("input1"))
            task2 = asyncio.create_task(flow2.run("input2"))
            
            # Wait for both to complete
            result1, result2 = await asyncio.gather(task1, task2)
            
            # Both should succeed
            self.assertIsNotNone(result1.result)
            self.assertIsNotNone(result2.result)
            
            # Both locks should be released
            self.assertFalse(flow1._execution_lock.locked())
            self.assertFalse(flow2._execution_lock.locked())
            self.assertFalse(flow1._running)
            self.assertFalse(flow2._running)
        
        asyncio.run(test_different_flows())
    
    def test_flow_reset_clears_running_state(self):
        """Test that Flow.reset() properly clears running state"""
        flow = Flow(
            start="test_step",
            steps={
                "test_step": FunctionStep("test_step", self.simple_test_function)
            },
            name="test_flow"
        )
        
        async def test_reset():
            # Execute flow
            result = await flow.run("test_input")
            self.assertIsNotNone(result.result)
            
            # Reset should clear state
            flow.reset()
            self.assertFalse(flow._running)
            self.assertFalse(flow._execution_lock.locked())
            
            # Should be able to run again
            result2 = await flow.run("test_input2")
            self.assertIsNotNone(result2.result)
        
        asyncio.run(test_reset())


if __name__ == '__main__':
    unittest.main()