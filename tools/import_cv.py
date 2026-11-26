"""Import the PUBLIC CV (.tex section files) into content/generated/*.json.

Usage:
  python tools/import_cv.py --cv-dir DIR --pdf DIR/IndranilRoychoudhury_CV.pdf

Never point this at the *_CV_SLB files. Every imported entry is checked
against the text of the public PDF; the run fails if anything is missing.
"""
from __future__ import annotations

import argparse
import html
import re
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sitegen.cvparse import extract_publications, parse_experience, parse_section, verify_against_pdf  # noqa: E402

SECTIONS = {
    "education": "education.tex",
    "honors": "honors.tex",
    "service": "prof-service.tex",
    "talks": "talks.tex",
    "teaching": "teaching.tex",
    "memberships": "professionalmembership.tex",
}
DROP_GROUPS = {"technical talks at slb"}


def _texts(obj):
    if isinstance(obj, dict):
        if "text" in obj:
            yield obj["text"]
        for k, v in obj.items():
            if k != "text":
                yield from _texts(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _texts(v)


def parse_all(cv_dir: Path) -> tuple[dict, list[dict]]:
    def read(name):
        return (cv_dir / name).read_text(encoding="utf-8")

    cv = {"experience": parse_experience(read("experience.tex"))}
    for key, fname in SECTIONS.items():
        sec = parse_section(read(fname))
        sec["groups"] = [g for g in sec["groups"] if (g["title"] or "").lower() not in DROP_GROUPS]
        cv[key] = sec
    pubs = extract_publications(parse_section(read("publications.tex")), parse_section(read("patents.tex")))
    return cv, pubs


def collect_checks(cv: dict, pubs: list[dict]) -> list[str]:
    """Every string that will reach the site, as plain text."""
    checks = list(_texts({k: v for k, v in cv.items() if k != "experience"}))
    checks += [g["title"] for k, v in cv.items() if k != "experience" for g in v["groups"] if g["title"]]
    for e in cv["experience"]:
        checks += [e["org"], e["role"], e["location"], e["dates"], *e["bullets"]]
    checks += [p["text"] for p in pubs]
    return [c for c in (html.unescape(re.sub(r"<[^>]+>", "", x)).strip() for x in checks) if c]


def run_import(cv_dir: Path, pdf_text: str, out: Path) -> list[str]:
    """Parse, verify against the PDF text, and write JSON only if everything verifies."""
    cv, pubs = parse_all(cv_dir)
    missing = verify_against_pdf(collect_checks(cv, pubs), pdf_text)
    if missing:
        return missing
    out.mkdir(parents=True, exist_ok=True)
    (out / "publications.json").write_text(json.dumps(pubs, indent=1, ensure_ascii=False) + "\n")
    (out / "cv.json").write_text(json.dumps(cv, indent=1, ensure_ascii=False) + "\n")
    counts: dict[str, int] = {}
    for p in pubs:
        counts[p["type"]] = counts.get(p["type"], 0) + 1
    print(f"publications: {len(pubs)} {counts}")
    print(f"experience entries: {len(cv['experience'])}")
    return []


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cv-dir", required=True, type=Path)
    ap.add_argument("--pdf", required=True, type=Path)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[1] / "content" / "generated")
    a = ap.parse_args(argv)
    if "SLB" in a.pdf.name:
        print("Refusing: use the public CV PDF, not the SLB version.", file=sys.stderr)
        return 2
    pdf_text = subprocess.run(["pdftotext", "-layout", str(a.pdf), "-"], capture_output=True,
                              text=True, check=True).stdout
    missing = run_import(a.cv_dir, pdf_text, a.out)
    if missing:
        print(f"{len(missing)} entries not found in the public PDF; nothing written:", file=sys.stderr)
        for m in missing:
            print("  -", m[:140], file=sys.stderr)
        return 1
    print("all entries verified against the public PDF")
    return 0


if __name__ == "__main__":
    sys.exit(main())
