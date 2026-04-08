from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from agents import CodeAnalysisAgent, HypothesisAgent, JudgeAgent, LogAnalysisAgent
from utils.config import load_config
from utils.db import init_db, retrieve_similar_incidents
from utils.llm import LLMClient
from utils.pipeline import MultiAgentDebugger


class DebugRequest(BaseModel):
    logs: str
    code: str
    verbose: bool = False


config = load_config()
llm = LLMClient(config)
pipeline = MultiAgentDebugger(
    log_agent=LogAnalysisAgent(llm),
    code_agent=CodeAnalysisAgent(llm),
    hypothesis_agent=HypothesisAgent(llm),
    judge_agent=JudgeAgent(llm),
)
init_db()

app = FastAPI(title="Logos Debugging Engine", version="1.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "llm_enabled": llm.enabled, "model": config.gemini_model}


@app.post("/debug")
def debug(request: DebugRequest) -> dict:
    retrieved_incidents = retrieve_similar_incidents(request.logs, limit=3)
    result = pipeline.run(
        logs=request.logs,
        code=request.code,
        verbose=request.verbose,
        retrieved_incidents=retrieved_incidents,
    )
    payload = result.model_dump()
    payload["retrieved_incidents"] = retrieved_incidents
    return payload
