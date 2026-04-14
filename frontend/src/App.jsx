import { useEffect, useState } from "react";
import { getStatus, queryRAG, resetIndex, uploadFile } from "./api/ragApi";
import AnswerPanel from "./components/AnswerPanel";
import FileUploader from "./components/FileUploader";
import QueryBox from "./components/QueryBox";
import SourceCard from "./components/SourceCard";

function App() {
  const [status, setStatus] = useState({ indexed_chunks: 0, collection_name: "rag_collection" });
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [responseTime, setResponseTime] = useState(0);
  const [banner, setBanner] = useState("System warming up...");

  async function refreshStatus() {
    try {
      const data = await getStatus();
      setStatus(data);
      setBanner(`Index online. ${data.indexed_chunks} chunks ready.`);
    } catch (error) {
      setBanner(error.message);
    }
  }

  useEffect(() => {
    refreshStatus();
  }, []);

  async function handleUpload(file) {
    const result = await uploadFile(file);
    await refreshStatus();
    setAnswer("");
    setSources([]);
    return result;
  }

  async function handleQuery() {
    if (!question.trim()) {
      return;
    }

    try {
      setLoading(true);
      const result = await queryRAG(question.trim());
      setAnswer(result.answer || "");
      setSources(result.sources || []);
      setResponseTime(result.response_time_seconds || 0);
      setBanner(`Query completed against ${status.collection_name}.`);
    } catch (error) {
      setAnswer(error.message);
      setSources([]);
      setResponseTime(0);
      setBanner("Query failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleReset() {
    const confirmed = window.confirm("Reset the full index? This removes all indexed chunks.");

    if (!confirmed) {
      return;
    }

    try {
      await resetIndex();
      await refreshStatus();
      setAnswer("");
      setSources([]);
      setResponseTime(0);
      setBanner("Index reset complete.");
    } catch (error) {
      setBanner(error.message);
    }
  }

  return (
    <div className="min-h-screen bg-canvas px-4 py-6 text-ink md:px-8">
      <div className="mx-auto grid max-w-7xl gap-6 lg:grid-cols-[360px_minmax(0,1fr)]">
        <aside className="space-y-6">
          <header className="glass-card rounded-3xl p-5">
            <p className="font-mono text-xs uppercase tracking-[0.32em] text-accent">Multimodal RAG</p>
            <h1 className="mt-3 font-heading text-3xl font-semibold text-ink">Grounded research cockpit</h1>
            <p className="mt-3 text-sm leading-7 text-muted">
              Index documents, OCR images, transcribe audio, and query only what your evidence set contains.
            </p>
          </header>

          <FileUploader
            onIngested={handleUpload}
            onUploadStart={() => setBanner("Ingesting file into the corpus...")}
            onUploadError={(error) => setBanner(error.message)}
          />

          <section className="glass-card rounded-3xl p-5">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="font-heading text-lg font-semibold text-ink">Index Status</p>
                <p className="font-mono text-xs text-muted">{status.collection_name}</p>
              </div>
              <button
                type="button"
                onClick={handleReset}
                className="rounded-full border border-rose-500/30 bg-rose-500/10 px-4 py-2 font-mono text-xs uppercase tracking-[0.18em] text-rose-300 transition hover:bg-rose-500/20"
              >
                Reset
              </button>
            </div>

            <div className="rounded-3xl border border-white/10 bg-black/20 p-4">
              <p className="font-mono text-xs uppercase tracking-[0.18em] text-muted">Indexed chunks</p>
              <p className="mt-2 font-heading text-4xl font-semibold text-ink">{status.indexed_chunks}</p>
              <p className="mt-3 text-sm text-muted">{banner}</p>
            </div>
          </section>
        </aside>

        <main className="space-y-6">
          <QueryBox value={question} onChange={setQuestion} onSubmit={handleQuery} loading={loading} />
          <AnswerPanel answer={answer} loading={loading} responseTime={responseTime} />

          <section className="glass-card rounded-3xl p-5">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="font-heading text-xl font-semibold text-ink">Source Evidence</p>
                <p className="font-mono text-xs text-muted">Citations mapped back to original file locations</p>
              </div>
              <span className="font-mono text-xs text-muted">{sources.length} refs</span>
            </div>

            <div className="grid gap-4 xl:grid-cols-2">
              {sources.length > 0 ? (
                sources.map((source) => <SourceCard key={`${source.ref}-${source.source}`} source={source} />)
              ) : (
                <div className="rounded-3xl border border-dashed border-white/10 bg-black/20 p-6 text-sm text-muted">
                  Retrieved source cards will appear here after a successful query.
                </div>
              )}
            </div>
          </section>
        </main>
      </div>

      <footer className="mx-auto mt-6 flex max-w-7xl items-center justify-between rounded-3xl border border-white/10 bg-black/20 px-5 py-3 font-mono text-xs text-muted">
        <span>{status.indexed_chunks} chunks indexed</span>
        <span>Collection: {status.collection_name}</span>
        <span>Created by Harshal More</span>
      </footer>
    </div>
  );
}

export default App;
