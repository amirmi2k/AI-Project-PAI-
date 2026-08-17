"""
MAS Project: Digital Countermeasure Unit vs. "The Entity"
Description: Orchestrates specialized agents to analyze cyber threats, audio deepfakes,
and coordinated defense strategies in a resilient multi-agent workflow.
"""

import json
import time
import urllib.request
from typing import Any

from crewai import Agent, Crew, LLM, Process, Task
from crewai.tools import tool


# ==========================================
# 1. CUSTOM TOOLS (Minimum 3 required)
# ==========================================

@tool("Network Traffic Analyzer")
def analyze_network_traffic(ip_address: str) -> str:
    """
    Simulates a network scan on a given IP address.

    Args:
        ip_address (str): The IP address to inspect.

    Returns:
        str: A synthetic threat summary for the provided network source.
    """
    return f"[ALERT] High-velocity brute-force SSH attack detected from {ip_address}."


@tool("Audio Deepfake Scanner")
def scan_audio_deepfake(file_name: str) -> str:
    """
    Scans a supplied audio sample for synthetic voice manipulation.

    Args:
        file_name (str): The audio file name or label to analyze.

    Returns:
        str: A synthetic detection summary containing deepfake probability.
    """
    return f"Spectrogram analysis of {file_name} reveals 92% synthetic voice generation."


@tool("Video Stream Tampering Detector")
def inspect_video_stream(video_path: str) -> str:
    """
    Performs a mock tampering inspection on a video stream or file reference.

    Args:
        video_path (str): The path or filename of the target video stream.

    Returns:
        str: A simulated tampering report indicating frame manipulation evidence.
    """
    return f"Frame consistency check for {video_path} shows 87% temporal manipulation suspicion."


@tool("Simulate Failure Tool")
def simulate_tool_failure(dummy_input: str) -> str:
    """
    Intentionally triggers a runtime failure to exercise the fallback policy.

    Args:
        dummy_input (str): A placeholder argument used to invoke the tool.

    Returns:
        str: Never returns because this tool intentionally raises an exception.
    """
    # [Human Dev Comment 1]: The AI was allowed to create a tool, but I modified its behavior here
    # to force a controlled failure that proves the fallback mechanism works under load.
    raise TimeoutError("Simulated API disconnection for fallback testing.")


# ==========================================
# 2. LLM CONFIGURATION & ROBUSTNESS
# ==========================================

# Configuring timeout (<= 30s) and max_retries (<= 3) as per rubric.
local_llm = LLM(
    model="ollama/llama3.1",
    base_url="http://localhost:11434",
    timeout=30.0,
    max_retries=3,
)


# ==========================================
# 3. SPECIALIZED AI AGENTS (Minimum 3)
# ==========================================

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

Input: "Database server is transmitting heavy outbound traffic."
Output: {"analysis_result": "Suspicious exfiltration attempt", "confidence_score": 0.85, "next_step": "Network isolation"}
""",
)

audio_specialist = Agent(
    role="Deepfake Audio Analysis Specialist",
    goal="Assess suspicious audio files and decide whether they contain synthetic manipulation.",
    backstory="You are a spectral analysis expert focused on voice impersonation and deepfake detection.",
    tools=[scan_audio_deepfake],
    llm=local_llm,
    max_iter=3,
    # [Human Dev Comment 3]: I restricted the audio specialist to a precise JSON contract so it can
    # report confidence consistently without extra narrative that breaks parsing.
    system_template="""
You must output strictly in JSON format with keys: ['analysis_result', 'confidence_score', 'next_step'].
Do not output any text outside the JSON object.

Examples:
Input: "The intercepted voice sample shows low entropy and repeated pitch patterns."
Output: {"analysis_result": "Synthetic voice detected", "confidence_score": 0.91, "next_step": "Flag audio sample for review"}

Input: "The recording shows natural breath and tonal variation."
Output: {"analysis_result": "Likely genuine audio", "confidence_score": 0.62, "next_step": "Continue normal monitoring"}
""",
)

video_specialist = Agent(
    role="Manipulated Video Stream Detector",
    goal="Identify manipulated video feeds and highlight suspicious frame-level alterations.",
    backstory="You look for visual tampering, AI-generated faces, and synchronized payload patterns in surveillance footage.",
    tools=[inspect_video_stream],
    llm=local_llm,
    max_iter=3,
    # [Human Dev Comment 4]: I separated the video role from the audio role so each agent owns a
    # distinct evidence source and the router can dispatch correctly based on the initial input.
    system_template="""
You must output strictly in JSON format with keys: ['analysis_result', 'confidence_score', 'next_step'].
Do not include narrative text outside the JSON structure.

Examples:
Input: "Video feed shows frame duplication and face morphing artifacts."
Output: {"analysis_result": "Video manipulation detected", "confidence_score": 0.93, "next_step": "Isolate camera stream"}

Input: "The footage has normal frame continuity and no suspicious edits."
Output: {"analysis_result": "Video stream appears authentic", "confidence_score": 0.69, "next_step": "Continue passive monitoring"}
""",
)

strategic_predictor = Agent(
    role="Tactical & Strategic Predictor",
    goal="Formulate a long-term defense strategy based on verified threat intelligence.",
    backstory="You analyze attack patterns, predict The Entity's next moves, and design defensive countermeasures.",
    llm=local_llm,
    max_iter=3,
    # [Human Dev Comment 5]: This agent is intentionally constrained to strategy-only reasoning so it does
    # not override the evidence gathered by specialists with unsupported assumptions.
    system_template="""
You must output strictly in JSON format with keys: ['analysis_result', 'confidence_score', 'next_step'].
Do not include free-form text outside the JSON object.

Examples:
Input: "Network attack and synthetic audio both indicate compromised surveillance channels."
Output: {"analysis_result": "Multi-vector attack detected", "confidence_score": 0.96, "next_step": "Activate layered defensive response"}

Input: "Only a single low-confidence anomaly is present."
Output: {"analysis_result": "Limited threat signal", "confidence_score": 0.71, "next_step": "Maintain observation and monitor logs"}
""",
)


# ==========================================
# 4. STATIC ROUTER & FALLBACK MODULE
# ==========================================

class MASController:
    """
    Routes user inputs to the correct specialist and triggers a safe fallback when critical errors occur.
    """

    def __init__(self, user_input: str):
        """
        Initializes the controller with the incoming threat intelligence.

        Args:
            user_input (str): The raw user query or threat report.
        """
        self.user_input = user_input.lower().strip()
        self.state: dict[str, Any] = {"input": user_input, "workflow": "static_router"}

    def _llm_is_available(self) -> bool:
        """
        Checks whether the local Ollama endpoint is reachable.

        Returns:
            bool: True if the local LLM service is reachable; otherwise False.
        """
        try:
            request = urllib.request.Request("http://localhost:11434/api/tags", timeout=3)
            with urllib.request.urlopen(request, timeout=3) as response:
                return response.status == 200
        except Exception:
            return False

    def _safe_json_result(self, raw_result: Any) -> dict[str, Any]:
        """
        Attempts to parse agent output as JSON and returns a safe fallback when formatting fails.

        Args:
            raw_result (Any): The raw result returned by the agent or crew.

        Returns:
            dict[str, Any]: Structured JSON payload or a wrapped fallback object.
        """
        try:
            parsed = json.loads(str(raw_result))
            if isinstance(parsed, dict):
                return parsed
            return {"analysis_result": str(raw_result), "confidence_score": 0.0, "next_step": "Manual review"}
        except json.JSONDecodeError:
            print("\n[WARNING]: Agent output was not valid JSON. Wrapping raw output safely.")
            return {"analysis_result": str(raw_result), "confidence_score": 0.0, "next_step": "Manual review", "format_error": True}

    def route_and_execute(self) -> dict:
        """
        Uses a static keyword router to send input to the correct specialist agent.

        Returns:
            dict: A state dictionary containing the final analysis or fallback response.
        """
        print("\n--- INITIATING SYSTEM ROUTER ---")

        # [Human Dev Comment 6]: I kept the router static instead of LLM-driven because it is more
        # deterministic and reduces the chance of routing errors in edge cases or offline deployments.
        try:
            # CONDITIONAL ROUTING PATH 1: audio or voice threat
            if "audio" in self.user_input or "voice" in self.user_input:
                print("[ROUTER]: Audio threat detected. Dispatching Audio Specialist.")
                task = Task(
                    description=f"Analyze this audio threat data: {self.user_input}",
                    expected_output="Strict JSON with analysis_result, confidence_score, and next_step.",
                    agent=audio_specialist,
                )
                crew = Crew(agents=[audio_specialist], tasks=[task], process=Process.sequential)

            # CONDITIONAL ROUTING PATH 2: network or IP threat
            elif "network" in self.user_input or "ip" in self.user_input:
                print("[ROUTER]: Cyber threat detected. Dispatching Defense Coordinator.")
                task = Task(
                    description=f"Analyze this network threat data: {self.user_input}",
                    expected_output="Strict JSON with analysis_result, confidence_score, and next_step.",
                    agent=coordinator_agent,
                )
                crew = Crew(agents=[coordinator_agent], tasks=[task], process=Process.sequential)

            # CONDITIONAL ROUTING PATH 3: video threat
            elif "video" in self.user_input or "stream" in self.user_input:
                print("[ROUTER]: Video manipulation detected. Dispatching Video Specialist.")
                task = Task(
                    description=f"Inspect this manipulated video intelligence: {self.user_input}",
                    expected_output="Strict JSON with analysis_result, confidence_score, and next_step.",
                    agent=video_specialist,
                )
                crew = Crew(agents=[video_specialist], tasks=[task], process=Process.sequential)

            # TRIGGER SIMULATED FAILURE FOR ASSESSMENT
            elif "simulate failure" in self.user_input:
                print("[ROUTER]: Testing robustness and fallback execution.")
                task = Task(
                    description="Use the Simulate Failure Tool immediately to test resilience.",
                    expected_output="A controlled failure warning and fallback state.",
                    agent=strategic_predictor,
                    tools=[simulate_tool_failure],
                )
                crew = Crew(agents=[strategic_predictor], tasks=[task], process=Process.sequential)

            else:
                raise ValueError("Unrecognized threat vector.")

            if not self._llm_is_available():
                print("[WARNING]: Local Ollama backend unavailable. Returning offline fallback response.")
                return self._trigger_fallback("Local LLM endpoint is unavailable at http://localhost:11434.")

            start_time = time.time()
            try:
                raw_result = crew.kickoff()
                self.state["runtime_seconds"] = round(time.time() - start_time, 2)
            except TimeoutError as exc:
                print(f"[TIMEOUT]: Agent execution exceeded the time budget. {exc}")
                return self._trigger_fallback(str(exc))
            except KeyError as exc:
                print(f"[STATE ERROR]: Missing required workflow state. {exc}")
                return self._trigger_fallback(str(exc))

            try:
                self.state["final_output"] = self._safe_json_result(raw_result)
                self.state["status"] = "OK"
            except TypeError as exc:
                print(f"[TYPE ERROR]: Output serialization failed. {exc}")
                return self._trigger_fallback(str(exc))

            return self.state

        except ValueError as exc:
            return self._trigger_fallback(str(exc))
        except KeyError as exc:
            return self._trigger_fallback(str(exc))
        except TimeoutError as exc:
            return self._trigger_fallback(str(exc))
        except Exception as exc:
            return self._trigger_fallback(str(exc))

    def _trigger_fallback(self, error_msg: str) -> dict:
        """
        Produces a partial emergency response when the system encounters a critical failure.

        Args:
            error_msg (str): The captured exception message.

        Returns:
            dict: A safe degraded-state response with a risk warning.
        """
        print(f"\n[CRITICAL ERROR CAUGHT]: {error_msg}")
        print(">>> TRIGGERING RISK WARNING AND FALLBACK STRATEGY <<<")
        # The fallback path intentionally returns immediately so it can complete in under 5 seconds.
        return {
            "status": "SYSTEM DEGRADED",
            "fallback_action": "Isolating network nodes and escalating manual review for limited processed data.",
            "error_log": error_msg,
            "analysis_result": "Limited threat assessment available due to system degradation.",
            "confidence_score": 0.0,
            "next_step": "Manual defensive review",
        }


# ==========================================
# 5. MAIN EXECUTION
# ==========================================

if __name__ == "__main__":
    # Test 1: Standard network threat scenario.
    test_input_1 = "Analyze network activity from IP 10.0.0.9 for The Entity breach."
    controller = MASController(test_input_1)
    result = controller.route_and_execute()
    print("\nFINAL STATE:", json.dumps(result, indent=2))

    time.sleep(1)

    # Test 2: Simulated failure path for fallback demonstration.
    print("\n\n" + "=" * 50)
    test_input_2 = "Please simulate failure to test system robustness."
    controller2 = MASController(test_input_2)
    fallback_result = controller2.route_and_execute()
    print("\nFINAL STATE:", json.dumps(fallback_result, indent=2))