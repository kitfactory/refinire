"""
Pipeline example with input guardrails
ガードレール（入力ガードレール）を使ったPipelineの例
"""

from agents_sdk_models.pipeline import Pipeline
from agents import Agent, input_guardrail, GuardrailFunctionOutput, InputGuardrailTripwireTriggered, Runner, RunContextWrapper
from pydantic import BaseModel
import asyncio

# ガードレール用の出力型
class MathHomeworkOutput(BaseModel):
    is_math_homework: bool
    reasoning: str

# ガードレール判定用エージェント
guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking you to do their math homework.",
    output_type=MathHomeworkOutput,
)

@input_guardrail
async def math_guardrail(ctx: RunContextWrapper, agent: Agent, input: str):
    """
    Detect if the input is a math homework request.
    入力が数学の宿題依頼かどうかを判定します。
    """
    result = await Runner.run(guardrail_agent, input, context=ctx.context)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_math_homework,
    )

def main():
    # パイプラインのエージェントにガードレールを設定
    pipeline = Pipeline(
        name="guardrail_pipeline",
        generation_template="""
        You are a helpful assistant. Please answer the user's question.
        あなたは役立つアシスタントです。ユーザーの質問に答えてください。
        """,
        evaluation_template=None,
        model="gpt-3.5-turbo",
    )
    # gen_agentにガードレールを追加
    pipeline.gen_agent.input_guardrails = [math_guardrail]

    user_inputs = [
        "Can you help me solve for x: 2x + 3 = 11?",
        "Tell me a joke about robots.",
    ]

    for user_input in user_inputs:
        print(f"\nInput: {user_input}")
        try:
            result = pipeline.run(user_input)
            print("Response:")
            print(result)
        except InputGuardrailTripwireTriggered:
            print("[Guardrail Triggered] Math homework detected. Request blocked.")

if __name__ == "__main__":
    main() 