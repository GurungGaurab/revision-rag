import pandas as pd 
import json 
import string
import hashlib
from pathlib import Path
from dataclasses import dataclass

DATA = Path(__file__).parent / "data"

@dataclass

class Document: 
    path: str
    size: int 
    sha256: str

def word_counts(path):
    with open(path) as f:
        text = f.read()
        new_text = text.lower().split()

    counts = {}
    for words in new_text:
        cleaned = words.strip(string.punctuation)
        counts[cleaned] = counts.get(cleaned,0) + 1

    return counts;


def document_from_path(path):
    

    with open(path, "rb") as f:
        h = hashlib.sha256()
        while True: 
            chunk = f.read(8192)
            if not chunk:
                break;
            h.update(chunk)

    document = h.hexdigest()
    return Document(path = str(path), size = Path(path).stat().st_size, sha256=document)
        



def top_scores(path, n = 3):
    df = pd.read_csv(path)
    top_score = df.sort_values("score", ascending=False, kind = "stable").head(n)

    results = []

    for row in top_score.itertuples(index = False):
        results.append((row.name,int(row.score)))

    return results


def lowest_paid (path , departement, n = 2):
    df = pd.read_csv(path)
    lowest = df[df["dept"] == departement].sort_values("salary", ascending = True, kind = "stable").head(n)
    results = []

    for row in lowest.itertuples(index = False):
        results.append((row.name, int(row.salary)))

    return results;

def add_field(path, out_path, key, value):
    with open(path) as f:
        data = json.load(f)

    for records in data: 
        records[key] = value

    with open(out_path, "w") as f:
        json.dump(data, f, indent = 2)

def safe_load_json(path):
    try:
        with open(path) as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"No such File exist: {path}")
        return None
    except json.JSONDecodeError:
        print(f"File is not a valid JSON Format: {path}")
        return None


if __name__ == "__main__":
    #print(top_scores(DATA / "scores.csv"))
    #print(lowest_paid(DATA / "employees.csv", "Data"))
    #print(add_field(DATA / "records.json", DATA / "try.json", "Tried?", "YES"))
    #print(document_from_path(DATA / "scores.csv"))
    #print(word_counts(DATA / "sample.txt"))
    print(safe_load_json(DATA / "records.json"))
    print(safe_load_json(DATA / "broken.json"))
    print(safe_load_json(DATA / "nope.json"))
