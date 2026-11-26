import re
from pathlib import Path

import pytest

from build import build_site


@pytest.fixture(scope="module")
def home(tmp_path_factory) -> str:
    out = tmp_path_factory.mktemp("site")
    build_site(out)
    return (out / "index.html").read_text()


def visible_text(html: str) -> str:
    html = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", html, flags=re.S)
    html = re.sub(r"<head>.*?</head>", " ", html, flags=re.S)
    return re.sub(r"<[^>]+>", " ", html)


def test_home_has_core_sections(home):
    assert re.search(r"<h1[^>]*>\s*Indranil Roychoudhury\s*</h1>", home)
    assert "Currently" in home
    band = re.search(r'<section class="band" aria-labelledby="currently".*?</section>', home, re.S).group(0)
    assert band.count("<li>") == 4
    for url in ("https://scholar.google.com/citations?user=65YthzIAAAAJ",
                "https://www.linkedin.com/in/indranilroychoudhury",
                "https://orcid.org/0009-0002-1438-0510"):
        assert url in home


def test_selected_work_links_to_research(home):
    links = re.findall(r'href="/home/research/#([a-z-]+)"', home)
    assert 3 <= len(set(links)) <= 4


def test_email_fallback_present(home):
    assert "indranil.r.c at gmail dot com" in home
    assert "indranil.r.c@gmail.com" not in home


def test_fellow_mentioned_once(home):
    assert visible_text(home).count("Fellow") == 1


def test_fan_svg_hidden_from_a11y(home):
    svg = re.search(r'<svg class="motif"[^>]*>', home).group(0)
    assert 'aria-hidden="true"' in svg
    assert svg.count("<path") == 0  # attributes only in the tag
    assert home.count('class="fan"') >= 1


def test_photo_has_alt(home):
    img = re.search(r'<img class="portrait"[^>]*>', home).group(0)
    assert 'alt="' in img and 'alt=""' not in img


def test_no_hype_or_em_dash(home):
    text = visible_text(home).lower()
    for bad in ("—", "passionate", "cutting-edge", "leverag", "innovative", "revolutioniz", "h-index", "citations"):
        assert bad not in text, bad
