"""Jinja environment and static-file helpers."""
from __future__ import annotations

import shutil
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


def write(out_dir: Path, rel: str, text: str) -> None:
    path = out_dir / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def render_markdown(text: str) -> Markup:
    return Markup(md.markdown(text or "", extensions=["extra", "smarty"],
                              extension_configs={"smarty": {"smart_dashes": False}}))
