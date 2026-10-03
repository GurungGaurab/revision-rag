# revision-rag

A learning project that I'm building toward a **revision-aware retrieval-augmented generation (RAG) system**.

## The problem

A RAG knowledge base often holds several versions of the same document. If old, superseded or withdrawn versions stay searchable, a model can answer from outdated information even when the current version exists.

The goal of this project is to manage documents through their whole lifecycle: tracking identity, revisions and status (active, superseded or withdrawn), so that retrieval only uses content that is currently valid.

## Why similarity search alone isn't enough

In [`experiments/docling`](experiments/docling/), I chunked two editions of the same (fictional) handbook with Docling and embedded them with `all-MiniLM-L6-v2`. The 2025 and 2026 versions of the late-penalty rule differ only in "10%" vs "20%", and their embeddings have a cosine similarity of **0.9997**. For the question *"What is the late submission penalty?"* the two scored **0.7884** and **0.7901**. The current edition came first, but only by 0.0017, and for no reason related to being current.

I then stored both editions in PostgreSQL with pgvector and asked 5 test questions (three about facts that changed, one about a fact that didn't, one about the past):

| Setup | Result |
|---|---|
| Vector search, no version filter | an outdated chunk was in the top 3 for **3/3** changed facts, and ranked first for 1/3 |
| Filter to the latest edition only | no outdated chunks, but the question about 2025 lost its source |
| LlamaIndex with default settings + local LLM | answered the late penalty with the **outdated** value (10%) |
| LlamaIndex, edition chosen per question | **5/5** correct |

So each chunk needs version metadata stored with it, and retrieval has to choose the right version for each question. That's what this project builds toward.

## Current status

**Early stage.** Pilot experiments done; the versioned database is next.

- `src/revrag/`: a small, tested package (standard library only)
  - `models.py`: `Document` (path, size, SHA-256) built from a file, hashed in chunks
  - `scan.py`: `scan(folder)` walks a folder recursively, skips hidden files and folders, stores relative paths
  - `manifest.py`: save/load the scan as a JSON manifest (a missing manifest means a first run)
  - `changes.py`: `compare(old, new)` labels each file **new / changed / unchanged / missing**
- `tests/`: 8 pytest tests (using temporary folders), passing on Python 3.12
- `experiments/docling/`: Docling parsing, embeddings, pgvector storage and search, and answers from a local LLM (see its README)
- `experiments/llamaindex/`: the same pipeline in LlamaIndex, with edition metadata, filters and per-question edition choice (see its README)
- `diagnostic/`: Python warm-up exercises (CSV, text, JSON, error handling, hashing)

## Planned

These steps are planned, not yet built:

1. Clear errors for a corrupt manifest; skip unreadable files; a command-line summary (`3 new, 1 changed, ...`).
2. A versioned schema in PostgreSQL: `documents` → `document_versions` (status, file hash, `valid_from`, `valid_to`) → `chunks`.
3. Choose the version per question: an explicit date in the question, then a relative date ("last year"), then the version valid today; abstain if no version covers the date.
4. A larger evaluation set (30–60 questions with outdated-version traps) to compare these strategies.

## Setup

Python 3.12:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

For the Docling experiments, install the extra dependencies with `pip install -e ".[dev,docling]"`. The database, LLM and LlamaIndex experiments need a few more packages and services; see each experiment's README.

The `diagnostic/` exercises also use pandas (`pip install pandas`).
