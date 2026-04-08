from __future__ import annotations

import json
from dataclasses import dataclass

from utils.config import PROMPTS_DIR
from utils.io import load_prompt
from utils.llm import LLMClient, LLMInvocationError, LLMUnavailableError
from utils.schemas import HypothesisOutput


@dataclass(frozen=True)
class Persona:
    name: str
    stance: str


PERSONAS = [
    Persona(
        name="Distributed Systems Expert",
        stance=(
            "Bias toward concurrency, cascading failures, backpressure gaps, retry amplification, "
            "and cross-service coordination faults."
        ),
    ),
    Persona(
        name="Backend Engineer",
        stance=(
            "Bias toward application logic defects, data access misuse, unsafe exception handling, "
            "and bug-level code smells."
        ),
    ),
    Persona(
        name="SRE / Infra Engineer",
        stance=(
            "Bias toward capacity saturation, infrastructure bottlenecks, runtime configuration, observability, "
            "and incident blast radius control."
        ),
    ),
]


class HypothesisAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def run(
        self,
        persona: Persona,
        log_analysis: dict,
        code_analysis: dict,
        code: str,
        retrieved_incidents: list[dict] | None = None,
    ) -> HypothesisOutput:
        system_prompt = load_prompt(PROMPTS_DIR / "system_general.txt")
        user_prompt = load_prompt(
            PROMPTS_DIR / "hypothesis_prompt.txt",
            persona_name=persona.name,
            persona_stance=persona.stance,
            log_signals=json.dumps(log_analysis, indent=2),
            code_signals=json.dumps(code_analysis, indent=2),
            code=code,
            retrieved_incidents=json.dumps(retrieved_incidents or [], indent=2),
        )

        try:
            payload = self.llm.json_completion(system_prompt, user_prompt)
            payload["persona"] = persona.name
            return HypothesisOutput.model_validate(payload)
        except (LLMUnavailableError, LLMInvocationError, Exception):
            return self._heuristic_fallback(persona)

    def _heuristic_fallback(self, persona: Persona) -> HypothesisOutput:
        # Deterministic fallback profiles keep the demo runnable without an API key.
        if persona.name == "Distributed Systems Expert":
            payload = {
                "persona": persona.name,
                "root_cause": "Retry storm amplified a constrained DB dependency, causing cascading request failures.",
                "reasoning": (
                    "The pattern of repeated timeouts plus quick retries suggests positive feedback: each timeout triggered "
                    "more retries, increasing pressure on an already constrained pool and extending queueing delays."
                ),
                "evidence": [
                    "Recurring timeout signatures",
                    "Retry-related log entries",
                    "Pool exhaustion indicators",
                ],
                "confidence": 0.76,
                "likely_fix": "Add exponential backoff with jitter and circuit breaking around DB-bound operations.",
            }
        elif persona.name == "Backend Engineer":
            payload = {
                "persona": persona.name,
                "root_cause": "A shared global DB session and broad exception retries caused connection leakage and pool exhaustion.",
                "reasoning": (
                    "The code uses a module-level session object and catches Exception broadly, then retries in a tight loop. "
                    "This combination can retain bad session state and multiply failing DB calls under load."
                ),
                "evidence": [
                    "Global SessionLocal() assignment",
                    "except Exception with retry loop",
                    "QueuePool timeout errors in logs",
                ],
                "confidence": 0.87,
                "likely_fix": "Scope DB sessions per request, close sessions deterministically, and narrow exception handling.",
            }
        else:
            payload = {
                "persona": persona.name,
                "root_cause": "DB capacity and pool settings were underprovisioned for burst traffic, leading to timeouts.",
                "reasoning": (
                    "Small pool size and low pool timeout make the service fragile during traffic spikes or slow queries. "
                    "Infra-level saturation likely triggered elevated latency and 5xx responses."
                ),
                "evidence": [
                    "Configured small pool_size with strict pool_timeout",
                    "Latency spikes prior to failures",
                    "5xx/upstream timeout errors",
                ],
                "confidence": 0.73,
                "likely_fix": "Tune pool and DB capacity, and add query latency/connection saturation alerts.",
            }

        return HypothesisOutput.model_validate(payload)
