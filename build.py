"""Build the static site into _site/ (or --out)."""
from __future__ import annotations

import argparse
import datetime as dt
import shutil
import sys
from pathlib import Path

from sitegen.data import load_content
from sitegen.render import copy_static, make_env, write
from sitegen.writing import atom_feed

ROOT = Path(__file__).resolve().parent

NAV = [("Research", "/research/", "research"), ("Publications", "/publications/", "publications"), ("CV", "/cv/", "cv")]

# (output path, template, page id)
PAGES = [
    ("index.html", "home.html.j2", "home"),
    ("research/index.html", "research.html.j2", "research"),
    ("publications/index.html", "publications.html.j2", "publications"),
    ("cv/index.html", "cv.html.j2", "cv"),
    ("404.html", "404.html.j2", "404"),
]


def build_site(out_dir: Path, include_drafts: bool = False, root: Path = ROOT) -> None:
    out_dir = Path(out_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    content = load_content(root, include_drafts=include_drafts)
    for w in content.warnings:
        print("warning:", w, file=sys.stderr)
    env = make_env(root / "templates", content.site)
    nav = list(NAV)
    if content.posts:
        nav.append(("Writing", "/writing/", "writing"))
    ctx = {"content": content, "profile": content.profile, "nav": nav, "build_date": dt.date.today()}
    paths = []
    for rel, tpl, pid in PAGES:
        path = "/" + rel.removesuffix("index.html")
        write(out_dir, rel, env.get_template(tpl).render(page_id=pid, page_path=path, **ctx))
        if pid != "404":
            paths.append(path)
    if content.posts:
        write(out_dir, "writing/index.html",
              env.get_template("writing_index.html.j2").render(page_id="writing", page_path="/writing/", **ctx))
        paths.append("/writing/")
        for post in content.posts:
            path = f"/writing/{post['slug']}/"
            write(out_dir, path.lstrip("/") + "index.html",
                  env.get_template("post.html.j2").render(page_id="writing", page_path=path, post=post, **ctx))
            paths.append(path)
        write(out_dir, "writing/feed.xml", atom_feed(content.posts, content.site))
    site_base = content.site["url"].rstrip("/") + (content.site.get("base_path") or "")
    write(out_dir, "sitemap.xml", sitemap(site_base, paths))
    write(out_dir, "robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {site_base}/sitemap.xml\n")
    if content.site.get("cname"):
        write(out_dir, "CNAME", content.site["cname"].strip() + "\n")
    copy_static(root / "static", out_dir)


def sitemap(site_base: str, paths: list[str]) -> str:
    urls = "".join(f"  <url><loc>{site_base}{p}</loc></url>\n" for p in paths)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(ROOT / "_site"))
    ap.add_argument("--drafts", action="store_true")
    args = ap.parse_args()
    build_site(Path(args.out), include_drafts=args.drafts)
    print(f"built {args.out}")


if __name__ == "__main__":
    main()
