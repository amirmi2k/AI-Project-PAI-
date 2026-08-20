"""
MAS Project: Tools Module
Description: Contains all custom tools and data-processing functions for the AI agents.
"""

import json
import os
from crewai.tools import tool

@tool("Network Traffic Analyzer")
def analyze_network_traffic(target_ip: str) -> str:
    """
    Scans a local JSON log file for suspicious activity related to a specific IP address.

    Args:
        target_ip (str): The IP address to search for in the logs.

    Returns:
        str: A formatted string containing the JSON log findings or an error state.
    """
    # [Human Dev Comment 1]: Upgraded this tool from a hardcoded simulation to actual 
    # file I/O operations, proving the system can ingest and parse real server logs.
    file_path = "server_logs.json"
    
    try:
        with open(file_path, "r") as file:
            logs = json.load(file)
            
        threat_logs = [log for log in logs if log.get("ip") == target_ip and log.get("event") == "failed_login"]
        
        if threat_logs:
            return f"[ALERT] Found {len(threat_logs)} threat events for {target_ip}. Data: {json.dumps(threat_logs)}"
        return f"[INFO] No suspicious activity found for {target_ip} in the logs."

    except FileNotFoundError:
        return f"[ERROR] The log file {file_path} is missing. Cannot verify threat."
    except json.JSONDecodeError:
        return "[ERROR] Log file is corrupted and cannot be parsed as JSON."

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
    raise TimeoutError("Simulated API disconnection for fallback testing.")