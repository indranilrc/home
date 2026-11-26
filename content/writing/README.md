# Writing

Each article is one Markdown file in this folder. The file name becomes the URL:
`why-prognostics.md` is published at `/writing/why-prognostics/`.

Start the file with front matter:

```
---
title: Why Prognostics Needs Humility
date: 2027-01-15
summary: One or two sentences shown in the list and in LinkedIn previews.
draft: true
---
```

Then write the article in Markdown below it. Leave `draft: true` while you work;
preview drafts locally with `python build.py --drafts`. Remove the line (or set
it to `false`) to publish. The "Writing" menu item and the home-page "Recent
writing" block appear automatically once one article is published.
