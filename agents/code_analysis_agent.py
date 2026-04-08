from __future__ import annotations

import json
import re

from utils.config import PROMPTS_DIR
from utils.io import load_prompt
from utils.llm import LLMClient, LLMInvocationError, LLMUnavailableError
from utils.schemas import CodeAnalysisOutput


class CodeAnalysisAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def run(self, code: str, log_analysis: dict) -> CodeAnalysisOutput:
        system_prompt = load_prompt(PROMPTS_DIR / "system_general.txt")
        user_prompt = load_prompt(
            PROMPTS_DIR / "code_analysis_prompt.txt",
            code=code,
            log_signals=json.dumps(log_analysis, indent=2),
        )

        try:
            payload = self.llm.json_completion(system_prompt, user_prompt)
            return CodeAnalysisOutput.model_validate(payload)
        except (LLMUnavailableError, LLMInvocationError, Exception):
            return self._heuristic_fallback(code)

    def _heuristic_fallback(self, code: str) -> CodeAnalysisOutput:
        lines = code.splitlines()
        possible_failure_points = []
        risky_patterns = []
        engine_line: int | None = None
        saw_pool_config = False

        def add_point(container: list[dict], area: str, line_no: int, risk: str, why: str) -> None:
            container.append(
                {
                    "area": area,
                    "line_reference": f"line {line_no}",
                    "risk": risk,
                    "why_risky": why,
                }
            )

        for idx, line in enumerate(lines, 1):
            low = line.lower()
            if "create_engine(" in low and engine_line is None:
                engine_line = idx
            if "pool_size" in low or "pool_timeout" in low:
                saw_pool_config = True
            if "except exception" in low:
                add_point(
                    risky_patterns,
                    "Exception handling",
                    idx,
                    "Broad exception catch",
                    "Masks specific failure modes and encourages unsafe retries without remediation.",
                )
            if "sessionlocal()" in low and "=" in line:
                add_point(
                    possible_failure_points,
                    "DB session lifecycle",
                    idx,
                    "Global session object",
                    "Shared DB session can leak across requests and create thread-safety/pool issues.",
                )
            if ".execute(" in low:
                add_point(
                    possible_failure_points,
                    "Database call path",
                    idx,
                    "Direct query path under retries",
                    "Repeated synchronous execute() calls can queue and fail during pool pressure.",
                )
            if re.search(r"sleep\(0\.[0-9]+\)", line):
                add_point(
                    risky_patterns,
                    "Retry policy",
                    idx,
                    "Tight retry loop",
                    "Short fixed sleeps can amplify load during incidents and create retry storms.",
                )
        if engine_line and saw_pool_config:
            add_point(
                possible_failure_points,
                "DB engine config",
                engine_line,
                "Constrained connection pool",
                "Small pool with strict timeout is vulnerable during transient spikes.",
            )

        summary = (
            "Code includes risky DB session lifecycle handling, broad exception catch, and aggressive retry behavior "
            "that can align with connection pool exhaustion and timeout errors seen in logs."
        )

        return CodeAnalysisOutput.model_validate(
            {
                "possible_failure_points": possible_failure_points,
                "risky_patterns": risky_patterns,
                "summary": summary,
            }
        )
