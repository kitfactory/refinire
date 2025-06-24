from agents import Agent, function_tool

@function_tool
def test_tool():
    return "test"

try:
    agent = Agent(name="test", instructions="test", tools=[test_tool])
    print("Agent created successfully with FunctionTool")
except Exception as e:
    print(f"Error creating Agent with FunctionTool: {e}")

try:
    agent = Agent(name="test2", instructions="test", tools=[])
    print("Agent created successfully without tools")
except Exception as e:
    print(f"Error creating Agent without tools: {e}") 