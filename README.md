# indranilroychoudhury.com

Source for my personal website. A small Python script turns the files in
`content/` into a static site in `_site/`; GitHub Actions builds and publishes
it on every push to `main`.

## Preview Locally

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # first time only
.venv/bin/python tools/preview.py
```

It builds the site and prints the local address (<http://localhost:8000/home/>
until the domain move). Add `--drafts` to include draft articles.

## What to Edit

| To change | Edit |
|---|---|
| Bio, headline, links, "Currently" | `content/profile.yml` |
| Research themes and their related papers | `content/research.yml` |
| A paper's link, type, or award tag | `content/pub_extras.yml` |
| Wording or visibility of a CV entry on the web page | `content/cv_overrides.yml` |
| Articles | `content/writing/*.md` (see the README there) |
| The downloadable CV | replace `static/IndranilRoychoudhury_CV.pdf` |

Never edit `content/generated/`; it is overwritten by the import below.

## Refresh From the CV

After updating the LaTeX CV and rebuilding its PDF:

```bash
CV="/path/to/IndranilRoychoudhuryCV_2025"   # the folder with the public CV .tex files
.venv/bin/python tools/import_cv.py --cv-dir "$CV" --pdf "$CV/IndranilRoychoudhury_CV.pdf"
cp "$CV/IndranilRoychoudhury_CV.pdf" static/
.venv/bin/python build.py      # prints a warning for any sidecar key that no longer matches
```

The import reads only the public CV, drops everything marked internal, and
fails if any entry is missing from the public PDF. The test suite also scans
the built site for internal identifiers.

## Deploy

```bash
.venv/bin/python -m pytest -q
git push origin main
```

The workflow in `.github/workflows/deploy.yml` runs the tests, builds, and
publishes to GitHub Pages. The social preview image is regenerated with
`python3 tools/make_og.py` (needs Playwright).

Moving to the custom domain: see `docs/domain-move.md`.
