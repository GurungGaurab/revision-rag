import json
from dataclasses import asdict
from revrag.models import Document

def save_manifest(docs, path):
    rows = []
    for doc in docs:
        rows.append(asdict(doc))
    with open(path, "w") as f:
        json.dump(rows, f, indent=2)

def load_manifest(path):
    try:
        with open(path, "r") as f:
            rows = json.load(f)
    except FileNotFoundError:
        return []
    docs = []
    for row in rows:
        docs.append(Document(path=row["path"], size=row["size"], sha256=row["sha256"]))
    return docs