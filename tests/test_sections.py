import re
import urllib.parse
from pathlib import Path

import pytest

from build import build_site
from tests.siteconf import BASE, URL

NAV = [("Research", "/research/"), ("Publications", "/publications/"), ("Talks &amp; Teaching", "/talks/"),
       ("Service", "/service/"), ("Awards", "/awards/"), ("Experience", "/experience/"),
       ("CV", "/IndranilRoychoudhury_CV.pdf")]


@pytest.fixture(scope="module")
def site(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("site")
    build_site(out)
    return out


def text(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html)


def test_nav_has_six_items_in_order(site):
    nav = re.search(r'<nav class="site-nav".*?</nav>', (site / "index.html").read_text(), re.S).group(0)
    found = re.findall(r'<a href="([^"]+)"[^>]*>([^<]+)', nav)
    assert found == [(BASE + path, label) for label, path in NAV]
    cv = re.search(r'<a href="[^"]+\.pdf"[^>]*>', nav).group(0)
    assert 'target="_blank"' in cv and "noopener" in cv


@pytest.mark.parametrize("slug,heads", [
    ("awards", ["Individual awards", "Group awards", "Paper awards", "Competition awards"]),
    ("service", ["Conference organization", "Reviewing: journals", "Reviewing: conferences and workshops", "Other service"]),
    ("talks", ["Invited talks and tutorials", "Teaching"]),
])
def test_section_pages(site, slug, heads):
    html = (site / slug / "index.html").read_text()
    assert re.findall(r"<h2[^>]*>([^<]+)</h2>", html) == heads
    assert f'href="{BASE}/{slug}/" aria-current="page"' in html


def test_awards_page_plain(site):
    t = text((site / "awards" / "index.html").read_text())
    assert "Fellow, Prognostics and Health Management Society, 2023" in t
    for bad in ("highest individual honor", "at most five", "1,000 submissions"):
        assert bad not in t.lower()


def test_service_hides_internal_role(site):
    assert "eureka" not in (site / "service" / "index.html").read_text().lower()


def test_experience_page_sections(site):
    html = (site / "experience" / "index.html").read_text()
    heads = re.findall(r'<section class="cv-section"[^>]*>\s*<h2[^>]*>([^<]+)</h2>', html)
    assert heads == ["Work", "Education", "Memberships"]
    assert "<h1>Experience</h1>" in html
    assert not (site / "cv").exists()
    for slug in ("awards", "service", "talks"):
        assert f'href="{BASE}/{slug}/"' in html


def test_external_links_open_in_new_tab(site):
    own = urllib.parse.urlparse(URL).hostname
    count = 0
    for f in site.rglob("*.html"):
        for tag in re.findall(r"<a\b[^>]*>", f.read_text()):
            m = re.search(r'href="(https?://[^"]+)"', tag)
            if not m or urllib.parse.urlparse(m.group(1)).hostname == own:
                continue
            count += 1
            assert 'target="_blank"' in tag, (f.name, tag)
            assert re.search(r'rel="[^"]*noopener', tag), (f.name, tag)
    assert count > 50


def test_internal_links_same_tab(site):
    for tag in re.findall(r"<a\b[^>]*>", (site / "index.html").read_text()):
        if re.search(r'href="/', tag) and ".pdf" not in tag:  # the CV PDF opens in a new tab on purpose
            assert "target=" not in tag, tag
