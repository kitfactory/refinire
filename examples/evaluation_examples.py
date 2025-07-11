#!/usr/bin/env python3
"""
Refinire Evaluation Examples
Refinire評価機能使用例

This example demonstrates comprehensive evaluation patterns with proper scoring 
and structured feedback format.
この例では、適切なスコアリングと構造化されたフィードバック形式を用いた
包括的な評価パターンを実演します。
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from refinire import RefinireAgent, Context

def demonstrate_basic_evaluation():
    """
    Basic evaluation with structured scoring and feedback
    構造化されたスコアリングとフィードバックを用いた基本評価
    """
    print("🎯 Basic Evaluation Example")
    print("=" * 50)
    
    agent = RefinireAgent(
        name="basic_evaluator",
        generation_instructions="Create clear, informative technical content with proper structure and examples",
        evaluation_instructions="""Evaluate the technical content quality on a scale of 0-100 based on:
        - Technical accuracy and correctness (0-25 points)
        - Clarity and readability (0-25 points)
        - Structure and organization (0-25 points)
        - Practical examples and applicability (0-25 points)
        
        Provide your evaluation as:
        Score: [0-100]
        Comments:
        - [Identify 2-3 specific strengths]
        - [Note 2-3 areas for improvement]
        - [Provide 1-2 enhancement suggestions]""",
        threshold=80.0,
        max_retries=3,
        model="gpt-4o-mini"
    )
    
    # Test with a technical topic
    result = agent.run("Explain Python list comprehensions with examples")
    
    print(f"📊 Quality Score: {result.evaluation_score}/100")
    print(f"✅ Content: {result.content[:200]}...")
    
    # Show evaluation details with Context
    ctx = Context()
    result = agent.run("Explain Python list comprehensions with examples", ctx)
    
    print(f"\n📈 Detailed Evaluation:")
    print(f"Score: {ctx.evaluation_result['score']}")
    print(f"Passed: {ctx.evaluation_result['passed']}")
    print(f"Feedback: {ctx.evaluation_result['feedback']}")
    print()

def demonstrate_domain_specific_evaluation():
    """
    Domain-specific evaluation for different content types
    異なるコンテンツタイプのドメイン固有評価
    """
    print("🎯 Domain-Specific Evaluation Example")
    print("=" * 50)
    
    # Technical Documentation Evaluator
    tech_doc_agent = RefinireAgent(
        name="tech_doc_evaluator",
        generation_instructions="Write comprehensive technical documentation with clear setup instructions and practical examples",
        evaluation_instructions="""Evaluate technical documentation quality (0-100):

        TECHNICAL ACCURACY (0-30 points):
        - Factual correctness of instructions and code examples
        - Up-to-date information and best practices
        - Proper use of technical terminology

        USABILITY (0-30 points):
        - Clear explanations for target audience
        - Logical flow and step-by-step guidance
        - Effective use of examples and code samples

        COMPLETENESS (0-25 points):
        - Comprehensive coverage of the topic
        - Prerequisites and setup instructions included
        - Troubleshooting and error handling guidance

        PRESENTATION (0-15 points):
        - Consistent formatting and style
        - Proper use of headings and code blocks
        - Easy navigation and reference

        Provide evaluation as:
        Score: [0-100]
        Comments:
        - Technical strengths: [Accuracy and completeness aspects]
        - Usability assessment: [Clarity and user experience]
        - Areas for improvement: [Specific enhancement suggestions]""",
        threshold=85.0,
        max_retries=2,
        model="gpt-4o-mini"
    )
    
    result = tech_doc_agent.run("Create installation guide for setting up a Python development environment")
    
    print(f"📚 Technical Documentation:")
    print(f"Score: {result.evaluation_score}/100")
    print(f"Content sample: {result.content[:150]}...")
    print()

def demonstrate_multi_criteria_evaluation():
    """
    Multi-criteria evaluation with weighted scoring
    重み付けスコアリングによる多基準評価
    """
    print("🎯 Multi-Criteria Evaluation Example")
    print("=" * 50)
    
    agent = RefinireAgent(
        name="multi_criteria_evaluator",
        generation_instructions="Create comprehensive, well-balanced content that serves both technical accuracy and user accessibility",
        evaluation_instructions="""Conduct comprehensive multi-dimensional evaluation (0-100):

        CONTENT QUALITY (0-40 points):
        - Accuracy and factual correctness (0-20)
        - Depth and comprehensiveness (0-20)

        COMMUNICATION EFFECTIVENESS (0-35 points):
        - Clarity and accessibility (0-18)
        - Structure and flow (0-17)

        PRACTICAL VALUE (0-25 points):
        - Actionability and usefulness (0-13)
        - Real-world applicability (0-12)

        For each dimension, provide specific scores and reasoning.

        Final evaluation format:
        Score: [0-100]
        Comments:
        - Content Quality: [Score/40] - [Specific strengths and areas for improvement]
        - Communication: [Score/35] - [Clarity and structure assessment]
        - Practical Value: [Score/25] - [Usefulness and applicability analysis]
        - Overall recommendations: [Priority improvements for next iteration]""",
        threshold=80.0,
        max_retries=3,
        model="gpt-4o-mini"
    )
    
    ctx = Context()
    result = agent.run("Explain how to optimize database queries for better performance", ctx)
    
    print(f"📊 Multi-Criteria Evaluation:")
    print(f"Final Score: {ctx.evaluation_result['score']}/100")
    print(f"Detailed feedback:\n{ctx.evaluation_result['feedback']}")
    print()

def demonstrate_iterative_improvement():
    """
    Demonstrate iterative improvement through evaluation feedback
    評価フィードバックによる反復改善の実演
    """
    print("🎯 Iterative Improvement Example")
    print("=" * 50)
    
    agent = RefinireAgent(
        name="improvement_focused_evaluator",
        generation_instructions="Create high-quality educational content with clear explanations and practical examples",
        evaluation_instructions="""Evaluate content with improvement focus (0-100):

        CURRENT ASSESSMENT:
        - Identify specific strengths to maintain
        - Pinpoint weaknesses requiring attention
        - Assess overall effectiveness and coherence

        IMPROVEMENT GUIDANCE:
        If score < 85, provide specific instructions for next iteration:
        - Preserve: [Elements that work well and should be maintained]
        - Enhance: [Specific aspects needing improvement with actionable steps]
        - Add: [Missing elements that would strengthen the content]

        Score: [0-100]
        Comments:
        - Strengths to preserve: [What works well]
        - Priority improvements: [Most important changes needed]
        - Enhancement opportunities: [Additional improvements possible]
        - Next iteration focus: [Specific guidance for regeneration]""",
        threshold=85.0,
        max_retries=4,  # Allow more retries for improvement demonstration
        model="gpt-4o-mini"
    )
    
    # Track improvement across attempts
    attempts = []
    
    # Use Context to track all attempts
    ctx = Context()
    result = agent.run("Explain the concept of machine learning algorithms", ctx)
    
    print(f"🔄 Improvement Process:")
    print(f"Final Score: {ctx.evaluation_result['score']}/100")
    print(f"Attempts made: {result.attempts}")
    print(f"Success: {'✅' if ctx.evaluation_result['passed'] else '❌'}")
    print()

def demonstrate_specialized_evaluation_patterns():
    """
    Specialized evaluation patterns for different use cases
    異なる用途の特殊化された評価パターン
    """
    print("🎯 Specialized Evaluation Patterns")
    print("=" * 50)
    
    # Code Quality Evaluator
    code_evaluator = RefinireAgent(
        name="code_quality_evaluator",
        generation_instructions="Write clean, efficient, well-documented Python code with proper error handling",
        evaluation_instructions="""Evaluate Python code quality (0-100):

        FUNCTIONALITY (0-30 points):
        - Correctness and logic (0-15)
        - Error handling and edge cases (0-15)

        CODE QUALITY (0-30 points):
        - Readability and clarity (0-15)
        - Naming conventions and structure (0-15)

        BEST PRACTICES (0-25 points):
        - Python idioms and patterns (0-13)
        - Performance considerations (0-12)

        DOCUMENTATION (0-15 points):
        - Comments and docstrings (0-8)
        - Usage examples (0-7)

        Score: [0-100]
        Comments:
        - Code strengths: [What works well]
        - Quality improvements: [Structure and style feedback]
        - Best practices assessment: [Standards compliance]
        - Documentation review: [Clarity and completeness]""",
        threshold=80.0,
        model="gpt-4o-mini"
    )
    
    result = code_evaluator.run("Create a Python function to parse CSV files with error handling")
    print(f"💻 Code Quality Score: {result.evaluation_score}/100")
    
    # Creative Content Evaluator
    creative_evaluator = RefinireAgent(
        name="creative_content_evaluator",
        generation_instructions="Write engaging, original content with strong narrative elements",
        evaluation_instructions="""Evaluate creative content quality (0-100):

        CREATIVITY & ORIGINALITY (0-35 points):
        - Unique concepts and fresh perspectives (0-18)
        - Innovation and creative elements (0-17)

        ENGAGEMENT & IMPACT (0-35 points):
        - Emotional resonance and connection (0-18)
        - Compelling narrative and flow (0-17)

        TECHNICAL CRAFT (0-30 points):
        - Language quality and style (0-15)
        - Structure and presentation (0-15)

        Score: [0-100]
        Comments:
        - Creative highlights: [Innovative and engaging elements]
        - Impact assessment: [Emotional and narrative effectiveness]
        - Craft evaluation: [Technical and stylistic strengths]
        - Enhancement opportunities: [Areas for creative development]""",
        threshold=85.0,
        model="gpt-4o-mini"
    )
    
    result = creative_evaluator.run("Write a short story about AI and human collaboration")
    print(f"✨ Creative Content Score: {result.evaluation_score}/100")
    print()

async def demonstrate_evaluation_monitoring():
    """
    Demonstrate evaluation result monitoring and analytics
    評価結果の監視と分析の実演
    """
    print("🎯 Evaluation Monitoring Example")
    print("=" * 50)
    
    agent = RefinireAgent(
        name="monitored_evaluator",
        generation_instructions="Create high-quality content suitable for professional publication",
        evaluation_instructions="""Evaluate content for professional publication standards (0-100):
        - Professional quality and polish (0-25 points)
        - Accuracy and reliability (0-25 points)
        - Clarity and accessibility (0-25 points)
        - Practical value and applicability (0-25 points)
        
        Score: [0-100]
        Comments:
        - Publication readiness: [Professional standards assessment]
        - Content strengths: [What makes it valuable]
        - Areas for refinement: [Improvements needed for publication]""",
        threshold=85.0,
        max_retries=2,
        model="gpt-4o-mini"
    )
    
    # Monitor multiple evaluations
    topics = [
        "Best practices for API design",
        "Introduction to microservices architecture",
        "Database optimization techniques"
    ]
    
    scores = []
    passed_count = 0
    total_attempts = 0
    
    for topic in topics:
        ctx = Context()
        result = agent.run(f"Write a comprehensive guide on: {topic}", ctx)
        
        score = ctx.evaluation_result['score']
        passed = ctx.evaluation_result['passed']
        attempts = result.attempts
        
        scores.append(score)
        total_attempts += attempts
        if passed:
            passed_count += 1
        
        print(f"📄 Topic: {topic}")
        print(f"   Score: {score}/100 ({'✅ Passed' if passed else '❌ Failed'})")
        print(f"   Attempts: {attempts}")
    
    # Calculate metrics
    avg_score = sum(scores) / len(scores)
    pass_rate = passed_count / len(topics)
    regeneration_rate = (total_attempts - len(topics)) / total_attempts if total_attempts > 0 else 0
    
    print(f"\n📊 Evaluation Analytics:")
    print(f"Average Score: {avg_score:.1f}/100")
    print(f"Pass Rate: {pass_rate:.1%}")
    print(f"Regeneration Rate: {regeneration_rate:.1%}")
    print(f"Score Distribution:")
    
    for range_name, (min_score, max_score) in [
        ("Excellent (90-100)", (90, 100)),
        ("Good (80-89)", (80, 89)),
        ("Acceptable (70-79)", (70, 79)),
        ("Needs Work (<70)", (0, 69))
    ]:
        count = len([s for s in scores if min_score <= s <= max_score])
        percentage = count / len(scores) * 100
        print(f"  {range_name}: {count} ({percentage:.1f}%)")
    
    print()

async def main():
    """Run all evaluation examples"""
    try:
        print("🧪 Refinire Evaluation Examples")
        print("=" * 60)
        
        # Basic evaluation
        demonstrate_basic_evaluation()
        
        # Domain-specific evaluation
        demonstrate_domain_specific_evaluation()
        
        # Multi-criteria evaluation
        demonstrate_multi_criteria_evaluation()
        
        # Iterative improvement
        demonstrate_iterative_improvement()
        
        # Specialized patterns
        demonstrate_specialized_evaluation_patterns()
        
        # Monitoring and analytics
        await demonstrate_evaluation_monitoring()
        
        print("✅ All evaluation examples completed successfully!")
        print("\n💡 Key Takeaways:")
        print("- Use structured 100-point scoring with clear criteria")
        print("- Provide specific, actionable feedback in comment lists")
        print("- Set appropriate thresholds for your quality requirements")
        print("- Monitor evaluation metrics for continuous improvement")
        print("- Customize evaluation criteria for different content domains")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())