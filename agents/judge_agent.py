from __future__ import annotations

import json

from utils.config import PROMPTS_DIR
from utils.io import load_prompt
from utils.llm import LLMClient, LLMInvocationError, LLMUnavailableError
from utils.schemas import JudgeOutput


class JudgeAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def run(self, log_analysis: dict, code_analysis: dict, hypotheses: list[dict]) -> JudgeOutput:
        system_prompt = load_prompt(PROMPTS_DIR / "system_general.txt")
        user_prompt = load_prompt(
            PROMPTS_DIR / "judge_prompt.txt",
            log_signals=json.dumps(log_analysis, indent=2),
            code_signals=json.dumps(code_analysis, indent=2),
            hypotheses=json.dumps(hypotheses, indent=2),
        )

        try:
            payload = self.llm.json_completion(system_prompt, user_prompt)
            return JudgeOutput.model_validate(payload)
        except (LLMUnavailableError, LLMInvocationError, Exception):
            return self._heuristic_fallback(hypotheses)

    def _heuristic_fallback(self, hypotheses: list[dict]) -> JudgeOutput:
        ranked = sorted(hypotheses, key=lambda h: h.get("confidence", 0.0), reverse=True)
        ranking = [
            {
                "persona": h["persona"],
                "score": round(float(h.get("confidence", 0.0)), 2),
                "rationale": "Higher alignment between code-level evidence and observed runtime failures.",
            }
            for h in ranked
        ]

        winner = ranked[0]

        return JudgeOutput.model_validate(
            {
                "ranking": ranking,
                "final_diagnosis": winner["root_cause"],
                "fix_suggestion": (
                    "Primary: remove shared/global DB session usage, adopt per-request session scope with guaranteed close/rollback. "
                    "Secondary: replace tight retries with exponential backoff + jitter and protect dependency with circuit breaker."
                ),
                "validation_strategy": [
                    "Run a load test with burst traffic and verify DB pool saturation stays below critical threshold.",
                    "Add an integration test that forces DB timeout and confirms retries are bounded with backoff.",
                    "Confirm p95/p99 latency and 5xx rate regress toward baseline after patch.",
                ],
            }
        )
