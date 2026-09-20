from pathlib import Path 
from revrag.models import document_from_path

def scan(folder):
    root = Path(folder)
    docs = []


    for name in sorted(root.rglob("*")):
        if not name.is_file():
            continue
        rel = name.relative_to(root)
        hidden = False
        for part in rel.parts:
            if part.startswith("."):
                hidden = True
        if hidden:
            continue
        doc = document_from_path(name)
        doc.path = rel.as_posix()
        docs.append(doc)

   
    return docs

