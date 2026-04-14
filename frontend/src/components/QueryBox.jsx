import { useEffect, useRef } from "react";

function QueryBox({ value, onChange, onSubmit, loading }) {
  const textareaRef = useRef(null);

  useEffect(() => {
    if (!textareaRef.current) {
      return;
    }

    textareaRef.current.style.height = "0px";
    textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
  }, [value]);

  return (
    <section className="glass-card rounded-3xl p-5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="font-heading text-xl font-semibold text-ink">Ask the indexed corpus</p>
          <p className="font-mono text-xs text-muted">Grounded retrieval with citation-enforced answers</p>
        </div>
        <span className="font-mono text-xs text-muted">{value.length} chars</span>
      </div>

      <textarea
        ref={textareaRef}
        value={value}
        disabled={loading}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={(event) => {
          if (event.ctrlKey && event.key === "Enter") {
            event.preventDefault();
            onSubmit();
          }
        }}
        rows={1}
        placeholder="Ask a question about your uploaded evidence..."
        className="min-h-32 w-full resize-none rounded-3xl border border-white/10 bg-black/20 px-4 py-4 font-body text-sm text-ink outline-none transition placeholder:text-muted focus:border-accent/50 focus:ring-2 focus:ring-accent/20 disabled:cursor-not-allowed disabled:opacity-60"
      />

      <div className="mt-4 flex items-center justify-between">
        <p className="font-mono text-xs text-muted">Submit with Ctrl+Enter</p>
        <button
          type="button"
          onClick={onSubmit}
          disabled={loading || !value.trim()}
          className="rounded-full border border-accent/40 bg-accent/15 px-5 py-2 font-mono text-xs uppercase tracking-[0.2em] text-accent transition hover:bg-accent/25 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {loading ? "Thinking..." : "Run Query"}
        </button>
      </div>
    </section>
  );
}

export default QueryBox;
