# Evaluation Guide - Automatic Quality Assurance

This comprehensive guide covers Refinire's built-in evaluation system, enabling automatic quality assessment and content improvement through structured feedback and scoring.

## Overview

Refinire's evaluation system provides:
- **100-point scoring scale** for consistent quality measurement
- **Structured comment lists** for actionable feedback
- **Automatic regeneration** when quality thresholds aren't met
- **Customizable evaluation criteria** for different content types
- **Multi-retry logic** with improvement prompts

## Table of Contents

1. [Basic Evaluation Setup](#basic-evaluation-setup)
2. [Evaluation Output Format](#evaluation-output-format)
3. [Writing Effective Evaluation Instructions](#writing-effective-evaluation-instructions)
4. [Advanced Evaluation Patterns](#advanced-evaluation-patterns)
5. [Domain-Specific Evaluation Examples](#domain-specific-evaluation-examples)
6. [Troubleshooting and Best Practices](#troubleshooting-and-best-practices)

## Basic Evaluation Setup

### Standard Evaluation Pattern

```python
from refinire import RefinireAgent

agent = RefinireAgent(
    name="content_evaluator",
    generation_instructions="Create comprehensive, well-structured content",
    evaluation_instructions="""Evaluate the content quality on a scale of 0-100 based on:
    - Clarity and readability (0-25 points)
    - Accuracy and factual correctness (0-25 points)
    - Structure and organization (0-25 points)
    - Engagement and writing style (0-25 points)
    
    Provide your evaluation as:
    Score: [0-100]
    Comments:
    - [Specific feedback on strengths]
    - [Areas for improvement]
    - [Suggestions for enhancement]""",
    threshold=85.0,  # Regenerate if below 85
    max_retries=3,
    model="gpt-4o-mini"
)

result = agent.run("Write a guide on Python decorators")
print(f"Quality Score: {result.evaluation_score}")
print(f"Evaluation Feedback: {result.evaluation_result}")
```

### Evaluation with Context

```python
from refinire import Context

ctx = Context()
result = agent.run("Explain machine learning concepts", ctx)

# Access detailed evaluation results
eval_result = ctx.evaluation_result
print(f"Score: {eval_result['score']}")
print(f"Passed: {eval_result['passed']}")
print(f"Feedback: {eval_result['feedback']}")
```

## Evaluation Output Format

### Expected Evaluation Response Structure

The evaluation system expects responses in this **exact format**:

```
Score: 87
Comments:
- Excellent technical accuracy and comprehensive coverage of key concepts
- Clear, logical structure that builds concepts progressively
- Strong use of practical examples to illustrate abstract concepts
- Could benefit from more visual diagrams for complex workflows
- Consider adding troubleshooting section for common issues
- Some paragraphs could be shortened for better readability
```

### Structured Evaluation Components

1. **Score Line**: Must start with "Score:" followed by integer 0-100
2. **Comments Section**: Must start with "Comments:" on its own line
3. **Comment List**: Each comment as bullet point starting with "- "
4. **Comment Categories**:
   - **Strengths**: What the content does well
   - **Weaknesses**: Areas needing improvement
   - **Suggestions**: Specific actionable recommendations

### Accessing Evaluation Results

```python
# After running agent with evaluation
result = agent.run("Create technical documentation")

# Basic score access
score = result.evaluation_score  # Integer 0-100

# Detailed evaluation data (when using Context)
ctx = Context()
result = agent.run("Create technical documentation", ctx)

eval_data = ctx.evaluation_result
score = eval_data["score"]           # 87
passed = eval_data["passed"]         # True/False based on threshold
feedback = eval_data["feedback"]     # Full evaluation text
comments = eval_data["comments"]     # Parsed comment list
```

## Writing Effective Evaluation Instructions

### Template for Comprehensive Evaluation

```python
evaluation_template = """Evaluate the {content_type} quality on a scale of 0-100 based on:

PRIMARY CRITERIA (80 points total):
- {criterion_1} (0-20 points): {criterion_1_description}
- {criterion_2} (0-20 points): {criterion_2_description}
- {criterion_3} (0-20 points): {criterion_3_description}
- {criterion_4} (0-20 points): {criterion_4_description}

BONUS CRITERIA (20 points total):
- Innovation and creativity (0-10 points)
- Practical applicability (0-10 points)

EVALUATION FORMAT:
Score: [0-100]
Comments:
- [Identify 2-3 key strengths with specific examples]
- [Note 2-3 areas for improvement with concrete suggestions]
- [Provide 1-2 enhancement recommendations]

SCORING GUIDELINES:
- 90-100: Exceptional quality, minimal improvements needed
- 80-89: High quality, minor improvements possible
- 70-79: Good quality, moderate improvements needed
- 60-69: Acceptable quality, significant improvements needed
- Below 60: Poor quality, major revision required"""
```

### Domain-Specific Evaluation Instructions

**Technical Documentation:**
```python
tech_doc_evaluation = """Evaluate technical documentation quality (0-100):

TECHNICAL ACCURACY (0-30 points):
- Factual correctness of code examples and technical details
- Up-to-date information and best practices
- Proper use of technical terminology

CLARITY AND USABILITY (0-30 points):
- Clear explanations accessible to target audience
- Logical flow and progressive complexity
- Effective use of examples and illustrations

COMPLETENESS (0-25 points):
- Comprehensive coverage of topic
- Inclusion of prerequisites and setup instructions
- Error handling and troubleshooting guidance

FORMATTING AND STRUCTURE (0-15 points):
- Consistent formatting and style
- Proper use of headings, code blocks, and lists
- Easy navigation and reference

Provide evaluation as:
Score: [0-100]
Comments:
- [Strengths in technical accuracy and clarity]
- [Areas needing improvement]
- [Specific enhancement suggestions]"""
```

**Creative Writing:**
```python
creative_writing_evaluation = """Evaluate creative writing quality (0-100):

STORYTELLING (0-30 points):
- Compelling narrative structure and pacing
- Character development and dialogue quality
- Plot coherence and engagement

LANGUAGE AND STYLE (0-25 points):
- Prose quality and word choice
- Voice consistency and tone appropriateness
- Literary devices and stylistic elements

ORIGINALITY (0-25 points):
- Unique concepts and creative elements
- Fresh perspective or innovative approach
- Avoidance of clichés and overused tropes

TECHNICAL CRAFT (0-20 points):
- Grammar, spelling, and punctuation
- Sentence structure variety
- Proper formatting and presentation

Provide evaluation as:
Score: [0-100]
Comments:
- [Creative strengths and compelling elements]
- [Technical or narrative areas for improvement]
- [Suggestions for enhancement]"""
```

## Advanced Evaluation Patterns

### Multi-Aspect Evaluation

```python
multi_aspect_agent = RefinireAgent(
    name="comprehensive_evaluator",
    generation_instructions="Create content that balances technical accuracy with accessibility",
    evaluation_instructions="""Conduct multi-dimensional evaluation (0-100):

TECHNICAL DIMENSION (0-40 points):
- Accuracy and precision (0-20)
- Depth and comprehensiveness (0-20)

COMMUNICATION DIMENSION (0-40 points):
- Clarity and accessibility (0-20)
- Structure and organization (0-20)

PRACTICAL DIMENSION (0-20 points):
- Actionability and usefulness (0-10)
- Real-world applicability (0-10)

For each dimension, provide:
1. Dimension score and reasoning
2. Specific strengths and weaknesses
3. Improvement recommendations

Final evaluation format:
Score: [0-100]
Comments:
- Technical: [Score/40] - [Analysis]
- Communication: [Score/40] - [Analysis]  
- Practical: [Score/20] - [Analysis]
- Overall suggestions: [Enhancement recommendations]""",
    threshold=80.0,
    max_retries=2,
    model="gpt-4o-mini"
)
```

### Progressive Improvement Evaluation

```python
improvement_agent = RefinireAgent(
    name="improvement_evaluator",
    generation_instructions="Create high-quality content with continuous improvement",
    evaluation_instructions="""Evaluate content with improvement focus (0-100):

CURRENT QUALITY ASSESSMENT:
- Content strengths (what works well)
- Content weaknesses (what needs work)
- Overall coherence and effectiveness

IMPROVEMENT ROADMAP:
- Priority 1: Most critical improvements needed
- Priority 2: Moderate enhancements possible
- Priority 3: Nice-to-have optimizations

REGENERATION GUIDANCE:
If score < 85, provide specific instructions for next attempt:
- Maintain: [List elements to preserve]
- Improve: [List specific changes needed]
- Add: [List missing elements to include]

Score: [0-100]
Comments:
- Current strengths: [What to maintain]
- Critical improvements: [Priority 1 items]
- Enhancement opportunities: [Priority 2-3 items]
- Next iteration focus: [Specific guidance for regeneration]""",
    threshold=85.0,
    max_retries=3,
    model="gpt-4o-mini"
)
```

## Domain-Specific Evaluation Examples

### Code Review Evaluation

```python
code_review_agent = RefinireAgent(
    name="code_reviewer",
    generation_instructions="Write clean, efficient, well-documented code",
    evaluation_instructions="""Evaluate code quality (0-100):

FUNCTIONALITY (0-25 points):
- Correctness and logic
- Edge case handling
- Performance considerations

CODE QUALITY (0-25 points):
- Readability and clarity
- Naming conventions
- Code organization

BEST PRACTICES (0-25 points):
- Design patterns usage
- Error handling
- Security considerations

DOCUMENTATION (0-25 points):
- Comments and docstrings
- README and setup instructions
- Usage examples

Score: [0-100]
Comments:
- Functional strengths: [What works well]
- Code quality observations: [Structure and style feedback]
- Best practices assessment: [Adherence to standards]
- Documentation review: [Clarity and completeness]
- Improvement priorities: [Specific enhancement areas]""",
    threshold=80.0,
    model="gpt-4o-mini"
)
```

### Marketing Content Evaluation

```python
marketing_agent = RefinireAgent(
    name="marketing_evaluator",
    generation_instructions="Create compelling, persuasive marketing content",
    evaluation_instructions="""Evaluate marketing content effectiveness (0-100):

MESSAGE CLARITY (0-25 points):
- Clear value proposition
- Target audience alignment
- Key benefits communication

PERSUASION POWER (0-25 points):
- Emotional appeal and engagement
- Credibility and trust building
- Call-to-action effectiveness

BRAND ALIGNMENT (0-25 points):
- Consistent brand voice and tone
- Brand value reflection
- Market positioning accuracy

PRACTICAL EFFECTIVENESS (0-25 points):
- Actionable next steps
- Conversion potential
- Measurable objectives

Score: [0-100]
Comments:
- Message strengths: [Clear value and benefits]
- Persuasion elements: [Emotional and logical appeals]
- Brand consistency: [Voice and positioning alignment]
- Effectiveness factors: [Conversion and action potential]
- Optimization suggestions: [Specific improvement areas]""",
    threshold=85.0,
    model="gpt-4o-mini"
)
```

## Troubleshooting and Best Practices

### Common Evaluation Issues

**1. Inconsistent Scoring:**
```python
# Problem: Vague evaluation criteria
evaluation_instructions="Rate the quality from 0-100"

# Solution: Specific, detailed criteria
evaluation_instructions="""Rate quality (0-100) based on:
- Accuracy (0-30): Factual correctness and precision
- Clarity (0-30): Clear communication and understanding
- Completeness (0-20): Comprehensive coverage
- Style (0-20): Appropriate tone and presentation

Score: [0-100]
Comments: [Detailed feedback]"""
```

**2. Poor Evaluation Format:**
```python
# Ensure evaluations follow exact format
def validate_evaluation_format(evaluation_text):
    """Validate evaluation follows required format"""
    lines = evaluation_text.strip().split('\n')
    
    # Check for Score: line
    score_line = next((line for line in lines if line.startswith('Score:')), None)
    if not score_line:
        return False, "Missing 'Score:' line"
    
    # Check for Comments: section
    comments_line = next((line for line in lines if line.startswith('Comments:')), None)
    if not comments_line:
        return False, "Missing 'Comments:' section"
    
    return True, "Valid format"
```

**3. Threshold Tuning:**
```python
# Start with conservative thresholds and adjust
initial_threshold = 70.0  # Lower for initial testing
production_threshold = 85.0  # Higher for production quality

# Monitor regeneration rates
regeneration_rate = (attempts - 1) / attempts
if regeneration_rate > 0.5:  # If >50% regeneration
    # Consider lowering threshold or improving instructions
    pass
```

### Best Practices

**1. Evaluation Instruction Design:**
- Use specific, measurable criteria
- Include point distributions for transparency
- Provide clear format requirements
- Include examples of good/poor performance

**2. Threshold Management:**
- Start with lower thresholds during development
- Gradually increase for production systems
- Monitor regeneration rates and adjust accordingly
- Consider different thresholds for different content types

**3. Content Quality Improvement:**
- Use evaluation feedback to improve generation instructions
- Analyze common failure patterns
- Iterate on both generation and evaluation prompts
- Consider multi-stage evaluation for complex content

**4. Monitoring and Analytics:**
```python
# Track evaluation metrics
evaluation_metrics = {
    "average_score": sum(scores) / len(scores),
    "pass_rate": len([s for s in scores if s >= threshold]) / len(scores),
    "regeneration_rate": regenerations / total_attempts,
    "score_distribution": {
        "90-100": len([s for s in scores if s >= 90]),
        "80-89": len([s for s in scores if 80 <= s < 90]),
        "70-79": len([s for s in scores if 70 <= s < 80]),
        "below_70": len([s for s in scores if s < 70])
    }
}
```

## Conclusion

Refinire's evaluation system enables consistent, high-quality content generation through:
- **Structured 100-point scoring** for objective quality measurement
- **Detailed comment lists** for actionable improvement guidance
- **Automatic regeneration** for continuous quality improvement
- **Flexible evaluation criteria** adaptable to any domain or content type

By following the patterns and examples in this guide, you can create robust evaluation systems that ensure consistent, high-quality output for your specific use cases.

**Next Steps**: Explore [Advanced Features](advanced_features_en.md) to learn about combining evaluation with streaming, context management, and workflow orchestration.