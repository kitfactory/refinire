from __future__ import annotations

"""Pipeline — ultra‑light builder for OpenAI Agents SDK.

v1.5  — **Guardrails 対応**
   • 生成・評価それぞれに `generation_guardrails` / `evaluation_guardrails` を追加
   • `Agent(..., guardrails=…)` に注入して実行時に適用
"""

from dataclasses import dataclass, is_dataclass
from typing import Callable, List, Dict, Any, Optional, Type
import json
import re

from agents import Agent, Runner
from agents_sdk_models.llm import get_llm

try:
    from pydantic import BaseModel  # type: ignore
except ImportError:
    BaseModel = object  # type: ignore


@dataclass
class EvaluationResult:
    """
    Result of evaluation for generated content
    生成されたコンテンツの評価結果を保持するクラス
    """
    score: int  # Evaluation score (0-100) / 評価スコア（0-100）
    comment: List[str]  # List of evaluation comments / 評価コメントのリスト


class Pipeline:
    """
    Pipeline class for managing the generation and evaluation of content using OpenAI Agents SDK
    OpenAI Agents SDKを使用してコンテンツの生成と評価を管理するパイプラインクラス

    This class handles:
    このクラスは以下を処理します：
    - Content generation using templates / テンプレートを使用したコンテンツ生成
    - Content evaluation with scoring / スコアリングによるコンテンツ評価
    - Session history management / セッション履歴の管理
    - Output formatting and routing / 出力のフォーマットとルーティング
    """

    def __init__(
        self,
        name: str,
        generation_instructions: str,
        evaluation_instructions: Optional[str],
        *,
        input_guardrails: Optional[list] = None,
        output_guardrails: Optional[list] = None,
        output_model: Optional[Type[Any]] = None,
        model: str | None = None,
        generation_tools: Optional[list] = None,
        evaluation_tools: Optional[list] = None,
        routing_func: Optional[Callable[[Any], Any]] = None,
        session_history: Optional[list] = None,
        history_size: int = 10,
        threshold: int = 85,
        retries: int = 3,
        debug: bool = False,
        improvement_callback: Optional[Callable[[Any, EvaluationResult], None]] = None,
    ) -> None:
        """
        Initialize the Pipeline with configuration parameters
        設定パラメータでパイプラインを初期化する

        Args:
            name: Pipeline name / パイプライン名
            generation_instructions: System prompt for generation / 生成用システムプロンプト
            evaluation_instructions: System prompt for evaluation / 評価用システムプロンプト
            input_guardrails: Guardrails for generation / 生成用ガードレール
            output_guardrails: Guardrails for evaluation / 評価用ガードレール
            output_model: Model for output formatting / 出力フォーマット用モデル
            model: LLM model name / LLMモデル名
            generation_tools: Tools for generation / 生成用ツール
            evaluation_tools: Tools for evaluation / 評価用ツール
            routing_func: Function for output routing / 出力ルーティング用関数
            session_history: Session history / セッション履歴
            history_size: Size of history to keep / 保持する履歴サイズ
            threshold: Evaluation score threshold / 評価スコアの閾値
            retries: Number of retry attempts / リトライ試行回数
            debug: Debug mode flag / デバッグモードフラグ
            improvement_callback: Callback for improvement suggestions / 改善提案用コールバック
        """
        self.name = name
        self.generation_instructions = generation_instructions.strip()
        self.evaluation_instructions = evaluation_instructions.strip() if evaluation_instructions else None
        self.output_model = output_model

        self.model = model
        self.generation_tools = generation_tools or []
        self.evaluation_tools = evaluation_tools or []
        self.input_guardrails = input_guardrails or []
        self.output_guardrails = output_guardrails or []
        self.routing_func = routing_func
        self.session_history = session_history if session_history is not None else []
        self.history_size = history_size
        self.threshold = threshold
        self.retries = retries
        self.debug = debug
        self.improvement_callback = improvement_callback

        # Get LLM instance
        llm = get_llm(model) if model else None

        # Agents ---------------------------------------------------------
        self.gen_agent = Agent(
            name=f"{name}_generator",
            model=llm,
            tools=self.generation_tools,
            instructions=self.generation_instructions,
            input_guardrails=self.input_guardrails,
        )
        self.eval_agent = (
            Agent(
                name=f"{name}_evaluator",
                model=llm,
                tools=self.evaluation_tools,
                instructions=self.evaluation_instructions,
                output_guardrails=self.output_guardrails,
            )
            if self.evaluation_instructions
            else None
        )

        self._runner = Runner()
        self._pipeline_history: List[Dict[str, str]] = []

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _build_generation_prompt(self, user_input: str) -> str:
        """
        Build the prompt for content generation
        コンテンツ生成用のプロンプトを構築する

        Args:
            user_input: User input text / ユーザー入力テキスト

        Returns:
            str: Formatted prompt for generation / 生成用のフォーマット済みプロンプト
        """
        recent = "\n".join(f"User: {h['input']}\nAI: {h['output']}"
                          for h in self._pipeline_history[-self.history_size:])
        session = "\n".join(self.session_history)
        return "\n".join(filter(None, [session, recent, f"UserInput: {user_input}"]))

    def _build_evaluation_prompt(self, user_input: str, generated_output: str) -> str:
        """
        Build the prompt for content evaluation
        コンテンツ評価用のプロンプトを構築する

        Args:
            user_input: Original user input / 元のユーザー入力
            generated_output: Generated content to evaluate / 評価対象の生成コンテンツ

        Returns:
            str: Formatted prompt for evaluation / 評価用のフォーマット済みプロンプト
        """
        json_instr = "上記を JSON で次の形式にしてください:\n{\n  \"score\": int,\n  \"comment\": [str]\n}"
        parts = [
            self.evaluation_instructions or "",
            json_instr,
            "----",
            f"ユーザー入力:\n{user_input}",
            "----",
            f"生成結果:\n{generated_output}",
        ]
        return "\n".join(filter(None, parts)).strip()

    @staticmethod
    def _extract_json(text: str) -> Dict[str, Any]:
        """
        Extract JSON from text
        テキストからJSONを抽出する

        Args:
            text: Text containing JSON / JSONを含むテキスト

        Returns:
            Dict[str, Any]: Extracted JSON data / 抽出されたJSONデータ

        Raises:
            ValueError: If JSON is not found in text / テキスト内にJSONが見つからない場合
        """
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            raise ValueError("JSON not found in evaluation output")
        return json.loads(match.group(0))

    def _coerce_output(self, text: str):
        """
        Convert output to specified model format
        出力を指定されたモデル形式に変換する

        Args:
            text: Output text to convert / 変換対象の出力テキスト

        Returns:
            Any: Converted output in specified format / 指定された形式の変換済み出力
        """
        if self.output_model is None:
            return text
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return text
        try:
            if isinstance(self.output_model, type) and issubclass(self.output_model, BaseModel):
                return self.output_model.model_validate(data)
            if is_dataclass(self.output_model):
                return self.output_model(**data)
            return self.output_model(**data)
        except Exception:
            return text

    def _append_to_session(self, user_input: str, raw_output: str):
        """
        Append interaction to session history
        セッション履歴にインタラクションを追加する

        Args:
            user_input: User input text / ユーザー入力テキスト
            raw_output: Generated output text / 生成された出力テキスト
        """
        if self.session_history is None:
            return
        self.session_history.append(f"User: {user_input}\nAI: {raw_output}")

    def _route(self, parsed_output):
        """
        Route the parsed output through routing function if specified
        指定されている場合、パース済み出力をルーティング関数で処理する

        Args:
            parsed_output: Parsed output to route / ルーティング対象のパース済み出力

        Returns:
            Any: Routed output / ルーティング済み出力
        """
        return self.routing_func(parsed_output) if self.routing_func else parsed_output

    # ------------------------------------------------------------------
    # public
    # ------------------------------------------------------------------

    def run(self, user_input: str):
        """
        Run the pipeline with user input
        ユーザー入力でパイプラインを実行する

        Args:
            user_input: User input text / ユーザー入力テキスト

        Returns:
            Any: Processed output or None if evaluation fails / 処理済み出力、または評価失敗時はNone
        """
        attempt = 0
        while attempt <= self.retries:
            # ---------------- Generation ----------------
            gen_prompt = self._build_generation_prompt(user_input)
            if self.debug:
                print("[Generation prompt]\n", gen_prompt)

            gen_result = self._runner.run_sync(self.gen_agent, gen_prompt)
            raw_output_text = getattr(gen_result, "final_output", str(gen_result))
            if hasattr(gen_result, "tool_calls") and gen_result.tool_calls:
                raw_output_text = str(gen_result.tool_calls[0].call())

            parsed_output = self._coerce_output(raw_output_text)
            self._pipeline_history.append({"input": user_input, "output": raw_output_text})

            # ---------------- Evaluation ----------------
            if not self.eval_agent:
                return self._route(parsed_output)

            eval_prompt = self._build_evaluation_prompt(user_input, raw_output_text)
            if self.debug:
                print("[Evaluation prompt]\n", eval_prompt)

            eval_raw = self._runner.run_sync(self.eval_agent, eval_prompt)
            eval_text = getattr(eval_raw, "final_output", str(eval_raw))
            try:
                eval_dict = self._extract_json(eval_text)
                eval_result = EvaluationResult(**eval_dict)
            except Exception:
                eval_result = EvaluationResult(score=0, comment=["評価 JSON の解析に失敗"])

            if self.debug:
                print("[Evaluation result]", eval_result)

            if eval_result.score >= self.threshold:
                self._append_to_session(user_input, raw_output_text)
                return self._route(parsed_output)

            attempt += 1

        if self.improvement_callback:
            self.improvement_callback(parsed_output, eval_result)
        return None
