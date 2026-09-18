# revision-rag

A learning project that I'm building toward a **revision-aware retrieval-augmented generation (RAG) system**.

## The problem

A RAG knowledge base often holds several versions of the same document. If old, superseded or withdrawn versions stay searchable, a model can answer from outdated information even when the current version exists.

The goal of this project is to manage documents through their whole lifecycle: tracking identity, revisions and status (active, superseded or withdrawn), so that retrieval only uses content that is currently valid.

## Current status

**Early stage.** I'm rebuilding my Python fundamentals before the main build.

- `diagnostic/`: Python exercises covering CSV processing (pandas), text processing, JSON read-modify-write, error handling, and chunked SHA-256 file hashing. The hashing is the basis for detecting changed documents later.

## Planned

These steps are planned, not yet built:

1. Scan a folder of documents and record a manifest (path, size, SHA-256).
2. Detect new, changed, unchanged and missing files between scans.
3. Move the catalogue into PostgreSQL, with documents and immutable revisions.
4. Add chunking, embeddings and retrieval with pgvector, filtering to active revisions only.
5. Evaluate retrieval against simpler update strategies.

## Running the exercises

```bash
python -m venv .venv
source .venv/bin/activate
pip install pandas
python diagnostic/diag.py
```
