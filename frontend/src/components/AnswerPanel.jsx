function renderAnswer(answer) {
  const parts = answer.split(/(\[\d+\])/g);

  return parts.map((part, index) => {
    if (/^\[\d+\]$/.test(part)) {
      return (
        <span key={`${part}-${index}`} className="citation">
          {part}
        </span>
      );
    }

    return <span key={`${part}-${index}`}>{part}</span>;
  });
}

function AnswerPanel({ answer, loading, responseTime }) {
  const isFallback = answer === "I could not find relevant information in the indexed data.";

  return (
    <section className="glass-card rounded-3xl p-5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="font-heading text-xl font-semibold text-ink">Findings</p>
          <p className="font-mono text-xs text-muted">Answer is constrained to retrieved evidence only</p>
        </div>
        <span className="font-mono text-xs text-muted">
          {responseTime ? `${responseTime.toFixed(2)}s` : "--"}
        </span>
      </div>

      <div
        className={`min-h-48 rounded-3xl border px-4 py-4 text-sm leading-7 transition ${
          isFallback
            ? "border-yellow-500/20 bg-yellow-500/10 text-yellow-100"
            : "border-white/10 bg-black/20 text-ink"
        } ${answer ? "animate-floatin" : ""}`}
      >
        {loading ? (
          <div className="font-mono text-sm text-muted">
            Thinking
            <span className="ml-1 inline-flex gap-1">
              <span className="animate-pulse">.</span>
              <span className="animate-pulse [animation-delay:120ms]">.</span>
              <span className="animate-pulse [animation-delay:240ms]">.</span>
            </span>
          </div>
        ) : answer ? (
          renderAnswer(answer)
        ) : (
          <div className="font-mono text-sm text-muted">
            Upload documents, run a query, and the grounded answer will appear here.
          </div>
        )}
      </div>
    </section>
  );
}

export default AnswerPanel;
