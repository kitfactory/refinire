#!/usr/bin/env python3
"""
RoutingAgent - Single-purpose routing agent for RefinireAgent workflow routing
RefinireAgentワークフローのルーティング専用エージェント
"""

import asyncio
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from ..core.llm import get_llm
from ..core.routing import RoutingResult
from .flow.context import Context


class RoutingAgent:
    """
    Single-purpose routing agent for RefinireAgent workflow routing
    RefinireAgentワークフローのルーティング専用エージェント
    
    Features:
    - Uses Context.shared_state for last_prompt/last_generation access
    - Structured output with RoutingResult
    - Lightweight and fast routing decisions
    - Compatible with RefinireAgent interface
    """
    
    def __init__(
        self,
        name: str,
        routing_instruction: str,
        routing_destinations: Optional[List[str]] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,  # 低温度でより確実な判定
        max_retries: int = 3,
        timeout: Optional[float] = None,
        **kwargs
    ):
        """
        Initialize RoutingAgent
        
        Args:
            name: Agent name for identification
            routing_instruction: Instructions for routing decision logic
            routing_destinations: List of possible routing destinations (optional)
            model: LLM model to use
            temperature: Low temperature for consistent routing
            # provider: Automatically detected from model name patterns and environment variables
            max_retries: Maximum retry attempts
            timeout: Request timeout
        """
        self.name = name
        self.routing_instruction = routing_instruction
        self.routing_destinations = routing_destinations or []
        self.model_name = model
        self.temperature = temperature
        self.max_retries = max_retries
        self.timeout = timeout
        self.kwargs = kwargs
        
        # Initialize LLM with structured output
        # 構造化出力でLLMを初期化
        self.llm = get_llm(
            model=model,
            temperature=temperature,
            **kwargs
        )
    
    async def run_async(
        self, 
        input_text: str, 
        context: Context,
        **kwargs
    ) -> Context:
        """
        Execute routing decision asynchronously
        
        Args:
            input_text: Input text (typically routing instruction)
            context: Context containing shared_state with last_prompt/last_generation
            
        Returns:
            Context: Updated context with routing result stored in context.routing_result
            
        Process:
            1. Extract last_prompt and last_generation from context.shared_state
            2. Build routing prompt with context information
            3. Execute LLM call with structured output (RoutingResult)
            4. Store routing result in context.routing_result
            5. Store LLMResult in context.result
            6. Return updated context
        """
        try:
            # Build routing prompt using shared_state
            # shared_stateを使用してルーティングプロンプトを構築
            routing_prompt = self._build_routing_prompt(context, input_text)
            
            # Execute LLM call with structured output
            # 構造化出力でLLM呼び出しを実行
            for attempt in range(self.max_retries):
                try:
                    llm_result = await self._execute_llm_call(routing_prompt)
                    
                    # Parse routing result
                    # ルーティング結果を解析
                    routing_result = self._parse_routing_result(llm_result, context)
                    
                    # Validate routing destination if specified
                    # 分岐先が指定されている場合は検証
                    if not self._validate_routing_destination(routing_result.next_route):
                        # Create fallback routing result for invalid destination
                        # 無効な分岐先に対するフォールバックルーティング結果を作成
                        routing_result = self._create_fallback_routing_result(
                            context, routing_result.next_route
                        )
                    
                    # Store results in context
                    # 結果をcontextに保存
                    context.routing_result = routing_result
                    context.result = self._create_llm_result(routing_result, True)
                    
                    return context
                    
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        # Final attempt failed, create error routing result
                        # 最終試行が失敗、エラールーティング結果を作成
                        error_routing = RoutingResult(
                            content="routing_error",
                            next_route="error",
                            confidence=0.0,
                            reasoning=f"Routing failed after {self.max_retries} attempts: {str(e)}"
                        )
                        context.routing_result = error_routing
                        context.result = self._create_llm_result(error_routing, False)
                        return context
                    
                    # Wait before retry
                    # リトライ前に待機
                    await asyncio.sleep(0.5 * (attempt + 1))
            
        except Exception as e:
            # Handle unexpected errors
            # 予期しないエラーを処理
            error_routing = RoutingResult(
                content="routing_error",
                next_route="error", 
                confidence=0.0,
                reasoning=f"Unexpected routing error: {str(e)}"
            )
            context.routing_result = error_routing
            context.result = self._create_llm_result(error_routing, False)
            return context
            
    def run(self, input_text: str, context: Context, **kwargs) -> Context:
        """Synchronous wrapper for run_async"""
        return asyncio.run(self.run_async(input_text, context, **kwargs))
    
    def _build_routing_prompt(self, context: Context, input_text: str) -> str:
        """
        Build routing prompt using context shared_state and routing destinations
        コンテキストのshared_stateとrouting_destinationsを使用してルーティングプロンプトを構築
        """
        last_prompt = context.shared_state.get('_last_prompt', 'N/A')
        last_generation = context.shared_state.get('_last_generation', 'N/A')
        
        # Format available destinations if provided
        # 利用可能な分岐先を整形（提供されている場合）
        destinations_section = ""
        if self.routing_destinations:
            destinations_text = self._format_routing_destinations()
            destinations_section = f"""
=== 利用可能な分岐先 ===
{destinations_text}
"""
        
        prompt = f"""直前の生成プロセスを分析し、ルーティング判断を行ってください。

=== 直前の生成プロンプト ===
{last_prompt}

=== 直前の生成結果 ===
{last_generation}
{destinations_section}
=== ルーティング指示 ===
{self.routing_instruction}

上記の情報に基づいて、適切なルーティング判断を行い、以下のJSON形式で出力してください：

{{
  "content": "生成結果のコピー",
  "next_route": "次のルート名{' (上記の分岐先から選択)' if self.routing_destinations else ''}",
  "confidence": 0.0〜1.0の信頼度,
  "reasoning": "判断理由の説明"
}}"""
        
        return prompt
    
    def _format_routing_destinations(self) -> str:
        """
        Format routing destinations for display in prompt
        プロンプト表示用にルーティング先を整形
        """
        if not self.routing_destinations:
            return "指定なし"
        
        formatted_destinations = []
        for i, dest in enumerate(self.routing_destinations, 1):
            # Add description for flow control constants
            # フロー制御定数に説明を追加
            if dest in ("_FLOW_END_", "_FLOW_TERMINATE_", "_FLOW_FINISH_"):
                formatted_destinations.append(f"{i}. '{dest}' - フロー終了")
            else:
                formatted_destinations.append(f"{i}. '{dest}'")
        
        return "\n".join(formatted_destinations)
    
    def _validate_routing_destination(self, selected_route: str) -> bool:
        """
        Validate if the selected route is in the allowed destinations
        選択されたルートが許可された分岐先に含まれるかを検証
        
        Args:
            selected_route: The route selected by the LLM
            
        Returns:
            True if valid or no destinations specified, False otherwise
        """
        if not self.routing_destinations:
            # No restrictions if destinations not specified
            # 分岐先が指定されていない場合は制限なし
            return True
        
        return selected_route in self.routing_destinations
    
    async def _execute_llm_call(self, prompt: str) -> Any:
        """Execute LLM call with timeout handling"""
        from agents import Runner, Agent
        
        # Create a simple agent for the LLM call
        # LLM呼び出し用のシンプルなエージェントを作成
        temp_agent = Agent(
            name="routing_agent",
            instructions="You are a routing decision agent. Provide JSON output as requested.",
            model=self.llm
        )
        
        if self.timeout:
            return await asyncio.wait_for(
                Runner.run(temp_agent, prompt),
                timeout=self.timeout
            )
        else:
            return await Runner.run(temp_agent, prompt)
    
    def _parse_routing_result(self, llm_result: Any, context: Context) -> RoutingResult:
        """Parse LLM result into RoutingResult"""
        try:
            # Try to extract content from LLM result
            # LLM結果からコンテンツを抽出を試行
            if hasattr(llm_result, 'final_output'):
                content = llm_result.final_output
            elif hasattr(llm_result, 'content'):
                content = llm_result.content
            else:
                content = str(llm_result)
            
            # Try to parse as JSON if it looks like JSON
            # JSON形式の場合は解析を試行
            if isinstance(content, str) and content.strip().startswith('{'):
                import json
                try:
                    parsed = json.loads(content.strip())
                    return RoutingResult(
                        content=parsed.get('content', context.shared_state.get('_last_generation', '')),
                        next_route=parsed.get('next_route', 'continue'),
                        confidence=float(parsed.get('confidence', 0.8)),
                        reasoning=parsed.get('reasoning', 'Parsed from JSON response')
                    )
                except json.JSONDecodeError:
                    pass
            
            # Fallback: create routing result based on content analysis
            # フォールバック: コンテンツ分析に基づくルーティング結果を作成
            return self._analyze_content_for_routing(content, context)
            
        except Exception as e:
            # Error case: create safe fallback routing
            # エラー時: 安全なフォールバックルーティングを作成
            return RoutingResult(
                content=context.shared_state.get('_last_generation', ''),
                next_route='continue',
                confidence=0.3,
                reasoning=f"Failed to parse routing result, using fallback: {str(e)}"
            )
    
    def _analyze_content_for_routing(self, content: str, context: Context) -> RoutingResult:
        """Analyze content to determine routing when JSON parsing fails"""
        content_lower = content.lower()
        
        # Simple keyword-based routing analysis
        # シンプルなキーワードベースのルーティング分析
        if any(word in content_lower for word in ['error', 'fail', 'exception']):
            next_route = 'error'
            confidence = 0.7
            reasoning = 'Detected error indicators in response'
        elif any(word in content_lower for word in ['end', 'finish', 'complete', 'done']):
            next_route = 'end'
            confidence = 0.6
            reasoning = 'Detected completion indicators in response'
        elif any(word in content_lower for word in ['continue', 'next', 'proceed']):
            next_route = 'continue'
            confidence = 0.6
            reasoning = 'Detected continuation indicators in response'
        else:
            next_route = 'continue'
            confidence = 0.4
            reasoning = 'Default routing decision based on content analysis'
        
        return RoutingResult(
            content=context.shared_state.get('_last_generation', content[:100]),
            next_route=next_route,
            confidence=confidence,
            reasoning=reasoning
        )
    
    def _create_fallback_routing_result(self, context: Context, invalid_route: str) -> RoutingResult:
        """
        Create fallback routing result when invalid destination is selected
        無効な分岐先が選択された場合のフォールバックルーティング結果を作成
        
        Args:
            context: Current context
            invalid_route: The invalid route that was selected
            
        Returns:
            RoutingResult with fallback route
        """
        # Choose fallback route: first destination if available, otherwise 'continue'
        # フォールバックルートを選択: 利用可能な場合は最初の分岐先、そうでなければ'continue'
        fallback_route = (
            self.routing_destinations[0] 
            if self.routing_destinations 
            else 'continue'
        )
        
        return RoutingResult(
            content=context.shared_state.get('_last_generation', ''),
            next_route=fallback_route,
            confidence=0.3,
            reasoning=f"無効なルート '{invalid_route}' が選択されました。利用可能な分岐先: {self.routing_destinations}。フォールバック先 '{fallback_route}' を使用します。"
        )
    
    def _create_llm_result(self, routing_result: RoutingResult, success: bool) -> Any:
        """Create LLMResult-like object for compatibility"""
        from ..agents.pipeline.llm_pipeline import LLMResult
        
        return LLMResult(
            content=routing_result,
            success=success,
            metadata={
                'agent_name': self.name,
                'agent_type': 'routing',
                'model': self.model_name,
                'temperature': self.temperature
            },
            attempts=1
        )