"""Build the static site into _site/ (or --out)."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import yaml

from sitegen.render import copy_static, make_env, write

ROOT = Path(__file__).resolve().parent


def build_site(out_dir: Path, include_drafts: bool = False) -> None:
    out_dir = Path(out_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    site = yaml.safe_load((ROOT / "content" / "site.yml").read_text())
    env = make_env(ROOT / "templates", site)
    write(out_dir, "index.html", env.get_template("base.html.j2").render())
    copy_static(ROOT / "static", out_dir)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(ROOT / "_site"))
    ap.add_argument("--drafts", action="store_true")
    args = ap.parse_args()
    build_site(Path(args.out), include_drafts=args.drafts)


if __name__ == "__main__":
    main()
