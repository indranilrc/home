import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from build import ROOT, build_site
from tests.siteconf import BASE, SITE, URL  # noqa: F401
from sitegen.data import ContentError
from sitegen.writing import load_posts


def project_copy(tmp_path: Path) -> Path:
    root = tmp_path / "proj"
    for d in ("content", "templates", "static"):
        shutil.copytree(ROOT / d, root / d)
    return root


def add_post(root: Path, name: str, front: str, body: str = "Hello **world**.\n\n## A heading\n\nText.") -> None:
    (root / "content" / "writing" / name).write_text(f"---\n{front}\n---\n{body}\n")


def test_no_posts_no_writing_pages_or_nav(tmp_path):
    out = tmp_path / "out"
    build_site(out)
    assert not (out / "writing").exists()
    assert "Writing" not in (out / "index.html").read_text()


def test_post_renders_and_nav_appears(tmp_path):
    root = project_copy(tmp_path)
    add_post(root, "first-note.md", "title: A First Note\ndate: 2026-12-01\nsummary: Why prognostics needs humility.")
    out = tmp_path / "out"
    build_site(out, root=root)
    post = (out / "writing" / "first-note" / "index.html").read_text()
    assert "<h1>A First Note</h1>" in post
    assert "<strong>world</strong>" in post
    assert 'property="og:type" content="article"' in post
    home = (out / "index.html").read_text()
    nav = re.search(r'<nav class="site-nav".*?</nav>', home, re.S).group(0)
    labels = re.findall(r'<a href="[^"]+"[^>]*>([^<]+)', nav)
    assert labels[:3] == ["Research", "Publications", "Writing"]
    assert "Recent writing" in home
    index = (out / "writing" / "index.html").read_text()
    assert "Why prognostics needs humility." in index
    feed = ET.fromstring((out / "writing" / "feed.xml").read_text())
    ns = {"a": "http://www.w3.org/2005/Atom"}
    entries = feed.findall("a:entry", ns)
    assert len(entries) == 1
    assert entries[0].find("a:title", ns).text == "A First Note"
    assert entries[0].find("a:link", ns).get("href") == f"{URL}/writing/first-note/"


def test_draft_excluded_unless_flag(tmp_path):
    d = tmp_path / "w"
    d.mkdir()
    (d / "README.md").write_text("# how to")
    (d / "a.md").write_text("---\ntitle: A\ndate: 2026-01-02\nsummary: s\n---\nx")
    (d / "b.md").write_text("---\ntitle: B\ndate: 2026-03-04\nsummary: s\ndraft: true\n---\nx")
    assert [p["slug"] for p in load_posts(d, include_drafts=False)] == ["a"]
    assert [p["slug"] for p in load_posts(d, include_drafts=True)] == ["b", "a"]


def test_post_missing_date_raises(tmp_path):
    d = tmp_path / "w"
    d.mkdir()
    (d / "x.md").write_text("---\ntitle: X\n---\nbody")
    with pytest.raises(ContentError) as e:
        load_posts(d, include_drafts=False)
    assert "x.md" in str(e.value)


def test_domain_mode_build(tmp_path):
    root = project_copy(tmp_path)
    (root / "content" / "site.yml").write_text(
        'title: Indranil Roychoudhury\nurl: https://indranilroychoudhury.com\nbase_path: ""\ncname: indranilroychoudhury.com\n')
    out = tmp_path / "out"
    build_site(out, root=root)
    home = (out / "index.html").read_text()
    assert 'href="/css/site.css"' in home and "/home/" not in home
    assert '<link rel="canonical" href="https://indranilroychoudhury.com/">' in home
    assert (out / "CNAME").read_text().strip() == "indranilroychoudhury.com"
