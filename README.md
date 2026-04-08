# Logos: A Memory-Augmented Multi-Agent Debugging System

Logos is a multi-agent system for root cause analysis.

Pitch:
`Logos is a multi-agent debugging system that can use a memory backend (for example AlloyDB) to remember past failures and reason about new ones.`

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
│   ├── db.py
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
- Retrieved similar incidents from memory (`retrieved_incidents`)
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

DB_HOST=<alloydb_or_postgres_host>
DB_PORT=5432
DB_NAME=debugger
DB_USER=postgres
DB_PASSWORD=<password>
DB_CONNECT_TIMEOUT=3
# DB_SSLMODE=require
```

Note: If `GEMINI_API_KEY` is not set, the system runs in heuristic fallback mode so demo still works.
If DB vars are missing, memory retrieval/storage is skipped safely.
If DB is configured but unreachable, `DB_CONNECT_TIMEOUT` avoids long startup/request hangs.

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
.venv/bin/python -m uvicorn server:app --reload --host 127.0.0.1 --port 8000
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

`POST /debug` now also returns:

```json
{
  "retrieved_incidents": [
    {
      "id": 12,
      "final_diagnosis": "connection pool exhaustion due to retry storm",
      "created_at": "2026-04-08T12:00:00",
      "logs_excerpt": "...",
      "signals": {},
      "hypotheses": []
    }
  ]
}
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
5. Memory layer stores the completed incident back into AlloyDB.

Design goals:
- Modular agents
- Prompt files separated from logic
- Structured Pydantic schemas
- Gemini SDK LLM wrapper
- AlloyDB-backed persistent memory and retrieval
- Fallback mode for offline/demo reliability

## 10) AlloyDB Setup (Phase 2)

Use any PostgreSQL-compatible AlloyDB endpoint.

```sql
CREATE TABLE IF NOT EXISTS incidents (
  id SERIAL PRIMARY KEY,
  logs TEXT,
  code TEXT,
  signals JSONB,
  hypotheses JSONB,
  final_diagnosis TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

The app auto-runs `init_db()` on startup and before pipeline retrieval.
Memory retrieval currently uses keyword-based `ILIKE` matching for speed and reliability.

## 11) Why Some Values Are Hardcoded

Some constants are intentionally fixed for demo reliability:
- `demo/sample_*` files contain intentionally broken sample data.
- Fallback hypotheses/confidence values are deterministic so output still works without `GEMINI_API_KEY`.
- Default model/temperature are set in `utils/config.py` but can be overridden by `.env`.
- `cloudbuild.yaml` uses a fixed default region (`asia-southeast1`) and can be edited per deployment.

## 12) Quick Demo Files

- Logs: `demo/sample_logs.txt`
- Code: `demo/sample_code.py`

These reproduce a realistic incident pattern around DB timeout + connection pool exhaustion + retry amplification.

## 13) Troubleshooting

`[vite] http proxy error: /debug` with `ECONNREFUSED` means frontend cannot reach backend.

```bash
# 1) Start backend in the project venv
source .venv/bin/activate
python -m uvicorn server:app --host 127.0.0.1 --port 8000

# 2) In another terminal, verify backend
curl http://127.0.0.1:8000/health

# 3) Start frontend
cd frontend
npm run dev
```

If health fails:
- install deps into `.venv` (`pip install -r requirements.txt`)
- ensure nothing else is using port `8000`
- lower DB timeout to fail fast when DB is unavailable (`DB_CONNECT_TIMEOUT=1`).
