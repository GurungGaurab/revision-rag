# Docling + embedding experiments

Small experiments with [Docling](https://docling-project.github.io/docling/), sentence embeddings, pgvector and a local LLM, as groundwork for a version-aware RAG (retrieval-augmented generation) pipeline.

The question behind it: **if a knowledge base holds two editions of the same document, can vector search tell the current one from the outdated one?**

## Test data

Two fictional handbooks, `handbook_2025.pdf` and `handbook_2026.pdf` ("Northbridge University", 2 pages each). They are identical except for three facts:

| Fact | 2025 | 2026 |
|---|---|---|
| Withdrawal period without penalty | 14 days | 21 days |
| Late submission penalty | 10% per day | 20% per day |
| BSc Computer Science fee | HKD 88,000 | HKD 92,000 |

Test questions (the current edition is 2026):

1. What is the late submission penalty? → 20% (2026)
2. How many days do I have to withdraw without penalty? → 21 days (2026)
3. How much is the BSc Computer Science fee? → HKD 92,000 (2026)
4. When is the first-semester fee due? → 30 September (same in both)
5. What was the late penalty in 2025? → 10% (needs the old edition)

## Setup

From the repository root, with Python 3.12 (some Docling dependencies had no wheels for newer versions at the time):

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,docling]"
```

The first run downloads Docling's layout model and the `all-MiniLM-L6-v2` embedding model (about 90 MB) from Hugging Face.

The database and LLM scripts also need:

```bash
pip install "psycopg[binary]" pgvector ollama
```

- **PostgreSQL with pgvector.** I used PostgreSQL 15 (Homebrew) with pgvector 0.8.6 built from source. Create the database and table once:

  ```sql
  CREATE DATABASE revrag;
  \c revrag
  CREATE EXTENSION vector;
  CREATE TABLE chunks (
      id bigserial PRIMARY KEY,
      edition int,
      heading text,
      content text,
      embedding_model text,
      embedding vector(384)
  );
  ```

- **Ollama** running locally with `qwen3:4b-instruct` (`ollama pull qwen3:4b-instruct`).

The early scripts open the handbook PDFs by name, so run them from this folder:

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
| `store_new_chunks.py` | Chunks and embeds both editions and inserts them into the `chunks` table (18 rows: 9 per edition). Run it once; it appends, so use `TRUNCATE chunks;` to start again |
| `search_no_filter.py` | Asks the 5 test questions and prints the 3 closest chunks (cosine distance, `<=>`) with no version filter |
| `search_filter_2026.py` | Same search restricted to `WHERE edition = 2026` |
| `ask_qwen.py` | Retrieves the top 3 chunks, labels each with its edition and section, and asks the local Qwen model to answer with a citation |

All scripts use the pypdfium2 PDF backend with OCR turned off (see findings).

## Findings so far

1. **PDF reader matters.** With Docling's default PDF backend, this font lost full stops and at least one letter ("ate submission"). Turning OCR off did not change it, so OCR was not the cause. Switching to the pypdfium2 backend fixed it. (Checked on these test files only.)
2. **Heading levels are flat.** Every section header comes out as level 1, so "1.1" is not nested under "1.". Docling's layout model detects *that* a line is a heading, not *how deep* it is. As a result, `HybridChunker` replaces "3. Assessment" with "3.1 Late submission" and the parent heading never reaches the chunk metadata.
3. **Chunk size.** Default settings (`all-MiniLM-L6-v2` tokenizer, 256-token limit): **9 chunks**, one per subsection. With `max_tokens=40`: **17 chunks**. Most splits fell on sentence ends, but the fees table was cut mid-name ("MSc Data" / "Science") and one sentence was cut at a comma.
4. **Old and new editions embed almost identically.** The 2025 and 2026 late-penalty chunks (identical except 10% vs 20%) have a cosine similarity of **0.9997**. For the question *"What is the late submission penalty?"* the scores were **0.7884** (2025) and **0.7901** (2026). The current edition ranked first, but only by 0.0017, and for no reason related to being current.
5. **With no filter, outdated chunks are always retrieved.** Over the 5 questions (top 3):

   | Measure | Questions counted | Result |
   |---|---|---|
   | Outdated chunk ranked first | 1–3 (changed facts) | **1/3** (the fee question) |
   | Outdated chunk anywhere in the top 3 | 1–3 | **3/3** |
   | Right section and edition in the top 3 | all 5 | **5/5** |

   Question 4 is an exact tie (identical text). Question 5 mentions 2025, but the 2026 chunk still ranked first, because no chunk's text mentions its year.
6. **A fixed filter fails one type of question.** `WHERE edition = 2026`: 0/3 outdated, but question 5 loses its source (4/5). Filtering to 2025 instead: outdated first for 3/3 changed facts (2/5 overall).
7. **Labels in the prompt let the LLM sort out mixed retrieval.** With no filter but each chunk labelled `[2025 edition | heading]` / `[2026 edition | heading]`, Qwen answered **5/5** correctly, including 10% for question 5. It assumed the newest edition is current; the prompt never said so.

**Takeaway:** similarity search alone cannot separate current from superseded content. Each chunk needs version metadata stored with it, and the system has to choose the right version for each question (see [`../llamaindex`](../llamaindex/)).

## Next steps

- Versioned schema: `documents` → `document_versions` (status, `valid_from`, `valid_to`) → `chunks`
- Read effective dates from the document itself (the title section says "Effective from 1 September 2026")
- Try inferring heading levels (numbering such as "1.2") so chunks keep their full section path
