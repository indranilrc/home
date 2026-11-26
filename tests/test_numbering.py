import re
from pathlib import Path

import pytest

from build import build_site


@pytest.fixture(scope="module")
def site(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("site")
    build_site(out)
    return out


@pytest.mark.parametrize("page", ["awards", "service", "talks"])
def test_record_lists_are_ordered(site, page):
    html = (site / page / "index.html").read_text()
    main = re.search(r"<main.*?</main>", html, re.S).group(0)
    assert "<ul" not in main, page
    assert "<ol" in main


def test_experience_page_uses_plain_bullets(site):
    main = re.search(r"<main.*?</main>", (site / "experience" / "index.html").read_text(), re.S).group(0)
    assert "<ol" not in main and "<ul" in main


def test_publications_numbered_continuously_descending(site):
    html = (site / "publications" / "index.html").read_text()
    values = [int(v) for v in re.findall(r'<li class="pub" [^>]*value="(\d+)"', html)]
    assert values == list(range(len(values), 0, -1))
    assert len(values) == 106


def test_research_related_lists_ordered(site):
    html = (site / "research" / "index.html").read_text()
    related = re.findall(r'<div class="related">.*?</div>', html, re.S)
    assert related and all("<ol>" in r and "<ul>" not in r for r in related)


def test_css_shows_numbers(site):
    css = (site / "css" / "site.css").read_text()
    assert "list-style: decimal" in css
