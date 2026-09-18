# Day 1 diagnostic: no AI, no copy-paste, 60–90 min
Put everything in `diagnostic/diag.py`. Run each with `python diag.py`. Note the time you start.

1. `top_scores(path, n=3) -> list[tuple[str, int]]`
   On data/scores.csv → [('Bob', 95), ('Divya', 95), ('Farah', 88)]
   (Ties: keep file order. Scores must be ints, not strings.)

2. `word_counts(path) -> dict[str, int]`
   Case-insensitive, punctuation stripped. On data/sample.txt: 'the' → 5, 'old' → 3, 'index' → 2.

3. `add_field(path, out_path, key, value)`
   Load data/records.json, add "status": "active" to every record, write to out.json (pretty, indent=2).
   Must NOT modify the original file.

4. `@dataclass Document(path: str, size: int, sha256: str)` + `document_from_path(path) -> Document`
   Use hashlib; read the file in chunks (e.g. 8192 bytes), not all at once.
   Check: the hash of scores.csv should match `shasum -a 256 data/scores.csv` in the terminal.

5. `safe_load_json(path)`
   data/records.json → returns the list
   data/broken.json  → prints a clear message naming the file, returns None, doesn't crash
   data/nope.json    → prints a clear "not found" message, returns None, doesn't crash

When done, write down: time taken, and which ones you got stuck on and why.
