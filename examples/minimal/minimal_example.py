#!/usr/bin/env python3
"""
Minimal example of agents-sdk-models usage
agents-sdk-modelsの最小使用例

This module demonstrates the core features of the agents-sdk-models library:
このモジュールはagents-sdk-modelsライブラリの主要機能を示します:

- GenAgent for text generation
- ClarifyAgent for clarification
- Flow/Step for workflow management
- get_llm for multi-provider LLM access

Examples:
    Basic GenAgent usage:
    基本的なGenAgentの使用法:
    
    >>> import os
    >>> os.environ['OPENAI_API_KEY'] = 'your-api-key'  # doctest: +SKIP
    >>> from refinire import create_simple_gen_agent, get_llm  # doctest: +SKIP
    >>> llm = get_llm(provider="openai", model="gpt-4o-mini")  # doctest: +SKIP
    >>> agent = create_simple_gen_agent(llm=llm)  # doctest: +SKIP
    >>> result = agent.run("Hello, world!")  # doctest: +SKIP
    >>> isinstance(result.result, str)  # doctest: +SKIP
    True
"""

import os
import asyncio
from typing import Optional, Dict, Any

from refinire import (
    # GenAgent関連
    create_simple_gen_agent,
    create_evaluated_gen_agent,
    
    # ClarifyAgent関連
create_simple_clarify_agent,
create_evaluated_clarify_agent,
    
    # Flow/Step関連
    create_simple_flow,
    create_conditional_flow,
    UserInputStep,
    FunctionStep,
    ConditionStep,
    Context,
    Flow,
    
    # LLM関連
    get_llm,
    get_available_models_async
)


def example_genagent_simple() -> str:
    """
    Simple GenAgent example
    シンプルなGenAgentの例
    
    Returns:
        Generated text response
        生成されたテキストレスポンス
    
    Examples:
        >>> result = example_genagent_simple()  # doctest: +SKIP
        >>> isinstance(result, str)  # doctest: +SKIP
        True
    """
    # Create simple GenAgent
    # シンプルなGenAgentを作成
    agent = create_simple_gen_agent(
        name="simple_gen",
        instructions="あなたは親切なアシスタントです。ユーザーの質問に簡潔で分かりやすく答えてください。",
        model="gpt-4o-mini"
    )
    
    # Create context and run
    # コンテキストを作成して実行
    context = Context()
    context.add_user_message("こんにちは！日本の文化について簡潔に教えてください。")
    
    # Run the agent (it's async, so need to handle properly)
    # エージェントを実行（非同期なので適切に処理する必要があります）
    import asyncio
    result_context = asyncio.run(agent.run("こんにちは！日本の文化について簡潔に教えてください。", context))
    
    # Get result from the context
    # コンテキストから結果を取得
    return result_context.shared_state.get("simple_gen_result", "結果が見つかりません")


def example_genagent_with_evaluation() -> Dict[str, Any]:
    """
    GenAgent with evaluation example
    評価機能付きGenAgentの例
    
    Returns:
        Result with evaluation metrics
        評価指標付きの結果
    
    Examples:
        >>> result = example_genagent_with_evaluation()  # doctest: +SKIP
        >>> isinstance(result, dict)  # doctest: +SKIP
        True
        >>> 'result' in result  # doctest: +SKIP
        True
        >>> 'evaluation' in result  # doctest: +SKIP
        True
    """
    # Create evaluated GenAgent
    # 評価機能付きGenAgentを作成
    agent = create_evaluated_gen_agent(
        name="eval_gen",
        generation_instructions="人工知能の未来について200文字程度で分かりやすく説明してください。",
        evaluation_instructions="回答が200文字程度で、分かりやすく、正確な内容かを評価してください。",
        model="gpt-4o-mini"
    )
    
    # Create context and run with evaluation
    # コンテキストを作成して評価付きで実行
    context = Context()
    context.add_user_message("人工知能の未来について200文字程度で説明してください。")
    
    import asyncio
    result_context = asyncio.run(agent.run("人工知能の未来について200文字程度で説明してください。", context))
    
    return {
        'result': result_context.shared_state.get("eval_gen_result", "結果が見つかりません"),
        'evaluation': result_context.shared_state.get("eval_gen_evaluation", None)
    }


def example_clarify_agent() -> Dict[str, Any]:
    """
    ClarifyAgent example for handling ambiguous requests
    曖昧な要求を処理するClarifyAgentの例
    
    Returns:
        Clarification result
        明確化の結果
    
    Examples:
        >>> result = example_clarify_agent()  # doctest: +SKIP
        >>> isinstance(result, dict)  # doctest: +SKIP
        True
    """
    # Create ClarifyAgent
    # ClarifyAgentを作成
    agent = create_simple_clarify_agent(
        name="clarify_agent",
        instructions="ユーザーの曖昧な要求を明確にするために質問をしてください。要求が十分明確になったら、明確化された要求を出力してください。",
        model="gpt-4o-mini"
    )
    
    # Process ambiguous request
    # 曖昧な要求を処理
    ambiguous_request = "APIを作りたいです"
    context = Context()
    context.add_user_message(ambiguous_request)
    
    import asyncio
    result_context = asyncio.run(agent.run(ambiguous_request, context))
    
    return {
        'original_request': ambiguous_request,
        'clarified_request': result_context.shared_state.get("clarify_agent_result", "明確化中"),
        'questions': [msg.content for msg in result_context.messages if msg.role == "assistant"]
    }


def example_flow_simple() -> str:
    """
    Simple Flow example with steps
    ステップを含むシンプルなFlowの例
    
    Returns:
        Flow execution result
        Flow実行結果
    
    Examples:
        >>> result = example_flow_simple()  # doctest: +SKIP
        >>> isinstance(result, str)  # doctest: +SKIP
        True
    """
    # Create context with initial data
    # 初期データでコンテキストを作成
    context = Context()
    context.shared_state["user_name"] = "太郎"
    context.shared_state["task"] = "プログラミング学習"
    
    # Create function step
    # 関数ステップを作成
    def process_greeting(user_input: Optional[str], ctx: Context) -> Context:
        """Process greeting with user data / ユーザーデータで挨拶を処理"""
        name = ctx.shared_state.get("user_name", "名無し")
        task = ctx.shared_state.get("task", "何か")
        greeting = f"こんにちは、{name}さん！{task}について支援いたします。"
        ctx.shared_state["greeting"] = greeting
        # フローを終了するためにfinish()を呼ぶ
        ctx.finish()
        return ctx
    
    greeting_step = FunctionStep("greeting", process_greeting)
    
    # Create simple flow
    # シンプルなFlowを作成
    flow = create_simple_flow([("greeting", greeting_step)], context)
    
    # Execute flow
    # Flowを実行
    import asyncio
    result_context = asyncio.run(flow.run())
    
    return result_context.shared_state.get("greeting", "エラー")


def example_flow_conditional() -> str:
    """
    Conditional Flow example
    条件付きFlowの例
    
    Returns:
        Conditional flow result
        条件付きFlow結果
    
    Examples:
        >>> result = example_flow_conditional()  # doctest: +SKIP
        >>> isinstance(result, str)  # doctest: +SKIP
        True
    """
    # Create context
    # コンテキストを作成
    context = Context()
    context.shared_state["user_level"] = "beginner"
    
    # Create condition function
    # 条件関数を作成
    def is_beginner(ctx: Context) -> bool:
        """Check if user is beginner / ユーザーが初心者かチェック"""
        level = ctx.shared_state.get("user_level")
        return level == "beginner"
    
    # Create action functions
    # アクション関数を作成
    def beginner_action(user_input: Optional[str], ctx: Context) -> Context:
        """Action for beginners / 初心者向けアクション"""
        ctx.shared_state["message"] = "初心者向けのチュートリアルを開始します。"
        # フローを終了するためにfinish()を呼ぶ
        ctx.finish()
        return ctx
    
    def advanced_action(user_input: Optional[str], ctx: Context) -> Context:
        """Action for advanced users / 上級者向けアクション"""
        ctx.shared_state["message"] = "上級者向けのコンテンツを表示します。"
        # フローを終了するためにfinish()を呼ぶ
        ctx.finish()
        return ctx
    
    # Create condition step and action steps
    # 条件ステップとアクションステップを作成
    condition_step = ConditionStep("condition", is_beginner, "beginner", "advanced")
    beginner_step = FunctionStep("beginner", beginner_action)
    advanced_step = FunctionStep("advanced", advanced_action)
    
    # Create flow manually to handle conditional routing properly
    # 条件ルーティングを適切に処理するためにFlowを手動作成
    flow = Flow(
        start="condition",
        steps={
            "condition": condition_step,
            "beginner": beginner_step,
            "advanced": advanced_step
        },
        context=context
    )
    
    # Execute flow
    # Flowを実行
    import asyncio
    result_context = asyncio.run(flow.run())
    
    return result_context.shared_state.get("message", "エラー")


def example_multi_provider_llm() -> Dict[str, str]:
    """
    Multi-provider LLM example using get_llm
    get_llmを使用したマルチプロバイダーLLMの例
    
    Returns:
        Results from different providers
        異なるプロバイダーからの結果
    
    Examples:
        >>> result = example_multi_provider_llm()  # doctest: +SKIP
        >>> isinstance(result, dict)  # doctest: +SKIP
        True
        >>> 'providers' in result  # doctest: +SKIP
        True
    """
    prompt = "Hello in Japanese"
    results = {}
    
    # Available providers (based on environment)
    # 利用可能なプロバイダー（環境に基づく）
    providers_to_try = [
        ("openai", "gpt-4o-mini"),
        ("anthropic", "claude-3-haiku-20240307"),
        ("google", "gemini-1.5-flash"),
        ("ollama", "llama3.1:8b")
    ]
    
    for provider, model in providers_to_try:
        try:
            # Create GenAgent for each provider
            # 各プロバイダー用のGenAgentを作成
            agent = create_simple_gen_agent(
                name=f"agent_{provider}",
                instructions="ユーザーの質問に簡潔に答えてください。",
                model=model
            )
            
            # Create context and run generation (would need API keys in real usage)
            # コンテキストを作成して生成を実行（実際の使用にはAPIキーが必要）
            context = Context()
            context.add_user_message(prompt)
            
            import asyncio
            result_context = asyncio.run(agent.run(prompt, context))
            result_text = result_context.shared_state.get(f"agent_{provider}_result", "No result")
            results[f"{provider}_{model}"] = result_text[:100] + "..." if len(result_text) > 100 else result_text
            
        except Exception as e:
            results[f"{provider}_{model}"] = f"Error: {str(e)}"
    
    return {
        'prompt': prompt,
        'providers': results
    }


async def example_get_available_models() -> Dict[str, Any]:
    """
    Get available models example
    利用可能なモデルを取得する例
    
    Returns:
        Available models information
        利用可能なモデルの情報
    
    Examples:
        >>> import asyncio
        >>> result = asyncio.run(example_get_available_models())  # doctest: +SKIP
        >>> isinstance(result, dict)  # doctest: +SKIP
        True
    """
    try:
        # Get available models (async)
        # 利用可能なモデルを取得（非同期）
        models = await get_available_models_async("openai")
        
        return {
            'provider': 'openai',
            'models': [model.name for model in models[:5]],  # First 5 models
            'total_count': len(models)
        }
    except Exception as e:
        return {
            'provider': 'openai',
            'error': str(e),
            'models': []
        }


def main() -> None:
    """
    Main function demonstrating all examples
    すべての例を示すメイン関数
    """
    print("=== Minimal Examples of agents-sdk-models ===")
    print("=== agents-sdk-modelsの最小使用例 ===")
    
    # Check if API key is available
    # APIキーが利用可能かチェック
    if not os.getenv('OPENAI_API_KEY'):
        print("\n⚠️  Please set OPENAI_API_KEY environment variable for full functionality")
        print("⚠️  完全な機能のためにOPENAI_API_KEY環境変数を設定してください")
        print("\nRunning offline examples only...")
        print("オフライン例のみ実行中...")
        
        # Run only offline examples
        # オフライン例のみ実行
        print("\n3. Simple Flow / シンプルなFlow:")
        try:
            result = example_flow_simple()
            print(f"Result / 結果: {result}")
        except Exception as e:
            print(f"Error / エラー: {e}")
        
        print("\n4. Conditional Flow / 条件付きFlow:")
        try:
            result = example_flow_conditional()
            print(f"Result / 結果: {result}")
        except Exception as e:
            print(f"Error / エラー: {e}")
        
        return
    
    # Run all examples with API access
    # API アクセスですべての例を実行
    print("\n1. Simple GenAgent / シンプルなGenAgent:")
    try:
        result = example_genagent_simple()
        print(f"Result / 結果: {result}")
    except Exception as e:
        print(f"Error / エラー: {e}")
    
    print("\n2. GenAgent with Evaluation / 評価機能付きGenAgent:")
    try:
        result = example_genagent_with_evaluation()
        print(f"Result / 結果: {result['result']}")
        if result['evaluation']:
            print(f"Evaluation / 評価: {result['evaluation']}")
    except Exception as e:
        print(f"Error / エラー: {e}")
    
    print("\n3. ClarifyAgent / ClarifyAgent:")
    try:
        result = example_clarify_agent()
        print(f"Original / 元の要求: {result['original_request']}")
        print(f"Clarified / 明確化後: {result['clarified_request']}")
        if result['questions']:
            print(f"Questions / 質問: {result['questions']}")
    except Exception as e:
        print(f"Error / エラー: {e}")
    
    print("\n4. Simple Flow / シンプルなFlow:")
    try:
        result = example_flow_simple()
        print(f"Result / 結果: {result}")
    except Exception as e:
        print(f"Error / エラー: {e}")
    
    print("\n5. Conditional Flow / 条件付きFlow:")
    try:
        result = example_flow_conditional()
        print(f"Result / 結果: {result}")
    except Exception as e:
        print(f"Error / エラー: {e}")
    
    print("\n6. Multi-provider LLM / マルチプロバイダーLLM:")
    try:
        result = example_multi_provider_llm()
        print(f"Prompt / プロンプト: {result['prompt']}")
        for provider, response in result['providers'].items():
            print(f"  {provider}: {response}")
    except Exception as e:
        print(f"Error / エラー: {e}")
    
    print("\n7. Available Models / 利用可能なモデル:")
    try:
        result = asyncio.run(example_get_available_models())
        if 'error' in result:
            print(f"Error / エラー: {result['error']}")
        else:
            print(f"Provider / プロバイダー: {result['provider']}")
            print(f"Total models / 総モデル数: {result['total_count']}")
            print(f"Sample models / サンプルモデル: {result['models']}")
    except Exception as e:
        print(f"Error / エラー: {e}")


if __name__ == "__main__":
    main() 
