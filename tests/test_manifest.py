from revrag.scan import scan 
from revrag.manifest import save_manifest, load_manifest

def test_save_then_load_gives_same_documents(tmp_path):
    folder = tmp_path / "docs"
    folder.mkdir()
    (folder/ "a.txt").write_bytes(b"hello")

    docs = scan(folder)

    manifest = tmp_path / "manifest.json"

    save_manifest(docs, manifest)
    loaded = load_manifest(manifest)

    assert loaded == docs
    assert len(loaded) == 1

def test_missing_manifest_gives_empty_list(tmp_path):
    missing = tmp_path / "manifest.json"
    loaded = load_manifest(missing)
    assert loaded == []