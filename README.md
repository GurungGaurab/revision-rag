# revision-rag

A learning project that I'm building toward a **revision-aware retrieval-augmented generation (RAG) system**.

## The problem

A RAG knowledge base often holds several versions of the same document. If old, superseded or withdrawn versions stay searchable, a model can answer from outdated information even when the current version exists.

The goal of this project is to manage documents through their whole lifecycle: tracking identity, revisions and status (active, superseded or withdrawn), so that retrieval only uses content that is currently valid.

## Why similarity search alone isn't enough

In [`experiments/docling`](experiments/docling/), I chunked two editions of the same (fictional) handbook with Docling and embedded them with `all-MiniLM-L6-v2`. The 2025 and 2026 versions of the late-penalty rule differ only in "10%" vs "20%", and their embeddings have a cosine similarity of **0.9997**. For the question *"What is the late submission penalty?"* the two scored **0.7884** and **0.7901**. The current edition came first, but only by 0.0017, and for no reason related to being current.

So each chunk needs version metadata stored with it, and retrieval has to filter on it. That's what this project builds toward.

## Current status

**Early stage.**

- `src/revrag/`: a small, tested package (standard library only)
  - `models.py`: `Document` (path, size, SHA-256) built from a file, hashed in chunks
  - `scan.py`: `scan(folder)` walks a folder recursively, skips hidden files and folders, stores relative paths
  - `manifest.py`: save/load the scan as a JSON manifest (a missing manifest means a first run)
  - `changes.py`: `compare(old, new)` labels each file **new / changed / unchanged / missing**
- `tests/`: pytest tests using temporary folders
- `experiments/docling/`: Docling conversion, chunking and embedding experiments (see its README)
- `diagnostic/`: Python warm-up exercises (CSV, text, JSON, error handling, hashing)

## Planned

These steps are planned, not yet built:

1. Clear errors for a corrupt manifest; skip unreadable files; a command-line summary (`3 new, 1 changed, ...`).
2. Move the catalogue into PostgreSQL, with documents and immutable revisions.
3. Store chunks and embeddings with pgvector; measure how often outdated chunks are retrieved with no filtering (baseline).
4. Filter retrieval to active revisions and compare against simpler update strategies.

## Setup

Python 3.12:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

For the Docling experiments, install the extra dependencies with `pip install -e ".[dev,docling]"`.

The `diagnostic/` exercises also use pandas (`pip install pandas`).
