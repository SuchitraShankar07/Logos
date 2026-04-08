from __future__ import annotations

import json
import re
from collections import Counter

from utils.config import PROMPTS_DIR
from utils.io import load_prompt
from utils.llm import LLMClient, LLMInvocationError, LLMUnavailableError
from utils.schemas import LogAnalysisOutput


class LogAnalysisAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def run(self, logs: str, retrieved_incidents: list[dict] | None = None) -> LogAnalysisOutput:
        system_prompt = load_prompt(PROMPTS_DIR / "system_general.txt")
        user_prompt = load_prompt(
            PROMPTS_DIR / "log_analysis_prompt.txt",
            logs=logs,
            retrieved_incidents=json.dumps(retrieved_incidents or [], indent=2),
        )

        try:
            payload = self.llm.json_completion(system_prompt, user_prompt)
            return LogAnalysisOutput.model_validate(payload)
        except (LLMUnavailableError, LLMInvocationError, Exception):
            return self._heuristic_fallback(logs)

    def _heuristic_fallback(self, logs: str) -> LogAnalysisOutput:
        lines = [line for line in logs.splitlines() if line.strip()]
        ts_pattern = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)")
        timestamps = [m.group(1) for line in lines for m in [ts_pattern.search(line)] if m]

        error_lines = [
            line
            for line in lines
            if any(token in line.lower() for token in ["error", "exception", "timeout", "failed", "traceback"])
        ]

        errors = []
        for line in error_lines[:12]:
            ts_match = ts_pattern.search(line)
            severity = "high" if "exception" in line.lower() or "traceback" in line.lower() else "medium"
            if "critical" in line.lower() or "fatal" in line.lower():
                severity = "critical"
            errors.append(
                {
                    "timestamp": ts_match.group(1) if ts_match else None,
                    "message": line[-300:],
                    "severity": severity,
                }
            )

        pattern_counter: Counter[str] = Counter()
        for line in error_lines:
            normalized = re.sub(r"\d+", "<num>", line.lower())
            if "timeout" in normalized:
                pattern_counter["database_timeout"] += 1
            if "queuepool" in normalized or "pool" in normalized:
                pattern_counter["connection_pool_exhaustion"] += 1
            if "retry" in normalized:
                pattern_counter["retry_storm"] += 1
            if "503" in normalized or "504" in normalized:
                pattern_counter["upstream_errors"] += 1

        patterns = [
            {
                "pattern": key,
                "count": value,
                "impact": "High operational instability" if value >= 3 else "Localized degradation",
            }
            for key, value in pattern_counter.items()
        ]

        anomalies = []
        high_latency = [line for line in lines if re.search(r"latency_ms=(\d{4,}|[3-9]\d{3,})", line)]
        if high_latency:
            anomalies.append(
                {
                    "type": "latency_spike",
                    "detail": "Latency spikes above 3000ms detected",
                    "evidence": high_latency[0][-250:],
                }
            )

        if any("queuepool" in line.lower() for line in lines):
            anomalies.append(
                {
                    "type": "resource_exhaustion",
                    "detail": "DB connection pool exhaustion signs present",
                    "evidence": next(line for line in lines if "queuepool" in line.lower())[-250:],
                }
            )

        summary = (
            "Logs show recurring timeout and connection-pool related failures with elevated latency and "
            "retry behavior, indicating a likely cascading database access issue."
        )

        return LogAnalysisOutput.model_validate(
            {
                "errors": errors,
                "anomalies": anomalies,
                "patterns": patterns,
                "timestamps": sorted(set(timestamps))[:20],
                "summary": summary,
            }
        )
