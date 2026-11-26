"""Render static/img/og.jpg (1200x630 social preview) from tools/og_card.html."""
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 1200, "height": 630})
    page.goto((HERE / "og_card.html").as_uri())
    page.wait_for_timeout(300)
    page.screenshot(path=str(HERE.parent / "static" / "img" / "og.jpg"), type="jpeg", quality=88)
    b.close()
print("wrote static/img/og.jpg")
