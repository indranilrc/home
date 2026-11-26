import json
import re
from pathlib import Path

import pytest

from build import build_site
from tests.siteconf import BASE, SITE, URL  # noqa: F401
from tests.hygiene import denylisted

PAGES = ["index.html", "research/index.html", "publications/index.html", "talks/index.html",
         "service/index.html", "awards/index.html", "experience/index.html"]
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
        assert f'<link rel="canonical" href="{URL}{path}">' in html, rel
        assert 'property="og:title"' in html and 'property="og:image"' in html, rel
        assert f'content="{URL}/img/og.jpg"' in html, rel
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
        assert f"{URL}/" + rel.removesuffix("index.html") in xml
    assert "404" not in xml
    assert f"Sitemap: {URL}/sitemap.xml" in (site / "robots.txt").read_text()


def test_og_image_exists(site):
    assert (site / "img" / "og.jpg").stat().st_size > 10_000


def test_cname_only_when_configured(site):
    assert (site / "CNAME").exists() == bool(SITE.get("cname"))


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
        assert not denylisted(t), str(f.relative_to(site))


ALLOWED_HOSTS = {"doi.org", "patents.google.com", "scholar.google.com", "www.linkedin.com", "orcid.org",
                 "phmsociety.org", "www.slb.com", "indranilrc.github.io", "indranilroychoudhury.com"}


def test_external_links_use_known_hosts(site):
    import urllib.parse
    for f in site.rglob("*.html"):
        for url in re.findall(r'href="(https?://[^"]+)"', f.read_text()):
            host = urllib.parse.urlparse(url).hostname
            ok = host in ALLOWED_HOSTS or host.endswith(".phmsociety.org")
            assert ok and not (host.endswith(".slb.com") and host != "www.slb.com"), (f.name, host)
