function confidenceStyle(value) {
  if (value >= 0.7) return "bg-emerald-500";
  if (value >= 0.4) return "bg-amber-500";
  return "bg-rose-500";
}

export default function HypothesisCard({ hypothesis, index }) {
  const confidence = Math.max(0, Math.min(1, hypothesis?.confidence ?? 0));

  return (
    <article
      className="animate-[fadeIn_300ms_ease-out] rounded-xl border border-fuchsia-400/30 bg-slate-900/80 p-4"
      style={{ animationDelay: `${index * 90}ms` }}
    >
      <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-fuchsia-300">
        {hypothesis.persona}
      </p>
      <h4 className="mb-3 text-base font-semibold text-slate-100">{hypothesis.root_cause}</h4>

      <div className="mb-3">
        <div className="mb-1 flex items-center justify-between text-xs text-slate-300">
          <span>Confidence</span>
          <span>{Math.round(confidence * 100)}%</span>
        </div>
        <div className="h-2 overflow-hidden rounded bg-slate-700">
          <div
            className={`h-full ${confidenceStyle(confidence)} transition-all duration-500`}
            style={{ width: `${confidence * 100}%` }}
          />
        </div>
      </div>

      <p className="mb-2 text-sm text-slate-300">
        <span className="font-semibold text-slate-200">Reasoning: </span>
        {hypothesis.reasoning}
      </p>

      <p className="text-sm text-cyan-200">
        <span className="font-semibold">Suggested Fix: </span>
        {hypothesis.likely_fix}
      </p>
    </article>
  );
}
