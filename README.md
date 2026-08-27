# Project Sentinel: Multi-Agent Cyber Defense System

Project Sentinel is a CrewAI multi-agent system that simulates a cyber defense and counterintelligence workflow against an advanced rogue AI threat known as "The Entity". It uses a local Llama 3.1 model through Ollama, so incident analysis does not depend on an external cloud API.

## 1. Project Overview

When given an incident report, the system:

1. Generates synthetic network, audio, and video evidence files when they are missing.
2. Runs four specialist agents in a sequential pipeline.
3. Uses Python tools to read and analyze the local JSON evidence.
4. Combines the findings into a human-readable executive incident report.

## 2. System Architecture

### Orchestrator: `main.py`

`MASController` initializes the datasets, checks whether Ollama is available, executes the CrewAI pipeline, extracts malformed JSON safely, and returns a `SYSTEM DEGRADED` fallback when the local model is unavailable, times out, or raises an error.

### Agents: `agents.py`

The crew contains four specialized AI personas:

1. **Cyber Offense/Defense Coordinator:** Analyzes SSH brute-force attempts and network anomalies.
2. **Deepfake Audio Specialist:** Evaluates spectral analysis data for synthetic voice markers.
3. **Manipulated Video Detector:** Inspects surveillance logs for frame tampering.
4. **Tactical & Strategic Predictor:** Inherits the first three outputs and formulates a unified defense strategy.

### Forensic Tools: `tools.py`

Agents use custom tools backed by local JSON files:

- `Network Traffic Analyzer` reads `server_logs.json`.
- `Audio Deepfake Scanner` reads `audio_scan_results.json`.
- `Video Stream Tampering Detector` reads `video_scan_results.json`.
- `Simulate Failure Tool` raises a controlled timeout to exercise fallback behavior.

## 3. Technical Design

### Workflow and Communication

The system uses a sequential multi-agent pipeline. The cyber, audio, and video tasks run first. Their outputs are passed to the Tactical & Strategic Predictor through CrewAI's `context` parameter, allowing the final strategy to be grounded in evidence from all three domains.

### Robustness and Fallbacks

Two defensive mechanisms protect the workflow from unreliable local model output:

1. **Execution timeout:** The pipeline runs inside a `ThreadPoolExecutor`. If processing exceeds the configured limit, the controller returns a safe degraded-system response instead of crashing.
2. **Safe JSON extraction:** `_safe_json_result` tries normal JSON parsing first, then uses a regular expression to extract a JSON object from surrounding conversational or Markdown text. If parsing still fails, it returns the raw output with a zero confidence score and requests manual review.

### AI Usage and Human Engineering

AI assistance was used for initial CrewAI boilerplate and tool docstrings. The project-specific engineering includes synthetic dataset bootstrapping, local JSON file I/O, resilient model-output parsing, controlled failure handling, and recursive formatting for the terminal executive report.

## 4. Installation Guide

### Step 1: Open the Project

Open a terminal in the project directory. Python 3.10 or newer is recommended.

### Step 2: Create a Virtual Environment

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install crewai streamlit
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install crewai streamlit
```

### Step 3: Install and Start Ollama

1. Install Ollama from [ollama.com](https://ollama.com/).
2. Start Ollama and confirm that it is available at `http://127.0.0.1:11434`.
3. Pull the required model:

```bash
ollama pull llama3.1
```

## 5. Running the System

Run the default scenario from the project directory:

```bash
python main.py
```

The program creates the JSON evidence files if necessary, runs the four-agent analysis, and prints an executive incident report in the terminal.

### Launch the Streamlit Dashboard

From the project directory, with the virtual environment activated, run:

```bash
streamlit run main.py
```

Streamlit opens the Project Sentinel dashboard in your browser. Enter an incident report and select **Deploy Agents** to start the analysis.

## 6. Testing Dynamic Responses

To test a different incident:

1. Open `main.py`.
2. Find `master_incident_report` near the bottom of the file.
3. Replace its value with a new scenario, for example:

```python
master_incident_report = (
	"A user reported that the main lobby camera feed freezes every five seconds, "
	"but the network logs appear normal."
)
```

4. Save the file and run `python main.py` again.

The agents should adapt their analysis and recommend a response based on the new incident context and available evidence.

## 7. Project Files

| File | Purpose |
| --- | --- |
| `main.py` | Seeds evidence, orchestrates the crew, and prints the report |
| `agents.py` | Configures Ollama and defines the four agents |
| `tools.py` | Defines the local forensic analysis tools |
| `server_logs.json` | Network evidence dataset |
| `audio_scan_results.json` | Audio analysis dataset |
| `video_scan_results.json` | Video tampering dataset |