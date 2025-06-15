"""
Pipeline example with input guardrails
ガードレール（入力ガードレール）を使ったPipelineの例
"""

from refinire import AgentPipeline
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
    # パイプラインのエージェントにガードレールを設定（input_guardrailsで渡す）
    pipeline = AgentPipeline(
        name="guardrail_pipeline",
        generation_instructions="""
        You are a helpful assistant. Please answer the user's question.
        あなたは役立つアシスタントです。ユーザーの質問に答えてください。
        """,
        evaluation_instructions=None,
        model="gpt-4o",
        input_guardrails=[math_guardrail],  # ここで明示的に渡す
    )

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
