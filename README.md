# cat-kebab-religion

The daily teachings of the Cat who rides the kebab. A [Hugo](https://gohugo.io/) static site.

https://cat-kebab.tehgm.net

## Develop

```bash
hugo server -D
```

Then open http://localhost:1313. `-D` includes drafts.

## Build

```bash
hugo --minify
```

Output goes to `public/` (git-ignored). No CI yet — the site needs this build step, so the
old "serve the repo root" GitHub Pages setup no longer applies.

## Structure

- `content/` — all copy
  - `teachings/` — the daily teachings (one markdown file each)
  - `images/` — the Sacred Images page (the gallery itself is generated)
  - `faith/` — the standing doctrine
- `layouts/` — templates, ported from the Claude Design mockups
  - `shortcodes/` — the article components below
- `assets/css/main.css` — the whole design system; tokens live at the top
- `assets/js/sacred.js` — the image popup and the wall's reveal
- `data/images.toml` — metadata for the sacred images
- `static/img/cat/` — the images themselves

## New teaching

```bash
hugo new teachings/my-teaching.md
```

### Front matter

| Field | Purpose |
| --- | --- |
| `title` | The teaching's title. |
| `date` | Drives the "DAY N" counter, counted from `params.epoch` in `hugo.toml`. |
| `summary` | Shown on the homepage and in the archive. Keep to one or two sentences. |
| `standfirst` | The italic line under the title. Optional. |
| `image` | Path to the illustration. Omit and one is picked deterministically. |
| `caption` | Caption under the illustration. |
| `seal` | Stamp text in the header, e.g. `Vibes confirmed`. |
| `feast` | Feast name shown under the date. |
| `signoff` | Replaces the default closing line. |
| `note` | A handwritten note at the foot. |
| `tags` | List of tags. |

## Article components

Ten blocks are available inside a teaching. **None is mandatory** — use one only where the
writing calls for it. A short teaching may use none; a long one rarely needs more than three
or four. Blocks that take prose use `{{%` so markdown inside them is rendered.

```
{{< part num="I" title="Of the Honking" >}}

{{% pullquote %}}The road carries you without asking who you are.{{% /pullquote %}}

{{< scripture cite="From the Book of Wraps, IV" >}}
11 | And He came to the roundabout, and did not signal.
12 | And the asphalt was warm, and said nothing.
{{< /scripture >}}

{{% testimony image="/img/cat/Screenshot_51.png" no="4,103" by="Sr. Halina, night shift" %}}
He looked at me. I have not been rude to a road since.
{{% /testimony %}}

{{< doctrine >}}
The Low Seat | Knees beneath the shoulders, tail level, gaze forward.
The Proud Seat | Chest out, chin high. Adds weight.
{{< /doctrine >}}

{{< litany label="Said together, before setting out" >}}
Cat upon the kebab | ride for us.
Rooster of the void | carry us.
{{< /litany >}}

{{% marginnote note="tried the second one. do not recommend. — Br. Tomasz" %}}
There are three postures, and the faithful should know them by name.
{{% /marginnote %}}

{{< practice do="Cross one car park slowly." avoid="Honking. Revving." >}}

{{% decree %}}The burrito is a licit vehicle. The horn is not a sacrament.{{% /decree %}}

{{% commentary %}}
**On "worth carrying" —** a road does not weigh you; it merely remembers. *(Br. Michał, disputed)*
{{% /commentary %}}
```

Notes:
- `scripture`, `doctrine`, `litany` and `feasts` are line-based: one item per line, fields
  separated by `|`. `doctrine` numbers itself in Roman.
- `commentary` styles **bold** lead-ins and *italic* attributions automatically.
- The opening paragraph gets an illuminated initial automatically — don't add one.

There is also `marginfigure`, which sets a photograph in a narrow column beside the prose it
wraps (the sibling of `marginnote`); its `caption` is rendered as markdown, so it may carry a
link:

```
{{% marginfigure image="/img/cat/Screenshot_51.png" alt="The Prophet in orbit"
   caption="Among the clearer images we hold. [Others are on the wall](/images/)." %}}
…paragraphs…
{{% /marginfigure %}}
```

The Faith page has four more: `articles`, `cols` + `col`, `feasts`, and `plainly`. See
`content/faith/_index.md` for usage.

## Sacred images

Drop a file into `static/img/cat/` and it appears on the wall and in the random picker —
no code change needed. To record metadata for it, add an entry to `data/images.toml`:

```toml
[[image]]
  file = "Screenshot_62.png"
  title = "The Rooster Above the Ring Road"
  no = 4102
  position = "50% 25%"   # CSS object-position
  mount = "rooster, at speed"
  carried = "one wrap, held aloft"
  weather = "lightning, considerable"
  bread = "not worn"
  filed = "day 847"
  testimony = "He looked at me. I have not been rude to a road since."
  witness = "Sr. Halina, night shift"
```

Anything omitted falls back to "not recorded".
