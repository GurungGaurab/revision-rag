# LlamaIndex experiments

The same version test as [`../docling`](../docling/), rebuilt with [LlamaIndex](https://developers.llamaindex.ai/): Docling reader → Docling node parser → in-memory vector index → local LLM. The handbooks and the 5 test questions are the ones described in the Docling README.

## Setup

From the repository root, with the venv active:

```bash
pip install llama-index-core llama-index-readers-docling llama-index-node-parser-docling \
    llama-index-embeddings-huggingface llama-index-llms-ollama
```

Ollama must be running with `qwen3:4b-instruct`. Run the scripts from the repository root:

```bash
python experiments/llamaindex/03_per_question_filter.py
```

Each script reads both PDFs from `../docling/`, builds the index in memory and asks the questions. Settings used in all of them: embeddings `all-MiniLM-L6-v2`, LLM `qwen3:4b-instruct` (temperature 0), top 3 chunks, and a Docling converter with OCR off and the pypdfium2 PDF backend (passed to `DoclingReader` as `doc_converter`).

## Scripts

| Script | What it does |
|---|---|
| `01_in_memory.py` | The baseline: both editions in one index, an `edition` field added to each chunk's metadata (read from the file name), 5 questions |
| `02_filter_2026.py` | Same, with a metadata filter so only `edition == 2026` is searched |
| `03_per_question_filter.py` | `pick_edition()` looks for a year in the question (e.g. "in 2025") and filters on it; with no year it uses the current edition (2026) |

## Results (5 questions)

| Setup | Correct answers | Notes |
|---|---|---|
| Default metadata (no edition in the prompt) | late penalty answered **10% (outdated)** | the file name was in the metadata but not in the LLM's prompt |
| `edition` metadata | 4/5 | the fee question gave both fees (correctly labelled) |
| Filter to 2026 | 4/5 | the 2025 question was answered "not in the context" (a safe abstention) |
| Edition chosen per question | **5/5** | no outdated chunk reached the LLM for questions 1–3 |

## Observations

1. **Metadata in the store is not the same as metadata in the prompt.** LlamaIndex kept `origin.filename` for each chunk but left it out of the text sent to the LLM. Printing `node.get_content(metadata_mode=MetadataMode.LLM)` shows exactly what the LLM sees. With only the `edition` field added, the same 3 chunks in the same order changed the answer from 10% to 20%.
2. **Metadata is embedded too.** Adding `edition` lowered the late-penalty scores (0.7647 / 0.7600 → 0.7278 / 0.7218), and for "What was the late penalty in 2025?" the 2025 chunk moved to first place (0.4795 vs 0.4690).
3. **Parser settings change the chunks.** `DoclingNodeParser` gave 20 chunks with Docling's default reader and 22 with pypdfium2 (the fees intro and the fees table are always separate chunks; with pypdfium2 the withdrawal "Exception" paragraph also becomes its own chunk, one per edition), compared with 18 from `HybridChunker` in the Docling experiments.
4. **Default reader settings are heavy.** `DoclingReader` runs OCR by default; on my laptop that, plus the LLM, caused a 120-second timeout. Passing a converter with OCR off fixed it.

## Limits

Two fictional documents and 5 questions. `pick_edition()` only finds explicit years ("last year" is not handled), and the current edition is hard-coded. In the planned design it comes from each version's status and validity dates.
