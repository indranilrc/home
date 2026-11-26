import json
import re
from pathlib import Path

import pytest

from build import build_site

PAGES = ["index.html", "research/index.html", "publications/index.html", "cv/index.html"]
FORBIDDEN = ["idf-", "eureka", "sharepoint", "stic.slb.com", "degreed"]


@pytest.fixture(scope="module")
def site(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("site")
    build_site(out)
    return out


def test_each_page_has_canonical_and_og(site):
    for rel in PAGES:
        html = (site / rel).read_text()
        path = "/" + rel.removesuffix("index.html")
        assert f'<link rel="canonical" href="https://indranilrc.github.io/home{path}">' in html, rel
        assert 'property="og:title"' in html and 'property="og:image"' in html, rel
        assert 'content="https://indranilrc.github.io/home/img/og.jpg"' in html, rel
        assert 'name="twitter:card" content="summary_large_image"' in html, rel
        assert re.search(r'<meta name="description" content="[^"]{40,}">', html), rel


def test_titles(site):
    assert "<title>Indranil Roychoudhury</title>" in (site / "index.html").read_text()
    assert "<title>Research · Indranil Roychoudhury</title>" in (site / "research/index.html").read_text()


def test_person_jsonld_valid(site):
    html = (site / "index.html").read_text()
    raw = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1)
    data = json.loads(raw)
    assert data["@type"] == "Person"
    assert data["name"] == "Indranil Roychoudhury"
    assert data["jobTitle"] == "Principal AI Scientist"
    assert data["worksFor"]["name"] == "SLB"
    assert "https://orcid.org/0009-0002-1438-0510" in data["sameAs"]


def test_sitemap_lists_pages(site):
    xml = (site / "sitemap.xml").read_text()
    for rel in PAGES:
        assert "https://indranilrc.github.io/home/" + rel.removesuffix("index.html") in xml
    assert "404" not in xml
    assert "Sitemap: https://indranilrc.github.io/home/sitemap.xml" in (site / "robots.txt").read_text()


def test_og_image_exists(site):
    assert (site / "img" / "og.jpg").stat().st_size > 10_000


def test_no_cname_by_default(site):
    assert not (site / "CNAME").exists()


def test_site_has_no_forbidden_strings(site):
    for f in site.rglob("*"):
        if f.suffix not in {".html", ".xml", ".txt", ".js", ".css", ".json"}:
            continue
        t = f.read_text(encoding="utf-8")
        low = t.lower()
        for bad in FORBIDDEN:
            assert bad not in low, (str(f.relative_to(site)), bad)
        assert "internal" not in low.replace("international", ""), str(f.relative_to(site))
        assert "—" not in t, str(f.relative_to(site))
