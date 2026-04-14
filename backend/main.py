"""FastAPI entry point for the multimodal RAG backend."""

from __future__ import annotations

import asyncio
import tempfile
import time
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from config import ALLOWED_EXTENSIONS, TOP_K_FINAL, TOP_K_RETRIEVAL
from generation.answer_generator import generate_answer
from generation.context_builder import build_context
from ingestion import ingest_file
from processing.chunker import chunk_documents
from processing.embedder import embed_chunks, embed_query
from processing.indexer import COLLECTION_NAME, get_collection, index_chunks, reset_collection
from retrieval.bm25_search import build_bm25_index, invalidate_bm25_cache
from retrieval.fusion import hybrid_search
from retrieval.reranker import rerank
from utils.logger import log

app = FastAPI(title="Multimodal RAG System")

# Allow local frontend apps to call the API during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compress larger JSON responses so answer payloads move faster over the network.
app.add_middleware(GZipMiddleware, minimum_size=1000)


class QueryRequest(BaseModel):
    """JSON body for the /query endpoint."""

    query: str = Field(..., min_length=1, description="The natural-language question to ask the indexed data.")


@app.middleware("http")
async def request_timing_middleware(request, call_next):
    """Log method, path, and duration for every request."""

    start_time = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start_time
    log("REQUEST", f"{request.method} {request.url.path} - {duration:.2f}s")
    return response


@app.on_event("startup")
async def on_startup() -> None:
    """Warm up lightweight runtime state when the API starts."""

    collection = get_collection()

    if collection.count() > 0:
        await asyncio.to_thread(build_bm25_index)

    log("INFO", "RAG System ready. Models loaded.")


def _file_type_from_extension(extension: str) -> str:
    """Map a file extension to a human-readable type label."""

    if extension == ".pdf":
        return "document"

    if extension in {".png", ".jpg", ".jpeg"}:
        return "image"

    if extension in {".mp3", ".wav", ".m4a"}:
        return "audio"

    return "unknown"


def _run_ingestion_pipeline(file_path: str) -> int:
    """Execute the full synchronous ingestion pipeline for one file."""

    documents = ingest_file(file_path)
    chunks = chunk_documents(documents)
    embedded_chunks = embed_chunks(chunks)
    return index_chunks(embedded_chunks)


@app.post("/ingest")
async def ingest_endpoint(file: UploadFile = File(...)):
    """Accept a file upload, index its contents, and clean up the temp file."""

    if not file.filename:
        raise HTTPException(status_code=400, detail="A filename is required.")

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {extension}")

    temp_path = Path(tempfile.gettempdir()) / file.filename

    try:
        # Save the uploaded file to a temporary location before running the heavier sync pipeline.
        file_bytes = await file.read()
        temp_path.write_bytes(file_bytes)

        chunks_indexed = await asyncio.to_thread(_run_ingestion_pipeline, str(temp_path))

        # Mark the BM25 cache stale because the underlying corpus just changed.
        invalidate_bm25_cache()

        return {
            "status": "success",
            "chunks_indexed": chunks_indexed,
            "filename": file.filename,
            "type": _file_type_from_extension(extension),
        }
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        log("ERROR", f"Failed to ingest {file.filename}: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to process file: {exc}") from exc
    finally:
        # Always remove the temporary upload so repeated use does not leak disk space.
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)


@app.post("/query")
async def query_endpoint(payload: QueryRequest):
    """Run grounded retrieval and answer generation for a user query."""

    query = payload.query.strip()

    if not query:
        raise HTTPException(status_code=400, detail="Query must be a non-empty string.")

    start_time = time.perf_counter()
    log("INFO", f"Received query: {query}")

    query_embedding = await asyncio.to_thread(embed_query, query)
    fused_results = await hybrid_search(query, query_embedding, TOP_K_RETRIEVAL)
    reranked_results = await asyncio.to_thread(rerank, query, fused_results, TOP_K_FINAL)

    if not reranked_results:
        elapsed = time.perf_counter() - start_time
        return {
            "answer": "I could not find relevant information in the indexed data.",
            "sources": [],
            "query": query,
            "response_time_seconds": round(elapsed, 3),
        }

    context = await asyncio.to_thread(build_context, query, reranked_results)
    result = await asyncio.to_thread(generate_answer, context)

    elapsed = time.perf_counter() - start_time
    result["response_time_seconds"] = round(elapsed, 3)
    log("INFO", f"Query completed in {elapsed:.2f}s")
    return result


@app.get("/status")
async def status_endpoint():
    """Return current index status information."""

    collection = get_collection()
    return {
        "status": "ok",
        "indexed_chunks": collection.count(),
        "collection_name": COLLECTION_NAME,
    }


@app.delete("/reset")
async def reset_endpoint():
    """Delete and recreate the vector collection."""

    await asyncio.to_thread(reset_collection)
    invalidate_bm25_cache()
    return {"status": "reset complete"}


@app.get("/health")
async def health_endpoint():
    """Basic health probe used by local checks or deployment tooling."""

    return {"status": "healthy"}


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    """Return FastAPI HTTP errors as JSON objects."""

    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
