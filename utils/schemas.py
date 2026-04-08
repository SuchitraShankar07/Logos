from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ErrorSignal(BaseModel):
    timestamp: str | None = None
    message: str
    severity: Literal["critical", "high", "medium", "low"]


class AnomalySignal(BaseModel):
    type: str
    detail: str
    evidence: str


class PatternSignal(BaseModel):
    pattern: str
    count: int
    impact: str


class LogAnalysisOutput(BaseModel):
    errors: list[ErrorSignal] = Field(default_factory=list)
    anomalies: list[AnomalySignal] = Field(default_factory=list)
    patterns: list[PatternSignal] = Field(default_factory=list)
    timestamps: list[str] = Field(default_factory=list)
    summary: str


class CodeRiskItem(BaseModel):
    area: str
    line_reference: str
    risk: str
    why_risky: str


class CodeAnalysisOutput(BaseModel):
    possible_failure_points: list[CodeRiskItem] = Field(default_factory=list)
    risky_patterns: list[CodeRiskItem] = Field(default_factory=list)
    summary: str


class HypothesisOutput(BaseModel):
    persona: str
    root_cause: str
    reasoning: str
    evidence: list[str] = Field(default_factory=list)
    confidence: float
    likely_fix: str


class RankedHypothesis(BaseModel):
    persona: str
    score: float
    rationale: str


class JudgeOutput(BaseModel):
    ranking: list[RankedHypothesis] = Field(default_factory=list)
    final_diagnosis: str
    fix_suggestion: str
    validation_strategy: list[str] = Field(default_factory=list)


class PipelineOutput(BaseModel):
    log_analysis: LogAnalysisOutput
    code_analysis: CodeAnalysisOutput
    hypotheses: list[HypothesisOutput]
    judge: JudgeOutput
