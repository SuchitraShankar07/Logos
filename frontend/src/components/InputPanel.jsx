export default function InputPanel({
  logs,
  code,
  onLogsChange,
  onCodeChange,
  onSubmit,
  loading,
}) {
  return (
    <section className="rounded-2xl border border-slate-700/70 bg-slate-900/70 p-5 shadow-glow backdrop-blur">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-cyan-200">Input</h2>
        <button
          onClick={onSubmit}
          disabled={loading || !logs.trim() || !code.trim()}
          className="rounded-lg bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:bg-slate-600 disabled:text-slate-300"
        >
          {loading ? "Running..." : "Run Debug"}
        </button>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <label className="block">
          <p className="mb-2 text-sm font-medium text-slate-300">Application Logs</p>
          <textarea
            value={logs}
            onChange={(e) => onLogsChange(e.target.value)}
            placeholder="Paste logs here..."
            className="h-72 w-full resize-y rounded-lg border border-slate-700 bg-slate-950/70 p-3 text-sm text-slate-100 outline-none ring-cyan-400/40 placeholder:text-slate-500 focus:ring"
          />
        </label>

        <label className="block">
          <p className="mb-2 text-sm font-medium text-slate-300">Code Snippet</p>
          <textarea
            value={code}
            onChange={(e) => onCodeChange(e.target.value)}
            placeholder="Paste relevant code here..."
            className="h-72 w-full resize-y rounded-lg border border-slate-700 bg-slate-950/70 p-3 text-sm text-slate-100 outline-none ring-cyan-400/40 placeholder:text-slate-500 focus:ring"
          />
        </label>
      </div>
    </section>
  );
}
