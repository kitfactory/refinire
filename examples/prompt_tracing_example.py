"""
Example of using PromptStore with tracing for agent instructions
エージェントの指示にPromptStoreとトレースを使用する例
"""

from pathlib import Path
import tempfile
from refinire.core import PromptStore, PromptReference
from refinire import RefinireAgent


def main():
    # Use temporary directory for this example
    # この例では一時ディレクトリを使用
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_storage = Path(temp_dir)
        
        print("=== PromptStore Tracing Example ===")
        print(f"Using temporary storage: {temp_storage}")
        print()
        
        # Store some prompts in PromptStore
        # PromptStoreにプロンプトを保存
        print("1. Storing prompts...")
        
        # Store generation instruction
        PromptStore.store(
            name="code_generator",
            content="You are a Python code generator. Generate clean, well-documented Python code based on user requirements.",
            tag="generation",
            language="en",
            storage_dir=temp_storage
        )
        
        # Store evaluation instruction
        PromptStore.store(
            name="code_evaluator", 
            content="Evaluate the generated Python code for correctness, readability, and best practices. Rate from 0-100.",
            tag="evaluation",
            language="en",
            storage_dir=temp_storage
        )
        
        print("✓ Prompts stored successfully")
        print()
        
        # Retrieve prompts with metadata for tracing
        # トレース用のメタデータ付きでプロンプトを取得
        print("2. Retrieving prompts with metadata...")
        
        generation_prompt = PromptStore.get(
            name="code_generator",
            tag="generation", 
            language="en",
            storage_dir=temp_storage
        )
        
        evaluation_prompt = PromptStore.get(
            name="code_evaluator",
            tag="evaluation",
            language="en", 
            storage_dir=temp_storage
        )
        
        if not generation_prompt or not evaluation_prompt:
            print("❌ Failed to retrieve prompts")
            return
        
        print(f"✓ Generation prompt: {generation_prompt.name} (tag: {generation_prompt.tag})")
        print(f"✓ Evaluation prompt: {evaluation_prompt.name} (tag: {evaluation_prompt.tag})")
        print()
        
        # Show prompt metadata
        # プロンプトメタデータを表示
        print("3. Prompt metadata:")
        print("Generation prompt metadata:")
        for key, value in generation_prompt.get_metadata().items():
            print(f"  {key}: {value}")
        print()
        print("Evaluation prompt metadata:")
        for key, value in evaluation_prompt.get_metadata().items():
            print(f"  {key}: {value}")
        print()
        
        # Create agent with traced prompts
        # トレースされたプロンプトでエージェントを作成
        print("4. Creating agent with traced prompts...")
        
        try:
            pipeline = RefinireAgent(
                name="code_generator_pipeline",
                generation_instructions=generation_prompt,  # PromptReference object
                evaluation_instructions=evaluation_prompt,  # PromptReference object
                model="gpt-4o-mini",
                threshold=70.0
            )
            
            print("✓ Pipeline created successfully")
            print(f"  Pipeline name: {pipeline.name}")
            print(f"  Model: {pipeline.model}")
            print()
            
            # Test the pipeline (this would normally make an API call)
            # パイプラインをテスト（通常はAPI呼び出しを行う）
            print("5. Pipeline configuration (with prompt metadata):")
            print(f"Generation instructions: {pipeline.generation_instructions[:100]}...")
            print(f"Evaluation instructions: {pipeline.evaluation_instructions[:100]}...")
            
            # Show internal metadata
            # 内部メタデータを表示
            if pipeline._generation_prompt_metadata:
                print("\nGeneration prompt metadata captured:")
                for key, value in pipeline._generation_prompt_metadata.items():
                    print(f"  {key}: {value}")
            
            if pipeline._evaluation_prompt_metadata:
                print("\nEvaluation prompt metadata captured:")
                for key, value in pipeline._evaluation_prompt_metadata.items():
                    print(f"  {key}: {value}")
            
            print()
            print("✓ Prompt metadata is now available for tracing!")
            print("  When this pipeline runs, the trace will include:")
            print("  - Prompt names and tags")
            print("  - Language information")
            print("  - Retrieval timestamps")
            print("  - Source tracking from PromptStore")
            
        except Exception as e:
            print(f"❌ Error creating pipeline: {e}")
            print("This might happen if OpenAI dependencies are not available")
        
        print()
        print("=== Example Complete ===")
        print()
        print("Benefits of this approach:")
        print("• Centralized prompt management")
        print("• Full traceability of prompt usage")
        print("• Version control for prompts")
        print("• Multilingual support")
        print("• Metadata-rich tracing")


if __name__ == "__main__":
    main()