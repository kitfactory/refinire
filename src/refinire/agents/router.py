"""
RouterAgent implementation for routing inputs based on classification.

The RouterAgent analyzes input data and routes it to appropriate processing paths
based on configurable routing logic and classification results.
"""
# RouterAgent implementation for routing inputs based on classification.
# RouterAgentは入力データを分析し、設定可能なルーティングロジックと分類結果に基づいて適切な処理パスにルーティングします。

from typing import Any, Dict, List, Optional, Union, Callable, Literal
from pydantic import BaseModel, Field, field_validator
from abc import ABC, abstractmethod
import logging

from .flow.step import Step
from .flow.context import Context
from .pipeline.llm_pipeline import RefinireAgent, create_simple_agent

logger = logging.getLogger(__name__)


class RouteClassifier(ABC):
    """
    Abstract base class for route classification logic.
    ルート分類ロジックの抽象基底クラス。
    """
    
    @abstractmethod
    def classify(self, input_data: Any, context: Context) -> str:
        """
        Classify input data and return the route key.
        入力データを分類してルートキーを返します。
        
        Args:
            input_data: The input data to classify / 分類する入力データ
            context: The execution context / 実行コンテキスト
            
        Returns:
            str: The route key for the classified input / 分類された入力のルートキー
        """
        pass


class LLMClassifier(RouteClassifier):
    """
    LLM-based classifier for route determination.
    ルート決定のためのLLMベース分類器。
    """
    
    def __init__(
        self,
        pipeline: RefinireAgent,
        classification_prompt: str,
        routes: List[str],
        examples: Optional[Dict[str, List[str]]] = None
    ):
        """
        Initialize LLM classifier.
        LLM分類器を初期化します。
        
        Args:
            pipeline: LLM pipeline for classification / 分類用のLLMパイプライン
            classification_prompt: Prompt template for classification / 分類用のプロンプトテンプレート
            routes: List of possible route keys / 可能なルートキーのリスト
            examples: Optional examples for each route / 各ルートのオプション例
        """
        self.pipeline = pipeline
        self.classification_prompt = classification_prompt
        self.routes = routes
        self.examples = examples or {}
    
    def classify(self, input_data: Any, context: Context) -> str:
        """
        Classify input using LLM.
        LLMを使用して入力を分類します。
        """
        # Build classification prompt with examples
        # 例を含む分類プロンプトを構築
        examples_text = ""
        if self.examples:
            examples_text = "\n\nExamples:\n"
            for route, example_list in self.examples.items():
                examples_text += f"Route '{route}':\n"
                for example in example_list:
                    examples_text += f"- {example}\n"
        
        routes_text = ", ".join(self.routes)
        
        full_prompt = f"""
{self.classification_prompt}

Available routes: {routes_text}
{examples_text}

Input to classify: {input_data}

Respond with only the route key (one of: {routes_text})
"""
        
        try:
            result = self.pipeline.run(full_prompt, context)
            
            # Clean and validate the result
            # 結果をクリーンアップして検証
            classified_route = result.strip().lower()
            
            # Find matching route (case insensitive)
            # 一致するルートを検索（大文字小文字を区別しない）
            for route in self.routes:
                if route.lower() == classified_route:
                    return route
            
            # If no exact match, try partial matching
            # 完全一致しない場合、部分一致を試行
            for route in self.routes:
                if route.lower() in classified_route or classified_route in route.lower():
                    logger.warning(f"Partial route match: '{classified_route}' -> '{route}'")
                    return route
            
            # Return None to let RouterAgent handle fallback
            # RouterAgentにフォールバックを処理させるためNoneを返す
            logger.warning(f"Could not classify input, returning None for RouterAgent fallback")
            return None
            
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return None  # Let RouterAgent handle fallback / RouterAgentにフォールバックを処理させる


class RuleBasedClassifier(RouteClassifier):
    """
    Rule-based classifier using callable functions.
    呼び出し可能な関数を使用したルールベース分類器。
    """
    
    def __init__(self, rules: Dict[str, Callable[[Any, Context], bool]]):
        """
        Initialize rule-based classifier.
        ルールベース分類器を初期化します。
        
        Args:
            rules: Dictionary mapping route keys to classification functions
                   ルートキーを分類関数にマッピングする辞書
        """
        self.rules = rules
    
    def classify(self, input_data: Any, context: Context) -> str:
        """
        Classify input using rules.
        ルールを使用して入力を分類します。
        """
        for route_key, rule_func in self.rules.items():
            try:
                if rule_func(input_data, context):
                    return route_key
            except Exception as e:
                logger.warning(f"Rule evaluation error for route '{route_key}': {e}")
                continue
        
        # If no rules match, return the first route as fallback
        # ルールに一致しない場合、最初のルートをフォールバックとして返す
        fallback_route = next(iter(self.rules.keys()))
        logger.warning(f"No rules matched, using fallback route: {fallback_route}")
        return fallback_route


class RouterConfig(BaseModel):
    """
    Configuration for RouterAgent.
    RouterAgentの設定。
    """
    
    name: str = Field(description="Name of the router agent / ルーターエージェントの名前")
    
    routes: Dict[str, str] = Field(
        description="Mapping of route keys to next step names / ルートキーから次のステップ名へのマッピング"
    )
    
    classifier_type: Literal["llm", "rule"] = Field(
        default="llm",
        description="Type of classifier to use / 使用する分類器のタイプ"
    )
    
    # LLM classifier options
    classification_prompt: Optional[str] = Field(
        default=None,
        description="Prompt for LLM classification / LLM分類用のプロンプト"
    )
    
    classification_examples: Optional[Dict[str, List[str]]] = Field(
        default=None,
        description="Examples for each route / 各ルートの例"
    )
    
    # Rule-based classifier options
    classification_rules: Optional[Dict[str, Callable[[Any, Context], bool]]] = Field(
        default=None,
        description="Rules for classification / 分類のためのルール"
    )
    
    # Fallback options
    default_route: Optional[str] = Field(
        default=None,
        description="Default route if classification fails / 分類が失敗した場合のデフォルトルート"
    )
    
    store_classification_result: bool = Field(
        default=True,
        description="Whether to store classification result in context / 分類結果をコンテキストに保存するかどうか"
    )
    
    @field_validator("routes")
    @classmethod
    def routes_not_empty(cls, v):
        """Validate that routes are not empty / ルートが空でないことを検証"""
        if not v:
            raise ValueError("Routes cannot be empty / ルートは空にできません")
        return v
    
    @field_validator("default_route")
    @classmethod
    def default_route_exists(cls, v, info):
        """Validate that default route exists in routes / デフォルトルートがルートに存在することを検証"""
        if v is not None and "routes" in info.data and v not in info.data["routes"]:
            raise ValueError(f"Default route '{v}' must exist in routes / デフォルトルート'{v}'はルートに存在する必要があります")
        return v


class RouterAgent(RefinireAgent):
    """
    Router agent that classifies input and routes to appropriate next steps.
    入力を分類して適切な次のステップにルーティングするルーターエージェント。
    
    The RouterAgent analyzes input data using either LLM-based or rule-based
    classification and determines which processing path the input should follow.
    RouterAgentはLLMベースまたはルールベースの分類を使用して入力データを分析し、
    入力がどの処理パスに従うべきかを決定します。
    """
    
    def __init__(self, config: RouterConfig, llm_pipeline: Optional[RefinireAgent] = None):
        """
        Initialize RouterAgent.
        RouterAgentを初期化します。
        
        Args:
            config: Router configuration / ルーター設定
            llm_pipeline: Optional LLM pipeline for LLM-based classification
                         LLMベース分類用のオプションのLLMパイプライン
        """
        # Initialize RefinireAgent base class
        # RefinireAgent基底クラスを初期化
        default_instructions = f"You are a routing agent that classifies input into categories: {', '.join(config.routes.keys())}"
        super().__init__(
            name=config.name,
            generation_instructions=config.classification_prompt or default_instructions,
            model="gpt-4o-mini"
        )
        self.config = config
        
        # Initialize classifier based on type
        # タイプに基づいて分類器を初期化
        if config.classifier_type == "llm":
            if llm_pipeline is None:
                # Create default LLM pipeline if none provided
                # 提供されていない場合はデフォルトのLLMパイプラインを作成
                llm_pipeline = create_simple_agent(
                    name="router_classifier",
                    instructions="You are a classification assistant. Classify the input text into the provided categories."
                )
            
            # Use provided prompt or create default
            # 提供されたプロンプトを使用するか、デフォルトを作成
            prompt = config.classification_prompt or self._create_default_classification_prompt()
            
            self.classifier = LLMClassifier(
                pipeline=llm_pipeline,
                classification_prompt=prompt,
                routes=list(config.routes.keys()),
                examples=config.classification_examples
            )
            
        elif config.classifier_type == "rule":
            if config.classification_rules is None:
                raise ValueError("classification_rules must be provided for rule-based classifier")
            
            self.classifier = RuleBasedClassifier(config.classification_rules)
            
        else:
            raise ValueError(f"Unsupported classifier type: {config.classifier_type}")
    
    def _create_default_classification_prompt(self) -> str:
        """
        Create default classification prompt.
        デフォルトの分類プロンプトを作成します。
        """
        return f"""
Classify the given input into one of the available routes.
Consider the context and content of the input to determine the most appropriate route.

Available routes: {', '.join(self.config.routes.keys())}

Choose the route that best matches the input's intent, content, or characteristics.
"""
    
    async def run_async(self, user_input: Optional[str], ctx: Context) -> Context:
        """
        Execute the routing logic.
        ルーティングロジックを実行します。
        
        Args:
            user_input: User input to classify and route / 分類・ルーティングするユーザー入力
            ctx: Execution context / 実行コンテキスト
            
        Returns:
            Context: Updated context with routing information / ルーティング情報を含む更新されたコンテキスト
        """
        # Update step info
        # ステップ情報を更新
        ctx.update_step_info(self.name)
        
        try:
            # Use user_input as input_data for classification
            # 分類にuser_inputをinput_dataとして使用
            input_data = user_input or ctx.get_user_input() or ""
            
            # Classify the input
            # 入力を分類
            route_key = self.classifier.classify(input_data, ctx)
            
            # Check if classification failed (returned None)
            # 分類が失敗したかチェック（Noneが返された）
            classification_failed = route_key is None
            
            # Validate route exists
            # ルートが存在することを検証
            if route_key is None or route_key not in self.config.routes:
                logger.warning(f"Invalid route key '{route_key}', using default")
                route_key = self.config.default_route or next(iter(self.config.routes.keys()))
            
            # Store classification result in context if requested
            # 要求された場合は分類結果をコンテキストに保存
            if self.config.store_classification_result:
                ctx.shared_state[f"{self.name}_classification"] = route_key
                ctx.shared_state[f"{self.name}_next_step"] = self.config.routes[route_key]
                
                # Store error info if classification failed
                # 分類が失敗した場合はエラー情報を保存
                if classification_failed:
                    ctx.shared_state[f"{self.name}_error"] = "Classification failed"
            
            # Set the next step for flow control
            # フロー制御用に次のステップを設定
            next_step_name = self.config.routes[route_key]
            ctx.goto(next_step_name)
            
            logger.info(f"RouterAgent '{self.name}' classified input as '{route_key}' -> '{next_step_name}'")
            
            return ctx
            
        except Exception as e:
            logger.error(f"RouterAgent '{self.name}' error: {e}")
            
            # Use fallback route
            # フォールバックルートを使用
            fallback_route = self.config.default_route or next(iter(self.config.routes.keys()))
            fallback_step = self.config.routes[fallback_route]
            
            ctx.goto(fallback_step)
            
            if self.config.store_classification_result:
                ctx.shared_state[f"{self.name}_classification"] = fallback_route
                ctx.shared_state[f"{self.name}_next_step"] = fallback_step
                ctx.shared_state[f"{self.name}_error"] = str(e)
            
            logger.info(f"RouterAgent '{self.name}' using fallback route '{fallback_route}' -> '{fallback_step}'")
            
            return ctx
    
    async def run_as_agent(self, user_input: Optional[str], ctx: Context) -> Context:
        """
        Execute RouterAgent using parent RefinireAgent functionality
        親のRefinireAgent機能を使用してRouterAgentを実行
        
        This method allows RouterAgent to be used as a regular RefinireAgent
        when routing features are not needed.
        このメソッドは、ルーティング機能が不要な場合にRouterAgentを
        通常のRefinireAgentとして使用可能にします。
        
        Args:
            user_input: User input for the agent / エージェント用ユーザー入力
            ctx: Current workflow context / 現在のワークフローコンテキスト
        
        Returns:
            Context: Updated context with agent results / エージェント結果付き更新済みコンテキスト
        """
        # Use parent RefinireAgent's run_async method for standard agent functionality
        # 標準エージェント橜能については親のRefinireAgentのrun_asyncメソッドを使用
        return await super().run_async(user_input, ctx)
    
    def route(self, input_text: str, context: Optional[Context] = None) -> str:
        """
        Direct routing method without Flow integration
        Flow統合なしの直接ルーティングメソッド
        
        Args:
            input_text: Text to classify and route / 分類・ルーティングするテキスト
            context: Optional context for classification / 分類用オプションコンテキスト
        
        Returns:
            str: Route destination / ルート先
        """
        if context is None:
            from .flow.context import Context
            context = Context()
        
        route_key = self.classifier.classify(input_text, context)
        
        if route_key is None or route_key not in self.config.routes:
            route_key = self.config.default_route or next(iter(self.config.routes.keys()))
        
        return self.config.routes[route_key]


# Utility functions for creating common router configurations
# 一般的なルーター設定を作成するためのユーティリティ関数

def create_intent_router(
    name: str = "intent_router",
    intents: Dict[str, str] = None,
    llm_pipeline: Optional[RefinireAgent] = None
) -> RouterAgent:
    """
    Create a router for intent-based routing.
    意図ベースのルーティング用のルーターを作成します。
    
    Args:
        name: Name of the router / ルーターの名前
        intents: Mapping of intent names to step names / 意図名からステップ名へのマッピング
        llm_pipeline: Optional LLM pipeline / オプションのLLMパイプライン
        
    Returns:
        RouterAgent: Configured intent router / 設定された意図ルーター
    """
    if intents is None:
        intents = {
            "question": "qa_step",
            "request": "service_step", 
            "complaint": "support_step",
            "other": "general_step"
        }
    
    config = RouterConfig(
        name=name,
        routes=intents,
        classifier_type="llm",
        classification_prompt="""
Analyze the user input and classify it based on the user's intent.

Intents:
- question: User is asking for information or clarification
- request: User is requesting a service or action
- complaint: User is expressing dissatisfaction or reporting a problem
- other: Input doesn't fit the above categories

Consider the tone, content, and context of the input to determine the intent.
""",
        classification_examples={
            "question": [
                "How does this work?",
                "What is the difference between X and Y?",
                "Can you explain this feature?"
            ],
            "request": [
                "Please update my account",
                "I need to change my password",
                "Can you help me set this up?"
            ],
            "complaint": [
                "This is not working properly",
                "I'm having issues with the service",
                "This is frustrating and needs to be fixed"
            ]
        }
    )
    
    return RouterAgent(config, llm_pipeline)


def create_content_type_router(
    name: str = "content_router",
    content_types: Dict[str, str] = None,
    llm_pipeline: Optional[RefinireAgent] = None
) -> RouterAgent:
    """
    Create a router for content type-based routing.
    コンテンツタイプベースのルーティング用のルーターを作成します。
    
    Args:
        name: Name of the router / ルーターの名前
        content_types: Mapping of content types to step names / コンテンツタイプからステップ名へのマッピング
        llm_pipeline: Optional LLM pipeline / オプションのLLMパイプライン
        
    Returns:
        RouterAgent: Configured content type router / 設定されたコンテンツタイプルーター
    """
    if content_types is None:
        content_types = {
            "document": "document_processor",
            "image": "image_processor",
            "code": "code_processor",
            "data": "data_processor"
        }
    
    config = RouterConfig(
        name=name,
        routes=content_types,
        classifier_type="llm", 
        classification_prompt="""
Analyze the input and classify it based on content type.

Content types:
- document: Text documents, articles, reports, letters
- image: Images, photos, diagrams, charts
- code: Programming code, scripts, configuration files
- data: Structured data, databases, spreadsheets, JSON/XML

Consider the format, structure, and content characteristics.
""",
        classification_examples={
            "document": [
                "This is a business report about quarterly results...",
                "Dear Sir/Madam, I am writing to inform you...",
                "Executive Summary: The following document outlines..."
            ],
            "code": [
                "def hello_world():\n    print('Hello, World!')",
                "SELECT * FROM users WHERE age > 18;",
                "{\n  \"name\": \"config\",\n  \"version\": \"1.0\"\n}"
            ]
        }
    )
    
    return RouterAgent(config, llm_pipeline)
