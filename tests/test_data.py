import re
import json
from pathlib import Path

import pytest
import yaml

from sitegen.data import ContentError, load_content


def make_root(tmp_path: Path, *, extras=None, overrides=None, research=None) -> Path:
    c = tmp_path / "content"
    (c / "generated").mkdir(parents=True)
    (c / "site.yml").write_text(yaml.safe_dump({"title": "T", "url": "https://x", "base_path": ""}))
    (c / "profile.yml").write_text(yaml.safe_dump({"name": "N"}))
    pubs = [
        {"key": "J1", "label": "J1", "type": "journal", "year": 2024, "title": "A", "html": "a",
         "text": "a", "url": None, "award": None},
        {"key": "US1", "label": None, "type": "patent", "year": 2025, "title": "B", "html": "b",
         "text": "b", "url": None, "award": None},
    ]
    item = lambda k, t: {"key": k, "label": None, "html": t, "text": t, "children": []}  # noqa: E731
    cv = {
        "experience": [{"key": "slb", "org": "SLB", "location": "L", "dates": "D", "role": "R",
                        "bullets": ["long bullet"]}],
        "honors": {"title": "Honors", "intro_html": "", "groups": [
            {"title": "Individual", "items": [item("fellow", "Fellow, highest honor"), item("ieee", "IEEE")]}]},
        "service": {"title": "S", "intro_html": "", "groups": [{"title": "Other", "items": [item("sig", "Eureka")]}]},
    }
    (c / "generated" / "publications.json").write_text(json.dumps(pubs))
    (c / "generated" / "cv.json").write_text(json.dumps(cv))
    if extras is not None:
        (c / "pub_extras.yml").write_text(yaml.safe_dump(extras))
    if overrides is not None:
        (c / "cv_overrides.yml").write_text(yaml.safe_dump(overrides))
    if research is not None:
        (c / "research.yml").write_text(yaml.safe_dump(research))
    return tmp_path


def test_loads_minimal(tmp_path):
    content = load_content(make_root(tmp_path))
    assert content.site["title"] == "T"
    assert set(content.pubs_by_key) == {"J1", "US1"}
    assert content.research == [] and content.posts == [] and content.warnings == []


def test_extras_override_type_and_url(tmp_path):
    content = load_content(make_root(tmp_path, extras={"J1": {"type": "report", "url": "https://doi.org/x"}}))
    assert content.pubs_by_key["J1"]["type"] == "report"
    assert content.pubs_by_key["J1"]["url"] == "https://doi.org/x"


def test_unknown_extras_key_warns(tmp_path):
    content = load_content(make_root(tmp_path, extras={"GONE-99": {"url": "u"}}))
    assert any("GONE-99" in w and "pub_extras.yml" in w for w in content.warnings)


def test_research_unknown_pub_key_raises(tmp_path):
    research = [{"id": "auto-phm", "title": "A", "body": "b", "pubs": ["J1", "NOPE"]}]
    with pytest.raises(ContentError) as e:
        load_content(make_root(tmp_path, research=research))
    assert "auto-phm" in str(e.value) and "NOPE" in str(e.value)


def test_research_items_resolved(tmp_path):
    research = [{"id": "a", "title": "A", "body": "b", "pubs": ["US1", "J1"]}]
    content = load_content(make_root(tmp_path, research=research))
    assert [p["key"] for p in content.research[0]["items"]] == ["US1", "J1"]


def test_cv_override_hides_and_replaces(tmp_path):
    overrides = {
        "experience": {"slb": {"bullets": ["Plain one.", "Plain two."]}},
        "honors": {"fellow": {"html": "Fellow, PHM Society, 2023"}},
        "service": {"sig": {"hide": True}},
    }
    content = load_content(make_root(tmp_path, overrides=overrides))
    assert content.cv["experience"][0]["bullets"] == ["Plain one.", "Plain two."]
    items = content.cv["honors"]["groups"][0]["items"]
    assert items[0]["html"] == "Fellow, PHM Society, 2023"
    assert content.cv["service"]["groups"] == []  # group emptied by hide is dropped


def test_unknown_cv_override_key_warns(tmp_path):
    content = load_content(make_root(tmp_path, overrides={"honors": {"missing": {"hide": True}}}))
    assert any("cv_overrides.yml" in w and "missing" in w for w in content.warnings)


def test_sidecar_files_have_no_duplicate_keys():
    from build import ROOT
    for name in ("pub_extras.yml", "cv_overrides.yml", "profile.yml"):
        keys = re.findall(r"^([A-Za-z0-9_.-]+):", (ROOT / "content" / name).read_text(), re.M)
        dupes = {k for k in keys if keys.count(k) > 1}
        assert not dupes, (name, dupes)


def test_cv_override_adds_items(tmp_path):
    overrides = {"honors": {"_add": [{"key": "extra-award", "html": "<strong>Extra</strong>, 2020"}]}}
    content = load_content(make_root(tmp_path, overrides=overrides))
    items = content.cv["honors"]["groups"][-1]["items"]
    assert items[-1]["key"] == "extra-award" and items[-1]["html"] == "<strong>Extra</strong>, 2020"
    assert content.warnings == []
