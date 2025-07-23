#!/usr/bin/env python3
"""
EvaluationAgent - Single-purpose evaluation agent for RefinireAgent output quality assessment
RefinireAgent出力品質評価専用エージェント
"""

import asyncio
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from ..core.llm import get_llm
from .flow.context import Context


class EvaluationResult(BaseModel):
    """Evaluation result structure"""
    content: str = Field(description="Generated content (copied from generation)")
    score: float = Field(ge=0.0, le=1.0, description="Overall evaluation score")
    passed: bool = Field(description="Whether evaluation passed threshold")
    criteria_scores: Dict[str, float] = Field(default_factory=dict, description="Individual criteria scores")
    feedback: str = Field(description="Detailed evaluation feedback")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional evaluation metadata")


class EvaluationAgent:
    """
    Single-purpose evaluation agent for RefinireAgent output quality assessment
    RefinireAgent出力品質評価専用エージェント
    
    Features:
    - Uses Context.shared_state for last_prompt/last_generation access
    - Structured output with EvaluationResult
    - Configurable evaluation criteria and thresholds
    - Compatible with RefinireAgent interface
    """
    
    def __init__(
        self,
        name: str,
        evaluation_instruction: str,
        evaluation_criteria: Optional[Dict[str, Any]] = None,
        pass_threshold: float = 0.7,
        model: str = "gpt-4o-mini",
        temperature: float = 0.2,  # 低温度で一貫した評価
        max_retries: int = 3,
        timeout: Optional[float] = None,
        **kwargs
    ):
        """
        Initialize EvaluationAgent
        
        Args:
            name: Agent name for identification
            evaluation_instruction: Instructions for evaluation logic
            evaluation_criteria: Specific criteria for evaluation
            pass_threshold: Minimum score for passing evaluation
            model: LLM model to use
            temperature: Low temperature for consistent evaluation
            # provider: Automatically detected from model name patterns and environment variables
            max_retries: Maximum retry attempts
            timeout: Request timeout
        """
        self.name = name
        self.evaluation_instruction = evaluation_instruction
        self.evaluation_criteria = evaluation_criteria or {}
        self.pass_threshold = pass_threshold
        self.model_name = model
        self.temperature = temperature
        self.max_retries = max_retries
        self.timeout = timeout
        self.kwargs = kwargs
        
        # Initialize LLM
        # LLMを初期化
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
        Execute evaluation asynchronously
        
        Args:
            input_text: Input text (typically evaluation instruction)
            context: Context containing shared_state with last_prompt/last_generation
            
        Returns:
            Context: Updated context with evaluation result stored in context.evaluation_result
            
        Process:
            1. Extract last_prompt and last_generation from context.shared_state
            2. Build evaluation prompt with context and criteria
            3. Execute LLM call with structured output (EvaluationResult)
            4. Apply pass_threshold to determine pass/fail
            5. Store evaluation result in context.evaluation_result
            6. Store LLMResult in context.result
            7. Return updated context
        """
        try:
            # Build evaluation prompt using shared_state
            # shared_stateを使用して評価プロンプトを構築
            evaluation_prompt = self._build_evaluation_prompt(context, input_text)
            
            # Execute LLM call with structured output
            # 構造化出力でLLM呼び出しを実行
            for attempt in range(self.max_retries):
                try:
                    llm_result = await self._execute_llm_call(evaluation_prompt)
                    
                    # Parse evaluation result
                    # 評価結果を解析
                    evaluation_result = self._parse_evaluation_result(llm_result, context)
                    
                    # Apply pass_threshold to determine pass/fail
                    # pass_thresholdを適用して合格/不合格を判定
                    evaluation_result.passed = evaluation_result.score >= self.pass_threshold
                    
                    # Store results in context
                    # 結果をcontextに保存
                    context.evaluation_result = evaluation_result
                    context.result = self._create_llm_result(evaluation_result, True)
                    
                    return context
                    
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        # Final attempt failed, create error evaluation result
                        # 最終試行が失敗、エラー評価結果を作成
                        error_evaluation = EvaluationResult(
                            content=context.shared_state.get('_last_generation', 'evaluation_error'),
                            score=0.0,
                            passed=False,
                            feedback=f"Evaluation failed after {self.max_retries} attempts: {str(e)}",
                            suggestions=["Review evaluation criteria", "Check LLM availability"],
                            metadata={"error": str(e), "attempts": self.max_retries}
                        )
                        context.evaluation_result = error_evaluation
                        context.result = self._create_llm_result(error_evaluation, False)
                        return context
                    
                    # Wait before retry
                    # リトライ前に待機
                    await asyncio.sleep(0.5 * (attempt + 1))
            
        except Exception as e:
            # Handle unexpected errors
            # 予期しないエラーを処理
            error_evaluation = EvaluationResult(
                content=context.shared_state.get('_last_generation', 'evaluation_error'),
                score=0.0,
                passed=False,
                feedback=f"Unexpected evaluation error: {str(e)}",
                suggestions=["Review evaluation setup"],
                metadata={"error": str(e)}
            )
            context.evaluation_result = error_evaluation
            context.result = self._create_llm_result(error_evaluation, False)
            return context
            
    def run(self, input_text: str, context: Context, **kwargs) -> Context:
        """Synchronous wrapper for run_async"""
        return asyncio.run(self.run_async(input_text, context, **kwargs))
    
    def _build_evaluation_prompt(self, context: Context, input_text: str) -> str:
        """
        Build evaluation prompt using context shared_state
        
        Template:
        ```
        直前の生成プロセスを評価してください。
        
        === 元のプロンプト ===
        {context.shared_state.get('_last_prompt', 'N/A')}
        
        === 生成結果 ===
        {context.shared_state.get('_last_generation', 'N/A')}
        
        === 評価指示 ===
        {self.evaluation_instruction}
        
        === 評価基準 ===
        {self._format_evaluation_criteria()}
        
        上記の内容を評価し、指定されたJSON形式で評価結果を出力してください。
        ```
        """
        last_prompt = context.shared_state.get('_last_prompt', 'N/A')
        last_generation = context.shared_state.get('_last_generation', 'N/A')
        criteria_text = self._format_evaluation_criteria()
        
        prompt = f"""直前の生成プロセスを評価してください。

=== 元のプロンプト ===
{last_prompt}

=== 生成結果 ===
{last_generation}

=== 評価指示 ===
{self.evaluation_instruction}

=== 評価基準 ===
{criteria_text}

上記の内容を評価し、以下のJSON形式で評価結果を出力してください：

{{
  "content": "評価対象コンテンツのコピー",
  "score": 0.0〜1.0の総合評価スコア,
  "criteria_scores": {{
    "基準1": スコア,
    "基準2": スコア
  }},
  "feedback": "詳細な評価フィードバック",
  "suggestions": ["改善提案1", "改善提案2"],
  "metadata": {{
    "評価者": "{self.name}",
    "評価日時": "現在時刻"
  }}
}}

重要: scoreは0.0-1.0の範囲で、{self.pass_threshold}以上が合格基準です。"""
        
        return prompt
    
    def _format_evaluation_criteria(self) -> str:
        """Format evaluation criteria for prompt inclusion"""
        if not self.evaluation_criteria:
            return "一般的な品質基準（正確性、関連性、完全性）で評価してください。"
        
        criteria_text = []
        for criterion, details in self.evaluation_criteria.items():
            criteria_text.append(f"- {criterion}: {details}")
        
        return "\n".join(criteria_text)
    
    async def _execute_llm_call(self, prompt: str) -> Any:
        """Execute LLM call with timeout handling"""
        if self.timeout:
            return await asyncio.wait_for(
                self.llm.generate_async(prompt),
                timeout=self.timeout
            )
        else:
            return await self.llm.generate_async(prompt)
    
    def _parse_evaluation_result(self, llm_result: Any, context: Context) -> EvaluationResult:
        """Parse LLM result into EvaluationResult"""
        try:
            # Try to extract content from LLM result
            # LLM結果からコンテンツを抽出を試行
            if hasattr(llm_result, 'content'):
                content = llm_result.content
            else:
                content = str(llm_result)
            
            # Try to parse as JSON if it looks like JSON
            # JSON形式の場合は解析を試行
            if isinstance(content, str) and content.strip().startswith('{'):
                import json
                try:
                    parsed = json.loads(content.strip())
                    return EvaluationResult(
                        content=parsed.get('content', context.shared_state.get('_last_generation', '')),
                        score=float(parsed.get('score', 0.5)),
                        passed=False,  # Will be set later based on threshold
                        criteria_scores=parsed.get('criteria_scores', {}),
                        feedback=parsed.get('feedback', 'Parsed from JSON response'),
                        suggestions=parsed.get('suggestions', []),
                        metadata=parsed.get('metadata', {})
                    )
                except (json.JSONDecodeError, ValueError, TypeError):
                    pass
            
            # Fallback: create evaluation result based on content analysis
            # フォールバック: コンテンツ分析に基づく評価結果を作成
            return self._analyze_content_for_evaluation(content, context)
            
        except Exception as e:
            # Error case: create safe fallback evaluation
            # エラー時: 安全なフォールバック評価を作成
            return EvaluationResult(
                content=context.shared_state.get('_last_generation', ''),
                score=0.3,
                passed=False,
                feedback=f"Failed to parse evaluation result, using fallback: {str(e)}",
                suggestions=["Review evaluation format", "Check LLM response"],
                metadata={"parse_error": str(e)}
            )
    
    def _analyze_content_for_evaluation(self, content: str, context: Context) -> EvaluationResult:
        """Analyze content to create evaluation when JSON parsing fails"""
        content_lower = content.lower()
        
        # Simple keyword-based evaluation analysis
        # シンプルなキーワードベースの評価分析
        score = 0.5  # Default score
        feedback_parts = []
        suggestions = []
        
        # Check for positive indicators
        # ポジティブ指標をチェック
        positive_words = ['good', 'excellent', 'accurate', 'helpful', 'clear', 'complete']
        positive_count = sum(1 for word in positive_words if word in content_lower)
        
        # Check for negative indicators
        # ネガティブ指標をチェック
        negative_words = ['error', 'incorrect', 'unclear', 'incomplete', 'poor', 'bad']
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        # Adjust score based on indicators
        # 指標に基づいてスコアを調整
        if positive_count > negative_count:
            score = 0.7 + (positive_count * 0.05)
            feedback_parts.append("Detected positive evaluation indicators")
        elif negative_count > positive_count:
            score = 0.3 - (negative_count * 0.05)
            feedback_parts.append("Detected negative evaluation indicators")
            suggestions.append("Review and improve content quality")
        else:
            feedback_parts.append("Mixed or neutral evaluation indicators")
        
        # Ensure score is within bounds
        # スコアが範囲内であることを確認
        score = max(0.0, min(1.0, score))
        
        return EvaluationResult(
            content=context.shared_state.get('_last_generation', content[:100]),
            score=score,
            passed=score >= self.pass_threshold,
            feedback="; ".join(feedback_parts) if feedback_parts else "Content analysis evaluation",
            suggestions=suggestions,
            metadata={
                "analysis_method": "keyword_based",
                "positive_indicators": positive_count,
                "negative_indicators": negative_count
            }
        )
    
    def _create_llm_result(self, evaluation_result: EvaluationResult, success: bool) -> Any:
        """Create LLMResult-like object for compatibility"""
        from ..agents.pipeline.llm_pipeline import LLMResult
        
        return LLMResult(
            content=evaluation_result,
            success=success,
            metadata={
                'agent_name': self.name,
                'agent_type': 'evaluation',
                'model': self.model_name,
                'temperature': self.temperature,
                'pass_threshold': self.pass_threshold,
                'passed': evaluation_result.passed
            },
            evaluation_score=evaluation_result.score,
            attempts=1
        )