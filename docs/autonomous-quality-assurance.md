# Autonomous Quality Assurance

Refinire's second pillar, Autonomous Quality Assurance, provides an innovative system that automatically evaluates AI agent output quality and performs regeneration when necessary.

## Core Concept

Moving beyond traditional manual quality management, this system provides an autonomous quality assurance mechanism where AI evaluates and improves its own output.

```python
from refinire import RefinireAgent

# Agent with quality evaluation
agent = RefinireAgent(
    name="quality_assistant",
    generation_instructions="Generate helpful and accurate responses",
    evaluation_instructions="Evaluate accuracy and usefulness on a scale of 0-100",
    threshold=85.0,  # Require 85+ score
    max_retries=3,
    model="gpt-4o-mini"
)

# Automatic quality management
result = agent.run("Explain quantum computing")
print(f"Response: {result.result}")
```

## Basic Examples

### 1. Basic Quality Evaluation

```python
from refinire import RefinireAgent, Context

# Agent with quality threshold
agent = RefinireAgent(
    name="qa_agent",
    generation_instructions="Provide detailed and accurate answers",
    evaluation_instructions="Evaluate answer accuracy on a scale of 0-100",
    threshold=80.0,
    model="gpt-4o-mini"
)

# Execution with automatic evaluation
result = agent.run("Explain global warming")
print(f"Answer: {result.result}")
```

### 2. Custom Quality Standards

```python
# Agent with stricter evaluation criteria
strict_agent = RefinireAgent(
    name="strict_agent",
    generation_instructions="Provide scientifically accurate and detailed answers",
    evaluation_instructions="""
    Evaluate based on the following criteria:
    - Scientific accuracy (30 points)
    - Detail level (25 points)
    - Clarity and comprehensibility (25 points)
    - Completeness (20 points)
    Total score out of 100 points
    """,
    threshold=90.0,  # Require 90+ points
    max_retries=3,   # Maximum 3 retry attempts
    model="gpt-4o"
)

# Usage
result = strict_agent.run("How does photosynthesis work?")
print(f"High-quality response: {result.result}")
```

### 3. Quality Score Access

```python
from refinire import RefinireAgent, Context

agent = RefinireAgent(
    name="scored_agent",
    generation_instructions="Generate informative content",
    evaluation_instructions="Rate content quality from 0-100",
    threshold=75.0
)

# Execute with context to access evaluation details
ctx = Context()
result = agent.run("What is machine learning?", ctx)

# Access evaluation results
if hasattr(ctx, 'evaluation_result') and ctx.evaluation_result:
    eval_data = ctx.evaluation_result
    print(f"Quality Score: {eval_data.get('score', 'N/A')}")
    print(f"Passed Threshold: {eval_data.get('passed', 'N/A')}")
    print(f"Feedback: {eval_data.get('feedback', 'N/A')}")
```

## Intermediate Examples

### 4. Domain-Specific Quality Evaluation

```python
class MedicalQAAgent:
    """Quality-assured agent specialized for medical information"""
    
    def __init__(self):
        self.agent = RefinireAgent(
            name="medical_qa",
            generation_instructions="""
            Provide accurate and responsible medical information.
            Always include:
            1. Scientific evidence
            2. Scope and limitations
            3. Recommendation to consult healthcare professionals
            """,
            evaluation_instructions="""
            Evaluate medical information quality based on:
            - Medical accuracy (40 points)
            - Safety considerations (30 points)
            - Professional consultation recommendation (20 points)
            - Information completeness (10 points)
            """,
            threshold=95.0,  # High standard for medical information
            max_retries=5,
            model="gpt-4o"
        )
    
    def get_medical_info(self, question: str) -> str:
        result = self.agent.run(question)
        return result.result

# Usage example
medical_agent = MedicalQAAgent()
response = medical_agent.get_medical_info("What are the treatment options for hypertension?")
print(f"Medical response: {response}")
```

### 5. Multi-Layer Quality Evaluation System

```python
class MultiLayerQualitySystem:
    """Multi-layered quality evaluation system"""
    
    def __init__(self):
        # Basic quality check
        self.basic_agent = RefinireAgent(
            name="basic_check",
            generation_instructions="Provide basic accurate answers",
            evaluation_instructions="Evaluate basic accuracy and relevance",
            threshold=70.0,
            model="gpt-4o-mini"
        )
        
        # Detailed quality check
        self.detail_agent = RefinireAgent(
            name="detail_check",
            generation_instructions="Provide detailed, high-quality answers",
            evaluation_instructions="""
            Evaluate detailed quality based on:
            - Content depth (30 points)
            - Logical consistency (25 points)
            - Practical usefulness (25 points)
            - Originality (20 points)
            """,
            threshold=85.0,
            model="gpt-4o"
        )
        
        # Expert quality check
        self.expert_agent = RefinireAgent(
            name="expert_check",
            generation_instructions="Provide expert-level comprehensive answers",
            evaluation_instructions="""
            Evaluate expert-level quality based on:
            - Expert knowledge accuracy (35 points)
            - Current information (25 points)
            - Comprehensiveness (25 points)
            - Citations and evidence (15 points)
            """,
            threshold=92.0,
            model="gpt-4o"
        )
    
    def get_quality_response(self, question: str, quality_level: str = "basic"):
        """Generate response based on quality level"""
        if quality_level == "basic":
            result = self.basic_agent.run(question)
            return result.result
        elif quality_level == "detailed":
            result = self.detail_agent.run(question)
            return result.result
        elif quality_level == "expert":
            result = self.expert_agent.run(question)
            return result.result
        else:
            raise ValueError("Invalid quality level")

# Usage example
quality_system = MultiLayerQualitySystem()

# Get responses at different quality levels
basic_answer = quality_system.get_quality_response("What is AI?", "basic")
expert_answer = quality_system.get_quality_response("What is AI?", "expert")

print(f"Basic: {basic_answer}")
print(f"Expert: {expert_answer}")
```

## Advanced Examples

### 6. Adaptive Quality Learning System

```python
import json
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, asdict

@dataclass
class QualityFeedback:
    timestamp: str
    question: str
    response: str
    user_rating: int
    accuracy: int
    relevance: int
    completeness: int
    clarity: int

class AdaptiveQualitySystem:
    """Self-adaptive quality system that learns from user feedback"""
    
    def __init__(self):
        self.feedback_history: List[QualityFeedback] = []
        self.quality_metrics = {
            "accuracy": 0.8,
            "relevance": 0.8,
            "completeness": 0.8,
            "clarity": 0.8
        }
        
        self.agent = self._create_adaptive_agent()
    
    def _create_adaptive_agent(self) -> RefinireAgent:
        """Create agent with dynamic instructions based on learning"""
        return RefinireAgent(
            name="adaptive_agent",
            generation_instructions=self._generate_dynamic_instructions(),
            evaluation_instructions=self._generate_dynamic_evaluation(),
            threshold=self._calculate_dynamic_threshold(),
            model="gpt-4o"
        )
    
    def _generate_dynamic_instructions(self) -> str:
        """Generate dynamic instructions based on feedback"""
        base_instructions = "Generate high-quality responses."
        
        # Adjust based on weak areas
        if self.quality_metrics["accuracy"] < 0.7:
            base_instructions += " Pay special attention to accuracy and factual correctness."
        
        if self.quality_metrics["relevance"] < 0.7:
            base_instructions += " Focus directly on the question asked."
        
        if self.quality_metrics["completeness"] < 0.7:
            base_instructions += " Provide comprehensive and complete answers."
        
        if self.quality_metrics["clarity"] < 0.7:
            base_instructions += " Use clear and understandable language."
        
        return base_instructions
    
    def _generate_dynamic_evaluation(self) -> str:
        """Generate dynamic evaluation criteria"""
        # Adjust weights based on performance gaps
        weights = {}
        for metric, score in self.quality_metrics.items():
            # Lower performing areas get higher weight
            base_weight = {"accuracy": 30, "relevance": 25, "completeness": 25, "clarity": 20}[metric]
            adjustment = max(0, (0.8 - score) * 10)  # Up to 10 point boost for underperforming areas
            weights[metric] = min(40, base_weight + adjustment)
        
        # Normalize to 100 total
        total = sum(weights.values())
        weights = {k: int(v * 100 / total) for k, v in weights.items()}
        
        return f"""
        Evaluate based on these criteria:
        - Accuracy ({weights["accuracy"]} points)
        - Relevance ({weights["relevance"]} points)
        - Completeness ({weights["completeness"]} points)
        - Clarity ({weights["clarity"]} points)
        Total: 100 points
        """
    
    def _calculate_dynamic_threshold(self) -> float:
        """Calculate dynamic threshold based on performance"""
        avg_quality = sum(self.quality_metrics.values()) / len(self.quality_metrics)
        
        # Lower threshold if overall quality is poor to allow for improvement
        if avg_quality < 0.7:
            return 75.0
        elif avg_quality > 0.9:
            return 90.0
        else:
            return 80.0
    
    def process_feedback(self, question: str, response: str, user_rating: int,
                        accuracy: int, relevance: int, completeness: int, clarity: int):
        """Process user feedback and adapt quality metrics"""
        # Record feedback
        feedback = QualityFeedback(
            timestamp=datetime.now().isoformat(),
            question=question,
            response=response,
            user_rating=user_rating,
            accuracy=accuracy,
            relevance=relevance,
            completeness=completeness,
            clarity=clarity
        )
        self.feedback_history.append(feedback)
        
        # Update quality metrics using exponential moving average
        alpha = 0.1  # Learning rate
        new_scores = {
            "accuracy": accuracy / 100.0,
            "relevance": relevance / 100.0,
            "completeness": completeness / 100.0,
            "clarity": clarity / 100.0
        }
        
        for metric, new_score in new_scores.items():
            self.quality_metrics[metric] = (
                (1 - alpha) * self.quality_metrics[metric] + alpha * new_score
            )
        
        # Recreate agent with updated settings
        self.agent = self._create_adaptive_agent()
        print(f"Adapted based on feedback. New metrics: {self.quality_metrics}")
    
    def get_adaptive_response(self, question: str) -> tuple[str, Dict]:
        """Generate adaptive response with current quality settings"""
        result = self.agent.run(question)
        
        current_settings = {
            "threshold": self._calculate_dynamic_threshold(),
            "quality_metrics": self.quality_metrics.copy(),
            "feedback_count": len(self.feedback_history)
        }
        
        return result.result, current_settings
    
    def save_learning_data(self, filename: str):
        """Save learning data to file"""
        data = {
            "quality_metrics": self.quality_metrics,
            "feedback_history": [asdict(f) for f in self.feedback_history]
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_learning_data(self, filename: str):
        """Load learning data from file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.quality_metrics = data["quality_metrics"]
            self.feedback_history = [
                QualityFeedback(**f) for f in data["feedback_history"]
            ]
            self.agent = self._create_adaptive_agent()
            print(f"Loaded learning data: {len(self.feedback_history)} feedback entries")
        except FileNotFoundError:
            print("No previous learning data found")

# Usage example
adaptive_system = AdaptiveQualitySystem()

# Initial response
response1, settings1 = adaptive_system.get_adaptive_response("What is machine learning?")
print(f"Response: {response1[:200]}...")
print(f"Settings: {settings1}")

# Simulate user feedback (low ratings)
adaptive_system.process_feedback(
    "What is machine learning?",
    response1,
    2,  # Overall rating out of 5
    50,  # Accuracy out of 100
    80,  # Relevance out of 100
    40,  # Completeness out of 100
    90   # Clarity out of 100
)

# Response after learning (should be improved)
response2, settings2 = adaptive_system.get_adaptive_response("What is machine learning?")
print(f"\nLearned response: {response2[:200]}...")
print(f"Updated settings: {settings2}")

# Save learning progress
adaptive_system.save_learning_data("quality_learning.json")
```

### 7. Real-Time Quality Monitoring System

```python
import threading
import time
from collections import deque
from typing import Optional, Callable
from datetime import datetime
import statistics

class QualityAlert:
    def __init__(self, alert_type: str, message: str, severity: str, timestamp: str = None):
        self.alert_type = alert_type
        self.message = message
        self.severity = severity
        self.timestamp = timestamp or datetime.now().isoformat()

class RealTimeQualityMonitor:
    """Real-time quality monitoring system"""
    
    def __init__(self, window_size: int = 10, alert_callback: Optional[Callable] = None):
        self.window_size = window_size
        self.quality_scores = deque(maxlen=window_size)
        self.response_times = deque(maxlen=window_size)
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.quality_alerts: List[QualityAlert] = []
        self.alert_callback = alert_callback or self._default_alert_handler
        
        # Quality thresholds
        self.quality_thresholds = {
            "critical": 60,
            "warning": 75,
            "good": 85
        }
        
        self.agent = RefinireAgent(
            name="monitored_agent",
            generation_instructions="Generate high-quality responses under monitoring",
            evaluation_instructions="""
            Evaluate response quality comprehensively:
            - Accuracy and factual correctness (25 points)
            - Relevance to the question (25 points)
            - Completeness of answer (25 points)
            - Clarity and readability (25 points)
            """,
            threshold=80.0,
            model="gpt-4o-mini"
        )
    
    def _default_alert_handler(self, alert: QualityAlert):
        """Default alert handler"""
        severity_emoji = {"critical": "🚨", "warning": "⚠️", "info": "ℹ️"}
        print(f"{severity_emoji.get(alert.severity, '📢')} {alert.alert_type}: {alert.message}")
    
    def start_monitoring(self):
        """Start quality monitoring"""
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("✅ Quality monitoring started")
    
    def stop_monitoring(self):
        """Stop quality monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("🛑 Quality monitoring stopped")
    
    def _monitor_loop(self):
        """Monitoring loop that runs in background"""
        while self.monitoring_active:
            try:
                self._analyze_quality_trends()
                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                print(f"Monitor loop error: {e}")
                time.sleep(5)
    
    def _analyze_quality_trends(self):
        """Analyze quality trends and generate alerts"""
        if len(self.quality_scores) < 3:
            return
        
        recent_scores = list(self.quality_scores)
        avg_quality = statistics.mean(recent_scores)
        quality_std = statistics.stdev(recent_scores) if len(recent_scores) > 1 else 0
        
        # Critical quality drop
        if avg_quality < self.quality_thresholds["critical"]:
            alert = QualityAlert(
                "CRITICAL_QUALITY_DROP",
                f"Average quality dropped to {avg_quality:.1f} (threshold: {self.quality_thresholds['critical']})",
                "critical"
            )
            self.quality_alerts.append(alert)
            self.alert_callback(alert)
        
        # Quality warning
        elif avg_quality < self.quality_thresholds["warning"]:
            alert = QualityAlert(
                "QUALITY_WARNING",
                f"Quality below warning threshold: {avg_quality:.1f}",
                "warning"
            )
            self.quality_alerts.append(alert)
            self.alert_callback(alert)
        
        # High variability alert
        elif quality_std > 15:
            alert = QualityAlert(
                "HIGH_VARIABILITY",
                f"Quality variability high: std={quality_std:.1f}",
                "warning"
            )
            self.quality_alerts.append(alert)
            self.alert_callback(alert)
        
        # Quality improvement notification
        elif avg_quality > self.quality_thresholds["good"]:
            recent_trend = recent_scores[-3:]
            if len(recent_trend) == 3 and all(recent_trend[i] >= recent_trend[i-1] for i in range(1, 3)):
                alert = QualityAlert(
                    "QUALITY_IMPROVEMENT",
                    f"Quality trending upward: {avg_quality:.1f}",
                    "info"
                )
                self.alert_callback(alert)
    
    def get_monitored_response(self, question: str) -> Dict:
        """Generate response with quality monitoring"""
        start_time = time.time()
        
        try:
            # Get response with quality evaluation
            ctx = Context()
            result = self.agent.run(question, ctx)
            response = result.result
            
            # Record response time
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            
            # Extract quality score (simplified - in real implementation, 
            # this would come from the actual evaluation)
            quality_score = self._extract_quality_score(ctx)
            self.quality_scores.append(quality_score)
            
            return {
                "response": response,
                "quality_score": quality_score,
                "response_time": response_time,
                "monitoring_active": self.monitoring_active
            }
            
        except Exception as e:
            # Record failure
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            self.quality_scores.append(0)  # Failed response gets 0 quality
            
            alert = QualityAlert(
                "RESPONSE_FAILURE",
                f"Response generation failed: {str(e)}",
                "critical"
            )
            self.quality_alerts.append(alert)
            self.alert_callback(alert)
            
            return {
                "response": f"Error: {str(e)}",
                "quality_score": 0,
                "response_time": response_time,
                "monitoring_active": self.monitoring_active
            }
    
    def _extract_quality_score(self, context: Context) -> float:
        """Extract quality score from context"""
        # In a real implementation, this would extract the actual evaluation score
        # For demo purposes, we'll use a simulated score
        if hasattr(context, 'evaluation_result') and context.evaluation_result:
            return context.evaluation_result.get('score', 75.0)
        else:
            # Simulate quality score based on response characteristics
            import random
            return random.uniform(65, 95)
    
    def get_monitoring_report(self) -> Dict:
        """Generate comprehensive monitoring report"""
        if not self.quality_scores:
            return {"message": "No monitoring data available"}
        
        scores = list(self.quality_scores)
        times = list(self.response_times)
        
        report = {
            "monitoring_period": {
                "total_responses": len(scores),
                "monitoring_active": self.monitoring_active
            },
            "quality_metrics": {
                "average_quality": statistics.mean(scores),
                "min_quality": min(scores),
                "max_quality": max(scores),
                "quality_std": statistics.stdev(scores) if len(scores) > 1 else 0,
                "quality_trend": self._calculate_trend(scores)
            },
            "performance_metrics": {
                "average_response_time": statistics.mean(times),
                "min_response_time": min(times),
                "max_response_time": max(times)
            },
            "alerts": {
                "total_alerts": len(self.quality_alerts),
                "critical_alerts": len([a for a in self.quality_alerts if a.severity == "critical"]),
                "warning_alerts": len([a for a in self.quality_alerts if a.severity == "warning"]),
                "recent_alerts": [
                    {"type": a.alert_type, "message": a.message, "severity": a.severity, "timestamp": a.timestamp}
                    for a in self.quality_alerts[-5:]  # Last 5 alerts
                ]
            },
            "recommendations": self._generate_recommendations(scores)
        }
        
        return report
    
    def _calculate_trend(self, scores: List[float]) -> str:
        """Calculate quality trend"""
        if len(scores) < 2:
            return "insufficient_data"
        
        recent_half = scores[len(scores)//2:]
        early_half = scores[:len(scores)//2]
        
        recent_avg = statistics.mean(recent_half)
        early_avg = statistics.mean(early_half)
        
        diff = recent_avg - early_avg
        
        if diff > 5:
            return "improving"
        elif diff < -5:
            return "declining"
        else:
            return "stable"
    
    def _generate_recommendations(self, scores: List[float]) -> List[str]:
        """Generate recommendations based on quality patterns"""
        recommendations = []
        
        avg_quality = statistics.mean(scores)
        quality_std = statistics.stdev(scores) if len(scores) > 1 else 0
        
        if avg_quality < 70:
            recommendations.append("Consider adjusting generation instructions to improve overall quality")
        
        if quality_std > 15:
            recommendations.append("High quality variability detected - review evaluation consistency")
        
        if avg_quality > 90:
            recommendations.append("Excellent quality maintained - consider optimizing for speed")
        
        critical_alerts = [a for a in self.quality_alerts if a.severity == "critical"]
        if len(critical_alerts) > 3:
            recommendations.append("Multiple critical alerts - review system configuration")
        
        return recommendations

# Usage example
def custom_alert_handler(alert: QualityAlert):
    """Custom alert handler that could send notifications, log to file, etc."""
    print(f"[{alert.timestamp}] {alert.severity.upper()}: {alert.message}")
    
    # Could add additional handling like:
    # - Send email notifications
    # - Log to monitoring system
    # - Trigger automatic remediation

# Initialize monitoring system
monitor = RealTimeQualityMonitor(window_size=15, alert_callback=custom_alert_handler)
monitor.start_monitoring()

try:
    # Test with various questions
    test_questions = [
        "What is artificial intelligence?",
        "Explain quantum computing",
        "How does climate change work?",
        "What is the theory of relativity?",
        "Describe machine learning algorithms"
    ]
    
    for i, question in enumerate(test_questions):
        print(f"\n--- Question {i+1} ---")
        print(f"Q: {question}")
        
        result = monitor.get_monitored_response(question)
        print(f"A: {result['response'][:150]}...")
        print(f"Quality Score: {result['quality_score']:.1f}")
        print(f"Response Time: {result['response_time']:.2f}s")
        
        # Simulate some delay between requests
        time.sleep(3)
    
    # Generate final report
    print("\n" + "="*60)
    print("FINAL MONITORING REPORT")
    print("="*60)
    
    report = monitor.get_monitoring_report()
    print(f"Total Responses: {report['monitoring_period']['total_responses']}")
    print(f"Average Quality: {report['quality_metrics']['average_quality']:.1f}")
    print(f"Quality Trend: {report['quality_metrics']['quality_trend']}")
    print(f"Average Response Time: {report['performance_metrics']['average_response_time']:.2f}s")
    print(f"Total Alerts: {report['alerts']['total_alerts']}")
    
    if report['recommendations']:
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"- {rec}")

finally:
    monitor.stop_monitoring()
```

## RefinireAgent Integration

The Autonomous Quality Assurance system is seamlessly integrated into RefinireAgent:

```python
from refinire import RefinireAgent, Context

# Create agent with comprehensive quality assurance
quality_agent = RefinireAgent(
    name="quality_assured_agent",
    generation_instructions="""
    Generate comprehensive, accurate, and helpful responses.
    Ensure all information is factual and well-structured.
    """,
    evaluation_instructions="""
    Evaluate the response quality based on:
    - Factual accuracy (30 points)
    - Completeness and depth (25 points)
    - Clarity and organization (25 points)
    - Helpfulness and relevance (20 points)
    
    Score: [0-100]
    Comments:
    - [Specific strengths of the response]
    - [Areas that could be improved]
    - [Suggestions for enhancement]
    """,
    threshold=85.0,
    max_retries=3,
    model="gpt-4o-mini"
)

# Quality-assured execution
def quality_assured_chat():
    while True:
        user_input = input("\nYour question (or 'quit' to exit): ")
        if user_input.lower() == 'quit':
            break
        
        try:
            ctx = Context()
            result = quality_agent.run(user_input, ctx)
            
            print(f"\nResponse: {result.result}")
            
            # Display quality information if available
            if hasattr(ctx, 'evaluation_result') and ctx.evaluation_result:
                eval_data = ctx.evaluation_result
                print(f"Quality Score: {eval_data.get('score', 'N/A')}")
                if eval_data.get('comments'):
                    print(f"Quality Notes: {eval_data['comments'][:100]}...")
                    
        except Exception as e:
            print(f"Error: {e}")

# Start quality-assured chat
quality_assured_chat()
```

## Benefits

- **Automated Quality Management**: Eliminates need for manual quality checks
- **Consistent Quality**: Automatically maintains set standards
- **Continuous Improvement**: Automatic learning from feedback
- **Real-time Monitoring**: Immediate detection of quality degradation
- **Scalable Evaluation**: Handles high-volume quality assessment
- **Customizable Standards**: Flexible criteria for different use cases
- **Transparent Scoring**: Clear quality metrics and feedback

## Quality Evaluation Best Practices

### 1. Effective Evaluation Instructions

```python
# Good evaluation instruction example
evaluation_instructions = """
Evaluate the response on a scale of 0-100 based on:

ACCURACY (0-30 points):
- Factual correctness and precision
- Up-to-date information
- No misleading statements

RELEVANCE (0-25 points):
- Direct address of the question
- Appropriate scope and focus
- No unnecessary tangents

CLARITY (0-25 points):
- Clear and understandable language
- Logical structure and flow
- Appropriate level for audience

COMPLETENESS (0-20 points):
- Comprehensive coverage of topic
- Key points not missed
- Sufficient detail level

Score: [0-100]
Comments:
- [Specific strengths]
- [Areas for improvement]
- [Actionable suggestions]
"""
```

### 2. Threshold Setting Guidelines

- **Basic tasks**: 70-75 threshold
- **Professional content**: 80-85 threshold  
- **Critical applications**: 90-95 threshold
- **Creative tasks**: 65-75 threshold (allow more flexibility)

### 3. Retry Strategy

```python
# Configure retry behavior
agent = RefinireAgent(
    name="strategic_agent",
    generation_instructions="Generate high-quality content",
    evaluation_instructions="Evaluate comprehensively",
    threshold=85.0,
    max_retries=3,  # Balance quality vs. response time
    model="gpt-4o-mini"
)
```

Autonomous Quality Assurance liberates developers from quality management burden, allowing them to focus on more creative development while ensuring consistent, high-quality AI outputs.