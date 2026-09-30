# Docling + embedding experiments

Small experiments with [Docling](https://docling-project.github.io/docling/) and sentence embeddings, as groundwork for a version-aware RAG (retrieval-augmented generation) pipeline.

The question behind it: **if a knowledge base holds two editions of the same document, can vector search tell the current one from the outdated one?**

## Test data

Two fictional handbooks, `handbook_2025.pdf` and `handbook_2026.pdf` ("Northbridge University", 2 pages each). They are identical except for three facts:

| Fact | 2025 | 2026 |
|---|---|---|
| Withdrawal period without penalty | 14 days | 21 days |
| Late submission penalty | 10% per day | 20% per day |
| BSc Computer Science fee | HKD 88,000 | HKD 92,000 |

## Setup

From the repository root, with Python 3.12 (some Docling dependencies had no wheels for newer versions at the time):

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,docling]"
```

The first run downloads Docling's layout model and the `all-MiniLM-L6-v2` embedding model (about 90 MB) from Hugging Face.

Run the scripts from this folder, since they open the handbook PDFs by name:

```bash
cd experiments/docling
python chunk.py
```

## Scripts

| Script | What it does |
|---|---|
| `explore.py` | Converts a handbook and prints every item Docling found (type, text, heading level) |
| `chunk.py` | Splits a handbook with Docling's `HybridChunker` and prints each chunk with its headings |
| `embed_demo.py` | Embeds three example sentences and prints their cosine similarities |
| `embed_chunks.py` | Chunks both editions, embeds the "3.1 Late submission" chunk from each, and compares them with each other and with a question |

All scripts use the pypdfium2 PDF backend with OCR turned off (see findings).

## Findings so far

1. **PDF reader matters.** With Docling's default PDF backend, this font lost full stops and at least one letter ("ate submission"). Turning OCR off did not change it, so OCR was not the cause. Switching to the pypdfium2 backend fixed it. (Checked on these test files only.)
2. **Heading levels are flat.** Every section header comes out as level 1, so "1.1" is not nested under "1.". Docling's layout model detects *that* a line is a heading, not *how deep* it is. As a result, `HybridChunker` replaces "3. Assessment" with "3.1 Late submission" and the parent heading never reaches the chunk metadata.
3. **Chunk size.** Default settings (`all-MiniLM-L6-v2` tokenizer, 256-token limit): **9 chunks**, one per subsection. With `max_tokens=40`: **17 chunks**. Most splits fell on sentence ends, but the fees table was cut mid-name ("MSc Data" / "Science") and one sentence was cut at a comma.
4. **Old and new editions embed almost identically.** The 2025 and 2026 late-penalty chunks (identical except 10% vs 20%) have a cosine similarity of **0.9997**. For the question *"What is the late submission penalty?"* the scores were **0.7884** (2025) and **0.7901** (2026). The current edition ranked first, but only by 0.0017, and for no reason related to being current.

**Takeaway:** similarity search alone cannot reliably separate current from superseded content. Each chunk needs version metadata stored with it (document, edition, status), and retrieval has to filter on it.

## Next steps

- Store chunks and embeddings in PostgreSQL with pgvector
- Search with no version filter and measure how often outdated chunks are retrieved (baseline)
- Add version/status metadata and compare
- Try inferring heading levels (numbering such as "1.2") so chunks keep their full section path
