export default function FinalDiagnosis({ judge }) {
  if (!judge) return null;

  return (
    <section className="rounded-2xl border border-emerald-400/40 bg-emerald-500/10 p-5 shadow-glow">
      <h3 className="mb-3 text-xl font-bold text-emerald-200">Final Diagnosis</h3>

      <div className="space-y-4 text-sm">
        <div>
          <p className="mb-1 text-xs uppercase tracking-wide text-emerald-300">Root Cause</p>
          <p className="text-slate-100">{judge.final_diagnosis}</p>
        </div>

        <div>
          <p className="mb-1 text-xs uppercase tracking-wide text-emerald-300">Fix Suggestion</p>
          <p className="text-slate-100">{judge.fix_suggestion}</p>
        </div>

        <div>
          <p className="mb-1 text-xs uppercase tracking-wide text-emerald-300">Validation Strategy</p>
          <ul className="list-disc space-y-1 pl-5 text-slate-100">
            {(judge.validation_strategy || []).map((step, idx) => (
              <li key={idx}>{step}</li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
