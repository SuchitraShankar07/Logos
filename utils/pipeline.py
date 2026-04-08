from __future__ import annotations

from agents.code_analysis_agent import CodeAnalysisAgent
from agents.hypothesis_agent import HypothesisAgent, PERSONAS
from agents.judge_agent import JudgeAgent
from agents.log_analysis_agent import LogAnalysisAgent
from utils.db import init_db, retrieve_similar_incidents, store_incident
from utils.formatting import (
    print_banner,
    print_done,
    print_final_diagnosis,
    print_hypothesis_card,
    print_json_block,
    print_step,
)
from utils.schemas import PipelineOutput


class MultiAgentDebugger:
    def __init__(
        self,
        log_agent: LogAnalysisAgent,
        code_agent: CodeAnalysisAgent,
        hypothesis_agent: HypothesisAgent,
        judge_agent: JudgeAgent,
    ):
        self.log_agent = log_agent
        self.code_agent = code_agent
        self.hypothesis_agent = hypothesis_agent
        self.judge_agent = judge_agent

    def run(
        self,
        logs: str,
        code: str,
        verbose: bool = True,
        retrieved_incidents: list[dict] | None = None,
    ) -> PipelineOutput:
        if verbose:
            print_banner("LOGOS v1.0 - reasoning over failures")
            print_step("Pipeline", "starting analysis")

        if verbose:
            print_step("Memory Layer", "retrieving similar incidents...")
        init_db()
        memory_hits = retrieved_incidents if retrieved_incidents is not None else retrieve_similar_incidents(logs, limit=3)
        if verbose:
            print_step("Memory Layer", f"Retrieved {len(memory_hits)} similar incidents")
            if memory_hits:
                print_json_block("Retrieved Incidents", memory_hits)

        if verbose:
            print_step("Log Agent", "analyzing logs...")
        log_analysis = self.log_agent.run(logs, retrieved_incidents=memory_hits)
        if verbose:
            print_json_block("Log Analysis", log_analysis.model_dump())

        if verbose:
            print_step("Code Agent", "analyzing code...")
        code_analysis = self.code_agent.run(
            code,
            log_analysis.model_dump(),
            retrieved_incidents=memory_hits,
        )
        if verbose:
            print_json_block("Code Analysis", code_analysis.model_dump())

        hypotheses = []
        for persona in PERSONAS:
            if verbose:
                print_step(f"Hypothesis Agent - {persona.name}", "generating hypothesis...")
            result = self.hypothesis_agent.run(
                persona=persona,
                log_analysis=log_analysis.model_dump(),
                code_analysis=code_analysis.model_dump(),
                code=code,
                retrieved_incidents=memory_hits,
            )
            hypotheses.append(result)
            if verbose:
                print_json_block(f"Hypothesis - {persona.name}", result.model_dump())
                print_hypothesis_card(persona.name, result.model_dump())

        if verbose:
            print_step("Judge Agent", "evaluating hypotheses...")
        judge = self.judge_agent.run(
            log_analysis=log_analysis.model_dump(),
            code_analysis=code_analysis.model_dump(),
            hypotheses=[h.model_dump() for h in hypotheses],
        )
        if verbose:
            print_json_block("Judge Output", judge.model_dump())
            print_final_diagnosis(judge.model_dump())

        store_incident(
            logs=logs,
            code=code,
            signals={
                "log_analysis": log_analysis.model_dump(),
                "code_analysis": code_analysis.model_dump(),
            },
            hypotheses=[h.model_dump() for h in hypotheses],
            final_diagnosis=judge.final_diagnosis,
        )

        result = PipelineOutput(
            retrieved_incidents=memory_hits,
            log_analysis=log_analysis,
            code_analysis=code_analysis,
            hypotheses=hypotheses,
            judge=judge,
        )

        if verbose:
            print_done("Pipeline", "analysis completed")

        return result
