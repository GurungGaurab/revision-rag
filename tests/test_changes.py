from revrag.scan import scan
from revrag.changes import compare

def test_rerun_with_no_changes_is_all_unchanged(tmp_path):
    (tmp_path / "a.txt").write_bytes(b"hello")
    (tmp_path / "b.md").write_bytes(b"abc")

    first = scan(tmp_path)
    second = scan(tmp_path)


def test_edit_delete_and_add_are_detected(tmp_path):
    (tmp_path / "a.txt").write_bytes(b"hello")
    (tmp_path / "b.md").write_bytes(b"abc")
    (tmp_path / "old.txt").write_bytes(b"bye")

    first = scan(tmp_path)

    (tmp_path / "b.md").write_bytes(b"abc, edited")
    (tmp_path / "old.txt").unlink()
    (tmp_path / "new.txt").write_bytes(b"hi")

    second = scan(tmp_path)

    assert compare(first, second) == {"a.txt": "unchanged", "b.md": "changed", "old.txt": "missing", "new.txt": "new"}