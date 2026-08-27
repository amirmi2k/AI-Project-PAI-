"""
MAS Project: Agents Module
Description: Configures the local LLM and defines the specialized AI personas.
"""

from crewai import Agent, LLM
from tools import analyze_network_traffic, scan_audio_deepfake, inspect_video_stream

# Configuring timeout (<= 30s) and max_retries (<= 3) as per project requirements.
local_llm = LLM(
    model="ollama/llama3.1",
    base_url="http://127.0.0.1:11434",
    timeout=30.0,
    max_retries=3
)

coordinator_agent = Agent(
    role="Cyber Offense/Defense Coordinator",
    goal="Analyze network logs for attacks by The Entity and output strictly in JSON.",
    backstory="You are a senior cyber defense coordinator responsible for routing threat intelligence.",
    tools=[analyze_network_traffic],
    llm=local_llm,
    max_iter=3,
    # [Human Dev Comment 2]: I enforced a strict JSON schema and few-shot examples so the agent
    # cannot wander into free-form commentary when the system requires deterministic outputs.
    system_template="""
You must output strictly in JSON format with keys: ['analysis_result', 'confidence_score', 'next_step'].
Do not include any conversational text outside this JSON structure.

Examples:
Input: "System logs show 500 failed SSH login attempts from IP 192.168.1.45."
Output: {"analysis_result": "Brute-force attack detected", "confidence_score": 0.98, "next_step": "Block IP"}

Input: "Normal traffic on port 80."
Output: {"analysis_result": "No threat detected", "confidence_score": 0.10, "next_step": "Continue monitoring"}
"""
)

audio_specialist = Agent(
    role="Deepfake Audio Analysis Specialist",
    goal="Assess suspicious audio files and decide whether they contain synthetic manipulation.",
    backstory="You are a spectral analysis expert focused on voice impersonation and deepfake detection.",
    tools=[scan_audio_deepfake],
    llm=local_llm,
    max_iter=3,
    system_template="""
You must output strictly in JSON format with keys: ['analysis_result', 'confidence_score', 'next_step'].
Do not output any text outside the JSON object.

Examples:
Input: "The intercepted voice sample shows low entropy and repeated pitch patterns."
Output: {"analysis_result": "Synthetic voice detected", "confidence_score": 0.91, "next_step": "Flag audio sample for review"}
"""
)

video_specialist = Agent(
    role="Manipulated Video Stream Detector",
    goal="Identify manipulated video feeds and highlight suspicious frame-level alterations.",
    backstory="You look for visual tampering, AI-generated faces, and synchronized payload patterns in surveillance footage.",
    tools=[inspect_video_stream],
    llm=local_llm,
    max_iter=3,
    system_template="""
You must output strictly in JSON format with keys: ['analysis_result', 'confidence_score', 'next_step'].
Do not include narrative text outside the JSON structure.

Examples:
Input: "Video feed shows frame duplication and face morphing artifacts."
Output: {"analysis_result": "Video manipulation detected", "confidence_score": 0.93, "next_step": "Isolate camera stream"}
"""
)

strategic_predictor = Agent(
    role="Tactical & Strategic Predictor",
    goal="Formulate a long-term defense strategy based on verified threat intelligence.",
    backstory="You analyze attack patterns, predict The Entity's next moves, and design defensive countermeasures.",
    llm=local_llm,
    max_iter=3,
    system_template="""
You must output strictly in JSON format with keys: ['analysis_result', 'confidence_score', 'confidence_justification', 'next_step'].
Do not include free-form text outside the JSON object.
DO NOT include any comments (like // or /*) inside the JSON block. Output ONLY raw, parseable JSON.

Examples:
Input: "Network attack and synthetic audio both indicate compromised surveillance channels."
Output: {"analysis_result": "Multi-vector attack detected", "confidence_score": 0.96, "confidence_justification": "Audio tool returned 0.94 synthetic probability and network logs show 500 failed SSH attempts, yielding high overall certainty.", "next_step": "Activate layered defensive response"}
"""
)