# MCP Memory Integration Example - Practical Memory Management with Refinire

This tutorial demonstrates how to integrate Refinire with MCP (Model Context Protocol) servers using the popular `mcp-memory` server as a practical example. You'll learn how to set up memory management for AI agents that can remember information across conversations.

## What is MCP Memory?

MCP Memory is a standardized memory server that provides persistent storage for AI conversations. It allows agents to:

- Store and retrieve conversation history
- Remember user preferences and context
- Maintain knowledge across sessions
- Share memory between multiple agents

## Prerequisites

Before starting, ensure you have:

- Python 3.10+ installed
- Refinire package installed (`pip install refinire`)
- Node.js 18+ installed (for MCP servers)
- Basic understanding of Refinire agents

## Step 1: Install MCP Memory Server

First, install the MCP memory server using npm:

```bash
# Install the MCP memory server globally
npm install -g @modelcontextprotocol/server-memory

# Verify installation
mcp-memory --help
```

Alternative installation methods:

```bash
# Using npx (no global installation)
npx @modelcontextprotocol/server-memory --help

# Using uvx (if you have uv installed)
uvx @modelcontextprotocol/server-memory --help
```

## Step 2: Basic MCP Memory Setup

### Understanding MCP Memory Server

The MCP memory server provides these key tools:
- `memory_store`: Store information with a key
- `memory_retrieve`: Retrieve information by key
- `memory_list`: List all stored memory keys
- `memory_delete`: Delete stored information
- `memory_search`: Search through stored memories

### Simple Memory Agent

Create a basic agent that can store and retrieve memories:

```python
from refinire import RefinireAgent
import asyncio

# Create agent with MCP memory server
memory_agent = RefinireAgent(
    name="memory_assistant",
    generation_instructions="""
    You are a helpful assistant with memory capabilities. You can:
    1. Store information for later use with memory_store
    2. Retrieve previously stored information with memory_retrieve
    3. Search through your memories with memory_search
    4. List all your memories with memory_list
    
    Always use your memory tools to provide personalized and contextual responses.
    When users share important information, store it for future reference.
    """,
    mcp_servers=[
        "stdio://@modelcontextprotocol/server-memory"
    ],
    model="gpt-4o-mini"
)

async def main():
    # First conversation - storing information
    print("=== First Conversation ===")
    result1 = await memory_agent.run_async(
        "Hi! My name is Alice and I'm a software engineer working on Python projects. "
        "I prefer detailed technical explanations."
    )
    print(f"Agent: {result1.content}")
    
    # Second conversation - retrieving stored information
    print("\n=== Second Conversation ===")
    result2 = await memory_agent.run_async(
        "What do you remember about me? What kind of explanations do I prefer?"
    )
    print(f"Agent: {result2.content}")
    
    # Third conversation - adding more information
    print("\n=== Third Conversation ===")
    result3 = await memory_agent.run_async(
        "I'm currently learning about machine learning and specifically interested in PyTorch."
    )
    print(f"Agent: {result3.content}")
    
    # Fourth conversation - using accumulated memory
    print("\n=== Fourth Conversation ===")
    result4 = await memory_agent.run_async(
        "Can you suggest some Python libraries that might help with my current interests?"
    )
    print(f"Agent: {result4.content}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Step 3: Advanced Memory Management

### Structured Memory Agent

Create an agent with more sophisticated memory management:

```python
from refinire import RefinireAgent, Context
import asyncio
import json

class AdvancedMemoryAgent:
    def __init__(self):
        self.agent = RefinireAgent(
            name="advanced_memory_assistant",
            generation_instructions="""
            You are an advanced assistant with sophisticated memory management. You should:
            
            1. ALWAYS check existing memories before responding using memory_search or memory_list
            2. Store user information in structured format:
               - Personal info (name, role, preferences)
               - Project information
               - Conversation context
               - Important dates and events
            
            3. Use descriptive keys for memory storage:
               - user_profile_{user_name}
               - project_{project_name}
               - conversation_{date}_{topic}
               - preference_{category}
            
            4. Update existing memories when new information is provided
            5. Reference stored memories in your responses to show continuity
            
            Memory Tool Usage Guidelines:
            - memory_store: Store new information with descriptive keys
            - memory_retrieve: Get specific information by key
            - memory_search: Find related information using keywords
            - memory_list: See all available memories
            - memory_delete: Remove outdated information
            """,
            mcp_servers=[
                "stdio://@modelcontextprotocol/server-memory"
            ],
            model="gpt-4o-mini"
        )
    
    async def chat(self, message: str, user_id: str = "default_user") -> str:
        """Enhanced chat with user context"""
        # Add user context to the message
        enhanced_message = f"[User ID: {user_id}] {message}"
        
        result = await self.agent.run_async(enhanced_message)
        return result.content
    
    async def get_memory_summary(self) -> str:
        """Get a summary of all stored memories"""
        result = await self.agent.run_async(
            "Please use memory_list to show all stored memories and provide a summary of what you remember."
        )
        return result.content

# Example usage of advanced memory agent
async def advanced_memory_demo():
    agent = AdvancedMemoryAgent()
    
    print("=== Advanced Memory Management Demo ===\n")
    
    # Simulate a multi-session conversation
    conversations = [
        {
            "user": "alice",
            "message": "Hi! I'm Alice, a data scientist at TechCorp. I'm working on a customer segmentation project using Python and scikit-learn."
        },
        {
            "user": "alice", 
            "message": "I need help with clustering algorithms. We have 10,000 customer records with 15 features each."
        },
        {
            "user": "bob",
            "message": "Hello, I'm Bob, a web developer. I work with React and Node.js mainly."
        },
        {
            "user": "alice",
            "message": "Hi again! How's my customer segmentation project going? Any new insights on clustering?"
        },
        {
            "user": "bob",
            "message": "I'm building a real-time chat application. Do you remember what technologies I work with?"
        }
    ]
    
    for conv in conversations:
        print(f"👤 {conv['user'].title()}: {conv['message']}")
        response = await agent.chat(conv['message'], conv['user'])
        print(f"🤖 Assistant: {response}\n")
        
        # Add a small delay to simulate real conversation
        await asyncio.sleep(1)
    
    # Show memory summary
    print("=== Memory Summary ===")
    summary = await agent.get_memory_summary()
    print(f"🧠 Memory Summary: {summary}")

if __name__ == "__main__":
    asyncio.run(advanced_memory_demo())
```

## Step 4: Project Memory Management

### Project-Specific Memory Agent

Create an agent that manages project-related memories:

```python
from refinire import RefinireAgent
import asyncio
from datetime import datetime

class ProjectMemoryAgent:
    def __init__(self):
        self.agent = RefinireAgent(
            name="project_memory_assistant",
            generation_instructions="""
            You are a project management assistant with memory capabilities. You help users track:
            
            1. Project details and status
            2. Task assignments and deadlines
            3. Meeting notes and decisions
            4. Team member information
            5. Project milestones and goals
            
            Memory Organization:
            - project_info_{project_name}: Basic project information
            - task_{project_name}_{task_id}: Individual task details
            - meeting_{project_name}_{date}: Meeting notes
            - team_{project_name}: Team member information
            - milestone_{project_name}_{milestone_name}: Milestone tracking
            
            Always:
            1. Search existing project memories before responding
            2. Store new project information systematically
            3. Update task statuses when informed
            4. Reference previous decisions and context
            5. Provide project summaries when requested
            """,
            mcp_servers=[
                "stdio://@modelcontextprotocol/server-memory"
            ],
            model="gpt-4o-mini"
        )
    
    async def create_project(self, project_name: str, description: str, team_members: list):
        """Initialize a new project in memory"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        message = f"""
        Create a new project with the following details:
        - Project Name: {project_name}
        - Description: {description}
        - Team Members: {', '.join(team_members)}
        - Start Date: {current_date}
        - Status: Active
        
        Please store this information and confirm the project creation.
        """
        
        result = await self.agent.run_async(message)
        return result.content
    
    async def add_task(self, project_name: str, task_name: str, assignee: str, deadline: str):
        """Add a task to the project"""
        message = f"""
        Add a new task to project "{project_name}":
        - Task Name: {task_name}
        - Assigned to: {assignee}
        - Deadline: {deadline}
        - Status: Not Started
        
        Please store this task and provide an update on the project status.
        """
        
        result = await self.agent.run_async(message)
        return result.content
    
    async def update_task_status(self, project_name: str, task_name: str, new_status: str):
        """Update task status"""
        message = f"""
        Update the status of task "{task_name}" in project "{project_name}" to "{new_status}".
        Please retrieve the current task information, update it, and provide a project status summary.
        """
        
        result = await self.agent.run_async(message)
        return result.content
    
    async def get_project_summary(self, project_name: str):
        """Get comprehensive project summary"""
        message = f"""
        Please provide a comprehensive summary of project "{project_name}" including:
        1. Project overview and current status
        2. All tasks and their current status
        3. Team member assignments
        4. Upcoming deadlines
        5. Any meeting notes or important decisions
        
        Search through all relevant memories to compile this information.
        """
        
        result = await self.agent.run_async(message)
        return result.content

# Example project management workflow
async def project_management_demo():
    pm_agent = ProjectMemoryAgent()
    
    print("=== Project Memory Management Demo ===\n")
    
    # Create a new project
    print("📋 Creating new project...")
    result = await pm_agent.create_project(
        "Website Redesign",
        "Complete redesign of company website with modern UI/UX",
        ["Alice (Designer)", "Bob (Developer)", "Charlie (QA)"]
    )
    print(f"✅ {result}\n")
    
    # Add tasks
    print("📝 Adding project tasks...")
    tasks = [
        ("Design Wireframes", "Alice", "2024-02-15"),
        ("Frontend Development", "Bob", "2024-02-28"),
        ("Backend API Integration", "Bob", "2024-03-05"),
        ("Quality Assurance Testing", "Charlie", "2024-03-10")
    ]
    
    for task_name, assignee, deadline in tasks:
        result = await pm_agent.add_task("Website Redesign", task_name, assignee, deadline)
        print(f"📌 Added: {task_name}")
        await asyncio.sleep(0.5)
    
    print()
    
    # Update task statuses
    print("🔄 Updating task statuses...")
    updates = [
        ("Design Wireframes", "Completed"),
        ("Frontend Development", "In Progress"),
    ]
    
    for task_name, status in updates:
        result = await pm_agent.update_task_status("Website Redesign", task_name, status)
        print(f"✏️ Updated {task_name} to {status}")
        await asyncio.sleep(0.5)
    
    print()
    
    # Get project summary
    print("📊 Getting project summary...")
    summary = await pm_agent.get_project_summary("Website Redesign")
    print(f"📈 Project Summary:\n{summary}")

if __name__ == "__main__":
    asyncio.run(project_management_demo())
```

## Step 5: Configuration and Troubleshooting

### Configuration Options

You can configure the MCP memory server with different options:

```bash
# Basic usage
mcp-memory

# With custom port
mcp-memory --port 3001

# With specific memory file location
mcp-memory --memory-file ./custom-memory.json

# With debug logging
mcp-memory --debug
```

### Alternative Server Configurations

```python
# Different MCP server configurations
memory_configs = [
    # Standard stdio configuration
    "stdio://@modelcontextprotocol/server-memory",
    
    # With specific memory file
    "stdio://@modelcontextprotocol/server-memory --memory-file ./project-memory.json",
    
    # HTTP server (if available)
    "http://localhost:3001/mcp",
    
    # Multiple memory servers for different purposes
    [
        "stdio://@modelcontextprotocol/server-memory --memory-file ./user-memory.json",
        "stdio://@modelcontextprotocol/server-memory --memory-file ./project-memory.json"
    ]
]

# Use in RefinireAgent
agent = RefinireAgent(
    name="multi_memory_agent",
    generation_instructions="Use different memory servers for different types of information.",
    mcp_servers=memory_configs[3],  # Multiple servers
    model="gpt-4o-mini"
)
```

### Troubleshooting Common Issues

#### 1. MCP Server Not Found

```bash
# Error: mcp-memory command not found
# Solution: Install the server
npm install -g @modelcontextprotocol/server-memory

# Or use npx
npx @modelcontextprotocol/server-memory
```

#### 2. Permission Issues

```bash
# Error: Permission denied
# Solution: Check file permissions or use different directory
chmod 755 ./memory-file.json

# Or specify a different location
mcp-memory --memory-file ~/Documents/memory.json
```

#### 3. Agent Not Using Memory Tools

```python
# Problem: Agent doesn't use memory tools
# Solution: Improve instructions

agent = RefinireAgent(
    name="memory_agent",
    generation_instructions="""
    IMPORTANT: You MUST use memory tools for persistent storage:
    
    1. ALWAYS check existing memories with memory_search before responding
    2. ALWAYS store important user information with memory_store
    3. Use memory_retrieve to access specific stored information
    4. Use memory_list to see all available memories
    
    Example workflow:
    1. User shares information → use memory_store
    2. User asks about past information → use memory_search or memory_retrieve
    3. Before any response → check relevant memories first
    """,
    mcp_servers=["stdio://@modelcontextprotocol/server-memory"],
    model="gpt-4o-mini"
)
```

## Best Practices for MCP Memory Integration

### 1. Memory Key Naming Conventions

Use structured, descriptive keys:

```python
# Good key naming patterns
memory_keys = [
    "user_profile_alice_2024",
    "project_website_redesign_tasks",
    "meeting_2024_01_15_planning",
    "preference_alice_communication_style",
    "deadline_project_website_2024_03_01"
]

# Avoid these patterns
bad_keys = [
    "data1",
    "info",
    "temp",
    "user_stuff"
]
```

### 2. Memory Management Strategies

```python
# Memory lifecycle management
async def memory_cleanup_example():
    agent = RefinireAgent(
        name="cleanup_agent",
        generation_instructions="""
        Manage memory efficiently:
        1. Regular cleanup of outdated information
        2. Archive completed projects
        3. Update user preferences when they change
        4. Remove duplicate or conflicting memories
        """,
        mcp_servers=["stdio://@modelcontextprotocol/server-memory"],
        model="gpt-4o-mini"
    )
    
    # Example cleanup operations
    cleanup_tasks = [
        "List all memories and identify outdated project information",
        "Archive memories for completed projects from last year",
        "Update user preferences that have changed",
        "Remove any duplicate user profile information"
    ]
    
    for task in cleanup_tasks:
        result = await agent.run_async(task)
        print(f"Cleanup: {task}")
        print(f"Result: {result.content}\n")
```

### 3. Error Handling and Validation

```python
from refinire import RefinireAgent
import asyncio

class RobustMemoryAgent:
    def __init__(self):
        self.agent = RefinireAgent(
            name="robust_memory_agent",
            generation_instructions="""
            You are a robust memory assistant. Always:
            1. Validate information before storing
            2. Handle memory errors gracefully
            3. Provide fallback responses if memory fails
            4. Confirm successful memory operations
            5. Report any memory issues to users
            """,
            mcp_servers=["stdio://@modelcontextprotocol/server-memory"],
            model="gpt-4o-mini"
        )
    
    async def safe_store_memory(self, key: str, value: str):
        """Safely store memory with validation"""
        try:
            message = f"""
            Please store the following information safely:
            Key: {key}
            Value: {value}
            
            Before storing:
            1. Validate the key format is appropriate
            2. Check if this key already exists
            3. Store the information
            4. Confirm the storage was successful
            """
            
            result = await self.agent.run_async(message)
            return result.content
            
        except Exception as e:
            return f"Error storing memory: {str(e)}"
    
    async def safe_retrieve_memory(self, key: str):
        """Safely retrieve memory with fallback"""
        try:
            message = f"""
            Please retrieve the memory with key: {key}
            
            If the key doesn't exist:
            1. Try searching for similar keys
            2. Provide alternative suggestions
            3. Explain what information is available
            """
            
            result = await self.agent.run_async(message)
            return result.content
            
        except Exception as e:
            return f"Error retrieving memory: {str(e)}"

# Usage example
async def robust_memory_demo():
    agent = RobustMemoryAgent()
    
    # Safe storage
    result = await agent.safe_store_memory(
        "user_alice_preferences", 
        "Prefers detailed technical explanations, works with Python and ML"
    )
    print(f"Storage result: {result}")
    
    # Safe retrieval
    result = await agent.safe_retrieve_memory("user_alice_preferences")
    print(f"Retrieval result: {result}")

if __name__ == "__main__":
    asyncio.run(robust_memory_demo())
```

## Conclusion

MCP Memory integration with Refinire provides powerful persistent memory capabilities for AI agents. Key benefits include:

- **Persistent Memory**: Information survives across sessions
- **Structured Storage**: Organized memory management
- **Easy Integration**: Simple setup with Refinire
- **Flexible Usage**: Suitable for various applications

This integration enables building sophisticated AI assistants that can maintain context, remember user preferences, and provide personalized experiences across multiple interactions.

### Next Steps

1. Experiment with the provided examples
2. Adapt the patterns to your specific use case
3. Explore other MCP servers for different capabilities
4. Build custom memory management workflows
5. Integrate with your existing applications

For more advanced MCP integrations, explore the [Advanced Features Guide](advanced.md) and [ContextProvider Guide](context_provider_guide.md).