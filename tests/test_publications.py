import re

import pytest

from build import ROOT, build_site
from sitegen.data import load_content


@pytest.fixture(scope="module")
def page(tmp_path_factory) -> str:
    out = tmp_path_factory.mktemp("site")
    build_site(out)
    return (out / "publications" / "index.html").read_text()


def test_all_pubs_rendered_without_js(page):
    content = load_content(ROOT)
    assert page.count('<li class="pub"') == len(content.pubs)
    for p in content.pubs:
        assert f'id="pub-{p["key"]}"' in page


def test_filters_hidden_without_js(page):
    tag = re.search(r'<div class="filters"[^>]*>', page).group(0)
    assert " hidden" in tag


def test_filter_chips(page):
    chips = re.findall(r'<button class="chip"[^>]*data-filter="([a-z, ]+)"', page)
    assert chips == ["all", "journal", "conference", "book,chapter", "patent", "report,whitepaper,thesis"]


def test_years_descending(page):
    years = [y for y in re.findall(r'<h2 id="y-(\w+)"', page)]
    numeric = [int(y) for y in years if y.isdigit()]
    assert numeric == sorted(numeric, reverse=True)
    assert years[: len(numeric)] == [str(y) for y in numeric]


def test_patents_present(page):
    li = re.search(r'<li class="pub" id="pub-US12608592"[^>]*>', page).group(0)
    assert 'data-type="patent"' in li


def test_award_tag(page):
    li = re.search(r'<li class="pub" id="pub-PHM-11-a".*?</li>', page, re.S).group(0)
    assert '<span class="tag">' in li


def test_book_featured(page):
    assert 'class="book"' in page and "book-cover.png" in page


def test_book_details(page):
    book = re.search(r'<section class="book".*?</section>', page, re.S).group(0)
    assert "978-1539074830" in book
    assert "396 pages" in book
    assert 'href="https://a.co/f6TQn4B"' in book
    assert "NASA Ames" in book
