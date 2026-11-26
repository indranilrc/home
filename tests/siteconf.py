"""Expected URLs come from content/site.yml, so tests pass before and after the domain move."""
from pathlib import Path

import yaml

SITE = yaml.safe_load((Path(__file__).resolve().parents[1] / "content" / "site.yml").read_text())
BASE = SITE.get("base_path") or ""
URL = SITE["url"].rstrip("/") + BASE
