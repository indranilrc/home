# Personal Website Redesign: Design

**Date:** 2026-11-26
**Repo:** `indranilrc/home` (this repo), currently a Jupyter Book deployed to the `gh-pages` branch at `https://indranilrc.github.io/home/`
**Target:** `https://indranilroychoudhury.com/` (domain currently serves an old Weebly site)

---

## 1. Intent

Indranil wants one current, refined personal site that people land on when they "look him up," mainly for job opportunities and professional connections. Later he may write articles on it and link them from LinkedIn.

The current github.io site was last updated in 2023 (publications in 2024). The Weebly site at `indranilroychoudhury.com` is about 7 years out of date. Neither one mentions the PHM Society Fellowship (2023), any patents, or current work at SLB. The github.io site becomes the only site, and the custom domain moves to it.

## 2. Goals, Non-Goals, Anti-Goals

**Goals**
- Someone who arrives cold understands within 30 seconds who he is, what he works on, and how to reach him.
- The look is refined and personal. It should read as a site made by a careful person, not as a template or as AI-generated.
- Content is current and accurate against the public CV.
- Easy to update: edit a data file or a Markdown file, push, and the site rebuilds itself.
- Ready for articles later without a redesign.

**Non-goals**
- Comments, analytics dashboards, newsletter signup, CMS.
- A blog with posts at launch. The machinery exists, but it is hidden until the first article.

**Anti-goals (failure even if it works)**
- **Braggy.** No stat badges or counters in the hero, no "h-index" up top, no logo strip of affiliations, no "first-named inventor" language, no performance numbers. The Fellowship appears once, plainly, in the bio. Indranil explicitly asked for this.
- **Obviously AI-made.** No purple gradients, glassmorphism, emoji, "Hi, I'm X 👋", rocket icons, generic hero illustrations, or hype words ("passionate," "cutting-edge," "leveraging," "innovative," "revolutionizing"). Copy follows the `humanize` house rules: plain words, no em dashes, US English.
- **Leaking SLB-internal content.** See Section 4.

## 3. Approaches Considered

| | Approach | Trade-off | Outcome |
|---|---|---|---|
| A | Keep Jupyter Book and restyle it | Least work, but it still looks like documentation with a sidebar | Rejected |
| B | Jekyll al-folio academic theme (an earlier, abandoned attempt exists in OneDrive `cv-resume/website/`) | BibTeX built in, but looks like many other academic sites; heavy Ruby toolchain; fiddly to customize | Rejected |
| **C** | **Custom static site: hand-written HTML/CSS, a small Python build script, content in data files** | Full control of look, no framework churn, fast, ages well; more initial work | **Chosen by Indranil** |

## 4. Content Sources and Confidentiality

- **Source of truth:** the public CV, `IndranilRoychoudhury_CV.tex` and its section files (`summary.tex`, `experience.tex`, `honors.tex`, `patents.tex`, `publications.tex`, `prof-service.tex`, `talks.tex`, `teaching.tex`, `education.tex`, `professionalmembership.tex`, `software.tex`) in
  `$CV/`.
  The rendered `IndranilRoychoudhury_CV.pdf` has been reviewed as safe to publish as-is (see `WEBSITE_GAP_ANALYSIS.md` in that folder).
- **Section files contain internal content wrapped in markers.** `\internal{...}`, `\begin{internalblock}...\end{internalblock}`, and `\ifinternalcv ... \fi` content must be **dropped** during import, exactly as the public PDF build does. After import, cross-check the imported content against the text of the public PDF (`pdftotext`); anything not in the PDF must not be on the site.
- **Never use:** `IndranilRoychoudhury_CV_SLB.*`, the CNP files, the PSE documents, invention disclosure numbers, unpublished applications, or any `slb.com` intranet, SharePoint, eureka, or degreed URLs.
- **Reusable drafts:** five project write-ups from the abandoned al-folio site (`cv-resume/website/_projects/`: `gr-log-generation.md`, `rig-state-detection.md`, `flea.md`, `rtsm.md`, `distributed-diagnosis.md`). They were written to be public-only, but rewrite them in the plain voice and verify every claim against a published paper or patent.
- **Talks:** list external talks, tutorials, and panels only. Leave out the "Technical Talks at SLB" section.
- **Contact email:** `indranil.r.c@gmail.com` (as in the public CV), obfuscated against scrapers (assembled in JS with a readable no-JS fallback like "indranil.r.c at gmail").
- **Profile links:** Google Scholar, LinkedIn (`linkedin.com/in/indranilroychoudhury`), ORCID (`0009-0002-1438-0510`).
- **Photo:** `media/IRCphoto.png` (499×499, color, outdoors, smiling). Show in color.
- **CV download:** a copy of the public `IndranilRoychoudhury_CV.pdf` committed to the repo.

## 5. Site Structure

Navigation: **Research · Publications · Talks & Teaching · Service · Awards · Experience · CV ↗** (CV opens the full PDF in a new tab; the short web CV became the Experience page at `/experience/`, with plain bullets), plus the light/dark toggle (revised 2026-11-26 at Indranil's request: awards, service, and talks/teaching get their own pages, as on the old site; the CV page keeps experience, education, and memberships). All links to other sites open in a new tab (`target="_blank" rel="noopener"`). The name at the left links home. "Writing" joins the nav automatically once at least one article exists.

```
/                     Home
/research/            Research themes (one page, anchored sections)
/publications/        All publications and patents
/cv/                  Web CV + PDF download
/writing/             Article index (built, not linked until a post exists)
/writing/<slug>/      Individual article
/404.html
```

### 5.1 Home
1. Header/nav.
2. Hero: eyebrow "Principal AI Scientist · SLB", name as H1, one-sentence lede, short bio (3 to 4 sentences: physics plus ML for diagnostics and prognostics, NASA Ames to SLB, Fellow of the PHM Society, co-author of *Prognostics: The Science of Making Predictions*), then text links: Google Scholar, LinkedIn, ORCID, Email. Photo on the right (stacks above text on mobile).
3. Faint "forecast fan" SVG behind the hero (chosen by Indranil from six motifs; see `motifs.html`, option 2): a solid measured health signal from the left that, past a "now" point, splits into about 8 thin diverging future trajectories, some crossing a faint dotted failure-threshold line near the bottom. Accent color, opacity about 0.22 in light mode and 0.5 in dark. Decorative, `aria-hidden`, static (no animation). Hero only; other pages have no motif.
4. "Currently": 4 short items (Physics-informed ML; Automating PHM; Foundation models for time series; Teaching).
5. "Selected work": 3 to 4 research themes as quiet text cards linking into `/research/#<theme>`.
6. Footer: name, contact links, "Last updated <build date>".

The approved mockups are `../.superpowers/brainstorm/31994-1795680609/content/hybrid-v3.html` (layout, colors, photo) and `motifs.html` option 2 (background motif) (relative to the repo's parent folder). Wording in it is a first draft.

### 5.2 Research
One page with seven themed sections, each with: a title, a two-to-four-sentence plain description of the problem and the idea, the period and organization in small text, and a quiet "Related papers and patents" list linking to entries (DOI, USPTO, or Espacenet links where they exist). "We" voice; collaborators named where natural. No metrics.

1. **Automating PHM**: AutoPHM (US 2025/0315037), RUL algorithm evaluation (US 2026/0133574), adapting pre-trained models to field data (US 2025/0315649), Jacobian feature regression (US 2025/0315038), plus related papers.
2. **Physics-informed and hybrid models**: digital gamma-ray log generation (SPE Journal 2023/24 paper, EP 4 630 852), stick/slip prediction (SPE/IADC paper, EP 4 423 542), unified hybrid modeling tool (US 2026/0203471).
3. **Foundation models for industrial time series**: US 2026/0079511, US 2026/0079480.
4. **Learning from field images and failure data**: rig state from video (US 12,136,267, SPE/IADC 2021), gas leak detection from images (US 12,467,818), ESP failure analysis (US 12,608,592 / EP 4 162 150 B1).
5. **Airspace safety (NASA Ames)**: RTSM papers and NASA technical report.
6. **Aerospace health management (NASA Ames)**: FLEA testbed, UAV battery prognostics, water recycling system, prognostics V&V, the textbook.
7. **Distributed diagnosis (Vanderbilt, NASA Ames)**: dissertation and structural model decomposition papers.

### 5.3 Publications
- The textbook featured at the top (cover image `media/book-cover.png`, one line, link).
- Every entry from the public CV: books, book chapters, journals, conference papers, technical reports, whitepapers, theses, plus granted patents and published applications.
- Grouped by year, newest first. Filter chips by type (All, Journal, Conference, Book/Chapter, Patent, Report) and a text search box. Both are progressive enhancement: without JS, the full list renders.
- Author lists show his name subtly emphasized (medium weight, not bold color).
- Best-paper awards and nominations as a small plain tag after the entry.
- Link out per entry where a DOI or URL exists.

### 5.4 CV
Readable web version, in order: Experience (SLB; SGT Inc. at NASA Ames; Vanderbilt), Education, Honors and Awards (individual, group, paper awards), Professional Service (organization roles, reviewing), Talks and Tutorials (external only), Teaching, Memberships. A "Download PDF" link at the top. Compact typography and plain lists; no timeline graphics or skill bars.

**The anti-brag rules apply to the web CV too (builder's call).** It lists facts (role, organization, dates; award name and date; service role and event) and drops self-description:
- No citation counts, h-index, i10-index, or "first-named inventor" counts; the CV Summary section is omitted entirely.
- The Fellowship is listed as "Fellow, Prognostics and Health Management Society, 2023", without the "highest individual honor, at most five annually" description or the citation text.
- Experience gets 2 to 4 plain bullets per role (via `cv_overrides.yml`), not the PDF's full outcome-claim bullets.
- Software Implementations and Technical Skills are omitted from the web CV (not parsed by the import).
- The downloadable PDF stays the full public CV unchanged; that's where a reader who wants every detail goes.

### 5.5 Writing (Hidden at Launch)
Articles are Markdown files in `content/writing/` with front matter (`title`, `date`, `summary`, optional `draft: true`). Each renders at `/writing/<slug>/` with good long-form typography, Open Graph tags for LinkedIn previews, and an RSS/Atom feed at `/writing/feed.xml`. Drafts are excluded from the build. Nav link and Home "Recent writing" block appear only when at least one non-draft post exists.

## 6. Visual Design (Approved: "B + C Hybrid")

- **Light mode (default for light-system users):** white `#ffffff` background, text `#141414`, muted `#565656`, rules `#e2e2e2`, accent teal `#0b6e69`.
- **Dark mode:** charcoal `#14171a`, text `#e8e6e1`, muted `#b4b0a7`, rules `#2a2e33`, accent amber `#d9a441`.
- **Dark is the default for every visitor** (revised 2026-11-26 at Indranil's request), regardless of system setting. A round icon button toggles light/dark (the icon shows the mode a click switches to: sun in dark mode, moon in light mode; tooltip and aria-label say what a click does); the choice is remembered in `localStorage`, and a small inline script in `<head>` applies it before paint (no flash).
- **Type:** IBM Plex Sans (headings and body) and IBM Plex Mono (small UI details only, such as the toggle and dates). Self-host the WOFF2 files (no Google Fonts request) with `font-display: swap`.
- Body text (paragraphs and list items) is justified with automatic hyphenation (revised 2026-11-26 at Indranil's request); headings, navigation, dates, short link rows, and research related-paper titles stay left-aligned. Record lists are numbered: publications continuously from newest (highest) to oldest (1), other lists per group.
- Headline sizes are large and tight (H1 around 44px desktop, letter-spacing about -0.028em); body 16 to 17px, line-height about 1.6, measure about 65 characters.
- Small uppercase tracked labels for section headers ("CURRENTLY").
- Links are underlined with a thin rule that takes the accent color on hover.
- No drop shadows, no rounded "cards" with heavy borders; separation comes from rules and whitespace.
- Responsive down to 360px. Visible focus states. WCAG AA contrast in both themes. Respect `prefers-reduced-motion` (the only motion is the theme transition).

## 7. Build and Deploy (Builder's Call, Stated to Indranil)

- **Generator:** a small Python 3 script (`build.py`) using Jinja2 templates and a Markdown library, writing static files to `_site/`. Dependencies pinned in `requirements.txt`. No Node toolchain.
- **Content files:** `content/profile.yml` (bio, links, "Currently"), `content/research.yml`, `content/cv.yml` (experience, education, honors, service, talks, teaching, memberships), `content/publications.bib` (publications and patents, with a `type`/`keywords` field for filtering), `content/writing/*.md`.
- **Import script:** `tools/import_cv.py` reads the public CV `.tex` files (path passed as an argument), strips internal markers, and writes `content/generated/publications.bib` and `content/generated/cv.yml`. It runs locally only (OneDrive is not reachable from CI).
- **Ownership (builder's call):** the CV `.tex` stays the long-term source of truth for facts (publications, patents, roles, awards, service). Files in `content/generated/` are owned by the import script and are overwritten freely; never hand-edit them. Everything the site adds lives in hand-edited sidecar files keyed by the CV's `\bibitem` keys (e.g. `PHM-13-a`): `content/pub_extras.yml` (type override, DOI/URL, award tag, research-theme tags) and `content/cv_overrides.yml` (plain-voice replacement text, entries to hide). The build merges generated data with the sidecars and warns about sidecar keys that no longer exist. `profile.yml` and `research.yml` are fully hand-edited. Workflow for Indranil: update the CV as usual, run the import, push; or edit a sidecar or profile file and push.
- **Deploy:** GitHub Actions on push to `main` builds and publishes via the official Pages action (`actions/deploy-pages`). Pages source switches from the `gh-pages` branch to "GitHub Actions."
- **Old content:** Jupyter Book files (`_config.yml`, `_toc.yml`, `*.md` pages, `_build/`, `references.bib`) are removed from `main`. Git history keeps them. The `gh-pages` branch can be deleted after the new deploy works.
- **SEO and sharing:** per-page `<title>` and description, Open Graph and Twitter card tags with the photo, `Person` JSON-LD (name, jobTitle, affiliation, sameAs Scholar/LinkedIn/ORCID), `sitemap.xml`, `robots.txt`, favicon, canonical URLs on the custom domain.

## 8. Domain Move

1. Add `CNAME` file containing `indranilroychoudhury.com` to the build output.
2. At the domain registrar (likely Weebly/Square; Indranil must confirm and log in): apex `A` records to `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` (plus the `AAAA` equivalents), and `www` `CNAME` to `indranilrc.github.io`.
3. In repo settings, set the custom domain, verify the domain for the account, and enable "Enforce HTTPS" after the certificate issues.
4. Confirm `indranilrc.github.io/home/` redirects to the new domain.
5. Only then cancel or unpublish the Weebly site, keeping the domain registration.

Indranil does the registrar steps; the builder provides exact instructions.

## 9. Left to the Builder

- Exact copy for the bio, lede, "Currently," and research write-ups (follow Section 2 and the humanize rules; run `python3 ~/.claude/skills/humanize/scripts/lint.py` on the copy, and Indranil approves the final wording).
- LaTeX-to-BibTeX parsing details, filter UI details, and the exact 404 page.
- Verifying every link (DOI, USPTO, Espacenet) resolves.

## 10. Open Items Needing Indranil

- Which registrar holds `indranilroychoudhury.com` and login access (needed only at the domain-move step).

Google Scholar: `https://scholar.google.com/citations?user=65YthzIAAAAJ` (from the earlier al-folio config).
