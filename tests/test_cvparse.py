import json
from pathlib import Path

import pytest

from tests.hygiene import denylisted

from sitegen.cvparse import (
    extract_publications,
    parse_experience,
    parse_section,
    verify_against_pdf,
)

FIX = Path(__file__).parent / "fixtures"
ROOT = Path(__file__).resolve().parents[1]


def load(name: str) -> str:
    return (FIX / name).read_text()


def all_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from all_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from all_strings(v)


@pytest.fixture
def pubs():
    return extract_publications(parse_section(load("publications.tex")),
                                parse_section(load("patents.tex")))


def test_parse_section_titles_and_groups():
    sec = parse_section(load("publications.tex"))
    assert sec["title"] == "Publications"
    assert [g["title"] for g in sec["groups"]] == ["Book", "Journal Papers", "Conference Papers", "Theses", "Whitepapers"]
    assert sec["groups"][4]["items"] == []
    assert [i["key"] for i in sec["groups"][3]["items"]] == ["Dissertation"]


def test_parse_publications_fixture(pubs):
    by = {p["key"]: p for p in pubs}
    assert by["PROG-Book"]["type"] == "book"
    assert by["PROG-Book"]["label"] == "B1"
    assert by["SPEJ-24"]["type"] == "journal"
    assert by["SPEJ-24"]["year"] == 2024
    assert by["SPEJ-24"]["title"] == ("Real-Time Gamma Ray Log Generation from Drilling Parameters "
                                      "of Offset Wells Using Physics-Informed Machine Learning")
    assert by["JAS-15"]["label"] == "J7"
    assert "<strong>I. Roychoudhury</strong>" in by["SPEJ-24"]["html"]


def test_patent_keys_and_urls(pubs):
    by = {p["key"]: p for p in pubs}
    assert by["US12608592"]["type"] == "patent"
    assert by["US12608592"]["url"] == "https://patents.google.com/patent/US12608592B2/en"
    assert by["US12608592"]["year"] == 2026
    assert by["US20250315037"]["url"] is None
    assert "EP4630852" in by


def test_award_tag_extracted(pubs):
    p = {p["key"]: p for p in pubs}["PHM-11-c"]
    assert p["award"] == "Nominated for Best Paper Award"
    assert "Nominated" not in p["html"]
    assert "Total Citations" not in p["html"]


def test_internal_dropped_in_parse(pubs):
    patents = parse_section(load("patents.tex"))
    for s in list(all_strings(pubs)) + list(all_strings(patents)):
        assert "IDF" not in s and "eureka" not in s and "99 example" not in s
    assert patents["title"] == "Patents and Patent Applications"
    assert patents["intro_html"] == "Named inventor on 12 patents."


def test_parse_experience_fixture():
    exp = parse_experience(load("experience.tex"))
    assert len(exp) == 2
    slb = exp[0]
    assert slb["org"] == "SLB Software Technology Innovation Center"
    assert slb["location"] == "Menlo Park, California, USA"
    assert slb["dates"] == "October 2018 – Present"
    assert slb["role"] == "Principal AI Scientist"
    assert slb["bullets"] == ["Lead PHM research.", "Second bullet."]
    mct = exp[1]
    assert mct["org"] == "Mission Critical Technologies, Inc., NASA Ames Research Center"
    assert mct["dates"] == "Summer 2007"
    assert mct["role"] == "Intern, Intelligent Systems Division (Code TI)"
    assert slb["key"] != mct["key"]


def test_flat_section_and_keys_unique():
    edu = parse_section(load("education.tex"))
    assert edu["title"] == "Education"
    assert len(edu["groups"]) == 1 and edu["groups"][0]["title"] is None
    items = edu["groups"][0]["items"]
    assert len(items) == 2
    assert "GPA" not in items[0]["html"]
    assert "Dissertation:" in items[0]["text"]
    honors = parse_section(load("honors.tex"))
    keys = [i["key"] for g in honors["groups"] for i in g["items"]]
    assert len(keys) == len(set(keys)) == 3
    assert [g["title"] for g in honors["groups"]] == ["Individual Awards", "Other Service"]


def test_verify_against_pdf():
    pdf = "…alpha  beta\ngam-\nma “quoted” text – dash…"
    assert verify_against_pdf(["Alpha beta gamma", "Missing item", '"quoted" text - dash'], pdf) == ["Missing item"]


GEN = ROOT / "content" / "generated"
FORBIDDEN = ["idf-", "eureka.slb", "sharepoint", "stic.slb.com", "degreed"]


@pytest.mark.skipif(not (GEN / "publications.json").exists(), reason="no generated data yet")
def test_real_cv_has_no_residue():
    for name in ("publications.json", "cv.json"):
        data = json.loads((GEN / name).read_text())
        for s in all_strings(data):
            for bad in ("\\", "{", "}", "—"):
                assert bad not in s, (name, bad, s[:120])
            low = s.lower()
            for bad in FORBIDDEN:
                assert bad not in low, (name, bad, s[:120])
            assert "internal" not in low.replace("international", ""), (name, s[:120])
            assert not denylisted(s), name


def test_verify_checks_whole_string():
    head = "A" * 60
    assert verify_against_pdf([head + " secret tail"], head + " public tail") == [head + " secret tail"]


def _cv_dir(tmp_path):
    d = tmp_path / "cv"
    d.mkdir()
    for name in ("publications.tex", "patents.tex", "experience.tex", "honors.tex", "education.tex"):
        (d / name).write_text(load(name))
    for name, title in (("prof-service.tex", "Professional Service"), ("talks.tex", "Talks"),
                        ("teaching.tex", "Teaching"), ("professionalmembership.tex", "Professional Memberships")):
        (d / name).write_text(f"\\textsc{{\\Large{{{title}}}}}\n\\begin{{list}}{{}}{{}}\n\\item Example entry for {title}.\n\\end{{list}}\n")
    return d


def test_import_writes_nothing_when_verification_fails(tmp_path):
    from tools.import_cv import run_import
    out = tmp_path / "gen"
    missing = run_import(_cv_dir(tmp_path), "nothing matches here", out)
    assert missing
    assert not out.exists()


def test_import_checks_experience_fields(tmp_path):
    from tools.import_cv import run_import, collect_checks
    d = _cv_dir(tmp_path)
    checks = collect_checks(*__import__("tools.import_cv", fromlist=["parse_all"]).parse_all(d))
    assert "Principal AI Scientist" in checks
    assert "Menlo Park, California, USA" in checks
