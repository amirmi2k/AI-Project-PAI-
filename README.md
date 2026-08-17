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
```

## Quick Start (Download, Setup, Run)

Follow these steps from scratch on Windows.

### 1. Download the project

Option A: Clone with Git

```bash
git clone <your-repo-url>
cd "AI project (PAI)"
```

Option B: Download ZIP

1. Open the repository page.
2. Click **Code** -> **Download ZIP**.
3. Extract the ZIP.
4. Open a terminal in the extracted folder `AI project (PAI)`.

### 2. Install Python

1. Install Python 3.10 or newer from the official Python website.
2. During installation, enable **Add Python to PATH**.
3. Verify:

```bash
python --version
```

### 3. Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 4. Install project dependencies

```bash
pip install -r requirements.txt
```

### 5. Install and run Ollama

1. Install Ollama from the official Ollama website.
2. Start Ollama (it should run on `http://127.0.0.1:11434`).
3. Pull the model used by this project:

```bash
ollama pull llama3.1:latest
```

### 6. Run the AI system

From the project root:

```bash
python main.py
```

The script runs built-in scenarios and prints structured JSON output, including fallback behavior if needed.

## Run Tests

You can run the included tests from the project root:

```bash
pytest "test connection"
```

If `pytest` is not installed:

```bash
pip install pytest
pytest "test connection"
```

## Common Issues

- Ollama not reachable:
   - Ensure Ollama is running.
   - Verify `http://127.0.0.1:11434` is accessible.
   - Confirm the model is pulled: `ollama list`.

- `python` command not found:
   - Reinstall Python and enable **Add Python to PATH**.

- Dependency install errors:
   - Activate `.venv` first.
   - Upgrade pip: `python -m pip install --upgrade pip`

## Notes

- The model is configured in `main.py` as `ollama/llama3.1:latest`.
- If Ollama is unavailable, the app automatically uses an offline heuristic fallback path.
