"""Load generated CV data and hand-edited content, merge sidecars, validate."""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from pathlib import Path

import yaml

CV_SECTIONS = ("education", "honors", "service", "talks", "teaching", "memberships")


class ContentError(Exception):
    """Content that would produce a broken page."""


@dataclass
class Content:
    site: dict
    profile: dict
    research: list[dict]
    pubs: list[dict]
    pubs_by_key: dict
    cv: dict
    posts: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _yaml(path: Path, default):
    if not path.exists():
        return default
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return default if data is None else data


def _apply_pub_extras(pubs: list[dict], extras: dict, warnings: list[str]) -> None:
    by_key = {p["key"]: p for p in pubs}
    for key, fields in extras.items():
        if key not in by_key:
            warnings.append(f"pub_extras.yml: unknown key '{key}'")
            continue
        by_key[key].update(fields or {})


def _apply_item_overrides(section: dict, overrides: dict, name: str, warnings: list[str]) -> None:
    found: set[str] = set()

    def walk(items: list[dict]) -> list[dict]:
        kept = []
        for it in items:
            ov = overrides.get(it["key"])
            if ov is not None:
                found.add(it["key"])
                if ov.get("hide"):
                    continue
                if "html" in ov:
                    it["html"] = ov["html"]
            it["children"] = walk(it.get("children", []))
            kept.append(it)
        return kept

    for g in section["groups"]:
        g["items"] = walk(g["items"])
    added = [{"key": a["key"], "label": None, "html": a["html"], "text": a.get("text", ""), "children": []}
             for a in overrides.get("_add", []) or []]
    if added:
        if not section["groups"]:
            section["groups"].append({"title": None, "items": []})
        section["groups"][-1]["items"].extend(added)
    section["groups"] = [g for g in section["groups"] if g["items"]]
    for key in overrides:
        if key != "_add" and key not in found:
            warnings.append(f"cv_overrides.yml: unknown key '{key}' in {name}")


def _apply_cv_overrides(cv: dict, overrides: dict, warnings: list[str]) -> None:
    exp_ov = overrides.get("experience", {}) or {}
    keys = {e["key"] for e in cv.get("experience", [])}
    kept = []
    for e in cv.get("experience", []):
        ov = exp_ov.get(e["key"], {}) or {}
        if ov.get("hide"):
            continue
        if "bullets" in ov:
            e["bullets"] = ov["bullets"]
        kept.append(e)
    cv["experience"] = kept
    for key in exp_ov:
        if key not in keys:
            warnings.append(f"cv_overrides.yml: unknown key '{key}' in experience")
    for name in CV_SECTIONS:
        if name in cv:
            _apply_item_overrides(cv[name], overrides.get(name, {}) or {}, name, warnings)
    for name in overrides:
        if name != "experience" and name not in CV_SECTIONS:
            warnings.append(f"cv_overrides.yml: unknown section '{name}'")


def _resolve_research(research: list[dict], by_key: dict) -> None:
    for theme in research:
        items = []
        for key in theme.get("pubs", []) or []:
            if key not in by_key:
                raise ContentError(f"research.yml: theme '{theme.get('id')}' references unknown key '{key}'")
            items.append(by_key[key])
        theme["items"] = items


def load_content(root: Path, include_drafts: bool = False) -> Content:
    c = Path(root) / "content"
    warnings: list[str] = []
    pubs = json.loads((c / "generated" / "publications.json").read_text(encoding="utf-8"))
    cv = json.loads((c / "generated" / "cv.json").read_text(encoding="utf-8"))
    _apply_pub_extras(pubs, _yaml(c / "pub_extras.yml", {}), warnings)
    _apply_cv_overrides(cv, _yaml(c / "cv_overrides.yml", {}), warnings)
    by_key = {p["key"]: p for p in pubs}
    research = copy.deepcopy(_yaml(c / "research.yml", []))
    _resolve_research(research, by_key)
    from sitegen.writing import load_posts  # local import: writing depends on data

    posts = load_posts(c / "writing", include_drafts)
    return Content(
        site=_yaml(c / "site.yml", {}),
        profile=_yaml(c / "profile.yml", {}),
        research=research,
        pubs=pubs,
        pubs_by_key=by_key,
        cv=cv,
        posts=posts,
        warnings=warnings,
    )
