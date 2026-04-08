function ListBlock({ title, items, renderItem, emptyText = "No items" }) {
  return (
    <div className="rounded-lg border border-slate-700 bg-slate-950/50 p-3">
      <h4 className="mb-2 text-sm font-semibold text-slate-200">{title}</h4>
      {items?.length ? (
        <ul className="space-y-2 text-sm text-slate-300">
          {items.map((item, idx) => (
            <li key={`${title}-${idx}`} className="rounded border border-slate-800 bg-slate-900/40 p-2">
              {renderItem(item)}
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-slate-500">{emptyText}</p>
      )}
    </div>
  );
}

export function LogAnalysisPanel({ data }) {
  if (!data) return null;

  return (
    <section className="rounded-2xl border border-slate-700/70 bg-slate-900/70 p-5">
      <h3 className="mb-3 text-lg font-semibold text-cyan-200">Log Analysis</h3>
      <p className="mb-4 text-sm text-slate-300">{data.summary}</p>

      <div className="grid gap-3 lg:grid-cols-3">
        <ListBlock
          title="Errors"
          items={data.errors}
          renderItem={(e) => (
            <>
              <p className="mb-1 text-xs text-slate-400">{e.timestamp || "No timestamp"}</p>
              <p className="mb-1 break-words">{e.message}</p>
              <span className="rounded bg-rose-500/20 px-2 py-0.5 text-xs uppercase text-rose-200">{e.severity}</span>
            </>
          )}
        />

        <ListBlock
          title="Anomalies"
          items={data.anomalies}
          renderItem={(a) => (
            <>
              <p className="font-medium text-slate-200">{a.type}</p>
              <p>{a.detail}</p>
              <p className="mt-1 text-xs text-slate-400">{a.evidence}</p>
            </>
          )}
        />

        <ListBlock
          title="Patterns"
          items={data.patterns}
          renderItem={(p) => (
            <>
              <p className="font-medium text-slate-200">{p.pattern}</p>
              <p className="text-xs text-slate-400">Count: {p.count}</p>
              <p>{p.impact}</p>
            </>
          )}
        />
      </div>
    </section>
  );
}

export function CodeAnalysisPanel({ data }) {
  if (!data) return null;

  return (
    <section className="rounded-2xl border border-slate-700/70 bg-slate-900/70 p-5">
      <h3 className="mb-3 text-lg font-semibold text-cyan-200">Code Analysis</h3>
      <p className="mb-4 text-sm text-slate-300">{data.summary}</p>

      <div className="grid gap-3 lg:grid-cols-2">
        <ListBlock
          title="Possible Failure Points"
          items={data.possible_failure_points}
          renderItem={(item) => (
            <>
              <p className="font-medium text-slate-100">{item.area}</p>
              <p className="text-xs text-slate-400">{item.line_reference}</p>
              <p className="mt-1 text-sm text-amber-200">{item.risk}</p>
              <p className="text-sm text-slate-300">{item.why_risky}</p>
            </>
          )}
        />

        <ListBlock
          title="Risky Patterns"
          items={data.risky_patterns}
          renderItem={(item) => (
            <>
              <p className="font-medium text-slate-100">{item.area}</p>
              <p className="text-xs text-slate-400">{item.line_reference}</p>
              <p className="mt-1 text-sm text-rose-200">{item.risk}</p>
              <p className="text-sm text-slate-300">{item.why_risky}</p>
            </>
          )}
        />
      </div>
    </section>
  );
}
