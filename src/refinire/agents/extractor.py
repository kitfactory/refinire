"""
ExtractorAgent implementation for information extraction from unstructured data.

ExtractorAgentは非構造化データから情報抽出を行うエージェントです。
テキスト、HTML、JSONなどの様々な形式から特定の情報を抽出し、
構造化されたデータとして出力します。
"""

import logging
import re
import json
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict, Union, Callable
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import html
from html.parser import HTMLParser
from urllib.parse import urlparse

from .flow.context import Context
from .flow.step import Step
from .pipeline.llm_pipeline import RefinireAgent

logger = logging.getLogger(__name__)


class ExtractionRule(ABC):
    """
    Abstract base class for extraction rules.
    抽出ルールの抽象基底クラス。
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize extraction rule.
        抽出ルールを初期化します。
        
        Args:
            name: Rule name / ルール名
            description: Rule description / ルールの説明
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    def extract(self, data: str, context: Context) -> Any:
        """
        Extract information from the data.
        データから情報を抽出します。
        
        Args:
            data: Input data to extract from / 抽出対象の入力データ
            context: Execution context / 実行コンテキスト
            
        Returns:
            Any: Extracted information / 抽出された情報
        """
        pass


class RegexExtractionRule(ExtractionRule):
    """
    Rule to extract information using regular expressions.
    正規表現を使って情報を抽出するルール。
    """
    
    def __init__(self, name: str, pattern: str, group: int = 0, multiple: bool = False):
        """
        Initialize regex extraction rule.
        正規表現抽出ルールを初期化します。
        
        Args:
            name: Rule name / ルール名
            pattern: Regular expression pattern / 正規表現パターン
            group: Capture group number to extract / 抽出するキャプチャグループ番号
            multiple: Whether to extract all matches / 全てのマッチを抽出するかどうか
        """
        super().__init__(name, f"Extract using regex pattern: {pattern}")
        self.pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        self.group = group
        self.multiple = multiple
    
    def extract(self, data: str, context: Context) -> Union[str, List[str], None]:
        """Extract using regex pattern."""
        if not isinstance(data, str):
            return None
        
        if self.multiple:
            matches = self.pattern.findall(data)
            return matches if matches else []
        else:
            match = self.pattern.search(data)
            if match:
                return match.group(self.group)
            return None


class EmailExtractionRule(RegexExtractionRule):
    """
    Rule to extract email addresses.
    メールアドレスを抽出するルール。
    """
    
    def __init__(self, name: str = "email_extractor", multiple: bool = True):
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        super().__init__(name, pattern, group=0, multiple=multiple)


class PhoneExtractionRule(RegexExtractionRule):
    """
    Rule to extract phone numbers.
    電話番号を抽出するルール。
    """
    
    def __init__(self, name: str = "phone_extractor", multiple: bool = True):
        # Pattern for various phone number formats
        pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        super().__init__(name, pattern, group=0, multiple=multiple)


class URLExtractionRule(RegexExtractionRule):
    """
    Rule to extract URLs.
    URLを抽出するルール。
    """
    
    def __init__(self, name: str = "url_extractor", multiple: bool = True):
        pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        super().__init__(name, pattern, group=0, multiple=multiple)


class DateExtractionRule(RegexExtractionRule):
    """
    Rule to extract dates in various formats.
    様々な形式の日付を抽出するルール。
    """
    
    def __init__(self, name: str = "date_extractor", multiple: bool = True):
        # Pattern for common date formats
        pattern = r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b'
        super().__init__(name, pattern, group=0, multiple=multiple)


class SimpleHTMLParser(HTMLParser):
    """
    Simple HTML parser using standard library.
    標準ライブラリを使ったシンプルなHTMLパーサー。
    """
    
    def __init__(self, target_tag: str = None, target_attribute: str = None):
        super().__init__()
        self.target_tag = target_tag.lower() if target_tag else None
        self.target_attribute = target_attribute
        self.results = []
        self.current_tag = None
        self.current_attrs = {}
        self.current_data = ""
        self.capture_data = False
    
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag.lower()
        self.current_attrs = dict(attrs)
        
        if self.target_tag and tag.lower() == self.target_tag:
            self.capture_data = True
            self.current_data = ""
            
            # If we want an attribute, extract it now
            if self.target_attribute and self.target_attribute in self.current_attrs:
                self.results.append(self.current_attrs[self.target_attribute])
                self.capture_data = False
    
    def handle_endtag(self, tag):
        if self.capture_data and tag.lower() == self.target_tag:
            if self.current_data.strip():
                self.results.append(self.current_data.strip())
            self.capture_data = False
            self.current_data = ""
    
    def handle_data(self, data):
        if self.capture_data:
            self.current_data += data


class HTMLExtractionRule(ExtractionRule):
    """
    Rule to extract information from HTML using basic tag matching.
    基本的なタグマッチングを使ってHTMLから情報を抽出するルール。
    """
    
    def __init__(self, name: str, tag: str = None, attribute: str = None, multiple: bool = False):
        """
        Initialize HTML extraction rule.
        HTML抽出ルールを初期化します。
        
        Args:
            name: Rule name / ルール名
            tag: HTML tag name / HTMLタグ名
            attribute: Attribute to extract / 抽出する属性
            multiple: Whether to extract from all matching elements / 全てのマッチする要素から抽出するかどうか
        """
        super().__init__(name, f"Extract from HTML using tag: {tag}")
        self.tag = tag
        self.attribute = attribute
        self.multiple = multiple
    
    def extract(self, data: str, context: Context) -> Union[str, List[str], None]:
        """Extract from HTML using standard library HTMLParser."""
        try:
            if not self.tag:
                # If no tag specified, try to extract all text content
                parser = HTMLParser()
                parser.feed(data)
                # Simple text extraction - remove HTML tags
                clean_text = re.sub(r'<[^>]+>', ' ', data)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                return clean_text if clean_text else None
            
            # Use custom parser for specific tag extraction
            parser = SimpleHTMLParser(self.tag, self.attribute)
            parser.feed(data)
            
            results = parser.results
            
            if not results:
                return [] if self.multiple else None
            
            if self.multiple:
                return results
            else:
                return results[0] if results else None
                
        except Exception as e:
            logger.warning(f"HTML extraction error: {e}")
            return [] if self.multiple else None


class JSONExtractionRule(ExtractionRule):
    """
    Rule to extract information from JSON using JSONPath-like syntax.
    JSONPath類似の構文を使ってJSONから情報を抽出するルール。
    """
    
    def __init__(self, name: str, path: str, multiple: bool = False):
        """
        Initialize JSON extraction rule.
        JSON抽出ルールを初期化します。
        
        Args:
            name: Rule name / ルール名
            path: JSONPath-like expression (e.g., "data.items.*.name") / JSONPath類似の式
            multiple: Whether to extract all matches / 全てのマッチを抽出するかどうか
        """
        super().__init__(name, f"Extract from JSON using path: {path}")
        self.path = path.split('.')
        self.multiple = multiple
    
    def extract(self, data: str, context: Context) -> Union[Any, List[Any], None]:
        """Extract from JSON using simple path traversal."""
        try:
            if isinstance(data, str):
                json_data = json.loads(data)
            else:
                json_data = data
            
            results = self._extract_from_path(json_data, self.path, 0)
            
            if self.multiple:
                return results if isinstance(results, list) else [results] if results is not None else []
            else:
                return results[0] if isinstance(results, list) and results else results
                
        except Exception as e:
            logger.warning(f"JSON extraction error: {e}")
            return [] if self.multiple else None
    
    def _extract_from_path(self, data: Any, path: List[str], index: int) -> Any:
        """Recursively extract data following the path."""
        if index >= len(path):
            return data
        
        key = path[index]
        
        if key == '*':
            # Wildcard - extract from all items
            if isinstance(data, list):
                results = []
                for item in data:
                    result = self._extract_from_path(item, path, index + 1)
                    if result is not None:
                        if isinstance(result, list):
                            results.extend(result)
                        else:
                            results.append(result)
                return results
            elif isinstance(data, dict):
                results = []
                for value in data.values():
                    result = self._extract_from_path(value, path, index + 1)
                    if result is not None:
                        if isinstance(result, list):
                            results.extend(result)
                        else:
                            results.append(result)
                return results
            else:
                return None
        else:
            # Specific key
            if isinstance(data, dict) and key in data:
                return self._extract_from_path(data[key], path, index + 1)
            elif isinstance(data, list) and key.isdigit():
                idx = int(key)
                if 0 <= idx < len(data):
                    return self._extract_from_path(data[idx], path, index + 1)
            
            return None


class LLMExtractionRule(ExtractionRule):
    """
    Rule to extract information using LLM with natural language prompts.
    自然言語プロンプトを使ってLLMで情報を抽出するルール。
    """
    
    def __init__(self, name: str, prompt: str, llm_pipeline: RefinireAgent = None,
                 output_format: str = "text", multiple: bool = False):
        """
        Initialize LLM extraction rule.
        LLM抽出ルールを初期化します。
        
        Args:
            name: Rule name / ルール名
            prompt: Extraction prompt / 抽出プロンプト
            llm_pipeline: LLM pipeline to use / 使用するLLMパイプライン
            output_format: Expected output format ("text", "json", "list") / 期待する出力形式
            multiple: Whether to extract multiple items / 複数のアイテムを抽出するかどうか
        """
        super().__init__(name, f"Extract using LLM with prompt: {prompt[:50]}...")
        self.prompt = prompt
        self.llm_pipeline = llm_pipeline
        self.output_format = output_format.lower()
        self.multiple = multiple
    
    def extract(self, data: str, context: Context) -> Union[Any, List[Any], None]:
        """Extract using LLM pipeline."""
        if not self.llm_pipeline:
            logger.warning(f"No LLM pipeline provided for {self.name}")
            return [] if self.multiple else None
        
        try:
            # Create extraction prompt
            full_prompt = f"{self.prompt}\n\nInput data:\n{data}\n\nExtracted information:"
            
            # Use LLM to extract
            result = self.llm_pipeline.generate(full_prompt)
            
            if not result.success or not result.content:
                return [] if self.multiple else None
            
            extracted_text = result.content.strip()
            
            # Parse output based on format
            if self.output_format == "json":
                try:
                    parsed = json.loads(extracted_text)
                    return parsed
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse JSON output: {extracted_text}")
                    return [] if self.multiple else None
                    
            elif self.output_format == "list":
                # Split by lines and clean up
                lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
                return lines
            
            else:  # text format
                return extracted_text if extracted_text else ([] if self.multiple else None)
                
        except Exception as e:
            logger.error(f"LLM extraction error in {self.name}: {e}")
            return [] if self.multiple else None


class CustomFunctionExtractionRule(ExtractionRule):
    """
    Rule using a custom extraction function.
    カスタム抽出関数を使用するルール。
    """
    
    def __init__(self, name: str, extraction_func: Callable[[str, Context], Any]):
        """
        Initialize custom function extraction rule.
        カスタム関数抽出ルールを初期化します。
        
        Args:
            name: Rule name / ルール名
            extraction_func: Custom extraction function / カスタム抽出関数
        """
        super().__init__(name, "Custom extraction function")
        self.extraction_func = extraction_func
    
    def extract(self, data: str, context: Context) -> Any:
        """Extract using custom function."""
        try:
            return self.extraction_func(data, context)
        except Exception as e:
            logger.warning(f"Custom extraction function error: {e}")
            return None


class ExtractionResult:
    """
    Result of extraction operation.
    抽出操作の結果。
    """
    
    def __init__(self, extracted_data: Dict[str, Any], success: bool = True, 
                 errors: List[str] = None, warnings: List[str] = None):
        """
        Initialize extraction result.
        抽出結果を初期化します。
        
        Args:
            extracted_data: Extracted data by rule name / ルール名別の抽出データ
            success: Whether extraction was successful / 抽出が成功したかどうか
            errors: List of error messages / エラーメッセージのリスト
            warnings: List of warning messages / 警告メッセージのリスト
        """
        self.extracted_data = extracted_data
        self.success = success
        self.errors = errors or []
        self.warnings = warnings or []
        self.timestamp = datetime.now()
    
    def add_error(self, error: str):
        """Add an error message."""
        self.errors.append(error)
        self.success = False
    
    def add_warning(self, warning: str):
        """Add a warning message."""
        self.warnings.append(warning)
    
    def get_extracted(self, rule_name: str) -> Any:
        """Get extracted data for a specific rule."""
        return self.extracted_data.get(rule_name)
    
    def __str__(self) -> str:
        status = "SUCCESS" if self.success else "FAILED"
        return f"ExtractionResult({status}, {len(self.extracted_data)} rules, {len(self.errors)} errors)"


class ExtractorConfig(BaseModel):
    """
    Configuration for ExtractorAgent.
    ExtractorAgentの設定。
    """
    
    name: str = Field(description="Name of the extractor agent / エクストラクターエージェントの名前")
    
    rules: List[Dict[str, Any]] = Field(
        default=[],
        description="List of extraction rules configuration / 抽出ルール設定のリスト"
    )
    
    input_format: str = Field(
        default="auto",
        description="Expected input format (auto, text, html, json) / 期待する入力形式"
    )
    
    store_result: bool = Field(
        default=True,
        description="Store extraction result in context / 抽出結果をコンテキストに保存"
    )
    
    fail_on_error: bool = Field(
        default=False,
        description="Fail if any extraction rule fails / いずれかの抽出ルールが失敗した場合に失敗する"
    )
    
    @field_validator("input_format")
    @classmethod
    def validate_input_format(cls, v):
        """Validate input format."""
        allowed_formats = ["auto", "text", "html", "json"]
        if v not in allowed_formats:
            raise ValueError(f"input_format must be one of {allowed_formats}")
        return v


class ExtractorAgent(Step):
    """
    Extractor agent for information extraction from unstructured data.
    非構造化データから情報抽出を行うエクストラクターエージェント。
    
    The ExtractorAgent processes input data and extracts specific information
    using configured extraction rules (regex, HTML, JSON, LLM-based).
    ExtractorAgentは入力データを処理し、設定された抽出ルール
    （正規表現、HTML、JSON、LLMベース）を使って特定の情報を抽出します。
    """
    
    def __init__(self, config: ExtractorConfig, custom_rules: List[ExtractionRule] = None,
                 llm_pipeline: RefinireAgent = None):
        """
        Initialize ExtractorAgent.
        ExtractorAgentを初期化します。
        
        Args:
            config: Extractor configuration / エクストラクター設定
            custom_rules: Optional custom extraction rules / オプションのカスタム抽出ルール
            llm_pipeline: LLM pipeline for LLM-based extraction / LLMベース抽出用のLLMパイプライン
        """
        super().__init__(name=config.name)
        self.config = config
        self.llm_pipeline = llm_pipeline
        self.extraction_rules = self._build_extraction_rules(custom_rules or [])
    
    def _build_extraction_rules(self, custom_rules: List[ExtractionRule]) -> List[ExtractionRule]:
        """
        Build extraction rules from configuration and custom rules.
        設定とカスタムルールから抽出ルールを構築します。
        """
        rules = list(custom_rules)
        
        # Build rules from configuration
        # 設定からルールを構築
        for rule_config in self.config.rules:
            rule_type = rule_config.get("type")
            rule_name = rule_config.get("name", rule_type)
            
            if rule_type == "regex":
                pattern = rule_config.get("pattern")
                group = rule_config.get("group", 0)
                multiple = rule_config.get("multiple", False)
                if pattern:
                    rules.append(RegexExtractionRule(rule_name, pattern, group, multiple))
                    
            elif rule_type == "email":
                multiple = rule_config.get("multiple", True)
                rules.append(EmailExtractionRule(rule_name, multiple))
                
            elif rule_type == "phone":
                multiple = rule_config.get("multiple", True)
                rules.append(PhoneExtractionRule(rule_name, multiple))
                
            elif rule_type == "url":
                multiple = rule_config.get("multiple", True)
                rules.append(URLExtractionRule(rule_name, multiple))
                
            elif rule_type == "date":
                multiple = rule_config.get("multiple", True)
                rules.append(DateExtractionRule(rule_name, multiple))
                
            elif rule_type == "html":
                tag = rule_config.get("tag")
                attribute = rule_config.get("attribute")
                multiple = rule_config.get("multiple", False)
                rules.append(HTMLExtractionRule(rule_name, tag, attribute, multiple))
                
            elif rule_type == "json":
                path = rule_config.get("path")
                multiple = rule_config.get("multiple", False)
                if path:
                    rules.append(JSONExtractionRule(rule_name, path, multiple))
                    
            elif rule_type == "llm":
                prompt = rule_config.get("prompt")
                output_format = rule_config.get("output_format", "text")
                multiple = rule_config.get("multiple", False)
                if prompt:
                    rules.append(LLMExtractionRule(rule_name, prompt, self.llm_pipeline, 
                                                 output_format, multiple))
                    
            else:
                logger.warning(f"Unknown rule type: {rule_type}")
        
        return rules
    
    async def run_async(self, user_input: Optional[str], ctx: Context) -> Context:
        """
        Execute the extraction logic.
        抽出ロジックを実行します。
        
        Args:
            user_input: User input to extract from / 抽出対象のユーザー入力
            ctx: Execution context / 実行コンテキスト
            
        Returns:
            Context: Updated context with extraction results / 抽出結果を含む更新されたコンテキスト
        """
        # Update step info
        # ステップ情報を更新
        ctx.update_step_info(self.name)
        
        try:
            # Determine data to extract from
            # 抽出対象のデータを決定
            data_to_extract = user_input
            if data_to_extract is None:
                data_to_extract = ctx.last_user_input
            
            if not data_to_extract:
                logger.warning(f"No input data provided for extraction in {self.name}")
                data_to_extract = ""
            
            # Perform extraction
            # 抽出を実行
            extraction_result = self._extract_data(data_to_extract, ctx)
            
            # Store result in context if requested
            # 要求された場合は結果をコンテキストに保存
            if self.config.store_result:
                ctx.shared_state[f"{self.name}_result"] = {
                    "extracted_data": extraction_result.extracted_data,
                    "success": extraction_result.success,
                    "errors": extraction_result.errors,
                    "warnings": extraction_result.warnings,
                    "timestamp": extraction_result.timestamp.isoformat()
                }
            
            # Handle extraction failure
            # 抽出失敗を処理
            if not extraction_result.success:
                error_summary = f"Extraction failed: {', '.join(extraction_result.errors)}"
                
                if self.config.fail_on_error:
                    raise ValueError(error_summary)
                
                logger.warning(f"ExtractorAgent '{self.name}': {error_summary}")
                ctx.shared_state[f"{self.name}_status"] = "failed"
            else:
                logger.info(f"ExtractorAgent '{self.name}': Extraction successful, "
                          f"{len(extraction_result.extracted_data)} rules processed")
                ctx.shared_state[f"{self.name}_status"] = "success"
            
            # Add warnings to context if any
            # 警告があればコンテキストに追加
            if extraction_result.warnings:
                ctx.shared_state[f"{self.name}_warnings"] = extraction_result.warnings
            
            # Store individual extracted data for easy access
            # 簡単なアクセスのために個別の抽出データを保存
            for rule_name, extracted_value in extraction_result.extracted_data.items():
                ctx.shared_state[f"{self.name}_{rule_name}"] = extracted_value
            
            return ctx
            
        except Exception as e:
            logger.error(f"ExtractorAgent '{self.name}' error: {e}")
            
            if self.config.store_result:
                ctx.shared_state[f"{self.name}_result"] = {
                    "extracted_data": {},
                    "success": False,
                    "errors": [str(e)],
                    "warnings": [],
                    "timestamp": datetime.now().isoformat()
                }
                ctx.shared_state[f"{self.name}_status"] = "error"
            
            if self.config.fail_on_error:
                raise
            
            return ctx
    
    async def run(self, user_input: Optional[str], ctx: Context) -> Context:
        """
        Backward compatibility method that calls run_async.
        run_asyncを呼び出す後方互換性メソッド。
        """
        return await self.run_async(user_input, ctx)
    
    def _extract_data(self, data: str, context: Context) -> ExtractionResult:
        """
        Extract data using all configured rules.
        設定された全てのルールを使ってデータを抽出します。
        """
        result = ExtractionResult({})
        
        for rule in self.extraction_rules:
            try:
                extracted_value = rule.extract(data, context)
                result.extracted_data[rule.name] = extracted_value
                
                if extracted_value is None or (isinstance(extracted_value, list) and not extracted_value):
                    result.add_warning(f"Rule '{rule.name}' extracted no data")
                    
            except Exception as e:
                error_message = f"Rule '{rule.name}' execution error: {e}"
                result.add_error(error_message)
                logger.warning(error_message)
        
        return result
    
    def add_rule(self, rule: ExtractionRule):
        """
        Add an extraction rule to the agent.
        エージェントに抽出ルールを追加します。
        """
        self.extraction_rules.append(rule)
    
    def get_rules(self) -> List[ExtractionRule]:
        """
        Get all extraction rules.
        全ての抽出ルールを取得します。
        """
        return self.extraction_rules.copy()


# Utility functions for creating common extractors
# 一般的なエクストラクターを作成するためのユーティリティ関数

def create_contact_extractor(name: str = "contact_extractor") -> ExtractorAgent:
    """
    Create an extractor for contact information (emails, phones, URLs).
    連絡先情報（メール、電話、URL）用のエクストラクターを作成します。
    """
    config = ExtractorConfig(
        name=name,
        rules=[
            {"type": "email", "name": "emails"},
            {"type": "phone", "name": "phones"},
            {"type": "url", "name": "urls"}
        ]
    )
    return ExtractorAgent(config)


def create_html_extractor(name: str, tags: Dict[str, str]) -> ExtractorAgent:
    """
    Create an extractor for HTML content using tag names.
    タグ名を使ったHTMLコンテンツ用のエクストラクターを作成します。
    
    Args:
        name: Extractor name / エクストラクター名
        tags: Mapping of rule names to HTML tag names / ルール名からHTMLタグ名へのマッピング
    """
    rules = []
    for rule_name, tag in tags.items():
        rules.append({
            "type": "html",
            "name": rule_name,
            "tag": tag,
            "multiple": True
        })
    
    config = ExtractorConfig(name=name, rules=rules)
    return ExtractorAgent(config)


def create_json_extractor(name: str, paths: Dict[str, str]) -> ExtractorAgent:
    """
    Create an extractor for JSON data using paths.
    パスを使ったJSONデータ用のエクストラクターを作成します。
    
    Args:
        name: Extractor name / エクストラクター名
        paths: Mapping of rule names to JSON paths / ルール名からJSONパスへのマッピング
    """
    rules = []
    for rule_name, path in paths.items():
        rules.append({
            "type": "json",
            "name": rule_name,
            "path": path,
            "multiple": False
        })
    
    config = ExtractorConfig(name=name, rules=rules)
    return ExtractorAgent(config)


def create_llm_extractor(name: str, prompts: Dict[str, str], 
                        llm_pipeline: RefinireAgent) -> ExtractorAgent:
    """
    Create an extractor using LLM with custom prompts.
    カスタムプロンプトを持つLLMを使ったエクストラクターを作成します。
    
    Args:
        name: Extractor name / エクストラクター名
        prompts: Mapping of rule names to extraction prompts / ルール名から抽出プロンプトへのマッピング
        llm_pipeline: LLM pipeline to use / 使用するLLMパイプライン
    """
    rules = []
    for rule_name, prompt in prompts.items():
        rules.append({
            "type": "llm",
            "name": rule_name,
            "prompt": prompt,
            "output_format": "text"
        })
    
    config = ExtractorConfig(name=name, rules=rules)
    return ExtractorAgent(config, llm_pipeline=llm_pipeline) 
