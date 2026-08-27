"""
MAS Project: Digital Countermeasure Unit vs. "The Entity"
Description: Orchestrates a sequential 4-agent pipeline to process complex multi-vector threats.
"""

import json
import time
import urllib.request
import concurrent.futures
from typing import Any
import re
import os
from crewai import Crew, Process, Task

# Forcefully disable CrewAI telemetry for offline Air-Gapped execution
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"

def seed_synthetic_datasets():
    """Generates the required JSON datasets automatically if they are missing."""
    print("\n[INIT] Bootstrapping synthetic threat datasets...")
    
    if not os.path.exists("server_logs.json"):
        cyber_data = [
            {"timestamp": "2026-08-20T02:00:15Z", "ip": "192.168.1.50", "event": "successful_login", "protocol": "SSH"},
            {"timestamp": "2026-08-20T02:05:22Z", "ip": "10.0.0.9", "event": "failed_login", "protocol": "SSH", "notes": "Invalid cryptographic key presented."},
            {"timestamp": "2026-08-20T02:05:23Z", "ip": "10.0.0.9", "event": "failed_login", "protocol": "SSH", "notes": "High-velocity brute-force pattern detected."}
        ]
        with open("server_logs.json", "w") as f:
            json.dump(cyber_data, f, indent=2)
        print("  -> Created server_logs.json")

    if not os.path.exists("audio_scan_results.json"):
        audio_data = [
            {"file_name": "normal_call.wav", "synthetic_probability": 0.12, "anomalies": "None."},
            {"file_name": "exec_voicemail.wav", "synthetic_probability": 0.94, "anomalies": "Unnatural pitch shifts; cloned vocal markers present."}
        ]
        with open("audio_scan_results.json", "w") as f:
            json.dump(audio_data, f, indent=2)
        print("  -> Created audio_scan_results.json")

    if not os.path.exists("video_scan_results.json"):
        video_data = [
            {"video_id": "cam_01.mp4", "tamper_score": 0.05, "frame_analysis": "Continuous timestamp continuity."},
            {"video_id": "cam_04.mp4", "tamper_score": 0.88, "frame_analysis": "Duplicate frame glitches detected at 00:14."}
        ]
        with open("video_scan_results.json", "w") as f:
            json.dump(video_data, f, indent=2)
        print("  -> Created video_scan_results.json")

# Import your separated tools and agents from the other files
from tools import simulate_tool_failure
from agents import coordinator_agent, audio_specialist, video_specialist, strategic_predictor

class MASController:
    def __init__(self, incident_report: str):
        self.incident_report = incident_report
        self.state = {
            "input": incident_report,
            "runtime_seconds": 0.0,
            "status": "INITIALIZED",
            "final_output": None
        }

    def _llm_is_available(self) -> bool:
        try:
            with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=3) as response:
                return response.status == 200
        except Exception:
            return False

    def _safe_json_result(self, raw_result: Any) -> dict[str, Any]:
        raw_str = str(raw_result)
        try:
            parsed = json.loads(raw_str)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass 

        try:
            match = re.search(r'\{.*\}', raw_str, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                if isinstance(parsed, dict):
                    return parsed
        except json.JSONDecodeError:
            pass

        print("\n[WARNING]: Agent output was heavily malformed. Wrapping raw output safely.")
        return {"analysis_result": raw_str, "confidence_score": 0.0, "next_step": "Manual review required due to system formatting error.", "format_error": True}

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
        print("\n--- INITIATING DYNAMIC MAS PIPELINE ---")

        if not self._llm_is_available():
            return self._trigger_fallback("Local LLM endpoint is unavailable at http://127.0.0.1:11434.")

        # 1. DEFINE TASKS
        task_cyber = Task(
            description=f"Analyze network indicators in this report: {self.incident_report}",
            expected_output="Strict JSON with analysis_result, confidence_score, and next_step.",
            agent=coordinator_agent
        )
        
        task_audio = Task(
            description=f"Analyze audio markers mentioned in this report: {self.incident_report}",
            expected_output="Strict JSON with analysis_result, confidence_score, and next_step.",
            agent=audio_specialist
        )

        task_video = Task(
            description=f"Analyze video surveillance streams mentioned in this report: {self.incident_report}",
            expected_output="Strict JSON with analysis_result, confidence_score, and next_step.",
            agent=video_specialist
        )

        task_strategy_full = Task(
            description="Review the intelligence gathered by the network, audio, and video specialists. Formulate a final countermeasure strategy.",
            expected_output="Strict JSON with analysis_result, confidence_score, confidence_justification, and next_step.",
            agent=strategic_predictor,
            context=[task_cyber, task_audio, task_video]
        )
        
        task_strategy_basic = Task(
            description="Review the intelligence gathered by the network coordinator. Formulate a final cyber countermeasure strategy.",
            expected_output="Strict JSON with analysis_result, confidence_score, confidence_justification, and next_step.",
            agent=strategic_predictor,
            context=[task_cyber]
        )

        # 2. DYNAMIC ROUTER
        input_lower = self.incident_report.lower()
        if "audio" in input_lower or "video" in input_lower or "camera" in input_lower:
            print("[ROUTER]: Multi-vector threat detected. Routing to Full Specialist Crew.")
            active_agents = [coordinator_agent, audio_specialist, video_specialist, strategic_predictor]
            active_tasks = [task_cyber, task_audio, task_video, task_strategy_full]
        else:
            print("[ROUTER]: Standard cyber threat detected. Bypassing media specialists.")
            active_agents = [coordinator_agent, strategic_predictor]
            active_tasks = [task_cyber, task_strategy_basic]

        # 3. ASSEMBLE CREW
        dynamic_crew = Crew(
            agents=active_agents,
            tasks=active_tasks,
            process=Process.sequential
        )

        start_time = time.time()
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(dynamic_crew.kickoff)
                raw_result = future.result(timeout=180.0)
            
            self.state["runtime_seconds"] = round(time.time() - start_time, 2)
            self.state["final_output"] = self._safe_json_result(raw_result)
            self.state["status"] = "OK"
            return self.state

        except concurrent.futures.TimeoutError:
            print("\n[TIMEOUT]: Pipeline execution forcefully terminated.")
            return self._trigger_fallback("Execution exceeded the global time budget limit.")
        except Exception as exc:
            return self._trigger_fallback(str(exc))


# ==========================================
# TERMINAL EXECUTION (NO STREAMLIT)
# ==========================================
if __name__ == "__main__":
    import textwrap

    # Step 1: Automatically generate the JSON files
    seed_synthetic_datasets()

    # Step 2: Define the threat report
    master_incident_report = (
        "At 0200 hours, server 10.0.0.9 experienced a massive brute-force SSH attack. "
        "Simultaneously, intercepted audio file 'exec_voicemail.wav' showed unnatural pitch shifts, "
        "and security camera feed 'cam_04.mp4' exhibited duplicate frame glitches."
    )

    # Step 3: Run the system
    controller = MASController(master_incident_report)
    final_output = controller.execute_pipeline()
    
    # Step 4: Display the Human-Readable Terminal Report
    print("\n" + "="*75)
    print(" 🛡️  PROJECT SENTINEL: EXECUTIVE INCIDENT REPORT  🛡️ ")
    print("="*75)

    input_context = final_output.get("input", "No input context provided.")
    data = final_output.get("final_output", {})
    analysis = data.get("analysis_result", "No threat analysis provided.")
    confidence = data.get("confidence_score", 0)
    next_step = data.get("next_step", "No steps provided.")
    runtime = final_output.get("runtime_seconds", "0")
    justification = data.get("confidence_justification", "No justification provided.")

    try:
        conf_percent = float(confidence)
        if conf_percent <= 1.0: 
            conf_percent = int(conf_percent * 100)
    except (ValueError, TypeError):
        conf_percent = confidence

    print("\n🚨 INCIDENT BRIEF (SYSTEM INPUT):")
    print("-" * 75)
    print(textwrap.fill(str(input_context), width=75))

    print(f"\n⏱️  SYSTEM EXECUTION TIME : {runtime} seconds")
    print(f"🎯 AI CONFIDENCE LEVEL  : {conf_percent}%")
    print(f"🧠 CONFIDENCE RATIONALE : {justification}\n")
    
    print("-" * 75)
    print("🔍 EXECUTIVE SUMMARY (THREAT ANALYSIS):")
    print("-" * 75)
    
    if isinstance(analysis, (dict, list)):
        print(json.dumps(analysis, indent=2))
    else:
        print(textwrap.fill(str(analysis), width=75))
    print("\n")

    print("-" * 75)
    print("🚀 REQUIRED ACTIONS (COUNTERMEASURES):")
    print("-" * 75)
    
    if isinstance(next_step, dict):
        for category, actions in next_step.items():
            print(f"\n>> {category.upper()}:")
            if isinstance(actions, str):
                wrapped_text = textwrap.fill(actions, width=70, subsequent_indent="     ")
                print(f"   • {wrapped_text}")
            elif isinstance(actions, list):
                for action in actions:
                    print(f"   • {action}")
            elif isinstance(actions, dict):
                for sub_key, sub_value in actions.items():
                    clean_key = str(sub_key).replace('_', ' ').title()
                    wrapped_val = textwrap.fill(str(sub_value), width=65, subsequent_indent="         ")
                    print(f"   • [{clean_key}]: {wrapped_val}")
            else:
                print(f"   • {str(actions)}")
    elif isinstance(next_step, list):
        for action in next_step:
            print(f"   • {action}")
    else:
        print(textwrap.fill(str(next_step), width=75))
        
    print("\n" + "="*75)