from pathlib import Path

from build import build_site


def test_build_writes_index(tmp_path: Path):
    build_site(tmp_path)
    index = tmp_path / "index.html"
    assert index.exists()
    assert '<html lang="en"' in index.read_text()
    assert (tmp_path / "img" / "IRCphoto.jpg").exists()
