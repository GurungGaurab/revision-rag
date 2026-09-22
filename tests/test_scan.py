from revrag.scan import scan 

def test_scan_finds_visible_files_only(tmp_path):

    (tmp_path / "week1").mkdir()
    (tmp_path / "a.txt").write_bytes(b"hello")
    (tmp_path / "week1" / "b.md").write_bytes(b"abc")
    (tmp_path / ".secret.txt").write_bytes(b"x")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_bytes(b"y")

    docs = scan(tmp_path)

    paths = []
    for doc in docs:
        paths.append(doc.path)

    assert paths ==(["a.txt", "week1/b.md"])