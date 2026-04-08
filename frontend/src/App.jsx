import { useEffect, useMemo, useState } from "react";
import InputPanel from "./components/InputPanel";
import HypothesisCard from "./components/HypothesisCard";
import FinalDiagnosis from "./components/FinalDiagnosis";
import { CodeAnalysisPanel, LogAnalysisPanel } from "./components/AnalysisPanel";

const DEFAULT_LOGS = `2026-04-08T08:10:06Z ERROR request_id=7ad3 exception=TimeoutError detail="Query timed out after 1.0s" retry=1\n2026-04-08T08:10:09Z ERROR sqlalchemy.exc.TimeoutError QueuePool limit reached\n2026-04-08T08:10:12Z ERROR request_id=7adc exception=HTTPException status=503 detail="Service temporarily overloaded"`;

const DEFAULT_CODE = `def get_user_orders(user_id: int):\n    retries = 3\n    for attempt in range(retries):\n        try:\n            rows = global_session.execute(...)\n            return rows\n        except Exception as exc:\n            time.sleep(0.1)\n    return []`;

const AGENT_STEPS = [
  "Analyzing logs...",
  "Reviewing code risks...",
  "Generating hypotheses...",
  "Evaluating final diagnosis...",
];

function IncidentCard({ incident }) {
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-950/50 p-3 text-sm">
      <p className="mb-1 text-xs text-slate-400">#{incident.id ?? "N/A"} · {incident.created_at || "Unknown time"}</p>
      <p className="mb-2 font-medium text-slate-100">{incident.final_diagnosis || "No diagnosis recorded"}</p>
      <p className="max-h-20 overflow-auto whitespace-pre-wrap text-xs text-slate-400">{incident.logs_excerpt || "No logs excerpt"}</p>
    </div>
  );
}

export default function App() {
  const [logs, setLogs] = useState(DEFAULT_LOGS);
  const [code, setCode] = useState(DEFAULT_CODE);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [stepIndex, setStepIndex] = useState(0);

  useEffect(() => {
    if (!loading) return undefined;
    const timer = setInterval(() => {
      setStepIndex((prev) => (prev + 1) % AGENT_STEPS.length);
    }, 1200);
    return () => clearInterval(timer);
  }, [loading]);

  const apiUrl = import.meta.env.VITE_DEBUG_API_URL || "/debug";

  async function runDebug() {
    setLoading(true);
    setError("");
    setResult(null);
    setStepIndex(0);

    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ logs, code, verbose: false }),
      });

      if (!response.ok) {
        const body = await response.text();
        throw new Error(`Request failed (${response.status}): ${body}`);
      }

      const payload = await response.json();
      setResult(payload);
    } catch (err) {
      setError(err.message || "Request failed");
    } finally {
      setLoading(false);
    }
  }

  const retrievedIncidents = useMemo(() => result?.retrieved_incidents || [], [result]);

  return (
    <div className="mx-auto min-h-screen max-w-7xl px-4 py-6 md:px-6">
      <header className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-cyan-200">Logos Debugging Engine</h1>
          <p className="mt-1 text-sm text-slate-300">Multi-agent reasoning with persistent memory from AlloyDB.</p>
        </div>
        <span className="rounded-full border border-cyan-400/40 bg-cyan-500/10 px-3 py-1 text-xs text-cyan-200">
          API: {apiUrl}
        </span>
      </header>

      <div className="space-y-5">
        <InputPanel
          logs={logs}
          code={code}
          onLogsChange={setLogs}
          onCodeChange={setCode}
          onSubmit={runDebug}
          loading={loading}
        />

        {loading && (
          <section className="rounded-xl border border-cyan-400/30 bg-slate-900/80 p-4">
            <div className="flex items-center gap-3">
              <div className="h-5 w-5 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent" />
              <p className="font-medium text-cyan-200">Agents are reasoning...</p>
            </div>
            <p className="mt-2 text-sm text-slate-300">{AGENT_STEPS[stepIndex]}</p>
          </section>
        )}

        {error && (
          <section className="rounded-xl border border-rose-500/40 bg-rose-500/10 p-4 text-rose-200">
            <p className="font-semibold">Request failed</p>
            <p className="mt-1 text-sm">{error}</p>
          </section>
        )}

        {result && (
          <>
            <section className="rounded-2xl border border-slate-700/70 bg-slate-900/70 p-5">
              <h3 className="mb-3 text-lg font-semibold text-cyan-200">Retrieved Incidents (Memory)</h3>
              {retrievedIncidents.length ? (
                <div className="max-h-64 space-y-3 overflow-auto pr-1">
                  {retrievedIncidents.map((incident) => (
                    <IncidentCard key={incident.id ?? Math.random()} incident={incident} />
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-400">No similar incidents found in memory yet.</p>
              )}
            </section>

            <LogAnalysisPanel data={result.log_analysis} />
            <CodeAnalysisPanel data={result.code_analysis} />

            <section className="rounded-2xl border border-slate-700/70 bg-slate-900/70 p-5">
              <h3 className="mb-4 text-lg font-semibold text-cyan-200">Hypotheses</h3>
              <div className="grid gap-3 lg:grid-cols-3">
                {(result.hypotheses || []).map((hypothesis, idx) => (
                  <HypothesisCard
                    key={`${hypothesis.persona}-${idx}`}
                    hypothesis={hypothesis}
                    index={idx}
                  />
                ))}
              </div>
            </section>

            <FinalDiagnosis judge={result.judge} />
          </>
        )}
      </div>
    </div>
  );
}
