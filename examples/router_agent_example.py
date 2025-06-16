"""
RouterAgent Usage Examples

RouterAgentの使用例

This example demonstrates how to use RouterAgent for routing inputs
to different processing paths based on classification.
この例では、分類に基づいて入力を異なる処理パスにルーティングする
RouterAgentの使用方法を示します。
"""

import os
from typing import Any

# Set up environment for examples
# 例のための環境設定
os.environ.setdefault("OPENAI_API_KEY", "your-api-key-here")

from refinire.agents.router import (
    RouterAgent,
    RouterConfig,
    RuleBasedClassifier,
    create_intent_router,
    create_content_type_router
)
from refinire.context import Context
from refinire.pipeline.llm_pipeline import create_simple_llm_pipeline


def example_1_basic_llm_router():
    """
    Example 1: Basic LLM-based routing
    例1: 基本的なLLMベースルーティング
    """
    print("=== Example 1: Basic LLM-based Router ===")
    print("=== 例1: 基本的なLLMベースルーター ===")
    
    # Create router configuration
    # ルーター設定を作成
    config = RouterConfig(
        name="basic_router",
        routes={
            "greeting": "greeting_handler",
            "question": "qa_handler", 
            "complaint": "support_handler",
            "other": "general_handler"
        },
        classifier_type="llm",
        classification_prompt="""
Classify the user input into one of these categories:
- greeting: User is saying hello, hi, good morning, etc.
- question: User is asking a question
- complaint: User is expressing dissatisfaction
- other: Anything else

Respond with only the category name.
""",
        classification_examples={
            "greeting": ["Hello", "Hi there", "Good morning"],
            "question": ["How does this work?", "What is your name?"],
            "complaint": ["This is broken", "I'm not happy with the service"]
        }
    )
    
    # Create LLM pipeline (you would use a real API key in practice)
    # LLMパイプラインを作成（実際にはリアルなAPIキーを使用）
    try:
        pipeline = create_simple_llm_pipeline()
        router = RouterAgent(config, pipeline)
        
        # Test different inputs
        # 異なる入力をテスト
        test_inputs = [
            "Hello there!",
            "How can I reset my password?", 
            "This service is terrible!",
            "I need some help with my account"
        ]
        
        for input_text in test_inputs:
            context = Context()
            print(f"\nInput: {input_text}")
            
            # Run router (in real usage, this would be part of a Flow)
            # ルーターを実行（実際の使用では、これはFlowの一部になります）
            result = router.run(input_text, context)
            
            classification = context.shared_state.get("basic_router_classification")
            next_step = context.shared_state.get("next_step")
            
            print(f"Classification: {classification}")
            print(f"Next step: {next_step}")
            
    except Exception as e:
        print(f"Note: This example requires a valid OpenAI API key. Error: {e}")
        print("注意: この例には有効なOpenAI APIキーが必要です。")


def example_2_rule_based_router():
    """
    Example 2: Rule-based routing
    例2: ルールベースルーティング
    """
    print("\n=== Example 2: Rule-based Router ===")
    print("=== 例2: ルールベースルーター ===")
    
    # Define classification rules
    # 分類ルールを定義
    def is_email(input_data: Any, context: Context) -> bool:
        """Check if input contains email pattern"""
        text = str(input_data).lower()
        return "@" in text and "." in text
    
    def is_phone(input_data: Any, context: Context) -> bool:
        """Check if input contains phone pattern"""
        text = str(input_data)
        # Simple phone pattern check
        import re
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        return bool(re.search(phone_pattern, text))
    
    def is_url(input_data: Any, context: Context) -> bool:
        """Check if input contains URL pattern"""
        text = str(input_data).lower()
        return text.startswith(("http://", "https://", "www."))
    
    def is_default(input_data: Any, context: Context) -> bool:
        """Default case - always matches"""
        return True
    
    # Create rule-based router configuration
    # ルールベースルーター設定を作成
    config = RouterConfig(
        name="rule_router",
        routes={
            "email": "email_processor",
            "phone": "phone_processor",
            "url": "url_processor", 
            "text": "text_processor"
        },
        classifier_type="rule",
        classification_rules={
            "email": is_email,
            "phone": is_phone,
            "url": is_url,
            "text": is_default  # This will be the fallback
        }
    )
    
    router = RouterAgent(config)
    
    # Test different inputs
    # 異なる入力をテスト
    test_inputs = [
        "Contact me at john@example.com",
        "Call me at 555-123-4567",
        "Visit https://example.com",
        "This is just regular text"
    ]
    
    for input_text in test_inputs:
        context = Context()
        print(f"\nInput: {input_text}")
        
        result = router.run(input_text, context)
        
        classification = context.shared_state.get("rule_router_classification")
        next_step = context.shared_state.get("next_step")
        
        print(f"Classification: {classification}")
        print(f"Next step: {next_step}")


def example_3_intent_router():
    """
    Example 3: Using pre-built intent router
    例3: 事前構築された意図ルーターの使用
    """
    print("\n=== Example 3: Intent Router ===")
    print("=== 例3: 意図ルーター ===")
    
    # Create intent router with default intents
    # デフォルトの意図で意図ルーターを作成
    try:
        router = create_intent_router(
            name="customer_service_router",
            intents={
                "question": "faq_handler",
                "request": "service_handler",
                "complaint": "escalation_handler",
                "other": "general_handler"
            }
        )
        
        # Test customer service scenarios
        # カスタマーサービスシナリオをテスト
        test_inputs = [
            "How do I change my password?",
            "Please update my billing address",
            "Your service is down and I'm losing money!",
            "Thanks for your help"
        ]
        
        for input_text in test_inputs:
            context = Context()
            print(f"\nInput: {input_text}")
            
            result = router.run(input_text, context)
            
            classification = context.shared_state.get("customer_service_router_classification")
            next_step = context.shared_state.get("next_step")
            
            print(f"Intent: {classification}")
            print(f"Handler: {next_step}")
            
    except Exception as e:
        print(f"Note: This example requires a valid OpenAI API key. Error: {e}")
        print("注意: この例には有効なOpenAI APIキーが必要です。")


def example_4_content_type_router():
    """
    Example 4: Using pre-built content type router
    例4: 事前構築されたコンテンツタイプルーターの使用
    """
    print("\n=== Example 4: Content Type Router ===")
    print("=== 例4: コンテンツタイプルーター ===")
    
    try:
        router = create_content_type_router(
            name="content_processor",
            content_types={
                "document": "document_analyzer",
                "code": "code_reviewer",
                "data": "data_validator",
                "image": "image_processor"
            }
        )
        
        # Test different content types
        # 異なるコンテンツタイプをテスト
        test_inputs = [
            "This is a business report about Q4 earnings...",
            "def hello_world():\n    print('Hello, World!')",
            '{"name": "John", "age": 30, "city": "New York"}',
            "Please analyze this chart showing sales data"
        ]
        
        for input_text in test_inputs:
            context = Context()
            print(f"\nInput: {input_text[:50]}...")
            
            result = router.run(input_text, context)
            
            classification = context.shared_state.get("content_processor_classification")
            next_step = context.shared_state.get("next_step")
            
            print(f"Content type: {classification}")
            print(f"Processor: {next_step}")
            
    except Exception as e:
        print(f"Note: This example requires a valid OpenAI API key. Error: {e}")
        print("注意: この例には有効なOpenAI APIキーが必要です。")


def example_5_router_with_default_route():
    """
    Example 5: Router with default route configuration
    例5: デフォルトルート設定付きルーター
    """
    print("\n=== Example 5: Router with Default Route ===")
    print("=== 例5: デフォルトルート付きルーター ===")
    
    # Create router with default route
    # デフォルトルート付きルーターを作成
    config = RouterConfig(
        name="safe_router",
        routes={
            "urgent": "urgent_handler",
            "normal": "normal_handler",
            "low": "low_priority_handler"
        },
        classifier_type="rule",
        classification_rules={
            "urgent": lambda x, ctx: "urgent" in str(x).lower() or "emergency" in str(x).lower(),
            "normal": lambda x, ctx: "normal" in str(x).lower() or "regular" in str(x).lower(),
            # Note: no rule for "low" - will use default
        },
        default_route="low",  # Fallback to low priority
        store_classification_result=True
    )
    
    router = RouterAgent(config)
    
    # Test inputs including edge cases
    # エッジケースを含む入力をテスト
    test_inputs = [
        "This is an urgent request!",
        "Normal processing please",
        "Something completely different",  # Will use default route
        "Random text here"  # Will also use default route
    ]
    
    for input_text in test_inputs:
        context = Context()
        print(f"\nInput: {input_text}")
        
        result = router.run(input_text, context)
        
        classification = context.shared_state.get("safe_router_classification")
        next_step = context.shared_state.get("next_step")
        error = context.shared_state.get("safe_router_error")
        
        print(f"Classification: {classification}")
        print(f"Next step: {next_step}")
        if error:
            print(f"Error: {error}")


def example_6_router_properties():
    """
    Example 6: Exploring router properties and configuration
    例6: ルーターのプロパティと設定の探索
    """
    print("\n=== Example 6: Router Properties ===")
    print("=== 例6: ルーターのプロパティ ===")
    
    # Create a router and explore its properties
    # ルーターを作成してプロパティを探索
    config = RouterConfig(
        name="demo_router",
        routes={"route1": "step1", "route2": "step2"},
        classifier_type="rule",
        classification_rules={
            "route1": lambda x, ctx: True  # Always matches
        },
        store_classification_result=True
    )
    
    router = RouterAgent(config)
    
    print(f"Router name: {router.name}")
    print(f"Router config: {router.config}")
    print(f"Available routes: {list(router.config.routes.keys())}")
    print(f"Route mappings: {router.config.routes}")
    print(f"Classifier type: {router.config.classifier_type}")
    print(f"Store results: {router.config.store_classification_result}")
    
    # Test the router
    # ルーターをテスト
    context = Context()
    result = router.run("test input", context)
    
    print(f"\nAfter routing:")
    print(f"Shared state: {context.shared_state}")
    print(f"Next step: {context.shared_state.get('next_step')}")


if __name__ == "__main__":
    """
    Run all examples
    全ての例を実行
    """
    print("RouterAgent Examples")
    print("RouterAgentの例")
    print("=" * 50)
    
    # Run examples
    # 例を実行
    example_1_basic_llm_router()
    example_2_rule_based_router()
    example_3_intent_router()
    example_4_content_type_router()
    example_5_router_with_default_route()
    example_6_router_properties()
    
    print("\n" + "=" * 50)
    print("All examples completed!")
    print("全ての例が完了しました！")
    print("\nNote: Examples using LLM classification require a valid OpenAI API key.")
    print("注意: LLM分類を使用する例には有効なOpenAI APIキーが必要です。") 
