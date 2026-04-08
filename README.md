# Logos: A Memory-Augmented Multi-Agent Debugging System

Logos is a memory-augmented multi-agent system for root cause analysis.

Pitch:
`Logos is a multi-agent debugging system that uses AlloyDB to remember past failures and reason about new ones.`

Demo hook:
`Most debugging tools show you what broke. Logos tells you why, and remembers it.`

## 1) Project Structure

```text
project-root/
├── agents/
│   ├── __init__.py
│   ├── code_analysis_agent.py
│   ├── hypothesis_agent.py
│   ├── judge_agent.py
│   └── log_analysis_agent.py
├── demo/
│   ├── sample_code.py
│   └── sample_logs.txt
├── prompts/
│   ├── code_analysis_prompt.txt
│   ├── hypothesis_prompt.txt
│   ├── judge_prompt.txt
│   ├── log_analysis_prompt.txt
│   └── system_general.txt
├── utils/
│   ├── __init__.py
│   ├── config.py
│   ├── formatting.py
│   ├── io.py
│   ├── llm.py
│   ├── pipeline.py
│   └── schemas.py
├── .env.example
├── .gitignore
├── cloudbuild.yaml
├── Dockerfile
├── main.py
├── requirements.txt
├── server.py
└── README.md
```

## 2) What It Does

Input:
- Application logs
- Code snippet

Output:
- Structured log signals (errors, anomalies, patterns, timestamps)
- Code risk analysis
- 3 competing hypotheses from distinct personas:
  - Distributed Systems Expert
  - Backend Engineer
  - SRE / Infra Engineer
- Judge-ranked final diagnosis
- Suggested fix
- Suggested validation tests

## 3) Python Version

- Python 3.11+ recommended (3.10+ works in most cases)

## 4) Setup From Scratch

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set environment variables in `.env`:

```bash
GEMINI_API_KEY=<your_key>
GEMINI_MODEL=gemini-2.0-flash
GEMINI_TEMPERATURE=0.2
```

Note: If `GEMINI_API_KEY` is not set, the system runs in heuristic fallback mode so demo still works.

## 5) Run Locally (CLI)

### Default demo data

```bash
python main.py
```

### Custom files

```bash
python main.py --logs path/to/logs.txt --code path/to/code.py
```

### JSON-only mode

```bash
python main.py --json
```

## 6) Console Demo Experience

The CLI prints clear, step-by-step execution logs with rich formatting:

- `[Log Agent] analyzing logs...`
- `[Code Agent] analyzing code...`
- `[Hypothesis Agent - SRE / Infra Engineer] generating hypothesis...`
- `[Judge Agent] evaluating hypotheses...`

## 7) Optional API Server

Run FastAPI server locally:

```bash
uvicorn server:app --reload --port 8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Debug endpoint:

```bash
curl -X POST http://127.0.0.1:8000/debug \
  -H "Content-Type: application/json" \
  -d @- <<'JSON'
{
  "logs": "2026-04-08T08:10:06Z ERROR TimeoutError query timed out",
  "code": "def f():\n    pass",
  "verbose": false
}
JSON
```

## 8) Deployment

### Docker

```bash
docker build -t multi-agent-debugger .
docker run --rm -p 8000:8000 --env-file .env multi-agent-debugger
```

### Google Cloud Run (via Cloud Build)

- Ensure Google Cloud project is selected and APIs are enabled (`Cloud Run`, `Cloud Build`, `Artifact Registry`).
- Set secret/env var `GEMINI_API_KEY` in Cloud Run service settings.
- Run:

```bash
gcloud builds submit --config cloudbuild.yaml
```

## 9) Architecture Notes

Pipeline order:
1. `LogAnalysisAgent` extracts log signals.
2. `CodeAnalysisAgent` maps code risks to runtime signals.
3. `HypothesisAgent` runs three personas with differing bias.
4. `JudgeAgent` ranks hypotheses and returns final diagnosis/fix/tests.

Design goals:
- Modular agents
- Prompt files separated from logic
- Structured Pydantic schemas
- Gemini SDK LLM wrapper
- Fallback mode for offline/demo reliability

## 10) Quick Demo Files

- Logs: `demo/sample_logs.txt`
- Code: `demo/sample_code.py`

These reproduce a realistic incident pattern around DB timeout + connection pool exhaustion + retry amplification.
