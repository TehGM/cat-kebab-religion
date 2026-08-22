# random-cat-kebab

The sacred teachings of the Cat Kebab. A [Hugo](https://gohugo.io/) static site.

https://cat-kebab.tehgm.net

## Develop

```
hugo server -D
```

Then open http://localhost:1313. `-D` includes draft content.

## Build

```
hugo
```

Output is written to `public/` (git-ignored).

## Structure

- `content/` — pages and articles
  - `teachings/` — the daily teachings (blog posts / LLM-generated articles)
  - `gallery/` — the cat image gallery
  - `faith/` — explanation of the faith
- `layouts/` — templates (placeholder scaffolds; being replaced by the Claude Design work)
  - `shortcodes/` — custom inline components used from Markdown
- `static/` — files served as-is (`img/cat/`, `CNAME`)
- `archetypes/` — front-matter templates for `hugo new`

## New teaching

```
hugo new teachings/my-teaching.md
```
