import re

import pytest

from build import build_site
from tests.siteconf import BASE, SITE, URL  # noqa: F401

IDS = ["automating-phm", "hybrid-models", "foundation-models", "field-data",
       "airspace-safety", "aerospace-phm", "distributed-diagnosis"]


@pytest.fixture(scope="module")
def page(tmp_path_factory) -> str:
    out = tmp_path_factory.mktemp("site")
    build_site(out)
    return (out / "research" / "index.html").read_text()


def test_seven_themes_in_order(page):
    assert re.findall(r'<section class="theme" id="([a-z-]+)"', page) == IDS


def test_every_theme_has_related_items(page):
    sections = re.split(r'<section class="theme"', page)[1:]
    assert len(sections) == 7
    for s in sections:
        assert s.count('<li class="rel">') >= 1


def test_related_patent_links_out(page):
    assert 'href="https://patents.google.com/patent/US12136267B2/en"' in page


def test_research_nav_current(page):
    assert f'<a href="{BASE}/research/" aria-current="page">Research</a>' in page


def test_research_no_numbers_brag(page):
    text = re.sub(r"<[^>]+>", " ", page).lower()
    for bad in ("%", "h-index", "citations", "first-named", "—"):
        assert bad not in text, bad
