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
hugo --minify --printPathWarnings --panicOnWarning
```

Output goes to `public/` (git-ignored). `.github/workflows/deploy.yml` runs the same build
and publishes it to GitHub Pages on every push to `master`, and once a day regardless — the
masthead's DIES and the rail's date are worked out at build time, so a day with no new
teaching still needs a build. The old "serve the repo root" Pages setup no longer applies:
Pages must be set to deploy from **GitHub Actions** (Settings → Pages → Source).

`--panicOnWarning` makes any warning fail the build, so a teaching that names a missing
image, or collides with another's URL, never replaces a working site — the deploy stops and
the live site stays as it was.

`--printPathWarnings` is not optional decoration: without it, two pages that resolve to
the same URL build *silently* and one of them simply vanishes from the site. With it, Hugo
prints `Duplicate target paths` and the collision is at least visible.

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
- `data/calendar.toml` — the customary week and observances announced ahead; the Faith
  page's list of observances is rendered from it
- `assets/img/cat/` — the images themselves
- `lore/` — what the teachings keep to: `CANON.md` (settled) and `THREADS.md` (open)
- `scripts/teaching.py` — the daily writer's brief and checks; see
  [Automated teachings](#automated-teachings)
- `.claude/skills/daily-teaching/` — how a teaching is written, step by step, and in what voice

## New teaching

```bash
hugo new teachings/2026-08-25-my-teaching.md
```

Teachings are normally written by the scheduled routine — see
[Automated teachings](#automated-teachings). The rules below apply either way.

Name the file `YYYY-MM-DD-slug.md`. The date in the filename is what makes an automated
writer safe: a slug used twice on different days is two different files and two different
URLs, never an overwrite. Teachings publish at `/teachings/YYYY-MM-DD/slug/` — the date
comes from the `date` front matter, so the URL stays collision-proof even if a filename
forgets its prefix. Two teachings can only clash by sharing both a day and a slug, and
there is one teaching per day.

The date is its own path segment, but nothing is published at `/teachings/YYYY-MM-DD/`
itself; it is a container, not a page. Deep links always carry the slug.

**Always set `slug` in the front matter.** The date prefix on the filename is for the
filesystem only — without an explicit slug Hugo falls back to the whole filename and the
URL repeats itself as `/teachings/2026-08-25/2026-08-25-my-teaching/`. `hugo new` fills it
in for you; anything generating teachings automatically must write it.

**Dates are midnight UTC** — `date = 2026-08-25T00:00:00Z`. Hugo does not publish pages dated
in the future, so a teaching stamped 06:00 and built at 05:00 would sit unpublished until the
next build. Midnight is always in the past by the time anyone writes that day's teaching.
`hugo new` writes it this way, from the filename.

### Front matter

| Field | Purpose |
| --- | --- |
| `title` | The teaching's title. |
| `date` | Drives the "DAY N" counter, counted from `params.epoch` in `hugo.toml`, and the date segment of the URL. Midnight UTC — see above. |
| `slug` | The last URL segment. Required — see above. |
| `form` | What shape the teaching takes — `ruling`, `sighting`, `homily`, … Not rendered; it lets the writer see what the last few were and not repeat them. The list is in `.claude/skills/daily-teaching/style.md`. |
| `summary` | Shown on the homepage and in the archive. Keep to one or two sentences. |
| `standfirst` | The italic line under the title. Optional. |
| `image` | Filename of the illustration, from `assets/img/cat/`. Omit it, or set it to `''`, and the teaching simply has no illustration; see below. |
| `caption` | Caption under the illustration. Dropped along with it if there is none. |
| `seal` | Stamp text in the header, e.g. `Vibes confirmed`. |
| `feast` | Feast name shown under the date. |
| `signoff` | Replaces the default closing line. |
| `note` | A handwritten note at the foot. |
| `tags` | List of tags. |

### A teaching with no picture

Not how these are usually written, but supported.

```toml
image = 'Screenshot_62.png'   # that image
image = ''                    # no image
                              # omitted: no image either
```

A teaching is illustrated because someone chose the picture, or it is not illustrated at
all. Nothing is chosen on its behalf — `depicts` and `keywords` in `data/images.toml` exist
so that whoever writes the teaching can choose a fitting image without being able to see
one.

Nothing shifts when there is no picture. The article omits the figure; the homepage lead
omits its snapshot, and the caption goes with it. The homepage card drops the snapshot and
takes symmetric padding instead of the narrow gutter that seats it, keeping the grid's
height. The archive row is a four-column grid, so it keeps the slot rather than collapsing
it — as an empty album mount, photo corners still stuck to the leaf, marked NO PHOTOGRAPH.
Every other row stays aligned to the pixel.

## The homepage slips

The right-hand column of the homepage — Today's Litany, Signs & Wonders This Week, the
Calendar of Feasts — is `[[panels]]` in `content/_index.md`. These change often, so their
lines are structured rather than one blob of markup: a single day of the calendar can be
rewritten without touching the other three.

```toml
[[panels]]
  id = 'calendar'
  updated = 2026-09-25
  title = 'Calendar of Feasts'
  style = 'gold'                      # "dark", "gold", or omit for plain white
  lines = [
    { lead = "Fri", text = "Great Feast of the Rooster", strong = true },
    { lead = "Mon", text = "the Bread Hat" },
  ]
  note = 'bringing the good sauce Fri'
```

| Field | Purpose |
| --- | --- |
| `id` | `litany`, `signs` or `calendar`. Not rendered — it is how the daily writer and `scripts/teaching.py` find each slip. |
| `updated` | The day the slip was last rewritten. Not rendered; it is how the checks tell what is due. |
| `lead` | Optional. Set before an em dash — the day, or the call of a litany. |
| `text` | The line itself. Rendered as markdown, so it may carry emphasis or a link. |
| `strong` | `true` sets `text` bold — the response, or the feast that matters this week. |
| `note` | Optional, per panel. The handwritten scratch beneath the slip. |
| `body` | Raw HTML, used only when `lines` is absent — for a panel that is simply prose. |

Every panel takes the same three keys, whatever it holds: the litany pairs call with
response, the calendar pairs day with feast, and Signs & Wonders sets `text` alone.

They keep a rhythm, which `scripts/teaching.py check` enforces:

- **The litany** is rewritten every day.
- **The calendar** rolls forward every day. It opens with today, then the next observances of
  the coming week — two to four lines in all, in order. A day with nothing on is left off:
  when today has nothing on, the slip opens with the next observance and sets no line bold.
  It starts from `data/calendar.toml`, but the writer may add lesser observances of its own;
  the calendar is custom, not law.
- **Signs & Wonders** is rewritten every Monday.

## The 404 page

`layouts/404.html` renders to `/404.html` at the root of the build, which is what GitHub
Pages serves for any address it cannot find. It has no content file — its copy lives in
`[params.notFound]` in `hugo.toml`, and the rail and footer wording are overridden as
template blocks, because baseof renders those before `main` and a page with no front
matter has nothing for them to read.

Two things matter and are easy to break:

- **Every URL on the page must resolve from the root.** The 404 is served at whatever
  address the visitor mistyped, so a relative path resolves against *their* location, not
  the site root. The stylesheet, nav and `img-src.html` all emit root-relative paths
  already; anything added must too.
- **It carries `noindex`.** A 404 that returns HTML is otherwise a crawlable page. It stays
  out of the sitemap on its own.

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

The wording above is illustration, not lore — the Book of Wraps and the postures are ideas
from the development drafts (see `lore/THREADS.md`, Seeds), not canon.

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
`content/faith/_index.md` for usage. `feasts` self-closed — `{{< feasts />}}` — lists the
customary week from `data/calendar.toml`, which is how the Faith page uses it: the week can
change without anyone editing the page.

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

The writer picks whichever image fits the teaching best, but passes over any image a
teaching used in the last ten days unless nothing else fits. `scripts/teaching.py context`
lists every image with when it was last used; `check` warns about a recent repeat.

Cataloguing is done by hand, when an image is added. The daily writer only chooses among
images that have an entry here — a file without one has no `depicts` to be chosen by — and
never edits this file. A new entry's `Filed` day and number are canon, so give it a number
above the highest in use and a day at or before the day it is added.

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

### GIFs

Animations are the one thing Hugo cannot convert. Its pipeline decodes the first frame of
a GIF and nothing else, so putting one through it would silently replace a moving image
with a still. Encoding animated WebP needs a real encoder — ffmpeg's `libwebp_anim`, or
`gif2webp` — so it is a step in the deploy workflow rather than part of Hugo.

`img-src.html` looks for a derived copy and uses it when it finds one. The step in
`.github/workflows/deploy.yml` produces them, and has to:

- run **before** `hugo`, since Hugo reads `assets/` at build time;
- write to **`assets/img/derived/`** (gitignored — this is build output, and the GIFs in
  `assets/img/cat/` stay the source of truth);
- name each one **`<original filename>.webp`**, e.g. `giphy.gif` → `giphy.gif.webp`.

Measured on the three GIFs currently in the repo, that is 1.9 MB → 484 KB (55–78% off) at
identical dimensions and frame counts. Nothing needs committing and nobody needs ffmpeg
locally; without the step the build says so and serves the GIF.

One catch, only once `webp = true`: "the build says so" is a warning, and the strict build
(`--panicOnWarning`) fails on warnings. CI has ffmpeg and is fine; a local build, or the
daily routine's check build, would fail on the GIFs. Before turning WebP on, either run the
same ffmpeg loop in those places or drop `--panicOnWarning` from the routine's check.

Image references are bare filenames — `image = 'Screenshot_62.png'` in front matter,
`image="Screenshot_62.png"` in `testimony` and `marginfigure`. A full `/img/cat/…` path
still resolves. A name that matches no file warns at build time instead of shipping a 404.

## Automated teachings

A Claude Code [routine](https://code.claude.com/docs/en/routines) writes and publishes one
teaching a day. Everything it follows is in this repository:

- `.claude/skills/daily-teaching/SKILL.md` — the procedure: brief, plan, image, write, update
  the homepage slips and the lore, check, build, commit, push.
- `.claude/skills/daily-teaching/style.md` — the voice, the forms a teaching can take, and
  the variety rules.
- `lore/CANON.md` and `lore/THREADS.md` — what is settled, and what is open and how fast it
  may move. Each day's additions go into THREADS; CANON changes only when a thread has
  developed strongly over weeks.
- `data/calendar.toml` — the customary week and dated observances. The routine may add
  observances freely and, rarely, change the customs themselves.
- `scripts/teaching.py` — `context` prints the day's brief (day number, observance, week
  ahead, slips due, the last fortnight, every image and when it was last used); `check`
  validates the day's teaching and slips; `check --all` runs in CI.
- `scripts/install-hugo.sh`, run by the SessionStart hook in `.claude/settings.json` — installs
  Hugo in cloud sessions only. It comes from PyPI (`hugo==0.152.2`), because cloud sessions
  cannot download GitHub release assets from repositories not attached to the session.

### Setting it up

1. Merge this branch into `master`. The routine clones the default branch.
2. Settings → Pages → Source: **GitHub Actions**. Push, and check the Deploy workflow goes
   green and the site loads.
3. Leave `master` unprotected. The routine pushes straight to it as you (it carries your
   GitHub identity), and a cloud session can only push to a branch that isn't protected and
   has no commits authored by anyone else.
4. At [claude.ai/code/routines](https://claude.ai/code/routines), create a routine:
   - **Repository:** this one.
   - **Environment:** Default (Trusted network is enough — PyPI is on its allowlist).
   - **Connectors:** remove them all. It needs none.
   - **Trigger:** daily, early morning — but **after 01:00 UTC and before 22:00 UTC**. The
     writer takes "today" from the UTC date, and midnight UTC is when the Eternal Orbit
     turns over.
   - **Prompt:**

     > Write and publish today's teaching for the Church of Cat Kebab by following the
     > daily-teaching skill in this repository (.claude/skills/daily-teaching/SKILL.md) from
     > start to finish. Work on master and push to master; do not create a branch or a pull
     > request. If today's teaching already exists, only bring the homepage slips up to date.
     > If any check fails and you cannot fix it, do not push — report what failed.

5. Press **Run now** once and read the session: a green run only means it didn't crash.

A missed day leaves no gap to fill — the next run writes the next day, and the archive simply
has no teaching for the day that was missed.
