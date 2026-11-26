"""Parse the public CV's LaTeX section files into plain data."""
from __future__ import annotations

import re
import unicodedata

from sitegen.latex import find_braced, latex_to_html, latex_to_text, strip_internal

_ENV = r"(?:list|itemize|enumerate)"
_BEGIN_RE = re.compile(r"\\begin\{" + _ENV + r"\}")
_ANY_RE = re.compile(r"\\(begin|end)\{" + _ENV + r"\}")
_TOKEN = re.compile(
    r"\\(?:begin|end)\{" + _ENV + r"\}"
    r"|\\bibitem\s*(?:\[(?P<label>[^\]]*)\])?\s*\{(?P<key>[^}]*)\}"
    r"|\\item(?![A-Za-z])"
)

PUB_TYPES = {
    "book": "book",
    "book chapters": "chapter",
    "journal papers": "journal",
    "conference papers": "conference",
    "technical reports": "report",
    "whitepapers": "whitepaper",
    "theses": "thesis",
    "granted u.s. patents": "patent",
    "published patent applications": "patent",
}


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


# ---------------------------------------------------------------- list structure


def _list_body(s: str, begin_at: int) -> tuple[str, int]:
    """Given s[begin_at:] starting with \\begin{list}, return (body, index after \\end{list})."""
    m0 = _BEGIN_RE.match(s, begin_at)
    j = m0.end()
    for _ in range(2 if "{list}" in m0.group(0) else 0):  # \begin{list}{label}{settings}
        while j < len(s) and s[j] in " \t\n":
            j += 1
        if j < len(s) and s[j] == "{":
            _, j = find_braced(s, j)
    depth = 1
    k = j
    for m in _ANY_RE.finditer(s, j):
        depth += 1 if m.group(1) == "begin" else -1
        if depth == 0:
            return s[j : m.start()], m.end()
    raise ValueError("unterminated list")


def _top_level_lists(s: str) -> list[tuple[int, int, str]]:
    """Return (start, end, body) for each list at nesting depth 0 in s."""
    out = []
    pos = 0
    while True:
        m = _BEGIN_RE.search(s, pos)
        if not m:
            return out
        i = m.start()
        body, end = _list_body(s, i)
        out.append((i, end, body))
        pos = end


def _split_items(body: str) -> list[dict]:
    """Split a list body into raw items at depth 0: {label, key, tex}."""
    items: list[dict] = []
    depth = 0
    cur = None
    for m in _TOKEN.finditer(body):
        tok = m.group(0)
        if tok.startswith("\\begin"):
            depth += 1
            continue
        if tok.startswith("\\end"):
            depth -= 1
            continue
        if depth:
            continue
        if cur is not None:
            cur["tex"] = body[cur["start"] : m.start()]
            items.append(cur)
        cur = {"label": m.group("label"), "key": m.group("key"), "start": m.end()}
    if cur is not None:
        cur["tex"] = body[cur["start"] :]
        items.append(cur)
    return items


class _Keys:
    def __init__(self):
        self.seen: set[str] = set()

    def make(self, base: str) -> str:
        key = base or "item"
        n = 2
        while key in self.seen:
            key = f"{base}-{n}"
            n += 1
        self.seen.add(key)
        return key


def _build_item(raw: dict, keys: _Keys) -> dict:
    tex = raw["tex"]
    lists = _top_level_lists(tex)
    head = tex[: lists[0][0]] if lists else tex
    children = []
    for _, _, body in lists:
        children.extend(_build_item(r, keys) for r in _split_items(body))
    text = latex_to_text(head)
    return {
        "key": keys.make(raw["key"] or slugify(text[:60])),
        "label": raw["label"],
        "html": latex_to_html(head),
        "text": text,
        "children": children,
        "_tex": head,
    }


def _strip_private(obj):
    if isinstance(obj, dict):
        return {k: _strip_private(v) for k, v in obj.items() if not k.startswith("_")}
    if isinstance(obj, list):
        return [_strip_private(v) for v in obj]
    return obj


def _section_title(tex: str) -> tuple[str, int]:
    m = re.search(r"\\textsc\s*\{", tex)
    if not m:
        return "", 0
    arg, end = find_braced(tex, m.end() - 1)
    return latex_to_text(arg), end


_GROUP_HEAD = re.compile(r"\\textsc\s*\{|\\textbf\s*\{\s*\\textsc\s*\{")


def _parse_raw_section(tex: str) -> dict:
    tex = strip_internal(tex)
    title, after = _section_title(tex)
    rest = tex[after:]
    lists = _top_level_lists(rest)
    intro_tex = rest[: lists[0][0]] if lists else rest
    intro_tex = re.sub(r"\\hrule", "", intro_tex)
    keys = _Keys()
    groups: list[dict] = []
    loose: list[dict] = []
    for _, _, body in lists:
        for raw in _split_items(body):
            head = raw["tex"].lstrip()
            hm = _GROUP_HEAD.match(head)
            if hm:
                gtitle_tex, _ = find_braced(head, hm.end() - 1)
                item = _build_item({**raw, "tex": head}, keys)
                groups.append({"title": latex_to_text(gtitle_tex), "items": item["children"]})
            else:
                loose.append(_build_item(raw, keys))
    if loose:
        groups.insert(0, {"title": None, "items": loose})
    return {"title": title, "intro_html": latex_to_html(intro_tex), "groups": groups}


def parse_section(tex: str) -> dict:
    return _strip_private(_parse_raw_section(tex))


# ---------------------------------------------------------------- experience


def parse_experience(tex: str) -> list[dict]:
    sec = _parse_raw_section(tex)
    keys = _Keys()
    out = []
    for item in (i for g in sec["groups"] for i in g["items"]):
        head = item["_tex"]
        line1, _, role_tex = head.partition("\\\\")
        line1 = line1.replace("\\hfill", " ||| ")
        left, _, dates = latex_to_text(line1).partition("|||")
        parts = [p.strip() for p in left.split(",") if p.strip()]
        out.append({
            "key": keys.make(slugify(f"{parts[0]} {dates}")),
            "org": ", ".join(parts[:-3]),
            "location": ", ".join(parts[-3:]),
            "dates": dates.strip(),
            "role": latex_to_text(role_tex).strip(),
            "bullets": [c["html"] for c in item["children"]],
        })
    return out


# ---------------------------------------------------------------- publications

_AWARD = re.compile(r"\s*\(([^()]*Best [^()]*Award[^()]*)\)")
_YEAR = re.compile(r"\b(19\d\d|20\d\d)\b")
_HREF = re.compile(r"\\href\s*\{([^}]*)\}")


def _patent_key(text: str) -> str | None:
    m = re.search(r"Patent No\.\s*([\d,]{6,})", text)
    if m:
        return "US" + re.sub(r"\D", "", m.group(1))
    m = re.search(r"Publication No\.\s*(US\s*\d{4}/\d+)", text)
    if m:
        return re.sub(r"[^A-Z0-9]", "", m.group(1))
    m = re.search(r"Application No\.\s*(EP[\s\d]+?)\s*A\d", text)
    if m:
        return re.sub(r"[^A-Z0-9]", "", m.group(1))
    return None


def extract_publications(pubs_section: dict, patents_section: dict) -> list[dict]:
    out = []
    seen = _Keys()
    for sec in (pubs_section, patents_section):
        for g in sec["groups"]:
            ptype = PUB_TYPES.get((g["title"] or "").lower())
            if ptype is None:
                continue
            for it in g["items"]:
                html, text = it["html"], it["text"]
                award = None
                m = _AWARD.search(html)
                if m:
                    award = m.group(1).strip()
                    html = _AWARD.sub("", html, count=1).strip()
                    text = _AWARD.sub("", text, count=1).strip()
                years = _YEAR.findall(text)
                tm = re.search(r"“(.+?)”", text)
                title = tm.group(1).rstrip(",").strip() if tm else text[:120]
                um = re.search(r'href="([^"]+)"', html)
                key = it["key"]
                if ptype == "patent":
                    key = _patent_key(text) or key
                out.append({
                    "key": seen.make(key),
                    "label": it["label"],
                    "type": ptype,
                    "year": int(years[-1]) if years else None,
                    "title": title,
                    "html": html,
                    "text": text,
                    "url": um.group(1).replace("&amp;", "&") if um else None,
                    "award": award,
                })
    return out


# ---------------------------------------------------------------- verification


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).lower()
    return re.sub(r"[^a-z0-9]", "", s)


def verify_against_pdf(items: list[str], pdf_text: str) -> list[str]:
    hay = _norm(pdf_text)
    return [it for it in items if _norm(it)[:50] not in hay]
