"""Markdown posts and the Atom feed."""
from __future__ import annotations

import datetime as dt
from pathlib import Path
from xml.sax.saxutils import escape

import yaml

from sitegen.data import ContentError
from sitegen.render import render_markdown


def load_posts(directory: Path, include_drafts: bool) -> list[dict]:
    posts = []
    if not directory.exists():
        return posts
    for path in sorted(directory.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        raw = path.read_text(encoding="utf-8")
        if not raw.startswith("---"):
            raise ContentError(f"{path.name}: missing front matter")
        _, front, body = raw.split("---", 2)
        meta = yaml.safe_load(front) or {}
        for key in ("title", "date"):
            if not meta.get(key):
                raise ContentError(f"{path.name}: front matter needs '{key}'")
        if meta.get("draft") and not include_drafts:
            continue
        date = meta["date"]
        if isinstance(date, str):
            date = dt.date.fromisoformat(date)
        posts.append({
            "slug": path.stem,
            "title": str(meta["title"]),
            "date": date,
            "summary": str(meta.get("summary", "")),
            "draft": bool(meta.get("draft")),
            "html": render_markdown(body.strip()),
        })
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def atom_feed(posts: list[dict], site: dict) -> str:
    base = site["url"].rstrip("/") + (site.get("base_path") or "")
    updated = max(p["date"] for p in posts).isoformat() + "T00:00:00Z"
    out = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<feed xmlns="http://www.w3.org/2005/Atom">',
        f"<title>{escape(site['title'])}: Writing</title>",
        f'<link href="{base}/writing/"/>',
        f'<link rel="self" href="{base}/writing/feed.xml"/>',
        f"<id>{base}/writing/</id>",
        f"<updated>{updated}</updated>",
        f"<author><name>{escape(site['title'])}</name></author>",
    ]
    for p in posts:
        url = f"{base}/writing/{p['slug']}/"
        out += [
            "<entry>",
            f"<title>{escape(p['title'])}</title>",
            f'<link href="{url}"/>',
            f"<id>{url}</id>",
            f"<updated>{p['date'].isoformat()}T00:00:00Z</updated>",
            f"<summary>{escape(p['summary'])}</summary>",
            f'<content type="html">{escape(str(p["html"]))}</content>',
            "</entry>",
        ]
    out.append("</feed>")
    return "\n".join(out) + "\n"
