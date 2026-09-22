
def compare(old_docs, new_docs):
    old = {}
    for doc in old_docs:
        old[doc.path] = doc.sha256

    new = {}
    for doc in new_docs:
        new[doc.path] = doc.sha256

    labels = {}

    for path in new:
        if path not in old:
            labels[path] = "new"
        elif old[path] != new[path]:
            labels[path] = "changed"
        else:
            labels[path] = "unchanged"

    for path in old:
        if path not in new:
            labels[path] = "missing"

    return labels