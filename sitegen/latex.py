"""Small, purpose-built LaTeX helpers for the CV section files.

Not a general LaTeX parser: it handles exactly the constructs the CV uses.
"""
from __future__ import annotations

import html
import re
import unicodedata

# ---------------------------------------------------------------- braces


def find_braced(s: str, start: int) -> tuple[str, int]:
    """Return (argument, index after closing brace) for the group at s[start] == '{'."""
    if start >= len(s) or s[start] != "{":
        raise ValueError(f"expected '{{' at {start}")
    depth = 0
    i = start
    while i < len(s):
        c = s[i]
        if c == "\\":
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[start + 1 : i], i + 1
        i += 1
    raise ValueError("unbalanced braces")


def _skip_ws(s: str, i: int) -> int:
    while i < len(s) and s[i] in " \t\n":
        i += 1
    return i


def _replace_command(s: str, name: str, fn, nargs: int = 1) -> str:
    """Replace every \\name{a1}..{an} with fn(*args). Matches whole command names only."""
    pat = re.compile(r"\\" + name + r"(?![A-Za-z])\s*")
    out = []
    pos = 0
    while True:
        m = pat.search(s, pos)
        if not m:
            out.append(s[pos:])
            return "".join(out)
        j = m.end()
        args = []
        ok = True
        for _ in range(nargs):
            j = _skip_ws(s, j)
            if j < len(s) and s[j] == "{":
                a, j = find_braced(s, j)
                args.append(a)
            else:
                ok = False
                break
        if not ok:
            out.append(s[pos : m.end()])
            pos = m.end()
            continue
        out.append(s[pos : m.start()])
        out.append(fn(*args))
        pos = j


# ---------------------------------------------------------------- internal

_COMMENT = re.compile(r"(?<!\\)%[^\n]*")
_BLOCK = re.compile(r"\\begin\{internalblock\}.*?\\end\{internalblock\}", re.S)
_IFCV = re.compile(r"\\ifinternalcv\b(.*?)(?:\\else\b(.*?))?\\fi\b", re.S)
_LEGACY = re.compile(r"\\internal(?:new)?(?:on|off)(?![A-Za-z])")


def strip_internal(tex: str) -> str:
    """Remove comments and every SLB-internal marker exactly as the public CV build does."""
    tex = _COMMENT.sub("", tex)
    tex = _BLOCK.sub("", tex)
    tex = _replace_command(tex, "internalnew", lambda a: "")
    tex = _replace_command(tex, "internalclear", lambda a: a)
    tex = _replace_command(tex, "internal", lambda a: "")
    tex = _IFCV.sub(lambda m: m.group(2) or "", tex)
    tex = _LEGACY.sub("", tex)
    return tex


# ---------------------------------------------------------------- conversion

_ACCENTS = {
    '"': "\u0308", "'": "\u0301", "`": "\u0300", "~": "\u0303", "^": "\u0302", "c": "\u0327",
}
_ACCENT_RE = re.compile(r"""\\(["'`~^]|c(?=[{ ]))\s*(?:\{(\w)\}|(\w))""")
_ESCAPES = {r"\&": "&", r"\%": "%", r"\$": "$", r"\_": "_", r"\#": "#", r"\{": "{", r"\}": "}"}
_DROP_WITH_ARG = ("vspace", "hspace", "needspace", "label")
_DROP_BARE = re.compile(
    r"\\(hfill|noindent|newline|par|Large|large|small|footnotesize|normalsize|centering|bullet)(?![A-Za-z])\s*"
)

# Placeholders keep generated tags safe from html.escape and from brace stripping.
_TAG_OPEN, _TAG_CLOSE = "\x01", "\x02"


def latex_to_html(tex: str) -> str:
    tags: list[str] = []

    def _tag(t: str) -> str:
        tags.append("<" + t + ">")
        return f"{_TAG_OPEN}{len(tags) - 1}{_TAG_CLOSE}"

    s = tex
    s = re.sub(r"\$\\vert\$", "|", s)
    s = _ACCENT_RE.sub(lambda m: unicodedata.normalize(
        "NFC", (m.group(2) or m.group(3)) + _ACCENTS[m.group(1)]), s)
    for name in _DROP_WITH_ARG:
        s = _replace_command(s, name, lambda a: "")
    s = _DROP_BARE.sub("", s)
    s = re.sub(r"\\\\(\[[^\]]*\])?", " ", s)

    def link(url, text):
        return _tag(f'a href="{html.escape(url, quote=True)}"') + text + _tag("/a")

    s = _replace_command(s, "href", link, nargs=2)
    s = _replace_command(s, "url", lambda u: link(u, html.escape(u)))
    for name, t in (("textbf", "strong"), ("emph", "em"), ("textit", "em")):
        s = _replace_command(s, name, lambda a, t=t: _tag(t) + a + _tag("/" + t))
    for name in ("textsc", "Large", "large", "small", "mbox", "text"):
        s = _replace_command(s, name, lambda a: a)

    # Escaped specials -> private placeholders, so later steps leave them alone.
    holders = {}
    for k, v in _ESCAPES.items():
        ph = f"\x03{len(holders)}\x03"
        holders[ph] = v
        s = s.replace(k, ph)

    s = s.replace("``", "“").replace("''", "”")
    s = s.replace("`", "‘").replace("'", "’")
    s = s.replace("---", "–").replace("--", "–")
    s = s.replace("~", "\u00a0")
    s = re.sub(r"\\[A-Za-z]+\*?", "", s)  # any leftover command word
    s = s.replace("{", "").replace("}", "").replace("\\", "")

    for ph, v in holders.items():
        s = s.replace(ph, v)
    # Escape text, then restore tags (whose attribute values were escaped already).
    s = html.escape(s, quote=False)
    s = re.sub(f"{_TAG_OPEN}(\\d+){_TAG_CLOSE}", lambda m: tags[int(m.group(1))], s)
    s = re.sub(r"[ \t\n]+", " ", s).strip()
    s = re.sub(r" ([,.;:])", r"\1", s)
    return s


def latex_to_text(tex: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", latex_to_html(tex)))
