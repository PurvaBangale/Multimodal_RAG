"""Central project configuration for the multimodal RAG backend."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from backend/.env when that file exists.
load_dotenv()

# Resolve the backend directory so relative paths stay stable no matter where uvicorn is started.
BACKEND_DIR = Path(__file__).resolve().parent

# Read the Groq API key from the environment so it is never hard-coded in source control.
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Choose the Groq-hosted text model used for grounded answer generation.
GROQ_MODEL = "llama-3.3-70b-versatile"

# Pick the sentence-transformers model used to turn chunks and queries into embeddings.
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Pick the cross-encoder model used to rerank search candidates more precisely.
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

# Select the local Whisper model size used for audio transcription.
WHISPER_MODEL = "base"

# Store Chroma's persistent index files inside backend/storage/chroma_db.
CHROMA_PERSIST_DIR = str(BACKEND_DIR / "storage" / "chroma_db")

# Limit each chunk to roughly this many characters so retrieval stays focused.
CHUNK_SIZE = 400

# Repeat this many characters between neighboring chunks so sentence boundaries are less likely to be cut off.
CHUNK_OVERLAP = 80

# Fetch this many chunks before reranking so the reranker has enough candidates to compare.
TOP_K_RETRIEVAL = 20

# Keep only this many reranked chunks for the final LLM prompt to control latency and context size.
TOP_K_FINAL = 5

# Cap the generated answer length so responses stay concise and predictable.
MAX_ANSWER_TOKENS = 1024

# Restrict uploads to the file types the ingestion pipeline knows how to process.
ALLOWED_EXTENSIONS = [".pdf", ".png", ".jpg", ".jpeg", ".mp3", ".wav", ".m4a"]
