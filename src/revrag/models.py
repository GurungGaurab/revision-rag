import hashlib
from dataclasses import dataclass
from pathlib import Path



@dataclass
class Document: 
    path: str
    size: int 
    sha256: str

def document_from_path(path):
    

    with open(path, "rb") as f:
        h = hashlib.sha256()
        while True: 
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)

    document = h.hexdigest()
    return Document(path = str(path), size = Path(path).stat().st_size, sha256=document)

