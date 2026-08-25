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
- `assets/img/cat/` — the images themselves

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
| `image` | Filename of the illustration, from `assets/img/cat/`. Omit and one is picked deterministically — and the pick survives the catalogue changing. |
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

{{% testimony image="Screenshot_51.png" no="4,103" by="Sr. Halina, night shift" %}}
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
{{% marginfigure image="Screenshot_51.png" alt="The Prophet in orbit"
   caption="Among the clearer images we hold. [Others are on the wall](/images/)." %}}
…paragraphs…
{{% /marginfigure %}}
```

The Faith page has four more: `articles`, `cols` + `col`, `feasts`, and `plainly`. See
`content/faith/_index.md` for usage.

## Sacred images

Drop a file into `assets/img/cat/` and it appears on the wall and in the random picker —
no code change needed. To record metadata for it, add an entry to `data/images.toml`:

```toml
[[image]]
  file = "Screenshot_62.png"
  title = "The Rooster Above the Ring Road"
  no = 4102
  depicts = "A grey tabby riding a large red rooster through deep space, a kebab wrap held
             aloft, pink lasers from the eyes, forked lightning, purple starfield."
  keywords = ["rooster", "kebab", "lightning", "lasers", "night"]
  record = [
    { label = "Mount", value = "rooster, at speed" },
    { label = "Carried", value = "one wrap, held aloft" },
    { label = "Weather", value = "lightning, considerable" },
    { label = "Filed", value = "day 847" },
  ]
  testimony = "He looked at me. I have not been rude to a road since."
  witness = "Sr. Halina, night shift"
```

Every field but `file` is optional.

**`record` is free-form.** There is no fixed set of fields: an image records whatever it
records, under whatever labels suit it, in the order you write them. The panel is omitted
entirely when the list is empty, so an unrecorded image shows nothing rather than a column
of filler. To state that something is genuinely unknown, say so —
`{ label = "Bread", value = "not recorded" }`. The popup has room for one line and shows
the first three values, so put the telling ones first.

**`no` never moves.** Give a sighting number or don't; without one, a stable number is
derived from the filename. Nothing about an image depends on its position in the
directory, so adding or removing a file renumbers nothing.

**`hidden = true`** keeps an image off the wall, out of the random reveal and out of the
popup. A teaching can still name it directly.

**`note`** is a marginal scribble, shown in handwriting beneath the reveal. Keep it rare —
rarer than testimonies — and tie it to the specific image, or it reads as furniture.

**`depicts` and `keywords` are never rendered.** They exist so that whoever writes the
daily teaching can choose a fitting image without being able to see one. Describe the
picture, not the doctrine — subject, mount, colours, setting, mood. Anything writing a
teaching should read `data/images.toml` and match against these two fields, then set
`image` in the front matter to the filename it picked.

## Images and the build

Images live in `assets/`, not `static/`, so they can go through Hugo's pipeline. Every
`<img>` on the site resolves through `layouts/partials/img-src.html`, which is the one
place that decides what is actually served.

```toml
[params.images]
  webp = false
```

Set `webp = true` and every non-gallery image — article illustrations, homepage cards, the
masthead roundel — is served as WebP. The wall keeps its originals either way; it is the
record, and the record is not re-encoded.

Hugo does the conversion itself, during `hugo`. There is no separate build pipeline and
nothing to install: the extended binary encodes WebP, writes the results into `public/`,
and caches them in `resources/_gen/` so later builds reuse them.

### GIFs — not done yet

Animations are the one thing Hugo cannot convert. Its pipeline decodes the first frame of
a GIF and nothing else, so putting one through it would silently replace a moving image
with a still. Encoding animated WebP needs a real encoder — ffmpeg's `libwebp_anim`, or
`gif2webp` — which means a step in the deploy pipeline. **There is no pipeline yet, so
this is unimplemented.** GIFs are served as GIFs.

The site is already wired for it. `img-src.html` looks for a derived copy and uses it when
it finds one, so the only thing missing is whatever produces the files. When the GitHub
Actions workflow gets written, the step has to:

- run **before** `hugo`, since Hugo reads `assets/` at build time;
- write to **`assets/img/derived/`** (gitignored — this is build output, and the GIFs in
  `assets/img/cat/` stay the source of truth);
- name each one **`<original filename>.webp`**, e.g. `giphy.gif` → `giphy.gif.webp`.

Roughly:

```yaml
- run: |
    mkdir -p assets/img/derived
    for f in assets/img/cat/*.gif; do
      ffmpeg -loglevel error -i "$f" -c:v libwebp_anim -lossless 0 -q:v 75 \
        -preset picture -loop 0 "assets/img/derived/$(basename "$f").webp"
    done
```

Measured on the three GIFs currently in the repo, that is 1.9 MB → 484 KB (55–78% off) at
identical dimensions and frame counts. Nothing needs committing and nobody needs ffmpeg
locally; without the step the build says so and serves the GIF.

Image references are bare filenames — `image = 'Screenshot_62.png'` in front matter,
`image="Screenshot_62.png"` in `testimony` and `marginfigure`. A full `/img/cat/…` path
still resolves. A name that matches no file warns at build time instead of shipping a 404.
