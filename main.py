"""
MAS Project: Digital Countermeasure Unit vs. "The Entity"
Description: Orchestrates specialized agents to analyze cyber threats in a resilient multi-agent workflow.
"""

import json
import time
import urllib.request
import concurrent.futures
from typing import Any
from crewai import Crew, Process, Task

# Import your separated logic
from tools import simulate_tool_failure
from agents import coordinator_agent, audio_specialist, video_specialist, strategic_predictor

class MASController:
    """Routes user inputs to the correct specialist and triggers a safe fallback."""

    def __init__(self, user_input: str):
        self.user_input = user_input.lower().strip()
        self.state: dict[str, Any] = {"input": user_input, "workflow": "static_router"}

    def _llm_is_available(self) -> bool:
        try:
            with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=3) as response:
                return response.status == 200
        except Exception:
            return False

    def _safe_json_result(self, raw_result: Any) -> dict[str, Any]:
        try:
            parsed = json.loads(str(raw_result))
            if isinstance(parsed, dict):
                return parsed
            return {"analysis_result": str(raw_result), "confidence_score": 0.0, "next_step": "Manual review"}
        except json.JSONDecodeError:
            print("\n[WARNING]: Agent output was not valid JSON. Wrapping raw output safely.")
            return {"analysis_result": str(raw_result), "confidence_score": 0.0, "next_step": "Manual review", "format_error": True}

    def _offline_analysis(self) -> dict:
        result = {
            "analysis_result": "Threat indicators present, but the system is offline.",
            "confidence_score": 0.65,
            "next_step": "Continue manual monitoring"
        }
        self.state.update({
            "status": "OFFLINE_ANALYSIS",
            "final_output": result,
            "error_log": "Local LLM endpoint is unavailable."
        })
        return self.state

    def route_and_execute(self) -> dict:
        print("\n--- INITIATING SYSTEM ROUTER ---")

        try:
            if "audio" in self.user_input or "voice" in self.user_input:
                print("[ROUTER]: Audio threat detected. Dispatching Audio Specialist.")
                task = Task(description=f"Analyze: {self.user_input}", expected_output="Strict JSON", agent=audio_specialist)
                crew = Crew(agents=[audio_specialist], tasks=[task], process=Process.sequential)

            elif "network" in self.user_input or "ip" in self.user_input:
                print("[ROUTER]: Cyber threat detected. Dispatching Defense Coordinator.")
                task = Task(description=f"Analyze: {self.user_input}", expected_output="Strict JSON", agent=coordinator_agent)
                crew = Crew(agents=[coordinator_agent], tasks=[task], process=Process.sequential)

            elif "video" in self.user_input or "stream" in self.user_input:
                print("[ROUTER]: Video manipulation detected. Dispatching Video Specialist.")
                task = Task(description=f"Analyze: {self.user_input}", expected_output="Strict JSON", agent=video_specialist)
                crew = Crew(agents=[video_specialist], tasks=[task], process=Process.sequential)

            elif "simulate failure" in self.user_input:
                print("[ROUTER]: Testing robustness and fallback execution.")
                task = Task(description="Use the Simulate Failure Tool immediately.", expected_output="Fallback JSON", agent=strategic_predictor, tools=[simulate_tool_failure])
                crew = Crew(agents=[strategic_predictor], tasks=[task], process=Process.sequential)

            else:
                raise ValueError("Unrecognized threat vector.")

            if not self._llm_is_available():
                return self._offline_analysis()

            start_time = time.time()
            try:
                # [Human Dev Comment 6]: ThreadPoolExecutor forces a hard cutoff at 29 seconds, 
                # preventing the LLM generation from hanging the application and violating project specs.
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(crew.kickoff)
                    raw_result = future.result(timeout=29.0)
                
                self.state["runtime_seconds"] = round(time.time() - start_time, 2)
            except concurrent.futures.TimeoutError:
                print(f"[TIMEOUT]: Agent execution forcefully terminated at 29 seconds.")
                return self._trigger_fallback("Execution exceeded the 30-second time budget.")

            self.state["final_output"] = self._safe_json_result(raw_result)
            self.state["status"] = "OK"
            return self.state

        except Exception as exc:
            return self._trigger_fallback(str(exc))

    def _trigger_fallback(self, error_msg: str) -> dict:
        print(f"\n[CRITICAL ERROR CAUGHT]: {error_msg}")
        return {
            "status": "SYSTEM DEGRADED",
            "error_log": error_msg,
            "analysis_result": "Limited threat assessment due to system degradation.",
            "confidence_score": 0.0,
            "next_step": "Manual defensive review"
        }

if __name__ == "__main__":
    test_input_1 = "Analyze network activity from IP 10.0.0.9 for The Entity breach."
    controller = MASController(test_input_1)
    result = controller.route_and_execute()
    print("\nFINAL STATE:", json.dumps(result, indent=2))

    time.sleep(1)

    print("\n\n" + "=" * 50)
    test_input_2 = "Please simulate failure to test system robustness."
    controller2 = MASController(test_input_2)
    fallback_result = controller2.route_and_execute()
    print("\nFINAL STATE:", json.dumps(fallback_result, indent=2))