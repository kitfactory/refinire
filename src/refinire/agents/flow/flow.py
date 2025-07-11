from __future__ import annotations

"""Flow — Workflow orchestration engine for Step-based workflows.

Flowはステップベースワークフロー用のワークフローオーケストレーションエンジンです。
同期・非同期両方のインターフェースを提供し、CLI、GUI、チャットボット対応します。
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime
import traceback

from .context import Context
from .step import Step, ParallelStep
from ...core.trace_registry import get_global_registry, TraceRegistry


logger = logging.getLogger(__name__)


class FlowExecutionError(Exception):
    """
    Exception raised during flow execution
    フロー実行中に発生する例外
    """
    pass


class Flow:
    """
    Flow orchestration engine for Step-based workflows
    ステップベースワークフロー用フローオーケストレーションエンジン
    
    This class provides:
    このクラスは以下を提供します：
    - Declarative step-based workflow definition / 宣言的ステップベースワークフロー定義
    - Synchronous and asynchronous execution modes / 同期・非同期実行モード
    - User input coordination for interactive workflows / 対話的ワークフロー用ユーザー入力調整
    - Error handling and observability / エラーハンドリングとオブザーバビリティ
    """
    
    def __init__(
        self, 
        start: Optional[str] = None, 
        steps: Optional[Union[Dict[str, Step], List[Step], Step]] = None, 
        context: Optional[Context] = None,
        max_steps: int = 1000,
        trace_id: Optional[str] = None,
        name: Optional[str] = None
    ):
        """
        Initialize Flow with flexible step definitions
        柔軟なステップ定義でFlowを初期化
        
        This constructor now supports three ways to define steps:
        このコンストラクタは3つの方法でステップを定義できます：
        1. Traditional: start step name + Dict[str, Step]
        2. Sequential: List[Step] (creates sequential workflow)
        3. Single: Single Step (creates single-step workflow)
        
        Args:
            start: Start step label (optional for List/Single mode) / 開始ステップラベル（List/Singleモードでは省略可）
            steps: Step definitions - Dict[str, Step], List[Step], or Step / ステップ定義 - Dict[str, Step]、List[Step]、またはStep
            context: Initial context (optional) / 初期コンテキスト（オプション）
            max_steps: Maximum number of steps to prevent infinite loops / 無限ループ防止のための最大ステップ数
            trace_id: Trace ID for observability / オブザーバビリティ用トレースID
            name: Flow name for identification / 識別用フロー名
        """
        # Handle flexible step definitions
        # 柔軟なステップ定義を処理
        if isinstance(steps, dict):
            # Traditional mode: Dict[str, Step] with parallel support
            # 従来モード: 並列サポート付きDict[str, Step]
            if start is None:
                raise ValueError("start parameter is required when steps is a dictionary")
            self.start = start
            self.steps = self._process_dag_structure(steps)
        elif isinstance(steps, list):
            # Sequential mode: List[Step] 
            # シーケンシャルモード: List[Step]
            if not steps:
                raise ValueError("Steps list cannot be empty")
            
            # Validate that all items are Step instances, not other types like RefinireAgent
            # すべてのアイテムがStepインスタンスであり、RefinireAgentなどの他の型でないことを検証
            self.steps = {}
            prev_step_name = None
            
            for i, step in enumerate(steps):
                # Check if it's a common mistake: RefinireAgent instead of proper Step
                # 一般的な間違いをチェック: 適切なStepではなくRefinireAgent
                if hasattr(step, 'generation_instructions') and hasattr(step, 'evaluation_instructions'):
                    raise ValueError(
                        f"Step at index {i} appears to be a RefinireAgent, not a proper Step. "
                        f"RefinireAgent should not be used directly in Flow step lists. "
                        f"To use agents in Flow, wrap them in FunctionStep or create proper Step instances. "
                        f"Example: FunctionStep('agent_step', lambda u, c: your_agent.run_async(u, c))"
                    )
                
                if not isinstance(step, Step):
                    raise ValueError(
                        f"Step at index {i} must be a Step instance, got {type(step)}. "
                        f"Use FunctionStep, ConditionStep, or other Step subclasses."
                    )
                
                if not hasattr(step, 'name'):
                    raise ValueError(f"Step at index {i} must have a 'name' attribute")
                
                step_name = step.name
                self.steps[step_name] = step
                
                # Set sequential flow: each step goes to next step
                # シーケンシャルフロー設定: 各ステップが次のステップに進む
                if prev_step_name is not None and hasattr(self.steps[prev_step_name], 'next_step'):
                    if self.steps[prev_step_name].next_step is None:
                        self.steps[prev_step_name].next_step = step_name
                
                prev_step_name = step_name
            
            # Start with first step
            # 最初のステップから開始
            self.start = steps[0].name
            
        elif steps is not None:
            # Check if it's a Step instance
            # Stepインスタンスかどうかをチェック
            if isinstance(steps, Step):
                # Single step mode: Step
                # 単一ステップモード: Step
                if not hasattr(steps, 'name'):
                    raise ValueError("Step must have a 'name' attribute")
                
                step_name = steps.name
                self.start = step_name
                self.steps = {step_name: steps}
            else:
                # Not a valid type
                # 有効なタイプではない
                raise ValueError("steps must be Dict[str, Step], List[Step], or Step")
        else:
            raise ValueError("steps parameter cannot be None")
        
        self.context = context or Context()
        self.max_steps = max_steps
        self.name = name
        self.trace_id = trace_id or self._generate_trace_id()
        
        # Initialize context
        # コンテキストを初期化
        self.context.trace_id = self.trace_id
        self.context.next_label = self.start
        
        # Execution state
        # 実行状態
        self._running = False
        self._run_loop_task: Optional[asyncio.Task] = None
        self._execution_lock = asyncio.Lock()
        
        # Hooks for observability
        # オブザーバビリティ用フック
        self.before_step_hooks: List[Callable[[str, Context], None]] = []
        self.after_step_hooks: List[Callable[[str, Context, Any], None]] = []
        self.error_hooks: List[Callable[[str, Context, Exception], None]] = []
        
        # Register trace in global registry
        # グローバルレジストリにトレースを登録
        self._register_trace()
    
    def _process_dag_structure(self, steps_def: Dict[str, Any]) -> Dict[str, Step]:
        """
        Process DAG structure and convert parallel definitions to ParallelStep
        DAG構造を処理し、並列定義をParallelStepに変換
        
        Args:
            steps_def: Step definitions which may contain parallel structures
                      並列構造を含む可能性があるステップ定義
                      
        Returns:
            Dict[str, Step]: Processed step definitions with ParallelStep instances
                           ParallelStepインスタンスを含む処理済みステップ定義
        """
        processed_steps = {}
        
        for step_name, step_def in steps_def.items():
            if isinstance(step_def, dict) and "parallel" in step_def:
                # Handle parallel step definition
                # 並列ステップ定義を処理
                parallel_steps = step_def["parallel"]
                if not isinstance(parallel_steps, list):
                    raise ValueError(f"'parallel' value must be a list of steps for step '{step_name}'")
                
                # Validate all parallel steps are Step instances
                # 全並列ステップがStepインスタンスであることを検証
                for i, parallel_step in enumerate(parallel_steps):
                    if not isinstance(parallel_step, Step):
                        raise ValueError(f"Parallel step {i} in '{step_name}' must be a Step instance")
                
                # Get next step from definition
                # 定義から次ステップを取得
                next_step = step_def.get("next_step")
                max_workers = step_def.get("max_workers")
                
                # Create ParallelStep
                # ParallelStepを作成
                parallel_step_instance = ParallelStep(
                    name=step_name,
                    parallel_steps=parallel_steps,
                    next_step=next_step,
                    max_workers=max_workers
                )
                
                processed_steps[step_name] = parallel_step_instance
                
            elif isinstance(step_def, Step):
                # Regular step
                # 通常ステップ
                processed_steps[step_name] = step_def
            else:
                raise ValueError(f"Invalid step definition for '{step_name}': {type(step_def)}")
        
        return processed_steps
    
    def _register_trace(self) -> None:
        """
        Register trace in global registry
        グローバルレジストリにトレースを登録
        """
        try:
            registry = get_global_registry()
            registry.register_trace(
                trace_id=self.trace_id,
                flow_name=self.name,
                flow_id=self.flow_id,
                agent_names=self._extract_agent_names(),
                tags={"flow_type": "default"}
            )
        except Exception as e:
            logger.warning(f"Failed to register trace: {e}")
    
    def _extract_agent_names(self) -> List[str]:
        """
        Extract agent names from steps
        ステップからエージェント名を抽出
        
        Returns:
            List[str]: List of agent names / エージェント名のリスト
        """
        agent_names = []
        for step in self.steps.values():
            # Check for AgentPipelineStep
            # AgentPipelineStepをチェック
            if hasattr(step, 'pipeline'):
                # Try to get agent name from pipeline
                # パイプラインからエージェント名を取得しようとする
                if hasattr(step.pipeline, 'name'):
                    agent_names.append(step.pipeline.name)
                elif hasattr(step.pipeline, 'agent') and hasattr(step.pipeline.agent, 'name'):
                    agent_names.append(step.pipeline.agent.name)
                else:
                    # Use step name as agent name
                    # ステップ名をエージェント名として使用
                    agent_names.append(f"Pipeline_{step.name}")
            
            # Check for direct agent reference
            # 直接のエージェント参照をチェック
            elif hasattr(step, 'agent'):
                if hasattr(step.agent, 'name'):
                    agent_names.append(step.agent.name)
                else:
                    agent_names.append(f"Agent_{step.name}")
            
            # Check for agent-like step names
            # エージェントライクなステップ名をチェック
            elif hasattr(step, 'name') and any(keyword in step.name.lower() for keyword in ['agent', 'ai', 'llm', 'bot']):
                agent_names.append(step.name)
            
            # Check for function steps that might be agent-related
            # エージェント関連の可能性がある関数ステップをチェック
            elif hasattr(step, 'function') and hasattr(step.function, '__name__'):
                func_name = step.function.__name__
                if any(keyword in func_name.lower() for keyword in ['agent', 'ai', 'llm', 'generate', 'analyze', 'process']):
                    agent_names.append(f"Function_{func_name}")
        
        return list(set(agent_names))  # Remove duplicates
    
    def _update_trace_on_completion(self) -> None:
        """
        Update trace registry when flow completes
        フロー完了時にトレースレジストリを更新
        """
        try:
            registry = get_global_registry()
            trace_summary = self.context.get_trace_summary()
            
            registry.update_trace(
                trace_id=self.trace_id,
                status="completed",
                total_spans=trace_summary.get("total_spans", 0),
                error_count=trace_summary.get("error_spans", 0),
                artifacts=dict(self.context.artifacts),
                add_agent_names=self._extract_agent_names()
            )
        except Exception as e:
            logger.warning(f"Failed to update trace on completion: {e}")
    
    def _update_trace_on_error(self, step_name: str, error: Exception) -> None:
        """
        Update trace registry when flow encounters error
        フローがエラーに遭遇した時にトレースレジストリを更新
        
        Args:
            step_name: Name of the failed step / 失敗したステップ名
            error: The error that occurred / 発生したエラー
        """
        try:
            registry = get_global_registry()
            trace_summary = self.context.get_trace_summary()
            
            registry.update_trace(
                trace_id=self.trace_id,
                status="error",
                total_spans=trace_summary.get("total_spans", 0),
                error_count=trace_summary.get("error_spans", 0),
                artifacts=dict(self.context.artifacts),
                add_tags={
                    "error_step": step_name,
                    "error_type": type(error).__name__,
                    "error_message": str(error)
                }
            )
        except Exception as e:
            logger.warning(f"Failed to update trace on error: {e}")
    
    def _generate_trace_id(self) -> str:
        """
        Generate a unique trace ID based on flow name and timestamp
        フロー名とタイムスタンプに基づいてユニークなトレースIDを生成
        
        This method creates a trace ID independently without relying on external tracing systems.
        If agents.tracing is available and has an active trace context, it will attempt to use that,
        but will gracefully fall back to generating its own trace ID.
        このメソッドは外部トレーシングシステムに依存せずに独立してtrace IDを生成します。
        agents.tracingが利用可能でアクティブなトレースコンテキストがある場合はそれを使用しようとしますが、
        適切に自身のtrace ID生成にフォールバックします。
        
        Returns:
            str: Generated trace ID / 生成されたトレースID
        """
        # Optionally check if we're inside an active trace context
        # オプションとしてアクティブなトレースコンテキスト内にいるかチェック
        try:
            from agents.tracing import get_current_trace
            current_trace = get_current_trace()
            if current_trace and hasattr(current_trace, 'trace_id') and current_trace.trace_id:
                # Use the trace ID from the active trace context
                # アクティブなトレースコンテキストからtrace IDを使用
                logger.debug(f"Using trace ID from active trace context: {current_trace.trace_id}")
                return current_trace.trace_id
        except ImportError:
            # agents.tracing is not available - this is expected and normal
            # agents.tracingが利用できません - これは予期された正常な状況です
            logger.debug("agents.tracing not available, generating independent trace ID")
        except Exception as e:
            # If there's any issue with trace detection, fall back to default behavior
            # トレース検出で問題がある場合は、デフォルトの動作にフォールバック
            logger.debug(f"Unable to get current trace context ({e}), generating independent trace ID")
        
        # Generate independent trace ID with enhanced uniqueness
        # 強化されたユニーク性で独立したtrace IDを生成
        import uuid
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        random_suffix = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID for additional uniqueness
        
        if self.name:
            # Use flow name in trace ID for easier identification
            # 識別しやすくするためにフロー名をトレースIDに含める
            safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in self.name.lower())
            trace_id = f"{safe_name}_{timestamp}_{random_suffix}"
        else:
            trace_id = f"flow_{timestamp}_{random_suffix}"
        
        logger.debug(f"Generated independent trace ID: {trace_id}")
        return trace_id
    
    @property
    def finished(self) -> bool:
        """
        Check if flow is finished
        フローが完了しているかチェック
        
        Returns:
            bool: True if finished / 完了している場合True
        """
        return self.context.is_finished()
    
    @property
    def current_step_name(self) -> Optional[str]:
        """
        Get current step name
        現在のステップ名を取得
        
        Returns:
            str | None: Current step name / 現在のステップ名
        """
        return self.context.current_step
    
    @property
    def next_step_name(self) -> Optional[str]:
        """
        Get next step name
        次のステップ名を取得
        
        Returns:
            str | None: Next step name / 次のステップ名
        """
        return self.context.next_label
    
    @property
    def flow_id(self) -> str:
        """
        Get flow identifier (trace_id)
        フロー識別子（trace_id）を取得
        
        Returns:
            str: Flow identifier / フロー識別子
        """
        return self.trace_id
    
    @property
    def flow_name(self) -> Optional[str]:
        """
        Get flow name
        フロー名を取得
        
        Returns:
            str | None: Flow name / フロー名
        """
        return self.name
    
    async def run(self, input_data: Optional[str] = None, initial_input: Optional[str] = None) -> Context:
        """
        Run flow to completion without user input coordination
        ユーザー入力調整なしでフローを完了まで実行
        
        This is for non-interactive workflows that don't require user input.
        これはユーザー入力が不要な非対話的ワークフロー用です。
        
        Args:
            input_data: Input data to the flow (preferred parameter name) / フローへの入力データ（推奨パラメータ名）
            initial_input: Initial input to the flow (deprecated, use input_data) / フローへの初期入力（非推奨、input_dataを使用）
            
        Returns:
            Context: Final context / 最終コンテキスト
            
        Raises:
            FlowExecutionError: If execution fails / 実行失敗時
        """
        # Try to create trace context if agents.tracing is available
        # agents.tracingが利用可能な場合はトレースコンテキストを作成を試行
        try:
            from agents.tracing import trace
            
            # Create trace context for this flow execution
            # このフロー実行用のトレースコンテキストを作成
            trace_name = f"Flow({self.name or 'unnamed'})"
            with trace(trace_name):
                return await self._run_with_span(input_data, initial_input, None)
        except ImportError:
            # agents.tracing is not available - run without trace context
            # agents.tracingが利用できません - トレースコンテキストなしで実行
            logger.debug("agents.tracing not available, running without trace context")
            return await self._run_with_span(input_data, initial_input, None)
        except Exception as e:
            # If there's any issue with trace creation, fall back to no trace
            # トレース作成で問題がある場合は、トレースなしにフォールバック
            logger.debug(f"Unable to create trace context ({e}), running without trace context")
            return await self._run_with_span(input_data, initial_input, None)
    
    async def run_streamed(self, input_data: Optional[str] = None, callback: Optional[Callable[[str], None]] = None):
        """
        Run flow with streaming output for steps that support it
        ストリーミング出力をサポートするステップでフローを実行
        
        Args:
            input_data: Input data to the flow / フローへの入力データ
            callback: Optional callback function for streaming chunks / ストリーミングチャンク用オプションコールバック関数
            
        Yields:
            str: Streaming content chunks from supported steps / サポートされたステップからのストリーミングコンテンツチャンク
        """
        try:
            from agents.tracing import trace
            
            # Create trace context for this flow execution
            # このフロー実行用のトレースコンテキストを作成
            trace_name = f"Flow({self.name or 'unnamed'})"
            with trace(trace_name):
                async for chunk in self._run_streamed_with_span(input_data, callback):
                    yield chunk
        except ImportError:
            # agents.tracing is not available - run without trace context
            # agents.tracingが利用できません - トレースコンテキストなしで実行
            logger.debug("agents.tracing not available, running without trace context")
            async for chunk in self._run_streamed_with_span(input_data, callback):
                yield chunk
        except Exception as e:
            # If there's any issue with trace creation, fall back to no trace
            # トレース作成で問題がある場合は、トレースなしにフォールバック
            logger.debug(f"Unable to create trace context ({e}), running without trace context")
            async for chunk in self._run_streamed_with_span(input_data, callback):
                yield chunk
    
    async def _run_streamed_with_span(self, input_data: Optional[str] = None, callback: Optional[Callable[[str], None]] = None):
        """
        Internal streaming execution method for Flow
        Flow用内部ストリーミング実行メソッド
        """
        try:
            # Initialize context and input
            # コンテキストと入力を初期化
            effective_input = input_data or ""
            if effective_input:
                self.context.add_user_message(effective_input)
            
            current_step_name = self.start
            execution_count = 0
            
            while current_step_name and execution_count < self.max_steps:
                execution_count += 1
                
                if current_step_name not in self.steps:
                    error_msg = f"Step '{current_step_name}' not found in flow"
                    logger.error(error_msg)
                    yield f"Error: {error_msg}"
                    break
                
                current_step = self.steps[current_step_name]
                
                # Check if step supports streaming (is RefinireAgent with run_streamed)
                # ステップがストリーミングをサポートしているかチェック（run_streamedを持つRefinireAgent）
                if hasattr(current_step, 'run_streamed'):
                    logger.debug(f"Executing streaming step: {current_step_name}")
                    
                    step_has_output = False
                    async for chunk in current_step.run_streamed(effective_input, ctx=self.context, callback=callback):
                        step_has_output = True
                        yield chunk
                    
                    # If no output, yield step completion message
                    # 出力がない場合、ステップ完了メッセージをyield
                    if not step_has_output:
                        completion_msg = f"[Step {current_step_name} completed]"
                        if callback:
                            callback(completion_msg)
                        yield completion_msg
                
                else:
                    # For non-streaming steps, execute normally and yield result
                    # 非ストリーミングステップの場合、通常実行して結果をyield
                    logger.debug(f"Executing non-streaming step: {current_step_name}")
                    
                    try:
                        if hasattr(current_step, 'run_async'):
                            result = await current_step.run_async(effective_input, self.context)
                        elif hasattr(current_step, 'run'):
                            result = current_step.run(effective_input, self.context)
                        else:
                            error_msg = f"Step '{current_step_name}' has no run method"
                            logger.error(error_msg)
                            yield f"Error: {error_msg}"
                            break
                        
                        # Yield step result
                        # ステップ結果をyield
                        if hasattr(result, 'result') and result.result:
                            step_output = str(result.result)
                            if callback:
                                callback(step_output)
                            yield step_output
                        else:
                            completion_msg = f"[Step {current_step_name} completed]"
                            if callback:
                                callback(completion_msg)
                            yield completion_msg
                        
                        # Update context
                        # コンテキストを更新
                        self.context = result
                        
                    except Exception as e:
                        error_msg = f"Step '{current_step_name}' failed: {str(e)}"
                        logger.error(error_msg)
                        yield f"Error: {error_msg}"
                        break
                
                # Determine next step
                # 次のステップを決定
                if hasattr(current_step, 'next_step') and current_step.next_step:
                    current_step_name = current_step.next_step
                else:
                    # No next step defined, flow ends
                    # 次のステップが定義されていない、フロー終了
                    break
                
                # Clear input for subsequent steps
                # 後続ステップのために入力をクリア
                effective_input = ""
            
            # Flow completed
            # フロー完了
            if execution_count >= self.max_steps:
                warning_msg = f"Flow reached maximum steps ({self.max_steps})"
                logger.warning(warning_msg)
                yield f"Warning: {warning_msg}"
            
        except Exception as e:
            error_msg = f"Flow streaming execution failed: {str(e)}"
            logger.error(error_msg)
            yield f"Error: {error_msg}"
    
    def _create_flow_span(self):
        """
        Create a custom span for the entire flow execution
        フロー実行全体用のカスタムスパンを作成
        
        This method attempts to create a tracing span if agents.tracing is available,
        but gracefully handles the case when it's not available.
        agents.tracingが利用可能な場合はトレーシングスパンの作成を試行しますが、
        利用できない場合は適切に処理します。
        
        Returns:
            span object if tracing is available, None otherwise
            トレーシングが利用可能な場合はspanオブジェクト、そうでなければNone
        """
        try:
            # Attempt to import and use agents.tracing if available
            # agents.tracingが利用可能な場合はインポートして使用を試行
            from agents.tracing import custom_span
            
            span_name = f"Flow({self.name or 'unnamed'})"
            span = custom_span(
                name=span_name,
                data={
                    "flow.name": self.name or "unnamed",
                    "flow.id": self.flow_id,
                    "flow.start_step": self.start,
                    "flow.max_steps": self.max_steps,
                    "flow.step_count": len(self.steps),
                    "flow.step_names": list(self.steps.keys())
                }
            )
            logger.debug(f"Created flow span: {span_name}")
            return span
        except ImportError:
            # agents.tracing is not available - this is expected and normal
            # agents.tracingが利用できません - これは予期された正常な状況です
            logger.debug("agents.tracing not available, proceeding without flow span")
            return None
        except Exception as e:
            # Handle any other tracing-related errors gracefully
            # その他のトレーシング関連エラーを適切に処理
            logger.warning(f"Failed to create flow span due to error: {e}")
            return None
    
    async def _run_with_span(self, input_data: Optional[str], initial_input: Optional[str], span) -> Context:
        """
        Run flow with span tracking and improved lock management
        スパントラッキングと改善されたロック管理でフローを実行
        """
        # Add input to span
        effective_input = input_data or initial_input
        if span is not None and effective_input:
            span.span_data.data["flow_input"] = effective_input
        
        # Prevent re-entry from same flow instance
        # 同一フローインスタンスからの再入を防止
        if self._running:
            raise FlowExecutionError(f"Flow {self.name} is already running. Concurrent execution not allowed.")
        
        # Acquire lock with timeout to prevent deadlock
        # デッドロック防止のためタイムアウト付きでロックを取得
        try:
            # Use asyncio.wait_for to add timeout to lock acquisition
            # asyncio.wait_forを使用してロック取得にタイムアウトを追加
            await asyncio.wait_for(self._execution_lock.acquire(), timeout=30.0)
        except asyncio.TimeoutError:
            raise FlowExecutionError(f"Flow {self.name} failed to acquire execution lock within 30 seconds. Possible deadlock detected.")
        
        try:
            self._running = True
            logger.debug(f"Flow {self.name} acquired execution lock, starting execution")
            
            # Reset context for new execution
            # 新しい実行用にコンテキストをリセット
            if self.context.step_count > 0:
                self.context = Context(trace_id=self.trace_id)
                self.context.next_label = self.start
            
            # Determine input to use (input_data takes precedence)
            # 使用する入力を決定（input_dataが優先）
            effective_input = input_data or initial_input
            
            # Add input if provided
            # 入力が提供されている場合は追加
            if effective_input:
                self.context.add_user_message(effective_input)
            
            current_input = effective_input
            step_count = 0
            
            while not self.finished and step_count < self.max_steps:
                step_name = self.context.next_label
                if not step_name or step_name not in self.steps:
                    self.context.finish()  # Finish flow when no next step or unknown step
                    break
                
                step = self.steps[step_name]
                
                # Execute step
                # ステップを実行
                try:
                    await self._execute_step(step, current_input)
                    current_input = None  # Only use initial input for first step
                    step_count += 1
                    
                    # If step is waiting for user input, break
                    # ステップがユーザー入力を待機している場合、中断
                    if self.context.awaiting_user_input:
                        break
                        
                except Exception as e:
                    logger.error(f"Error executing step {step_name}: {e}")
                    self._handle_step_error(step_name, e)
                    break
            
            # Check for infinite loop
            # 無限ループのチェック
            if step_count >= self.max_steps:
                raise FlowExecutionError(f"Flow exceeded maximum steps ({self.max_steps})")
            
            # Finalize any remaining span when flow completes
            # フロー完了時に残りのスパンを終了
            self.context.finalize_flow_span()
            
            # Update flow span with execution results
            if span is not None:
                span.span_data.data["flow_completed"] = True
                span.span_data.data["final_step_count"] = step_count
                span.span_data.data["flow_finished"] = self.finished
                span.span_data.data["awaiting_user_input"] = self.context.awaiting_user_input
                if hasattr(self.context, 'result') and self.context.result is not None:
                    span.span_data.data["flow_result"] = str(self.context.result)[:500]  # Truncate long results
            
            # Update trace registry
            # トレースレジストリを更新
            self._update_trace_on_completion()
            
            return self.context
            
        except Exception as e:
            # Update span with error information
            if span is not None:
                span.span_data.data["flow_error"] = str(e)
                span.span_data.data["flow_completed"] = False
            raise
            
        finally:
            # Ensure proper cleanup regardless of how execution ends
            # 実行の終了方法に関係なく適切なクリーンアップを保証
            self._running = False
            logger.debug(f"Flow {self.name} releasing execution lock")
            
            # Release the lock explicitly
            # ロックを明示的に解放
            if self._execution_lock.locked():
                self._execution_lock.release()
    
    async def run_loop(self) -> None:
        """
        Run flow as background task with user input coordination
        ユーザー入力調整を含むバックグラウンドタスクとしてフローを実行
        
        This method runs the flow continuously, pausing when user input is needed.
        このメソッドはフローを継続的に実行し、ユーザー入力が必要な時に一時停止します。
        Use feed() to provide user input when the flow is waiting.
        フローが待機している時はfeed()を使用してユーザー入力を提供してください。
        """
        # Prevent re-entry from same flow instance
        # 同一フローインスタンスからの再入を防止
        if self._running:
            raise FlowExecutionError(f"Flow {self.name} is already running in loop mode. Concurrent execution not allowed.")
        
        # Acquire lock with timeout to prevent deadlock
        # デッドロック防止のためタイムアウト付きでロックを取得
        try:
            await asyncio.wait_for(self._execution_lock.acquire(), timeout=30.0)
        except asyncio.TimeoutError:
            raise FlowExecutionError(f"Flow {self.name} failed to acquire execution lock for run_loop within 30 seconds. Possible deadlock detected.")
        
        try:
            self._running = True
            logger.debug(f"Flow {self.name} acquired execution lock for run_loop, starting execution")
            
            # Reset context for new execution
            # 新しい実行用にコンテキストをリセット
            if self.context.step_count > 0:
                self.context = Context(trace_id=self.trace_id)
                self.context.next_label = self.start
            
            step_count = 0
            current_input = None
            
            while not self.finished and step_count < self.max_steps:
                step_name = self.context.next_label
                if not step_name or step_name not in self.steps:
                    self.context.finish()  # Finish flow when no next step or unknown step
                    break
                
                step = self.steps[step_name]
                
                # Execute step
                # ステップを実行
                try:
                    await self._execute_step(step, current_input)
                    current_input = None
                    step_count += 1
                    
                    # If step is waiting for user input, wait for feed()
                    # ステップがユーザー入力を待機している場合、feed()を待つ
                    if self.context.awaiting_user_input:
                        await self.context.wait_for_user_input()
                        # After receiving input, continue with the same step
                        # 入力受信後、同じステップで継続
                        current_input = self.context.last_user_input
                        continue
                        
                except Exception as e:
                    logger.error(f"Error executing step {step_name}: {e}")
                    self._handle_step_error(step_name, e)
                    break
            
            # Check for infinite loop
            # 無限ループのチェック
            if step_count >= self.max_steps:
                raise FlowExecutionError(f"Flow exceeded maximum steps ({self.max_steps})")
            
            # Finalize any remaining span when flow completes
            # フロー完了時に残りのスパンを終了
            self.context.finalize_flow_span()
            
            # Update trace registry
            # トレースレジストリを更新
            self._update_trace_on_completion()
            
        finally:
            # Ensure proper cleanup regardless of how execution ends
            # 実行の終了方法に関係なく適切なクリーンアップを保証
            self._running = False
            logger.debug(f"Flow {self.name} releasing execution lock from run_loop")
            
            # Release the lock explicitly
            # ロックを明示的に解放
            if self._execution_lock.locked():
                self._execution_lock.release()
    
    def next_prompt(self) -> Optional[str]:
        """
        Get next prompt for synchronous CLI usage
        同期CLI使用用の次のプロンプトを取得
        
        Returns:
            str | None: Prompt if waiting for user input / ユーザー入力待ちの場合のプロンプト
        """
        return self.context.clear_prompt()
    
    def feed(self, user_input: str) -> None:
        """
        Provide user input to the flow
        フローにユーザー入力を提供
        
        Args:
            user_input: User input text / ユーザー入力テキスト
        """
        self.context.provide_user_input(user_input)
    
    def step(self) -> None:
        """
        Execute one step synchronously
        1ステップを同期的に実行
        
        This method executes one step and returns immediately.
        このメソッドは1ステップを実行してすぐに返ります。
        Use for synchronous CLI applications.
        同期CLIアプリケーション用に使用してください。
        """
        if self.finished:
            return
        
        step_name = self.context.next_label
        if not step_name or step_name not in self.steps:
            self.context.finish()
            return
        
        step = self.steps[step_name]
        
        # Run step in event loop
        # イベントループでステップを実行
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, create a task
                # ループが実行中の場合、タスクを作成
                task = asyncio.create_task(self._execute_step(step, None))
                # This is a synchronous method, so we can't await
                # これは同期メソッドなので、awaitできない
                # The task will run in the background
                # タスクはバックグラウンドで実行される
            else:
                # If no loop is running, run until complete
                # ループが実行されていない場合、完了まで実行
                loop.run_until_complete(self._execute_step(step, None))
        except Exception as e:
            logger.error(f"Error executing step {step_name}: {e}")
            self._handle_step_error(step_name, e)
    
    async def _execute_step(self, step: Step, user_input: Optional[str]) -> None:
        """
        Execute a single step with hooks and error handling
        フックとエラーハンドリングで単一ステップを実行
        
        Args:
            step: Step to execute / 実行するステップ
            user_input: User input if any / ユーザー入力（あれば）
        """
        step_name = step.name
        
        # Before step hooks
        # ステップ前フック
        for hook in self.before_step_hooks:
            try:
                hook(step_name, self.context)
            except Exception as e:
                logger.warning(f"Before step hook error: {e}")
        
        start_time = datetime.now()
        result = None
        error = None
        
        try:
            # Execute step
            # ステップを実行
            result = await step.run_async(user_input, self.context)
            if result != self.context:
                # Step returned a new context, use it
                # ステップが新しいコンテキストを返した場合、それを使用
                self.context = result
            
            logger.debug(f"Step {step_name} completed in {datetime.now() - start_time}")
            
        except Exception as e:
            error = e
            logger.error(f"Step {step_name} failed: {e}")
            logger.debug(traceback.format_exc())
            
            # Add error to context
            # エラーをコンテキストに追加
            self.context.add_system_message(f"Step {step_name} failed: {str(e)}")
            
            # Call error hooks
            # エラーフックを呼び出し
            for hook in self.error_hooks:
                try:
                    hook(step_name, self.context, e)
                except Exception as hook_error:
                    logger.warning(f"Error hook failed: {hook_error}")
            
            raise e
        
        finally:
            # After step hooks
            # ステップ後フック
            for hook in self.after_step_hooks:
                try:
                    hook(step_name, self.context, result)
                except Exception as e:
                    logger.warning(f"After step hook error: {e}")
    
    def _handle_step_error(self, step_name: str, error: Exception) -> None:
        """
        Handle step execution error
        ステップ実行エラーを処理
        
        Args:
            step_name: Name of the failed step / 失敗したステップの名前
            error: The error that occurred / 発生したエラー
        """
        # Finalize current span with error status
        # エラーステータスで現在のスパンを終了
        self.context._finalize_current_span("error", str(error))
        
        # Mark flow as finished on error
        # エラー時はフローを完了としてマーク
        self.context.finish()
        self.context.set_artifact("error", {
            "step": step_name,
            "error": str(error),
            "type": type(error).__name__
        })
        
        # Update trace registry with error
        # エラーでトレースレジストリを更新
        self._update_trace_on_error(step_name, error)
    
    def add_hook(
        self, 
        hook_type: str, 
        callback: Callable
    ) -> None:
        """
        Add observability hook
        オブザーバビリティフックを追加
        
        Args:
            hook_type: Type of hook ("before_step", "after_step", "error") / フックタイプ
            callback: Callback function / コールバック関数
        """
        if hook_type == "before_step":
            self.before_step_hooks.append(callback)
        elif hook_type == "after_step":
            self.after_step_hooks.append(callback)
        elif hook_type == "error":
            self.error_hooks.append(callback)
        else:
            raise ValueError(f"Unknown hook type: {hook_type}")
    
    def get_step_history(self) -> List[Dict[str, Any]]:
        """
        Get execution history
        実行履歴を取得
        
        Returns:
            List[Dict[str, Any]]: Step execution history / ステップ実行履歴
        """
        # Use span_history from context as primary source
        # コンテキストのspan_historyを主要ソースとして使用
        if hasattr(self.context, 'span_history') and self.context.span_history:
            return self.context.span_history
        
        # Fallback: extract from messages
        # フォールバック: メッセージから抽出
        history = []
        for msg in self.context.messages:
            if msg.role == "system" and "Step" in msg.content:
                # Try to extract step name from message
                # メッセージからステップ名を抽出しようとする
                step_name = None
                if "executing step:" in msg.content.lower():
                    parts = msg.content.split(":")
                    if len(parts) > 1:
                        step_name = parts[1].strip()
                
                history.append({
                    "timestamp": msg.timestamp,
                    "step_name": step_name or "Unknown",
                    "message": msg.content,
                    "metadata": msg.metadata
                })
        
        return history
    
    def get_flow_summary(self) -> Dict[str, Any]:
        """
        Get flow execution summary
        フロー実行サマリーを取得
        
        Returns:
            Dict[str, Any]: Flow summary / フローサマリー
        """
        trace_summary = self.context.get_trace_summary()
        return {
            "flow_id": self.flow_id,
            "flow_name": self.flow_name,
            "trace_id": self.trace_id,
            "current_span_id": self.context.current_span_id,
            "start_step": self.start,
            "current_step": self.current_step_name,
            "next_step": self.next_step_name,
            "step_count": self.context.step_count,
            "finished": self.finished,
            "start_time": self.context.start_time,
            "execution_history": self.get_step_history(),
            "span_history": self.context.get_span_history(),
            "trace_summary": trace_summary,
            "artifacts": self.context.artifacts,
            "message_count": len(self.context.messages)
        }
    
    def reset(self) -> None:
        """
        Reset flow to initial state
        フローを初期状態にリセット
        """
        self.context = Context(trace_id=self.trace_id)
        self.context.next_label = self.start
        self._running = False
        if self._run_loop_task:
            self._run_loop_task.cancel()
            self._run_loop_task = None
    
    def show(self, format: str = "mermaid", include_history: bool = True) -> str:
        """
        Show flow structure and execution path as a diagram.
        フロー構造と実行パスを図として表示します。
        
        Args:
            format: Output format ("mermaid" or "text") / 出力形式（"mermaid" または "text"）
            include_history: Whether to include execution history / 実行履歴を含めるかどうか
            
        Returns:
            str: Flow diagram representation / フロー図の表現
        """
        if format == "mermaid":
            return self._generate_mermaid_diagram(include_history)
        elif format == "text":
            return self._generate_text_diagram(include_history)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_possible_routes(self, step_name: str) -> List[str]:
        """
        Get possible routes from a given step.
        指定されたステップから可能なルートを取得します。
        
        Args:
            step_name: Name of the step / ステップ名
            
        Returns:
            List[str]: List of possible next step names / 可能な次のステップ名のリスト
        """
        if step_name not in self.steps:
            return []
        
        step = self.steps[step_name]
        routes = []
        
        # Check different step types for routing information
        # 様々なステップタイプのルーティング情報をチェック
        if hasattr(step, 'next_step') and step.next_step:
            routes.append(step.next_step)
        
        if hasattr(step, 'if_true') and hasattr(step, 'if_false'):
            # ConditionStep
            routes.extend([step.if_true, step.if_false])
        
        if hasattr(step, 'branches'):
            # ForkStep
            routes.extend(step.branches)
        
        if hasattr(step, 'config') and hasattr(step.config, 'routes'):
            # RouterAgent
            routes.extend(step.config.routes.values())
        
        return list(set(routes))  # Remove duplicates
    
    def _generate_mermaid_diagram(self, include_history: bool) -> str:
        """
        Generate Mermaid flowchart diagram.
        Mermaidフローチャート図を生成します。
        
        Args:
            include_history: Whether to include execution history / 実行履歴を含めるかどうか
            
        Returns:
            str: Mermaid diagram code / Mermaid図のコード
        """
        lines = ["graph TD"]
        visited_nodes = set()
        execution_path = []
        
        # Get execution history if available
        # 実行履歴があれば取得
        if include_history:
            step_history = self.get_step_history()
            execution_path = [step['step_name'] for step in step_history if 'step_name' in step]
        
        # Add nodes and connections
        # ノードと接続を追加
        def add_node_and_connections(step_name: str, depth: int = 0):
            if step_name in visited_nodes or depth > 10:  # Prevent infinite recursion
                return
            
            visited_nodes.add(step_name)
            
            if step_name not in self.steps:
                # End node
                lines.append(f'    {step_name}["{step_name}<br/>(END)"]')
                return
            
            step = self.steps[step_name]
            
            # Determine node style based on step type and execution
            # ステップタイプと実行状況に基づいてノードスタイルを決定
            node_style = self._get_node_style(step, step_name, execution_path, include_history)
            lines.append(f'    {step_name}["{step_name}<br/>({step.__class__.__name__})"]{node_style}')
            
            # Add connections based on step type
            # ステップタイプに基づいて接続を追加
            possible_routes = self.get_possible_routes(step_name)
            
            if isinstance(step, self._get_condition_step_class()):
                # ConditionStep with labeled edges
                lines.append(f'    {step_name} -->|"True"| {step.if_true}')
                lines.append(f'    {step_name} -->|"False"| {step.if_false}')
                add_node_and_connections(step.if_true, depth + 1)
                add_node_and_connections(step.if_false, depth + 1)
                
            elif hasattr(step, 'config') and hasattr(step.config, 'routes'):
                # RouterAgent with route labels
                for route_key, next_step in step.config.routes.items():
                    lines.append(f'    {step_name} -->|"{route_key}"| {next_step}')
                    add_node_and_connections(next_step, depth + 1)
                    
            elif hasattr(step, 'branches'):
                # ForkStep
                for branch in step.branches:
                    lines.append(f'    {step_name} --> {branch}')
                    add_node_and_connections(branch, depth + 1)
                    
            else:
                # Simple step with next_step
                for next_step in possible_routes:
                    lines.append(f'    {step_name} --> {next_step}')
                    add_node_and_connections(next_step, depth + 1)
        
        # Start from the beginning
        # 開始点から始める
        add_node_and_connections(self.start)
        
        # Add execution path highlighting if history is included
        # 履歴が含まれる場合は実行パスをハイライト
        if include_history and execution_path:
            lines.append("")
            lines.append("    %% Execution path highlighting")
            for i, step_name in enumerate(execution_path):
                if i > 0:
                    prev_step = execution_path[i-1]
                    lines.append(f'    linkStyle {i-1} stroke:#ff3,stroke-width:4px')
        
        return "\n".join(lines)
    
    def _generate_text_diagram(self, include_history: bool) -> str:
        """
        Generate text-based flow diagram.
        テキストベースのフロー図を生成します。
        
        Args:
            include_history: Whether to include execution history / 実行履歴を含めるかどうか
            
        Returns:
            str: Text diagram / テキスト図
        """
        lines = ["Flow Diagram:"]
        lines.append("=" * 50)
        
        visited = set()
        
        def add_step_info(step_name: str, indent: int = 0):
            if step_name in visited:
                lines.append("  " * indent + f"→ {step_name} (already shown)")
                return
            
            visited.add(step_name)
            prefix = "  " * indent
            
            if step_name not in self.steps:
                lines.append(f"{prefix}→ {step_name} (END)")
                return
                
            step = self.steps[step_name]
            step_type = step.__class__.__name__
            
            lines.append(f"{prefix}→ {step_name} ({step_type})")
            
            # Show routing information
            # ルーティング情報を表示
            if hasattr(step, 'config') and hasattr(step.config, 'routes'):
                lines.append(f"{prefix}  Routes:")
                for route_key, next_step in step.config.routes.items():
                    lines.append(f"{prefix}    {route_key} → {next_step}")
                    
            elif isinstance(step, self._get_condition_step_class()):
                lines.append(f"{prefix}  True → {step.if_true}")
                lines.append(f"{prefix}  False → {step.if_false}")
                
            elif hasattr(step, 'branches'):
                lines.append(f"{prefix}  Branches:")
                for branch in step.branches:
                    lines.append(f"{prefix}    → {branch}")
            
            # Recursively show next steps
            # 次のステップを再帰的に表示
            possible_routes = self.get_possible_routes(step_name)
            for next_step in possible_routes:
                add_step_info(next_step, indent + 1)
        
        add_step_info(self.start)
        
        # Add execution history if requested
        # 要求された場合は実行履歴を追加
        if include_history:
            step_history = self.get_step_history()
            if step_history:
                lines.append("")
                lines.append("Execution History:")
                lines.append("-" * 30)
                for i, step_info in enumerate(step_history):
                    step_name = step_info.get('step_name', 'Unknown')
                    timestamp = step_info.get('timestamp', '')
                    lines.append(f"{i+1}. {step_name} ({timestamp})")
        
        return "\n".join(lines)
    
    def _get_node_style(self, step, step_name: str, execution_path: List[str], include_history: bool) -> str:
        """
        Get Mermaid node style based on step type and execution status.
        ステップタイプと実行状況に基づいてMermaidノードスタイルを取得します。
        """
        if include_history and step_name in execution_path:
            return ":::executed"
        elif step_name == self.start:
            return ":::start"
        elif hasattr(step, 'config') and hasattr(step.config, 'routes'):
            return ":::router"
        elif isinstance(step, self._get_condition_step_class()):
            return ":::condition"
        else:
            return ""
    
    def _get_condition_step_class(self):
        """Get ConditionStep class for type checking."""
        try:
            from .step import ConditionStep
            return ConditionStep
        except ImportError:
            return type(None)  # Fallback if import fails
    
    def stop(self) -> None:
        """
        Stop flow execution
        フロー実行を停止
        """
        self._running = False
        self.context.finalize_flow_span()  # Finalize current span before stopping
        self.context.finish()
        if self._run_loop_task:
            self._run_loop_task.cancel()
            self._run_loop_task = None
    
    async def start_background_task(self) -> asyncio.Task:
        """
        Start flow as background task
        フローをバックグラウンドタスクとして開始
        
        Returns:
            asyncio.Task: Background task / バックグラウンドタスク
        """
        if self._run_loop_task and not self._run_loop_task.done():
            raise RuntimeError("Flow is already running as background task")
        
        self._run_loop_task = asyncio.create_task(self.run_loop())
        return self._run_loop_task
    
    def __str__(self) -> str:
        """String representation of flow"""
        return f"Flow(start={self.start}, steps={len(self.steps)}, finished={self.finished})"
    
    def __repr__(self) -> str:
        return self.__str__()


# Utility functions for flow creation
# フロー作成用ユーティリティ関数

def create_simple_flow(
    steps: List[tuple[str, Step]], 
    context: Optional[Context] = None,
    name: Optional[str] = None
) -> Flow:
    """
    Create a simple linear flow from a list of steps
    ステップのリストから簡単な線形フローを作成
    
    Args:
        steps: List of (name, step) tuples / (名前, ステップ)タプルのリスト
        context: Initial context / 初期コンテキスト
        name: Flow name for identification / 識別用フロー名
        
    Returns:
        Flow: Created flow / 作成されたフロー
    """
    if not steps:
        raise ValueError("At least one step is required")
    
    step_dict = {}
    for i, (step_name, step) in enumerate(steps):
        # Set next step for each step
        # 各ステップの次ステップを設定
        if hasattr(step, 'next_step') and step.next_step is None:
            if i < len(steps) - 1:
                step.next_step = steps[i + 1][0]
        step_dict[step_name] = step
    
    return Flow(
        start=steps[0][0],
        steps=step_dict,
        context=context,
        name=name
    )


def create_conditional_flow(
    initial_step: Step,
    condition_step: Step,
    true_branch: List[Step],
    false_branch: List[Step],
    context: Optional[Context] = None,
    name: Optional[str] = None
) -> Flow:
    """
    Create a conditional flow with true/false branches
    true/falseブランチを持つ条件付きフローを作成
    
    Args:
        initial_step: Initial step / 初期ステップ
        condition_step: Condition step / 条件ステップ
        true_branch: Steps for true branch / trueブランチのステップ
        false_branch: Steps for false branch / falseブランチのステップ
        context: Initial context / 初期コンテキスト
        name: Flow name for identification / 識別用フロー名
        
    Returns:
        Flow: Created flow / 作成されたフロー
    """
    steps = {
        "start": initial_step,
        "condition": condition_step
    }
    
    # Add true branch steps
    # trueブランチステップを追加
    for i, step in enumerate(true_branch):
        step_name = f"true_{i}"
        steps[step_name] = step
        if i == 0 and hasattr(condition_step, 'if_true'):
            condition_step.if_true = step_name
    
    # Add false branch steps
    # falseブランチステップを追加
    for i, step in enumerate(false_branch):
        step_name = f"false_{i}"
        steps[step_name] = step
        if i == 0 and hasattr(condition_step, 'if_false'):
            condition_step.if_false = step_name
    
    # Connect initial step to condition
    # 初期ステップを条件に接続
    if hasattr(initial_step, 'next_step'):
        initial_step.next_step = "condition"
    
    return Flow(
        start="start",
        steps=steps,
        context=context,
        name=name
    ) 
