import datetime as dt
import re
from pathlib import Path

import pytest

from build import ROOT, build_site
from tests.siteconf import BASE, SITE, URL  # noqa: F401


@pytest.fixture(scope="module")
def site(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("site")
    build_site(out)
    return out


def test_theme_script_before_css(site):
    html = (site / "index.html").read_text()
    assert html.index("localStorage") < html.index("site.css")


def test_nav_without_posts(site):
    html = (site / "index.html").read_text()
    nav = re.search(r"<nav.*?</nav>", html, re.S).group(0)
    for label in ("Research", "Publications", "CV"):
        assert f">{label}</a>" in nav
    assert "Writing" not in nav
    assert f'href="{BASE}/research/"' in nav


def test_theme_toggle_present(site):
    html = (site / "index.html").read_text()
    assert 'class="theme-toggle"' in html
    assert (site / "js" / "theme.js").exists()


def test_404_exists(site):
    html = (site / "404.html").read_text()
    assert "404" in html or "not found" in html.lower()


def test_no_third_party_requests(site):
    for page in site.rglob("*.html"):
        html = page.read_text()
        for tag in re.findall(r"<(?:link|script|img|source)\b[^>]*>", html):
            for url in re.findall(r'(?:src|href)="([^"]+)"', tag):
                if tag.startswith("<link") and ('rel="canonical"' in tag or 'rel="alternate"' in tag):
                    continue
                assert not url.startswith(("http:", "https:", "//")), (page.name, tag)


def test_fonts_self_hosted(site):
    css = (site / "css" / "site.css").read_text()
    assert "@font-face" in css and "font-display: swap" in css
    assert len(list((site / "fonts").glob("*.woff2"))) >= 5


def test_css_has_mobile_breakpoint():
    css = (ROOT / "static" / "css" / "site.css").read_text()
    assert "max-width: 640px" in css
    assert "prefers-reduced-motion" in css
    assert "prefers-color-scheme: dark" in css


def test_footer_has_build_date(site):
    html = (site / "index.html").read_text()
    today = dt.date.today()
    assert f"Last updated {today:%B} {today.day}, {today.year}" in html
