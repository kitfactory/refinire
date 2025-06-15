import pytest
import asyncio
from refinire import Flow, FunctionStep, ParallelStep, Context


class TestDAGParallelProcessing:
    """Test DAG parallel processing functionality"""
    
    @pytest.mark.asyncio
    async def test_basic_parallel_step(self):
        """Test basic parallel step execution"""
        
        def step_a(input_data, ctx):
            ctx.shared_state["step_a_result"] = "Result A"
            return ctx
        
        def step_b(input_data, ctx):
            ctx.shared_state["step_b_result"] = "Result B"
            return ctx
        
        def step_c(input_data, ctx):
            ctx.shared_state["step_c_result"] = "Result C"
            return ctx
        
        # Create parallel steps
        parallel_steps = [
            FunctionStep("step_a", step_a),
            FunctionStep("step_b", step_b),
            FunctionStep("step_c", step_c)
        ]
        
        parallel_step = ParallelStep("parallel_test", parallel_steps)
        
        # Execute parallel step
        ctx = Context()
        result_ctx = await parallel_step.run("test_input", ctx)
        
        # Verify all results are present
        assert "step_a_result" in result_ctx.shared_state
        assert "step_b_result" in result_ctx.shared_state 
        assert "step_c_result" in result_ctx.shared_state
        assert result_ctx.shared_state["step_a_result"] == "Result A"
        assert result_ctx.shared_state["step_b_result"] == "Result B"
        assert result_ctx.shared_state["step_c_result"] == "Result C"
    
    @pytest.mark.asyncio
    async def test_dag_parallel_flow_definition(self):
        """Test DAG structure with parallel definition"""
        
        def preprocess(input_data, ctx):
            ctx.shared_state["preprocessed"] = f"Preprocessed: {input_data}"
            return ctx
        
        def analyze_sentiment(input_data, ctx):
            data = ctx.shared_state.get("preprocessed", input_data)
            ctx.shared_state["sentiment"] = f"Positive sentiment for: {data}"
            return ctx
        
        def extract_keywords(input_data, ctx):
            data = ctx.shared_state.get("preprocessed", input_data)
            ctx.shared_state["keywords"] = f"Keywords from: {data}"
            return ctx
        
        def classify_category(input_data, ctx):
            data = ctx.shared_state.get("preprocessed", input_data)
            ctx.shared_state["category"] = f"Category of: {data}"
            return ctx
        
        def aggregate_results(input_data, ctx):
            sentiment = ctx.shared_state.get("sentiment", "")
            keywords = ctx.shared_state.get("keywords", "")
            category = ctx.shared_state.get("category", "")
            
            ctx.shared_state["final_result"] = f"Final: {sentiment}, {keywords}, {category}"
            ctx.finish()
            return ctx
        
        # Create flow with DAG parallel structure
        flow_def = {
            "preprocess": FunctionStep("preprocess", preprocess),
            "parallel_analysis": {
                "parallel": [
                    FunctionStep("sentiment", analyze_sentiment),
                    FunctionStep("keywords", extract_keywords),
                    FunctionStep("category", classify_category)
                ],
                "next_step": "aggregate"
            },
            "aggregate": FunctionStep("aggregate", aggregate_results)
        }
        
        # Manually set next steps for sequential flow
        flow_def["preprocess"].next_step = "parallel_analysis"
        
        flow = Flow(start="preprocess", steps=flow_def)
        
        # Execute flow
        result = await flow.run("test data")
        
        # Verify all parallel processing completed
        assert "preprocessed" in result.shared_state
        assert "sentiment" in result.shared_state
        assert "keywords" in result.shared_state
        assert "category" in result.shared_state
        assert "final_result" in result.shared_state
        assert "Preprocessed: test data" in result.shared_state["final_result"]
    
    @pytest.mark.asyncio
    async def test_parallel_step_error_handling(self):
        """Test error handling in parallel steps"""
        
        def working_step(input_data, ctx):
            ctx.shared_state["working_result"] = "Success"
            return ctx
        
        def failing_step(input_data, ctx):
            raise ValueError("Test error")
        
        parallel_steps = [
            FunctionStep("working", working_step),
            FunctionStep("failing", failing_step)
        ]
        
        parallel_step = ParallelStep("test_parallel", parallel_steps)
        
        ctx = Context()
        
        # Should handle errors gracefully and record them
        result_ctx = await parallel_step.run("test", ctx)
        
        # Working step should complete successfully
        assert "working_result" in result_ctx.shared_state
        assert result_ctx.shared_state["working_result"] == "Success"
        
        # Failed step should have error recorded in messages
        assert "__failing_metadata__" in result_ctx.shared_state
        failing_meta = result_ctx.shared_state["__failing_metadata__"]
        assert failing_meta["status"] == "completed"
        assert len(failing_meta["messages"]) > 0
        error_message = failing_meta["messages"][0].content
        assert "error" in error_message.lower()
        assert "Test error" in error_message
    
    @pytest.mark.asyncio
    async def test_parallel_step_context_isolation(self):
        """Test that parallel steps have isolated contexts"""
        
        def step_modify_shared(input_data, ctx):
            # Each step modifies the same key differently
            ctx.shared_state["shared_key"] = f"Modified by {input_data}"
            return ctx
        
        parallel_steps = [
            FunctionStep("step1", lambda input_data, ctx: step_modify_shared("step1", ctx)),
            FunctionStep("step2", lambda input_data, ctx: step_modify_shared("step2", ctx)),
            FunctionStep("step3", lambda input_data, ctx: step_modify_shared("step3", ctx))
        ]
        
        parallel_step = ParallelStep("isolation_test", parallel_steps)
        
        ctx = Context()
        result_ctx = await parallel_step.run("test", ctx)
        
        # Should have step-specific results due to conflict resolution
        assert "shared_key" in result_ctx.shared_state or any(
            key.endswith("_shared_key") for key in result_ctx.shared_state.keys()
        )
        
        # Each step should have metadata stored
        assert "__step1_metadata__" in result_ctx.shared_state
        assert "__step2_metadata__" in result_ctx.shared_state
        assert "__step3_metadata__" in result_ctx.shared_state
        
        # Conflicting keys should be renamed
        assert "shared_key" in result_ctx.shared_state  # First one keeps original name
        assert "step2_shared_key" in result_ctx.shared_state  # Conflicts get prefixed
        assert "step3_shared_key" in result_ctx.shared_state
    
    @pytest.mark.asyncio
    async def test_dag_flow_with_max_workers(self):
        """Test parallel processing with max workers configuration"""
        
        def slow_step(input_data, ctx):
            # Simulate some processing time
            import time
            time.sleep(0.01)  # Small delay to test concurrency
            ctx.shared_state[f"result_{input_data}"] = f"Processed {input_data}"
            return ctx
        
        # Create many parallel steps
        parallel_steps = [
            FunctionStep(f"step_{i}", lambda input_data, ctx, i=i: slow_step(f"step_{i}", ctx))
            for i in range(10)
        ]
        
        # Test with limited workers
        flow_def = {
            "parallel_processing": {
                "parallel": parallel_steps,
                "max_workers": 3
            }
        }
        
        flow = Flow(start="parallel_processing", steps=flow_def)
        result = await flow.run("test")
        
        # Verify all steps completed - check metadata instead
        for i in range(10):
            assert f"__step_{i}_metadata__" in result.shared_state
            # Or check the actual results in shared_state
            assert f"result_step_{i}" in result.shared_state
    
    def test_dag_structure_validation(self):
        """Test validation of DAG structure definitions"""
        
        # Test invalid parallel definition (not a list)
        with pytest.raises(ValueError, match="must be a list of steps"):
            Flow(start="invalid", steps={
                "invalid": {
                    "parallel": "not_a_list"
                }
            })
        
        # Test invalid parallel step (not Step instances)
        with pytest.raises(ValueError, match="must be a Step instance"):
            Flow(start="invalid", steps={
                "invalid": {
                    "parallel": ["not_a_step"]
                }
            })
        
        # Test valid parallel definition
        valid_steps = [
            FunctionStep("step1", lambda input_data, ctx: ctx),
            FunctionStep("step2", lambda input_data, ctx: ctx)
        ]
        
        flow = Flow(start="valid", steps={
            "valid": {
                "parallel": valid_steps
            }
        })
        
        assert isinstance(flow.steps["valid"], ParallelStep)
        assert len(flow.steps["valid"].parallel_steps) == 2
    
    @pytest.mark.asyncio
    async def test_complex_dag_with_multiple_parallel_sections(self):
        """Test complex DAG with multiple parallel processing sections"""
        
        def init_step(input_data, ctx):
            ctx.shared_state["initialized"] = input_data
            return ctx
        
        def first_parallel_a(input_data, ctx):
            ctx.shared_state["first_a"] = "First A"
            return ctx
        
        def first_parallel_b(input_data, ctx):
            ctx.shared_state["first_b"] = "First B"
            return ctx
        
        def middle_step(input_data, ctx):
            ctx.shared_state["middle"] = "Middle processing"
            return ctx
        
        def second_parallel_x(input_data, ctx):
            ctx.shared_state["second_x"] = "Second X"
            return ctx
        
        def second_parallel_y(input_data, ctx):
            ctx.shared_state["second_y"] = "Second Y"
            return ctx
        
        def final_step(input_data, ctx):
            ctx.shared_state["final"] = "Final result"
            ctx.finish()
            return ctx
        
        # Complex DAG structure
        flow_def = {
            "init": FunctionStep("init", init_step),
            "first_parallel": {
                "parallel": [
                    FunctionStep("first_a", first_parallel_a),
                    FunctionStep("first_b", first_parallel_b)
                ],
                "next_step": "middle"
            },
            "middle": FunctionStep("middle", middle_step),
            "second_parallel": {
                "parallel": [
                    FunctionStep("second_x", second_parallel_x),
                    FunctionStep("second_y", second_parallel_y)
                ],
                "next_step": "final"
            },
            "final": FunctionStep("final", final_step)
        }
        
        # Set up sequential connections
        flow_def["init"].next_step = "first_parallel"
        flow_def["middle"].next_step = "second_parallel"
        
        flow = Flow(start="init", steps=flow_def)
        result = await flow.run("complex test")
        
        # Verify all steps executed
        assert result.shared_state["initialized"] == "complex test"
        assert result.shared_state["first_a"] == "First A"
        assert result.shared_state["first_b"] == "First B"
        assert result.shared_state["middle"] == "Middle processing"
        assert result.shared_state["second_x"] == "Second X"
        assert result.shared_state["second_y"] == "Second Y"
        assert result.shared_state["final"] == "Final result"
        assert result.finished 