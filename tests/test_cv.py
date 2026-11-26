import re

import pytest

from build import ROOT, build_site
from sitegen.data import load_content


@pytest.fixture(scope="module")
def page(tmp_path_factory) -> str:
    out = tmp_path_factory.mktemp("site")
    build_site(out)
    return (out / "cv" / "index.html").read_text()


def text(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html)


def test_cv_sections_in_order(page):
    heads = re.findall(r'<section class="cv-section"[^>]*>\s*<h2[^>]*>([^<]+)</h2>', page)
    assert heads == ["Experience", "Education", "Honors and awards", "Professional service",
                     "Talks and tutorials", "Teaching", "Memberships"]


def test_cv_has_pdf_link(page):
    assert 'href="/home/IndranilRoychoudhury_CV.pdf"' in page


def test_cv_no_brag_phrases(page):
    t = text(page).lower()
    for bad in ("h-index", "i10", "citations", "first-named", "highest individual honor",
                "at most five", "1,000 submissions", "—", "eureka", "digital singularity"):
        assert bad not in t, bad
    assert not re.search(r"\bstic\b", t)


def test_fellow_plain(page):
    assert "Fellow, Prognostics and Health Management Society, 2023" in text(page)


def test_every_experience_overridden():
    content = load_content(ROOT)
    import json
    raw = {e["key"]: e["bullets"] for e in json.loads((ROOT / "content/generated/cv.json").read_text())["experience"]}
    for e in content.cv["experience"]:
        assert 1 <= len(e["bullets"]) <= 4, e["key"]
        assert e["bullets"] != raw[e["key"]] or len(raw[e["key"]]) <= 1, e["key"]


def test_jobs_render(page):
    assert page.count('<article class="job">') == 7
    assert "Principal AI Scientist" in page


def test_no_slb_internal_talks(page):
    assert "Technical Talks at SLB" not in page
