"""Jinja environment and static-file helpers."""
from __future__ import annotations

import re
import shutil
import urllib.parse
from pathlib import Path

import jinja2
import markdown as md
from markupsafe import Markup


def make_env(templates_dir: Path, site: dict) -> jinja2.Environment:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(templates_dir)),
        autoescape=jinja2.select_autoescape(["html", "j2", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    base = site.get("base_path", "") or ""
    env.globals["base"] = base
    env.globals["site"] = site
    env.filters["url"] = lambda path: base + path
    env.filters["markdown"] = render_markdown
    env.filters["group_title"] = group_title
    env.filters["inline_markdown"] = lambda text: Markup(
        render_markdown(text).removeprefix("<p>").removesuffix("</p>"))
    return env


def copy_static(static_dir: Path, out_dir: Path) -> None:
    for item in static_dir.iterdir():
        target = out_dir / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)


GROUP_TITLES = {
    "invited talks and conference tutorials": "Invited talks and tutorials",
    "reviewing activities: journals": "Reviewing: journals",
    "reviewing activities: conferences and workshops": "Reviewing: conferences and workshops",
}


def group_title(title: str) -> str:
    """CV group headings in the site's sentence case."""
    if not title:
        return ""
    key = title.strip().lower()
    return GROUP_TITLES.get(key, key[:1].upper() + key[1:])


_A_TAG = re.compile(r"<a\b([^>]*)>")


def mark_external(html: str, own_host: str) -> str:
    """Make links to other sites open in a new tab (target=_blank, rel=noopener)."""
    def fix(m):
        attrs = m.group(1)
        href = re.search(r'href="(https?://[^"]+)"', attrs)
        if not href or urllib.parse.urlparse(href.group(1)).hostname == own_host or "target=" in attrs:
            return m.group(0)
        rel = re.search(r'rel="([^"]*)"', attrs)
        if rel:
            vals = rel.group(1).split()
            vals += [v for v in ("noopener",) if v not in vals]
            attrs = attrs.replace(rel.group(0), f'rel="{" ".join(vals)}"')
        else:
            attrs += ' rel="noopener"'
        return f'<a{attrs} target="_blank">'
    return _A_TAG.sub(fix, html)


def write(out_dir: Path, rel: str, text: str) -> None:
    path = out_dir / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def render_markdown(text: str) -> Markup:
    return Markup(md.markdown(text or "", extensions=["extra", "smarty"],
                              extension_configs={"smarty": {"smart_dashes": False}}))
