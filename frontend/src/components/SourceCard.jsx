import { useState } from "react";

const TYPE_STYLES = {
  document: "bg-sky-500/15 text-sky-300 border-sky-400/30",
  image: "bg-fuchsia-500/15 text-fuchsia-300 border-fuchsia-400/30",
  audio: "bg-orange-500/15 text-orange-300 border-orange-400/30",
};

function SourceCard({ source }) {
  const [expanded, setExpanded] = useState(false);
  const normalizedType = String(source.type || "unknown").toLowerCase();
  const scorePercent = Math.max(0, Math.min(100, Math.round((source.score || 0) * 100)));

  return (
    <article className="glass-card rounded-3xl p-4">
      <div className="mb-3 flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="rounded-2xl border border-accent/30 bg-accent/10 px-3 py-1 font-mono text-xs font-semibold text-accent">
            {source.ref}
          </span>
          <div>
            <p className="font-heading text-sm font-semibold text-ink">{source.source}</p>
            <p className="font-mono text-xs text-muted">{source.location}</p>
          </div>
        </div>
        <span
          className={`rounded-full border px-3 py-1 font-mono text-[11px] uppercase tracking-[0.18em] ${
            TYPE_STYLES[normalizedType] || "border-white/10 bg-white/5 text-muted"
          }`}
        >
          {normalizedType}
        </span>
      </div>

      <p className="text-sm leading-6 text-slate-200">
        {expanded ? source.text_snippet : `${source.text_snippet.slice(0, 160)}${source.text_snippet.length > 160 ? "..." : ""}`}
      </p>

      {source.text_snippet.length > 160 ? (
        <button
          type="button"
          onClick={() => setExpanded((value) => !value)}
          className="mt-3 font-mono text-xs text-accent"
        >
          {expanded ? "Show less" : "Expand snippet"}
        </button>
      ) : null}

      <div className="mt-4">
        <div className="mb-2 flex items-center justify-between font-mono text-xs text-muted">
          <span>Relevance</span>
          <span>{scorePercent}%</span>
        </div>
        <div className="h-2 rounded-full bg-white/10">
          <div className="h-2 rounded-full bg-accent" style={{ width: `${scorePercent}%` }} />
        </div>
      </div>
    </article>
  );
}

export default SourceCard;
