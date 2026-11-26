import re

from sitegen.latex import find_braced, latex_to_html, latex_to_text, strip_internal


def squash(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def test_find_braced_nested():
    s = r"\x{a{b}c\{d}rest"
    arg, end = find_braced(s, 2)
    assert arg == r"a{b}c\{d"
    assert s[end:] == "rest"


def test_strip_internal_inline():
    assert squash(strip_internal(r"A.\internal{ secret IDF-1.} B.")) == "A. B."


def test_strip_internal_nested_braces():
    tex = r"x\internal{ see \href{https://eureka.slb.com}{\textbf{y}} } z"
    assert squash(strip_internal(tex)) == "x z"


def test_strip_internalnew():
    assert squash(strip_internal(r"a\internalnew{ in Springfield} b")) == "a b"


def test_strip_internalblock():
    tex = "keep1\n\\begin{internalblock}\nsecret\n\\end{internalblock}\nkeep2"
    out = strip_internal(tex)
    assert "secret" not in out
    assert "keep1" in out and "keep2" in out


def test_ifinternalcv_else():
    tex = r"Patents and \ifinternalcv Invention Disclosures\else Patent Applications\fi"
    assert squash(strip_internal(tex)) == "Patents and Patent Applications"


def test_ifinternalcv_without_else():
    assert squash(strip_internal(r"a \ifinternalcv secret\fi b")) == "a b"


def test_internalclear_kept():
    assert strip_internal(r"\internalclear{kept}") == "kept"


def test_legacy_markers_removed():
    assert squash(strip_internal(r"\internalon a \internaloff")) == "a"


def test_comment_removed_but_escaped_percent_kept():
    assert strip_internal("95\\% ok % hidden") == "95\\% ok "


def test_latex_to_html_basic():
    tex = r"``Title,'' \emph{SPE Journal}, 1350--1360"
    assert latex_to_html(tex) == "“Title,” <em>SPE Journal</em>, 1350–1360"


def test_latex_to_html_bold_and_link():
    tex = r"\textbf{I. Roychoudhury} and \href{https://x.org/a?b=1&c=2}{\textbf{12,136,267}}"
    out = latex_to_html(tex)
    assert out == ('<strong>I. Roychoudhury</strong> and '
                   '<a href="https://x.org/a?b=1&amp;c=2"><strong>12,136,267</strong></a>')


def test_latex_to_html_escapes_text():
    assert latex_to_html(r"A < B \& C") == "A &lt; B &amp; C"


def test_no_latex_residue():
    tex = (r"\textsc{\textbf{Group}} G\"{o}bel, P\'erez, \c{c}a, Ni\~no, \`a ``q'' `s' "
           r"1--2 a---b x~y \& 5\% \_ \# $\vert$ \hfill \\ \vspace{3pt} \needspace{5\baselineskip}"
           r" \Large{Big} \emph{e} \textit{i} \url{https://a.b}")
    out = latex_to_html(tex)
    for bad in ("\\", "{", "}", "—", "$"):
        assert bad not in out, (bad, out)
    assert "Göbel" in out and "Pérez" in out and "ça" in out and "Niño" in out


def test_latex_to_text_strips_tags():
    assert latex_to_text(r"\textbf{A} \emph{B}") == "A B"
