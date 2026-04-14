import { useRef, useState } from "react";

const ACCEPTED_TYPES = ".pdf,.png,.jpg,.jpeg,.mp3,.wav,.m4a";

function FileUploader({ onIngested, onUploadStart, onUploadError }) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [status, setStatus] = useState("idle");
  const [message, setMessage] = useState("Drop a file here or click to browse.");

  async function handleFiles(fileList) {
    const files = Array.from(fileList || []);

    for (const file of files) {
      try {
        setStatus("uploading");
        setMessage(`Uploading ${file.name}...`);
        onUploadStart?.();
        const result = await onIngested(file);
        setStatus("success");
        setMessage(`OK ${result.filename} - ${result.chunks_indexed} chunks indexed (${result.type})`);
      } catch (error) {
        setStatus("error");
        setMessage(error.message);
        onUploadError?.(error);
      }
    }
  }

  function openPicker() {
    inputRef.current?.click();
  }

  return (
    <section className="glass-card rounded-3xl p-5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="font-heading text-lg font-semibold text-ink">Ingestion Queue</p>
          <p className="font-mono text-xs text-muted">PDF, image OCR, and audio transcription</p>
        </div>
        <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 font-mono text-[11px] uppercase tracking-[0.22em] text-accent">
          {status}
        </span>
      </div>

      <button
        type="button"
        onClick={openPicker}
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(event) => {
          event.preventDefault();
          setIsDragging(false);
          handleFiles(event.dataTransfer.files);
        }}
        className={`research-grid flex min-h-48 w-full flex-col items-center justify-center rounded-3xl border border-dashed px-6 py-8 text-center transition ${
          isDragging
            ? "border-accent bg-accent/10 shadow-glow"
            : "border-white/10 bg-white/[0.03] hover:border-accent/50 hover:bg-white/[0.05]"
        }`}
      >
        <div className="mb-3 h-12 w-12 rounded-2xl border border-accent/30 bg-accent/10" />
        <p className="font-heading text-base font-medium text-ink">Upload evidence files</p>
        <p className="mt-2 max-w-xs text-sm text-muted">{message}</p>
        <p className="mt-4 font-mono text-xs uppercase tracking-[0.22em] text-muted">
          Accepted: PDF, Images, Audio
        </p>
      </button>

      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_TYPES}
        multiple
        className="hidden"
        onChange={(event) => {
          handleFiles(event.target.files);
          event.target.value = "";
        }}
      />
    </section>
  );
}

export default FileUploader;
