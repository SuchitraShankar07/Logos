from __future__ import annotations

import argparse
import json

from agents import CodeAnalysisAgent, HypothesisAgent, JudgeAgent, LogAnalysisAgent
from utils.config import DEMO_DIR
from utils.config import load_config
from utils.io import read_text
from utils.llm import LLMClient
from utils.pipeline import MultiAgentDebugger


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Logos Debugging Engine")
    parser.add_argument(
        "--logs",
        type=str,
        default=str(DEMO_DIR / "sample_logs.txt"),
        help="Path to input logs file",
    )
    parser.add_argument(
        "--code",
        type=str,
        default=str(DEMO_DIR / "sample_code.py"),
        help="Path to input code snippet file",
    )
    parser.add_argument("--json", action="store_true", help="Print only final JSON output")
    parser.add_argument("--quiet", action="store_true", help="Disable step-by-step console logs")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config()

    logs = read_text(args.logs)
    code = read_text(args.code)

    llm = LLMClient(config)
    pipeline = MultiAgentDebugger(
        log_agent=LogAnalysisAgent(llm),
        code_agent=CodeAnalysisAgent(llm),
        hypothesis_agent=HypothesisAgent(llm),
        judge_agent=JudgeAgent(llm),
    )

    result = pipeline.run(logs=logs, code=code, verbose=not args.quiet and not args.json)
    print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
