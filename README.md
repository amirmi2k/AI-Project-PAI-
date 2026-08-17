# Digital Countermeasure Unit Against "The Entity"

A Multi-Agent System (MAS) built with CrewAI to simulate a cyber defense and counterintelligence workflow against an advanced rogue AI threat known as "The Entity". The system routes incoming threat data to specialized agents, analyzes cyber, audio, and video risks, and produces structured defensive recommendations.

This project is implemented in [main.py](main.py) and uses local Ollama models for inference.

## Project Overview

The system is designed to process complex multi-step security inputs and coordinate multiple specialist agents to detect:

- cyber intrusion attempts
- suspicious network activity
- voice deepfake or manipulated audio indicators
- video stream tampering or manipulation
- strategic defense recommendations

The project uses a static routing mechanism to dispatch requests to the relevant agent, while also including a fallback mechanism to prevent crashes during model failures or malformed outputs.

## System Architecture

### Router / Supervisor
The router receives the user input and decides which specialist agent should handle it based on keywords and threat categories.

Router types:
- Static router
- Keyword-based conditional dispatch
- Deterministic path selection for safety and repeatability

### Specialized Agents
The project includes 4 distinct agents:

1. Cyber Offense/Defense Coordinator
   - handles network threats, suspicious IP behavior, and cyber intrusion analysis

2. Deepfake Audio Analysis Specialist
   - detects manipulated or synthetic audio evidence

3. Manipulated Video Stream Detector
   - inspects suspicious or tampered video streams

4. Tactical & Strategic Predictor
   - formulates defense strategies and longer-term countermeasures

### Custom Tools
The system includes a minimum of 3 custom tools:

- Network Traffic Analyzer
- Audio Deepfake Scanner
- Video Stream Tampering Detector
- Simulate Failure Tool

## Communication Workflow

The agent workflow follows a sequential multi-agent pipeline:

1. Input is received
2. Router identifies the threat type
3. Appropriate agent is selected
4. Task is executed using the assigned model
5. Result is validated and structured as JSON
6. Fallback process is triggered if needed

This design ensures that specialist roles remain clear and that monitoring and error handling remain robust.

## Fallback & Risk Mitigation

The system includes a fallback mechanism to handle:

- unavailable local LLM endpoints
- malformed JSON output from the model
- tool execution errors
- retry/timeout issues
- unexpected exceptions

When the model fails or a simulated failure is triggered, the system does not crash. Instead, it produces a partial, safe response based on available processed information and logs the risk state.

## Technical Requirements Covered

- Minimum 3 distinct agents implemented
- Minimum 3 custom tools implemented
- At least 2 conditional routing paths present
- LLM timeout and retry configuration included
- Multiple exception handling blocks implemented
- Strict JSON output enforcement in agent prompts
- Few-shot prompting examples included
- Docstrings used for methods and custom tools
- Inline explanatory comments included

## Project Files

- [main.py](main.py) - Main MAS implementation
- [requirements.txt](requirements.txt) - Python dependencies
- [test_main.py](test_main.py) - Regression tests for offline analysis logic

## Requirements

Install the required dependencies:

```bash
pip install -r requirements.txt
