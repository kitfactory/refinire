"""LLM Pipeline - A replacement for deprecated AgentPipeline using OpenAI Python SDK directly.

LLMパイプライン - 非推奨のAgentPipelineに代わって、OpenAI Python SDKを直接使用する新しい実装。
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Callable, Dict, List, Optional, Type, Union
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import warnings

try:
    from openai import OpenAI, AsyncOpenAI
    from pydantic import BaseModel
except ImportError as e:
    raise ImportError(f"Required dependencies not found: {e}. Please install openai and pydantic.")


@dataclass
class LLMResult:
    """
    Result from LLM generation
    LLM生成結果
    
    Attributes:
        content: Generated content / 生成されたコンテンツ
        success: Whether generation was successful / 生成が成功したか
        metadata: Additional metadata / 追加メタデータ
        evaluation_score: Evaluation score if evaluated / 評価されている場合の評価スコア
        attempts: Number of attempts made / 実行された試行回数
    """
    content: Any
    success: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    evaluation_score: Optional[float] = None
    attempts: int = 1


@dataclass 
class EvaluationResult:
    """
    Result from evaluation process
    評価プロセスの結果
    
    Attributes:
        score: Evaluation score (0-100) / 評価スコア（0-100）
        passed: Whether evaluation passed threshold / 閾値を超えたか
        feedback: Evaluation feedback / 評価フィードバック
        metadata: Additional metadata / 追加メタデータ
    """
    score: float
    passed: bool
    feedback: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class LLMPipeline:
    """
    Modern LLM Pipeline using OpenAI Python SDK directly
    OpenAI Python SDKを直接使用するモダンなLLMパイプライン
    
    This class replaces the deprecated AgentPipeline with a cleaner, more maintainable implementation.
    このクラスは非推奨のAgentPipelineを、よりクリーンで保守しやすい実装で置き換えます。
    """
    
    def __init__(
        self,
        name: str,
        generation_instructions: str,
        evaluation_instructions: Optional[str] = None,
        *,
        model: str = "gpt-4o-mini",
        evaluation_model: Optional[str] = None,
        output_model: Optional[Type[BaseModel]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        timeout: float = 30.0,
        threshold: float = 85.0,
        max_retries: int = 3,
        input_guardrails: Optional[List[Callable[[str], bool]]] = None,
        output_guardrails: Optional[List[Callable[[Any], bool]]] = None,
        session_history: Optional[List[str]] = None,
        history_size: int = 10,
        improvement_callback: Optional[Callable[[LLMResult, EvaluationResult], str]] = None,
        locale: str = "en"
    ) -> None:
        """
        Initialize LLM Pipeline
        LLMパイプラインを初期化する
        
        Args:
            name: Pipeline name / パイプライン名
            generation_instructions: Instructions for generation / 生成用指示
            evaluation_instructions: Instructions for evaluation / 評価用指示
            model: OpenAI model name / OpenAIモデル名
            evaluation_model: Model for evaluation / 評価用モデル
            output_model: Pydantic model for structured output / 構造化出力用Pydanticモデル
            temperature: Sampling temperature / サンプリング温度
            max_tokens: Maximum tokens / 最大トークン数
            timeout: Request timeout / リクエストタイムアウト
            threshold: Evaluation threshold / 評価閾値
            max_retries: Maximum retry attempts / 最大リトライ回数
            input_guardrails: Input validation functions / 入力検証関数
            output_guardrails: Output validation functions / 出力検証関数
            session_history: Session history / セッション履歴
            history_size: History size limit / 履歴サイズ制限
            improvement_callback: Callback for improvement suggestions / 改善提案コールバック
            locale: Locale for messages / メッセージ用ロケール
        """
        # Basic configuration
        self.name = name
        self.generation_instructions = generation_instructions
        self.evaluation_instructions = evaluation_instructions
        self.model = model
        self.evaluation_model = evaluation_model or model
        self.output_model = output_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.threshold = threshold
        self.max_retries = max_retries
        self.locale = locale
        
        # Guardrails
        self.input_guardrails = input_guardrails or []
        self.output_guardrails = output_guardrails or []
        
        # History management
        self.session_history = session_history or []
        self.history_size = history_size
        self._pipeline_history: List[Dict[str, Any]] = []
        
        # Callbacks
        self.improvement_callback = improvement_callback
        
        # Initialize OpenAI clients
        self.sync_client = OpenAI()
        self.async_client = AsyncOpenAI()
    
    def run(self, user_input: str) -> LLMResult:
        """
        Run the pipeline synchronously
        パイプラインを同期的に実行する
        
        Args:
            user_input: User input / ユーザー入力
            
        Returns:
            LLMResult: Generation result / 生成結果
        """
        # Input validation
        if not self._validate_input(user_input):
            return LLMResult(
                content=None,
                success=False,
                metadata={"error": "Input validation failed", "input": user_input}
            )
        
        # Build prompt with history
        full_prompt = self._build_prompt(user_input)
        
        # Generation with retries
        for attempt in range(1, self.max_retries + 1):
            try:
                # Generate content
                generation_result = self._generate_content(full_prompt)
                
                # Output validation
                if not self._validate_output(generation_result):
                    if attempt < self.max_retries:
                        continue
                    return LLMResult(
                        content=None,
                        success=False,
                        metadata={"error": "Output validation failed", "attempts": attempt}
                    )
                
                # Parse structured output if model specified
                parsed_content = self._parse_structured_output(generation_result)
                
                # Evaluate if evaluation instructions provided
                evaluation_result = None
                if self.evaluation_instructions:
                    evaluation_result = self._evaluate_content(user_input, parsed_content)
                    
                    # Check if evaluation passed
                    if not evaluation_result.passed and attempt < self.max_retries:
                        # Generate improvement if callback provided
                        if self.improvement_callback:
                            improvement = self.improvement_callback(
                                LLMResult(content=parsed_content, success=True),
                                evaluation_result
                            )
                            full_prompt = f"{full_prompt}\n\nImprovement needed: {improvement}"
                        continue
                
                # Success - store in history and return
                result = LLMResult(
                    content=parsed_content,
                    success=True,
                    metadata={
                        "model": self.model,
                        "temperature": self.temperature,
                        "attempts": attempt
                    },
                    evaluation_score=evaluation_result.score if evaluation_result else None,
                    attempts=attempt
                )
                
                self._store_in_history(user_input, result)
                return result
                
            except Exception as e:
                if attempt == self.max_retries:
                    return LLMResult(
                        content=None,
                        success=False,
                        metadata={"error": str(e), "attempts": attempt}
                    )
                continue
        
        # Should not reach here
        return LLMResult(
            content=None,
            success=False,
            metadata={"error": "Maximum retries exceeded"}
        )
    
    async def run_async(self, user_input: str) -> LLMResult:
        """
        Run the pipeline asynchronously
        パイプラインを非同期的に実行する
        
        Args:
            user_input: User input / ユーザー入力
            
        Returns:
            LLMResult: Generation result / 生成結果
        """
        # For simplicity, run sync version in executor
        # In production, this would be fully async
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, self.run, user_input)
    
    def _validate_input(self, user_input: str) -> bool:
        """Validate input using guardrails / ガードレールを使用して入力を検証"""
        for guardrail in self.input_guardrails:
            if not guardrail(user_input):
                return False
        return True
    
    def _validate_output(self, output: str) -> bool:
        """Validate output using guardrails / ガードレールを使用して出力を検証"""
        for guardrail in self.output_guardrails:
            if not guardrail(output):
                return False
        return True
    
    def _build_prompt(self, user_input: str) -> str:
        """Build complete prompt with instructions and history / 指示と履歴を含む完全なプロンプトを構築"""
        prompt_parts = [self.generation_instructions]
        
        # Add history if available
        if self.session_history:
            history_text = "\n".join(self.session_history[-self.history_size:])
            prompt_parts.append(f"Previous context:\n{history_text}")
        
        prompt_parts.append(f"User input: {user_input}")
        
        return "\n\n".join(prompt_parts)
    
    def _generate_content(self, prompt: str) -> str:
        """Generate content using OpenAI API / OpenAI APIを使用してコンテンツを生成"""
        messages = [{"role": "user", "content": prompt}]
        
        # Prepare API call parameters
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "timeout": self.timeout
        }
        
        if self.max_tokens:
            params["max_tokens"] = self.max_tokens
        
        # Add structured output if model specified
        if self.output_model:
            params["response_format"] = {"type": "json_object"}
            
        response = self.sync_client.chat.completions.create(**params)
        return response.choices[0].message.content
    
    def _parse_structured_output(self, content: str) -> Any:
        """Parse structured output if model specified / モデルが指定されている場合は構造化出力を解析"""
        if not self.output_model:
            return content
            
        try:
            # Parse JSON and validate with Pydantic model
            data = json.loads(content)
            return self.output_model.model_validate(data)
        except Exception:
            # Fallback to raw content if parsing fails
            return content
    
    def _evaluate_content(self, user_input: str, generated_content: Any) -> EvaluationResult:
        """Evaluate generated content / 生成されたコンテンツを評価"""
        evaluation_prompt = f"""
{self.evaluation_instructions}

User Input: {user_input}
Generated Content: {generated_content}

Please provide a score from 0 to 100 and brief feedback.
Return your response as JSON with 'score' and 'feedback' fields.
"""
        
        messages = [{"role": "user", "content": evaluation_prompt}]
        
        try:
            response = self.sync_client.chat.completions.create(
                model=self.evaluation_model,
                messages=messages,
                temperature=0.3,  # Lower temperature for evaluation
                response_format={"type": "json_object"},
                timeout=self.timeout
            )
            
            eval_data = json.loads(response.choices[0].message.content)
            score = float(eval_data.get("score", 0))
            feedback = eval_data.get("feedback", "")
            
            return EvaluationResult(
                score=score,
                passed=score >= self.threshold,
                feedback=feedback,
                metadata={"model": self.evaluation_model}
            )
            
        except Exception as e:
            # Fallback evaluation
            return EvaluationResult(
                score=0.0,
                passed=False,
                feedback=f"Evaluation failed: {str(e)}",
                metadata={"error": str(e)}
            )
    
    def _store_in_history(self, user_input: str, result: LLMResult) -> None:
        """Store interaction in history / 対話を履歴に保存"""
        interaction = {
            "user_input": user_input,
            "result": result.content,
            "success": result.success,
            "metadata": result.metadata,
            "timestamp": json.dumps({"pipeline": self.name}, ensure_ascii=False)
        }
        
        self._pipeline_history.append(interaction)
        
        # Add to session history for context
        session_entry = f"User: {user_input}\nAssistant: {result.content}"
        self.session_history.append(session_entry)
        
        # Trim history if needed
        if len(self.session_history) > self.history_size:
            self.session_history = self.session_history[-self.history_size:]
    
    def clear_history(self) -> None:
        """Clear all history / 全履歴をクリア"""
        self._pipeline_history.clear()
        self.session_history.clear()
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get pipeline history / パイプライン履歴を取得"""
        return self._pipeline_history.copy()
    
    def update_instructions(
        self, 
        generation_instructions: Optional[str] = None,
        evaluation_instructions: Optional[str] = None
    ) -> None:
        """Update instructions / 指示を更新"""
        if generation_instructions:
            self.generation_instructions = generation_instructions
        if evaluation_instructions:
            self.evaluation_instructions = evaluation_instructions
    
    def set_threshold(self, threshold: float) -> None:
        """Set evaluation threshold / 評価閾値を設定"""
        if 0 <= threshold <= 100:
            self.threshold = threshold
        else:
            raise ValueError("Threshold must be between 0 and 100")
    
    def __str__(self) -> str:
        return f"LLMPipeline(name={self.name}, model={self.model})"
    
    def __repr__(self) -> str:
        return self.__str__()


# Utility functions for common configurations
# 共通設定用のユーティリティ関数

def create_simple_llm_pipeline(
    name: str,
    instructions: str,
    model: str = "gpt-4o-mini",
    **kwargs
) -> LLMPipeline:
    """
    Create a simple LLM pipeline
    シンプルなLLMパイプラインを作成
    """
    return LLMPipeline(
        name=name,
        generation_instructions=instructions,
        model=model,
        **kwargs
    )


def create_evaluated_llm_pipeline(
    name: str,
    generation_instructions: str,
    evaluation_instructions: str,
    model: str = "gpt-4o-mini",
    evaluation_model: Optional[str] = None,
    threshold: float = 85.0,
    **kwargs
) -> LLMPipeline:
    """
    Create an LLM pipeline with evaluation
    評価機能付きLLMパイプラインを作成
    """
    return LLMPipeline(
        name=name,
        generation_instructions=generation_instructions,
        evaluation_instructions=evaluation_instructions,
        model=model,
        evaluation_model=evaluation_model,
        threshold=threshold,
        **kwargs
    ) 