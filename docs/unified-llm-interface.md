# Unified LLM Interface

Refinire's first pillar, the Unified LLM Interface, provides an innovative abstraction layer that enables developers to operate multiple LLM providers through a single, consistent API.

## Core Concept

By handling multiple LLM providers through the same interface, developers can freely choose and switch between providers without being tied to provider-specific implementations.

### Environment Variable Setup

To use each provider, you must set the corresponding API keys in environment variables:

| Provider | Environment Variable | Description |
|----------|---------------------|-------------|
| **OpenAI** | `OPENAI_API_KEY` | OpenAI API key |
| **Anthropic** | `ANTHROPIC_API_KEY` | Anthropic Claude API key |
| **Google** | `GOOGLE_API_KEY` | Google Gemini API key |
| **Ollama** | `OLLAMA_BASE_URL` | Ollama server address (default: http://localhost:11434) |

#### Environment Variable Setup Examples

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY = "sk-your-openai-api-key"
$env:ANTHROPIC_API_KEY = "sk-ant-your-anthropic-api-key"
$env:GOOGLE_API_KEY = "your-google-api-key"
$env:OLLAMA_BASE_URL = "http://localhost:11434"
```

**macOS/Linux (Bash):**
```bash
export OPENAI_API_KEY="sk-your-openai-api-key"
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-api-key"
export GOOGLE_API_KEY="your-google-api-key"
export OLLAMA_BASE_URL="http://localhost:11434"
```

**Python Configuration:**
```python
import os

# Set environment variables within your program
os.environ["OPENAI_API_KEY"] = "sk-your-openai-api-key"
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-your-anthropic-api-key"
os.environ["GOOGLE_API_KEY"] = "your-google-api-key"
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
```

### Unified Interface

After setting environment variables, all providers are accessible through the same API:

```python
from refinire import get_llm

# Access different providers with the same interface
llm_openai = get_llm("gpt-4o-mini")
llm_anthropic = get_llm("claude-3-sonnet")
llm_google = get_llm("gemini-pro")
llm_ollama = get_llm("llama3.1:8b")

# Operate all with the same methods
response = llm_openai.complete("Hello, how are you?")
```

## Basic Examples

### 1. Basic LLM Usage

```python
from refinire import get_llm

# Get LLM instance
llm = get_llm("gpt-4o-mini")

# Generate text
response = llm.complete("Tell me about the future of AI")
print(response)
```

### 2. Environment Variable Setup Verification

```python
import os
from refinire import get_llm

def check_api_setup():
    """Verify API configuration"""
    providers_check = {
        "OpenAI": "OPENAI_API_KEY",
        "Anthropic": "ANTHROPIC_API_KEY", 
        "Google": "GOOGLE_API_KEY",
        "Ollama": "OLLAMA_BASE_URL"
    }
    
    for provider, env_var in providers_check.items():
        if env_var in os.environ:
            print(f"✓ {provider}: Configured")
        else:
            print(f"✗ {provider}: {env_var} not set")

# Check API configuration
check_api_setup()
```

### 3. Provider Switching

```python
def test_providers():
    """Test execution with available providers"""
    providers = [
        ("gpt-4o-mini", "OpenAI"),
        ("claude-3-haiku-20240307", "Anthropic"),
        ("gemini-1.5-flash", "Google"),
        ("llama3.1:8b", "Ollama")
    ]
    question = "What is quantum computing?"
    
    for model, provider in providers:
        try:
            llm = get_llm(model)
            response = llm.complete(question)
            print(f"✓ {provider} ({model}): {response[:100]}...")
        except Exception as e:
            print(f"✗ {provider} ({model}): Error - {e}")

# Execute provider test
test_providers()
```

## Intermediate Examples

### 4. Strategic Provider Differentiation

```python
class MultiProviderService:
    def __init__(self):
        self.fast_llm = get_llm("gpt-4o-mini")      # Fast responses
        self.smart_llm = get_llm("gpt-4o")          # High performance
        self.creative_llm = get_llm("claude-3-sonnet")  # Creativity
    
    def quick_answer(self, question: str) -> str:
        return self.fast_llm.complete(f"Answer briefly: {question}")
    
    def detailed_analysis(self, topic: str) -> str:
        return self.smart_llm.complete(f"Detailed analysis: {topic}")
    
    def creative_writing(self, theme: str) -> str:
        return self.creative_llm.complete(f"Creative writing: {theme}")

# Usage example
service = MultiProviderService()
print(service.quick_answer("What is machine learning?"))
print(service.detailed_analysis("Impact of AI on healthcare"))
print(service.creative_writing("A story about time travel"))
```

### 5. Fallback Mechanism

```python
class RobustLLMService:
    def __init__(self, provider_hierarchy):
        self.provider_hierarchy = provider_hierarchy
        self.llms = {}
        
        # Initialize LLMs for available providers
        for provider in provider_hierarchy:
            try:
                self.llms[provider] = get_llm(provider)
            except Exception as e:
                print(f"Failed to initialize {provider}: {e}")
    
    def complete_with_fallback(self, prompt: str):
        """Try providers in order until one succeeds"""
        for provider in self.provider_hierarchy:
            if provider not in self.llms:
                continue
                
            try:
                response = self.llms[provider].complete(prompt)
                return response, provider
            except Exception as e:
                print(f"{provider} failed: {e}")
        
        raise Exception("All providers failed")

# Usage with fallback hierarchy
service = RobustLLMService([
    "gpt-4o-mini", 
    "claude-3-haiku-20240307", 
    "gemini-1.5-flash"
])

try:
    response, used_provider = service.complete_with_fallback("Explain neural networks")
    print(f"Response from {used_provider}: {response}")
except Exception as e:
    print(f"All providers failed: {e}")
```

## Advanced Examples

### 6. Intelligent Provider Selection

```python
from enum import Enum
import re

class TaskType(Enum):
    CREATIVE = "creative"
    TECHNICAL = "technical"
    CASUAL = "casual"
    ANALYTICAL = "analytical"

class SmartProviderSelector:
    def __init__(self):
        self.provider_profiles = {
            "gpt-4o-mini": {
                "strengths": [TaskType.CASUAL, TaskType.TECHNICAL],
                "cost": 1,
                "speed": 5
            },
            "claude-3-sonnet": {
                "strengths": [TaskType.CREATIVE, TaskType.ANALYTICAL],
                "cost": 3,
                "speed": 3
            },
            "gpt-4o": {
                "strengths": [TaskType.TECHNICAL, TaskType.ANALYTICAL],
                "cost": 4,
                "speed": 2
            },
            "gemini-1.5-pro": {
                "strengths": [TaskType.TECHNICAL, TaskType.CREATIVE],
                "cost": 2,
                "speed": 4
            }
        }
    
    def classify_task(self, prompt: str) -> TaskType:
        """Classify task type based on prompt content"""
        prompt_lower = prompt.lower()
        
        # Creative indicators
        creative_keywords = ["story", "creative", "write", "imagine", "poem", "narrative"]
        if any(keyword in prompt_lower for keyword in creative_keywords):
            return TaskType.CREATIVE
        
        # Technical indicators
        technical_keywords = ["code", "programming", "algorithm", "technical", "implement"]
        if any(keyword in prompt_lower for keyword in technical_keywords):
            return TaskType.TECHNICAL
        
        # Analytical indicators
        analytical_keywords = ["analyze", "compare", "evaluate", "research", "study"]
        if any(keyword in prompt_lower for keyword in analytical_keywords):
            return TaskType.ANALYTICAL
        
        return TaskType.CASUAL
    
    def select_provider(self, prompt: str, priority="balanced"):
        """Select optimal provider based on task and priority"""
        task_type = self.classify_task(prompt)
        
        # Score providers based on task match and priority
        scores = {}
        for provider, profile in self.provider_profiles.items():
            score = 0
            
            # Task match bonus
            if task_type in profile["strengths"]:
                score += 10
            
            # Priority-based scoring
            if priority == "cost":
                score += (5 - profile["cost"])  # Lower cost = higher score
            elif priority == "speed":
                score += profile["speed"]
            elif priority == "quality":
                score += profile["cost"]  # Higher cost often means better quality
            else:  # balanced
                score += (profile["speed"] + (5 - profile["cost"])) / 2
            
            scores[provider] = score
        
        # Return provider with highest score
        return max(scores, key=scores.get)
    
    def smart_complete(self, prompt: str, priority="balanced"):
        """Complete prompt with intelligently selected provider"""
        selected_provider = self.select_provider(prompt, priority)
        task_type = self.classify_task(prompt)
        
        print(f"Selected {selected_provider} for {task_type.value} task")
        
        llm = get_llm(selected_provider)
        return llm.complete(prompt)

# Usage example
selector = SmartProviderSelector()

# Different tasks will use different providers
creative_task = "Write a short story about a robot learning to love"
technical_task = "Implement a binary search algorithm in Python"
analytical_task = "Compare the pros and cons of renewable energy sources"

print("Creative task:")
print(selector.smart_complete(creative_task, priority="quality"))

print("\nTechnical task:")
print(selector.smart_complete(technical_task, priority="speed"))

print("\nAnalytical task:")
print(selector.smart_complete(analytical_task, priority="balanced"))
```

### 7. Performance Monitoring and Auto-Optimization

```python
import time
from dataclasses import dataclass
from typing import Dict, List
import statistics

@dataclass
class ProviderMetrics:
    total_requests: int = 0
    total_response_time: float = 0.0
    success_count: int = 0
    error_count: int = 0
    
    @property
    def average_response_time(self) -> float:
        return self.total_response_time / max(1, self.total_requests)
    
    @property
    def success_rate(self) -> float:
        return self.success_count / max(1, self.total_requests)

class OptimizedLLMService:
    def __init__(self, providers: List[str]):
        self.providers = providers
        self.llms = {}
        self.metrics: Dict[str, ProviderMetrics] = {}
        
        # Initialize providers and metrics
        for provider in providers:
            try:
                self.llms[provider] = get_llm(provider)
                self.metrics[provider] = ProviderMetrics()
            except Exception as e:
                print(f"Failed to initialize {provider}: {e}")
    
    def _record_request(self, provider: str, response_time: float, success: bool):
        """Record performance metrics for a provider"""
        metrics = self.metrics.get(provider)
        if metrics:
            metrics.total_requests += 1
            metrics.total_response_time += response_time
            if success:
                metrics.success_count += 1
            else:
                metrics.error_count += 1
    
    def get_best_provider(self, exclude: List[str] = None) -> str:
        """Select provider with best performance metrics"""
        exclude = exclude or []
        available_providers = [p for p in self.providers if p not in exclude and p in self.llms]
        
        if not available_providers:
            raise Exception("No available providers")
        
        # Score based on success rate and response time
        best_provider = None
        best_score = -1
        
        for provider in available_providers:
            metrics = self.metrics[provider]
            
            # Providers with no history get neutral score
            if metrics.total_requests == 0:
                score = 0.5
            else:
                # Combine success rate (weight: 0.7) and speed (weight: 0.3)
                success_score = metrics.success_rate
                speed_score = 1 / (1 + metrics.average_response_time)  # Inverse of response time
                score = 0.7 * success_score + 0.3 * speed_score
            
            if score > best_score:
                best_score = score
                best_provider = provider
        
        return best_provider
    
    def optimized_complete(self, prompt: str, max_retries: int = 2) -> str:
        """Complete prompt with performance-optimized provider selection"""
        tried_providers = []
        
        for attempt in range(max_retries + 1):
            try:
                provider = self.get_best_provider(exclude=tried_providers)
                tried_providers.append(provider)
                
                start_time = time.time()
                llm = self.llms[provider]
                response = llm.complete(prompt)
                response_time = time.time() - start_time
                
                # Record successful request
                self._record_request(provider, response_time, True)
                
                print(f"✓ Used {provider} (response time: {response_time:.2f}s)")
                return response
                
            except Exception as e:
                response_time = time.time() - start_time
                self._record_request(provider, response_time, False)
                
                print(f"✗ {provider} failed: {e}")
                
                if attempt == max_retries:
                    raise Exception(f"All retry attempts failed. Last error: {e}")
        
        raise Exception("Unexpected error in optimized_complete")
    
    def get_performance_report(self) -> str:
        """Generate performance report for all providers"""
        report = "Provider Performance Report:\n"
        report += "=" * 50 + "\n"
        
        for provider, metrics in self.metrics.items():
            if metrics.total_requests > 0:
                report += f"\n{provider}:\n"
                report += f"  Total requests: {metrics.total_requests}\n"
                report += f"  Success rate: {metrics.success_rate:.2%}\n"
                report += f"  Avg response time: {metrics.average_response_time:.2f}s\n"
                report += f"  Errors: {metrics.error_count}\n"
            else:
                report += f"\n{provider}: No requests yet\n"
        
        return report

# Usage example
service = OptimizedLLMService([
    "gpt-4o-mini",
    "claude-3-haiku-20240307",
    "gemini-1.5-flash"
])

# Make several requests to build performance history
test_prompts = [
    "What is artificial intelligence?",
    "Explain machine learning in simple terms",
    "What are the benefits of renewable energy?",
    "How does blockchain technology work?",
    "Describe the process of photosynthesis"
]

for prompt in test_prompts:
    try:
        response = service.optimized_complete(prompt)
        print(f"Response: {response[:100]}...\n")
    except Exception as e:
        print(f"Failed to get response: {e}\n")

# View performance report
print(service.get_performance_report())
```

## RefinireAgent Integration

The Unified LLM Interface seamlessly integrates with RefinireAgent for advanced workflows:

```python
from refinire import RefinireAgent

# Create agents with different providers for specialized tasks
creative_agent = RefinireAgent(
    name="creative_writer",
    generation_instructions="You are a creative writer specializing in engaging narratives.",
    model="claude-3-sonnet"  # Optimized for creativity
)

technical_agent = RefinireAgent(
    name="tech_expert",
    generation_instructions="You are a technical expert providing precise, accurate information.",
    model="gpt-4o"  # Optimized for technical accuracy
)

quick_agent = RefinireAgent(
    name="quick_responder",
    generation_instructions="Provide quick, concise answers.",
    model="gpt-4o-mini"  # Optimized for speed
)

# Use different agents based on task requirements
def smart_response(query: str) -> str:
    if any(word in query.lower() for word in ["story", "creative", "imagine"]):
        return creative_agent.run(query).result
    elif any(word in query.lower() for word in ["code", "technical", "algorithm"]):
        return technical_agent.run(query).result
    else:
        return quick_agent.run(query).result

# Examples
print(smart_response("Write a story about space exploration"))
print(smart_response("How do I implement a REST API?"))
print(smart_response("What's the weather like?"))
```

## Benefits

- **Provider Transparency**: Unified API for multiple provider operations
- **Easy Migration**: Minimal changes required for provider switching
- **Robust Fallback**: Comprehensive error handling and redundancy
- **Intelligent Optimization**: Automatic provider selection based on task requirements
- **Performance Monitoring**: Built-in metrics and optimization capabilities
- **Cost Management**: Strategic provider selection for cost optimization

## Supported Providers & Models

### OpenAI
- **Models**: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo
- **Strengths**: General purpose, fast responses, good technical accuracy
- **Best for**: Everyday tasks, technical questions, quick responses

### Anthropic Claude
- **Models**: claude-3-5-sonnet-20241022, claude-3-sonnet, claude-3-haiku
- **Strengths**: Creative writing, analytical thinking, nuanced understanding
- **Best for**: Creative tasks, complex analysis, ethical reasoning

### Google Gemini
- **Models**: gemini-1.5-pro, gemini-1.5-flash, gemini-pro
- **Strengths**: Multimodal capabilities, large context windows
- **Best for**: Complex reasoning, document analysis, multimodal tasks

### Ollama (Local)
- **Models**: llama3.1:8b, llama3.1:70b, mistral:7b, codellama:7b
- **Strengths**: Privacy, no API costs, customizable
- **Best for**: Privacy-sensitive tasks, cost-conscious development, offline usage

The Unified LLM Interface empowers developers to focus on creating value in AI applications without being constrained by provider-specific implementations, enabling flexible, robust, and optimized AI solutions.