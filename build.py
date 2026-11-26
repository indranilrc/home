"""Build the static site into _site/ (or --out)."""
from __future__ import annotations

import argparse
import datetime as dt
import shutil
import sys
from pathlib import Path

from sitegen.data import load_content
from sitegen.render import copy_static, make_env, write

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
    content = load_content(root)
    for w in content.warnings:
        print("warning:", w, file=sys.stderr)
    env = make_env(root / "templates", content.site)
    nav = list(NAV)
    if content.posts:
        nav.append(("Writing", "/writing/", "writing"))
    ctx = {"content": content, "profile": content.profile, "nav": nav, "build_date": dt.date.today()}
    for rel, tpl, pid in PAGES:
        write(out_dir, rel, env.get_template(tpl).render(page_id=pid, **ctx))
    copy_static(root / "static", out_dir)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(ROOT / "_site"))
    ap.add_argument("--drafts", action="store_true")
    args = ap.parse_args()
    build_site(Path(args.out), include_drafts=args.drafts)
    print(f"built {args.out}")


if __name__ == "__main__":
    main()
