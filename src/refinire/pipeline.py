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
import textwrap  # English: Import textwrap for dedenting multi-line JSON instruction strings. 日本語: JSON指示文字列の字下げを削除するためにtextwrapをインポートします。
from enum import Enum  # English: Import Enum for defining comment importance levels. 日本語: コメント重要度レベル定義用Enumをインポートします。

from agents import Agent, Runner
from refinire.llm import get_llm
from refinire.message import get_message  # Import for localized messages

try:
    from pydantic import BaseModel  # type: ignore
except ImportError:
    BaseModel = object  # type: ignore

# English: Enum for comment importance levels.
# 日本語: コメントの重要度レベルを表す列挙型
class CommentImportance(Enum):
    SERIOUS = "serious"  # English: Serious importance. 日本語: シリアス
    NORMAL = "normal"    # English: Normal importance. 日本語: ノーマル
    MINOR = "minor"      # English: Minor importance. 日本語: マイナー

@dataclass
class Comment:
    """
    Evaluation comment with importance and content
    評価コメントの重要度と内容を保持するクラス

    Attributes:
        importance: Importance level of the comment (serious/normal/minor) / コメントの重要度レベル（シリアス/ノーマル/マイナー）
        content: Text content of the comment / コメント内容
    """
    importance: CommentImportance  # Importance level (serious/normal/minor) / 重要度レベル（シリアス/ノーマル/マイナー）
    content: str  # Comment text / コメント内容

@dataclass
class EvaluationResult:
    """
    Result of evaluation for generated content
    生成されたコンテンツの評価結果を保持するクラス

    Attributes:
        score: Evaluation score (0-100) / 評価スコア（0-100）
        comment: List of Comment instances containing importance and content / 重要度と内容を持つCommentクラスのリスト
    """
    score: int  # Evaluation score (0-100) / 評価スコア（0-100）
    comment: List[Comment]  # List of evaluation comments / 評価コメントのリスト


class AgentPipeline:
    """
    AgentPipeline class for managing the generation and evaluation of content using OpenAI Agents SDK
    OpenAI Agents SDKを使用してコンテンツの生成と評価を管理するパイプラインクラス

    .. deprecated:: 0.0.22
       AgentPipeline is deprecated and will be removed in v0.1.0. 
       Use GenAgent with Flow/Step architecture instead.
       See migration guide: docs/deprecation_plan.md

    This class handles:
    このクラスは以下を処理します：
    - Content generation using instructions / instructionsを使用したコンテンツ生成
    - Content evaluation with scoring / スコアリングによるコンテンツ評価
    - Session history management / セッション履歴の管理
    - Output formatting and routing / 出力のフォーマットとルーティング

    Preferred alternative:
    推奨代替手段：
    - Use GenAgent for single-step pipeline functionality
    - Use Flow/Step architecture for complex workflows
    - See examples/gen_agent_example.py for migration examples
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
        evaluation_model: str | None = None,
        generation_tools: Optional[list] = None,
        evaluation_tools: Optional[list] = None,
        routing_func: Optional[Callable[[Any], Any]] = None,
        session_history: Optional[list] = None,
        history_size: int = 10,
        threshold: int = 85,
        retries: int = 3,
        improvement_callback: Optional[Callable[[Any, EvaluationResult], None]] = None,
        dynamic_prompt: Optional[Callable[[str], str]] = None,
        retry_comment_importance: Optional[list[str]] = None,
        locale: str = "en",
    ) -> None:
        """
        Initialize the Pipeline with configuration parameters
        設定パラメータでパイプラインを初期化する

        .. deprecated:: 0.0.22
           AgentPipeline is deprecated and will be removed in v0.1.0. 
           Use GenAgent with Flow/Step architecture instead.
           See migration guide: docs/deprecation_plan.md

        Args:
            name: Pipeline name / パイプライン名
            generation_instructions: System prompt for generation / 生成用システムプロンプト
            evaluation_instructions: System prompt for evaluation / 評価用システムプロンプト
            input_guardrails: Guardrails for generation / 生成用ガードレール
            output_guardrails: Guardrails for evaluation / 評価用ガードレール
            output_model: Model for output formatting / 出力フォーマット用モデル
            model: LLM model name / LLMモデル名
            evaluation_model: Optional LLM model name for evaluation; if None, uses model. 日本語: 評価用のLLMモデル名（Noneの場合はmodelを使用）
            generation_tools: Tools for generation / 生成用ツール
            evaluation_tools: Tools for evaluation / 評価用ツール
            routing_func: Function for output routing / 出力ルーティング用関数
            session_history: Session history / セッション履歴
            history_size: Size of history to keep / 保持する履歴サイズ
            threshold: Evaluation score threshold / 評価スコアの閾値
            retries: Number of retry attempts / リトライ試行回数
            improvement_callback: Callback for improvement suggestions / 改善提案用コールバック
            dynamic_prompt: Optional function to dynamically build prompt / 動的プロンプト生成関数（任意）
            retry_comment_importance: Importance levels of comments to include on retry / リトライ時にプロンプトに含めるコメントの重大度レベル（任意）
            locale: Language code for localized messages ("en" or "ja")
        """
        import warnings
        warnings.warn(
            "AgentPipeline is deprecated and will be removed in v0.1.0. "
            "Use GenAgent with Flow/Step architecture instead. "
            "See migration guide: docs/deprecation_plan.md",
            DeprecationWarning,
            stacklevel=2
        )
        self.name = name
        self.generation_instructions = generation_instructions.strip()
        self.evaluation_instructions = evaluation_instructions.strip() if evaluation_instructions else None
        self.output_model = output_model

        self.model = model
        self.evaluation_model = evaluation_model
        self.generation_tools = generation_tools or []
        self.evaluation_tools = evaluation_tools or []
        self.input_guardrails = input_guardrails or []
        self.output_guardrails = output_guardrails or []
        self.routing_func = routing_func
        self.session_history = session_history if session_history is not None else []
        self.history_size = history_size
        self.threshold = threshold
        self.retries = retries
        self.improvement_callback = improvement_callback
        self.dynamic_prompt = dynamic_prompt
        self.retry_comment_importance = retry_comment_importance or []
        # Language code for localized messages ("en" or "ja")
        self.locale = locale

        # English: Get generation LLM instance; default tracing setting applied in get_llm
        # 日本語: 生成用LLMインスタンスを取得します。tracing設定はget_llm側でデフォルト値を使用
        llm = get_llm(model) if model else None
        # English: Determine evaluation LLM instance, fallback to generation model if evaluation_model is None
        # 日本語: 評価用LLMインスタンスを決定。evaluation_modelがNoneの場合は生成モデルを使用
        eval_source = evaluation_model if evaluation_model else model
        llm_eval = get_llm(eval_source) if eval_source else None

        # Agents ---------------------------------------------------------
        self.gen_agent = Agent(
            name=f"{name}_generator",
            model=llm,
            tools=self.generation_tools,
            instructions=self.generation_instructions,
            input_guardrails=self.input_guardrails,
        )

        # Localized evaluation format instructions
        format_header = get_message("eval_output_format_header", self.locale)
        schema_instruction = get_message("eval_json_schema_instruction", self.locale)
        # JSON schema remains unlocalized
        json_schema = textwrap.dedent("""\
        {
            "score": int(0～100),
            "comment": [
                {
                    "importance": "serious" | "normal" | "minor",  # Importance field / 重要度フィールド
                    "content": str  # Comment content / コメント内容
                }
            ]
        }
        """)
        json_instr = "\n".join(["+----", format_header, schema_instruction, json_schema])
        self.eval_agent = (
            Agent(
                name=f"{name}_evaluator",
                model=llm_eval,
                tools=self.evaluation_tools,
                instructions=self.evaluation_instructions + json_instr,
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
        # Use localized prefix for user input
        prefix = get_message("user_input_prefix", self.locale)
        return "\n".join(filter(None, [session, recent, f"{prefix} {user_input}"]))

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
        parts = []
        
        # Add evaluation instructions if provided
        # 評価指示が提供されている場合は追加
        if self.evaluation_instructions:
            parts.append(self.evaluation_instructions)
        
        parts.extend([
            "----",
            f"ユーザー入力:\n{user_input}",
            "----",
            f"生成結果:\n{generated_output}",
            "上記を JSON で必ず次の形式にしてください"
        ])
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

    async def run_async(self, user_input: str):
        """
        Run the pipeline asynchronously with user input
        ユーザー入力でパイプラインを非同期実行する

        Args:
            user_input: User input text / ユーザー入力テキスト

        Returns:
            Any: Processed output or None if evaluation fails / 処理済み出力、または評価失敗時はNone
        """
        attempt = 0
        last_eval_result: Optional[EvaluationResult] = None  # Store last evaluation result for retry
        while attempt <= self.retries:
            # ---------------- Generation ----------------
            # On retry, include prior evaluation comments if configured
            if attempt > 0 and last_eval_result and self.retry_comment_importance:
                # Filter comments by importance
                try:
                    comments = [c for c in last_eval_result.comment if c.get("importance") in self.retry_comment_importance]
                except Exception:
                    comments = []
                # Format serious comments with header
                # Localized header for evaluation feedback
                feedback_header = get_message("evaluation_feedback_header", self.locale)
                # English: Format each comment line. 日本語: 各コメント行をフォーマット
                formatted_comments = [f"- ({c.get('importance')}) {c.get('content')}" for c in comments]
                # English: Combine header and comment lines. 日本語: ヘッダーとコメント行を結合
                comment_block = "\n".join([feedback_header] + formatted_comments)
            else:
                comment_block = ""
            # Build base prompt
            if attempt > 0 and comment_block:
                if self.dynamic_prompt:
                    # English: Use dynamic prompt if provided. 日本語: dynamic_promptがあればそれを使用
                    gen_prompt = self.dynamic_prompt(user_input)
                else:
                    # Localized header for AI history
                    ai_history_header = get_message("ai_history_header", self.locale)
                    # English: Extract AI outputs from pipeline history, omit user inputs. 日本語: パイプライン履歴からAIの出力のみ取得
                    ai_outputs = "\n".join(h["output"] for h in self._pipeline_history[-self.history_size:])
                    # Localized prefix for user input line
                    prefix = get_message("user_input_prefix", self.locale)
                    # English: Current user input line. 日本語: 現在のユーザー入力行
                    user_input_line = f"{prefix} {user_input}"
                    # English: Combine AI outputs, feedback, and current user input. 日本語: AI出力、フィードバック、現在のユーザー入力を結合
                    gen_prompt = "\n\n".join([ai_history_header, ai_outputs, comment_block, user_input_line])
            else:
                if self.dynamic_prompt:
                    gen_prompt = self.dynamic_prompt(user_input)
                else:
                    gen_prompt = self._build_generation_prompt(user_input)

            from agents import Runner
            gen_result = await Runner.run(self.gen_agent, gen_prompt)
            raw_output_text = getattr(gen_result, "final_output", str(gen_result))
            if hasattr(gen_result, "tool_calls") and gen_result.tool_calls:
                raw_output_text = str(gen_result.tool_calls[0].call())

            parsed_output = self._coerce_output(raw_output_text)
            self._pipeline_history.append({"input": user_input, "output": raw_output_text})

            # ---------------- Evaluation ----------------
            if not self.eval_agent:
                return self._route(parsed_output)

            eval_prompt = self._build_evaluation_prompt(user_input, raw_output_text)

            eval_raw = await Runner.run(self.eval_agent, eval_prompt)
            eval_text = getattr(eval_raw, "final_output", str(eval_raw))
            try:
                eval_dict = self._extract_json(eval_text)
                eval_result = EvaluationResult(**eval_dict)
            except Exception:
                eval_result = EvaluationResult(score=0, comment=[Comment(importance=CommentImportance.SERIOUS, content="評価 JSON の解析に失敗")])

            if eval_result.score >= self.threshold:
                self._append_to_session(user_input, raw_output_text)
                return self._route(parsed_output)

            # Store for next retry
            last_eval_result = eval_result
            attempt += 1

        if self.improvement_callback:
            self.improvement_callback(parsed_output, eval_result)
        return None

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
        last_eval_result: Optional[EvaluationResult] = None  # Store last evaluation result for retry
        while attempt <= self.retries:
            # ---------------- Generation ----------------
            # On retry, include prior evaluation comments if configured
            if attempt > 0 and last_eval_result and self.retry_comment_importance:
                # Filter comments by importance
                try:
                    comments = [c for c in last_eval_result.comment if c.get("importance") in self.retry_comment_importance]
                except Exception:
                    comments = []
                # Format serious comments with header
                # Localized header for evaluation feedback
                feedback_header = get_message("evaluation_feedback_header", self.locale)
                # English: Format each comment line. 日本語: 各コメント行をフォーマット
                formatted_comments = [f"- ({c.get('importance')}) {c.get('content')}" for c in comments]
                # English: Combine header and comment lines. 日本語: ヘッダーとコメント行を結合
                comment_block = "\n".join([feedback_header] + formatted_comments)
            else:
                comment_block = ""
            # Build base prompt
            if attempt > 0 and comment_block:
                if self.dynamic_prompt:
                    # English: Use dynamic prompt if provided. 日本語: dynamic_promptがあればそれを使用
                    gen_prompt = self.dynamic_prompt(user_input)
                else:
                    # Localized header for AI history
                    ai_history_header = get_message("ai_history_header", self.locale)
                    # English: Extract AI outputs from pipeline history, omit user inputs. 日本語: パイプライン履歴からAIの出力のみ取得
                    ai_outputs = "\n".join(h["output"] for h in self._pipeline_history[-self.history_size:])
                    # Localized prefix for user input line
                    prefix = get_message("user_input_prefix", self.locale)
                    # English: Current user input line. 日本語: 現在のユーザー入力行
                    user_input_line = f"{prefix} {user_input}"
                    # English: Combine AI outputs, feedback, and current user input. 日本語: AI出力、フィードバック、現在のユーザー入力を結合
                    gen_prompt = "\n\n".join([ai_history_header, ai_outputs, comment_block, user_input_line])
            else:
                if self.dynamic_prompt:
                    gen_prompt = self.dynamic_prompt(user_input)
                else:
                    gen_prompt = self._build_generation_prompt(user_input)

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

            eval_raw = self._runner.run_sync(self.eval_agent, eval_prompt)
            eval_text = getattr(eval_raw, "final_output", str(eval_raw))
            try:
                eval_dict = self._extract_json(eval_text)
                eval_result = EvaluationResult(**eval_dict)
            except Exception:
                eval_result = EvaluationResult(score=0, comment=[Comment(importance=CommentImportance.SERIOUS, content="評価 JSON の解析に失敗")])

            if eval_result.score >= self.threshold:
                self._append_to_session(user_input, raw_output_text)
                return self._route(parsed_output)

            # Store for next retry
            last_eval_result = eval_result
            attempt += 1

        if self.improvement_callback:
            self.improvement_callback(parsed_output, eval_result)
        return None
