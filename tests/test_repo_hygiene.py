"""The repo is public: no SLB-internal identifiers in any tracked file (see tests/hygiene.py)."""
import re
import subprocess
from pathlib import Path

from tests.hygiene import denylisted

ROOT = Path(__file__).resolve().parents[1]
BINARY = {".pdf", ".png", ".jpg", ".jpeg", ".woff2", ".ico", ".gif"}


def tracked_files():
    out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    for rel in out.splitlines():
        p = ROOT / rel
        if p.suffix.lower() not in BINARY and p.is_file():
            yield rel, p.read_text(encoding="utf-8", errors="ignore")


def test_no_disclosure_numbers():
    for rel, text in tracked_files():
        for m in re.finditer(r"IDF-\d{3,}", text):
            assert m.group(0) == "IDF-00000", (rel, "disclosure-style number")


def test_no_denylisted_terms():
    for rel, text in tracked_files():
        n = denylisted(text)
        assert not n, (rel, f"{n} denylisted term(s)")
