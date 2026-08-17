from crewai import Agent, Task, Crew, LLM

# Target the exact IP
test_llm = LLM(model="ollama/llama3.1", base_url="http://127.0.0.1:11434")

# 1. Define the Agent
agent = Agent(
    role="Tester", 
    goal="Say hello", 
    backstory="You are a connection tester.", 
    llm=test_llm
)

# 2. Define the Task (This is what was missing!)
task = Task(
    description="Say the exact word 'Hello' and nothing else.",
    expected_output="A single word: Hello",
    agent=agent
)

# 3. Form the Crew and Kickoff
crew = Crew(agents=[agent], tasks=[task])
print("--- SENDING REQUEST TO OLLAMA ---")
result = crew.kickoff()

print("\n--- OLLAMA RESPONSE ---")
print(result)
