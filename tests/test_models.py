from revrag.models import Document, document_from_path

def test_document_field():
    doc = Document(path = "notes.txt", size = 5, sha256 = "abc")
    assert doc.size == 5

def test_hash_of_known_content(tmp_path):
    p = tmp_path / "hello.txt"
    p.write_bytes(b"hello")
    doc = document_from_path(p)
    assert doc.sha256 == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    assert doc.size == 5

def test_empty_file(tmp_path):
    p = tmp_path / "hello.txt"
    p.write_bytes(b"")
    doc = document_from_path(p)
    assert doc.sha256 == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert doc.size == 0