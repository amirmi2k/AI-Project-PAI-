"""
MAS Project: Digital Countermeasure Unit vs. "The Entity"
Description: Orchestrates a sequential 4-agent pipeline to process complex multi-vector threats.
"""

import json
import time
import urllib.request
import concurrent.futures
from typing import Any
from crewai import Crew, Process, Task

# Import your separated tools and agents from the other files
from tools import simulate_tool_failure
from agents import coordinator_agent, audio_specialist, video_specialist, strategic_predictor

class MASController:
    """Manages the end-to-end multi-agent pipeline and enforces system robustness."""

    def __init__(self, incident_report: str):
        self.incident_report = incident_report.strip()
        self.state: dict[str, Any] = {"input": self.incident_report, "workflow": "sequential_pipeline"}

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

    def _trigger_fallback(self, error_msg: str) -> dict:
        print(f"\n[CRITICAL ERROR CAUGHT]: {error_msg}")
        return {
            "status": "SYSTEM DEGRADED",
            "error_log": error_msg,
            "analysis_result": "Pipeline execution halted due to system degradation or timeout.",
            "confidence_score": 0.0,
            "next_step": "Manual defensive review immediately"
        }

    def execute_pipeline(self) -> dict:
        print("\n--- INITIATING 4-AGENT SEQUENTIAL PIPELINE ---")

        if not self._llm_is_available():
            return self._trigger_fallback("Local LLM endpoint is unavailable at http://127.0.0.1:11434.")

        # 1. Cyber Task
        task_cyber = Task(
            description=f"Analyze network indicators in this report: {self.incident_report}",
            expected_output="Strict JSON with analysis_result, confidence_score, and next_step.",
            agent=coordinator_agent
        )
        
        # 2. Audio Task
        task_audio = Task(
            description=f"Analyze audio markers mentioned in this report: {self.incident_report}",
            expected_output="Strict JSON with analysis_result, confidence_score, and next_step.",
            agent=audio_specialist
        )

        # 3. Video Task
        task_video = Task(
            description=f"Analyze video surveillance streams mentioned in this report: {self.incident_report}",
            expected_output="Strict JSON with analysis_result, confidence_score, and next_step.",
            agent=video_specialist
        )

        # 4. Strategic Task (Synthesizes the first 3)
        task_strategy = Task(
            description="Review the intelligence gathered by the network, audio, and video specialists. Formulate a final countermeasure strategy.",
            expected_output="Strict JSON with analysis_result, confidence_score, and next_step.",
            agent=strategic_predictor,
            context=[task_cyber, task_audio, task_video] # Explicitly links the previous outputs
        )

        # Assemble the full crew
        full_crew = Crew(
            agents=[coordinator_agent, audio_specialist, video_specialist, strategic_predictor],
            tasks=[task_cyber, task_audio, task_video, task_strategy],
            process=Process.sequential
        )

        start_time = time.time()
        try:
            # [Human Dev Comment 6]: To strictly adhere to the project's time budget limit, 
            # we enforce a hard cutoff at 29 seconds for the entire pipeline execution.
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(full_crew.kickoff)
                raw_result = future.result(timeout=29.0)
            
            self.state["runtime_seconds"] = round(time.time() - start_time, 2)
            self.state["final_output"] = self._safe_json_result(raw_result)
            self.state["status"] = "OK"
            return self.state

        except concurrent.futures.TimeoutError:
            print("\n[TIMEOUT]: Pipeline execution forcefully terminated at 29 seconds.")
            return self._trigger_fallback("Execution exceeded the strict 30-second time budget limit.")
        except Exception as exc:
            return self._trigger_fallback(str(exc))


if __name__ == "__main__":
    # A complex threat report designed to trigger all 4 agents
    master_incident_report = (
        "At 0200 hours, server 10.0.0.9 experienced a massive brute-force SSH attack. "
        "Simultaneously, intercepted audio file 'exec_voicemail.wav' showed unnatural pitch shifts, "
        "and security camera feed 'cam_04.mp4' exhibited duplicate frame glitches."
    )

    controller = MASController(master_incident_report)
    final_output = controller.execute_pipeline()
    
    print("\nFINAL PIPELINE STATE:")
    print(json.dumps(final_output, indent=2))