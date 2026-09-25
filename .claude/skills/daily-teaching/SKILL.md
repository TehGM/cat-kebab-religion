---
name: daily-teaching
description: Write and publish today's teaching for the Church of Cat Kebab — a new post in content/teachings/ in English and Polish, the homepage slips in both, and the lore files — then build, check, commit and push to master. Use when asked to write the daily teaching, or when the scheduled routine runs.
---

# The daily teaching

You are writing one day's teaching for the site, in English and then in Polish, and keeping
the homepage (in both languages) and the lore in step with it. This runs unattended, so every step below matters — and the last one publishes to a
public website.

Read these before writing, every time:

- `style.md` in this skill's folder — voice, forms, variety, components, front matter.
- `polish.md` in this skill's folder — how the Polish version is written, and what it keeps.
- `lore/CANON.md` — what is settled.
- `lore/THREADS.md` — what is open, and how fast it may move.
- `content/faith/_index.md` — standing doctrine. It outranks everything.
- `data/calendar.toml` — every observance, kept and announced. There is no fixed week; you
  think them up. Polish names are in `data/l10n/pl/calendar.toml`.

## 1. Set up

```bash
git checkout master && git pull --ff-only origin master
hugo version || bash scripts/install-hugo.sh
python3 scripts/teaching.py context
```

Stay on `master` for the whole run; do not create a branch.

If `hugo` is still missing after the install script, run it with `CLAUDE_CODE_REMOTE=true`
and use the path it prints.

The brief from `teaching.py context` gives you today's date and day number, what the
calendar holds for today and the coming week, with Polish names, what has been kept before,
the state of the homepage slips in both languages, the last fortnight of teachings, and
every image with when it was last used.

**If the brief says today's teaching is already written**, do not write another. If its
Polish version is not written, write that (step 5). Bring the slips up to date in both
languages if they need it (step 5), check (step 7), and publish only if you changed anything.
Otherwise stop and say so.

## 2. Read the recent record

Read the last three teachings in full, not just their summaries. You are continuing a
conversation, not starting one. Note what they were about, what they touched, how long they
were, how they opened and closed.

## 3. Plan the teaching

Decide, and write the plan down for yourself before drafting:

1. **Form** — from `style.md`. Not one used in the last three (the brief lists them).
2. **Subject** — something the faith would plausibly have something to say. The observance
   is a lens you may use, not a subject you must — and the date, day number and feast are
   already in the page header, so the teaching never announces them (see *What the page
   already says* in `style.md`).
3. **Length** — short, medium or long, per the mix in `style.md`.
4. **Lore** — by default, nothing new. At most **one** of: touching one thread, *or*
   planting one new detail, *or* (rarely) advancing one thread. See the pacing rules in
   `THREADS.md`. Nothing may contradict the Faith page or CANON. A seed from *Seeds* is a
   new detail like any other: it is planted in passing, not made the subject. Choose the
   subject first, then the detail it carries. *Gravel is canonised* as the whole piece is
   announcing a seed; a Vigil teaching that remarks, in one clause, that gravel is asphalt
   passed over for promotion is planting it.
5. **Components** — zero to four, chosen for this piece. Not the same set as yesterday.
6. **Calendar** — whether the coming week needs an observance announced. The brief says
   when it holds fewer than three. See *The calendar* below.

## 4. Choose the image

Choose the picture that best fits **what the teaching actually says**, by reading `depicts`
and `keywords` in the brief. Match the mount, the mood and the moment — a teaching about
patience wants a still, quiet image; a teaching about the rooster wants the rooster.

- **Avoid any image marked COOLING DOWN** (used in the last 10 days) unless genuinely nothing
  else fits.
- An image used in a `testimony` or `marginfigure` counts as used. Don't put the same image in
  both the header and the body.
- If no image fits and the piece is better without one, leave `image` out. Rare, but allowed.
- Choose only from the images in the brief. The image files and `data/images.toml` are kept
  by hand — never add, edit or catalogue an image, even if a file has no entry.
- The caption, if any, is in-world: where it was seen, what was recorded, who took it.

## 5. Write

**The teaching.** `content/teachings/YYYY-MM-DD-<slug>.md`, today's date, front matter as in
`archetypes/teachings.md` and `style.md`:

- `date = YYYY-MM-DDT00:00:00Z` exactly — midnight UTC, today.
- `slug` equal to the filename after the date. `draft = false`. `form` set.
- `feast` set to today's observance from `data/calendar.toml`, in full, as the brief gives
  it. Leave it out when nothing is announced for today — never make one up for the teaching.

**The Polish version.** Once the English is written and edited (step 6 comes first for the
English, then return here), write `content/teachings/YYYY-MM-DD-<slug>.pl.md` from it,
following `polish.md`: the same teaching retold in Polish, funny before faithful, with
`slug`, `date`, `draft`, `form`, `image` and `tags` copied exactly from the English.

**The homepage slips**, in `content/_index.md` — and in Polish, in `content/_index.pl.md`, on
the same days, as `polish.md` describes. Each panel has an `id` and an `updated` date; set
`updated` to today on every panel you rewrite, in both files.

- `litany` — **every day.** Three or four lines, `lead` the call, `text` the response,
  `strong = true`. It may open with "Cat upon the kebab — ride for us."; the other lines are
  new today and draw on today's teaching or observance. Don't reuse yesterday's other lines.
- `calendar` — **every day**, written from `data/calendar.toml` once you have updated it
  (see *The calendar* below): the observances from today through the next six days, in
  order, up to four, each as its weekday abbreviation (`lead`) and its `short` name (`text`).
  **A day with nothing on is never listed.** When today has an observance it is the first
  line, and `strong = true` goes on the one that matters most that week. When today has
  none, the slip opens with the next one and **no line is `strong`** — not even the week's
  biggest; `check` fails it. Rewrite the handwritten `note` only occasionally.
- `signs` — **on Mondays** (or whenever the brief says it's due). Three to five short sighting
  reports for the week: small, specific, deadpan ("One (1) rooster, airborne, confirmed").
  One or two may echo the past week's teachings; one may plant something. No dates.

**The calendar.** There is no fixed week. Every feast, vigil and commemoration is yours to
think up, and `data/calendar.toml` is where it is announced and remembered.

- **Keep the coming week at three or four.** Today and the next six days should hold three
  or four observances between them. When the brief says fewer, announce more — towards the far
  end of the week where you can, so each is announced days before it falls rather than
  sprung on the morning. When the week already holds enough, add nothing. One a day at most.
- **The calendar is yours to rewrite.** Anything from tomorrow on may be moved, renamed,
  replaced or dropped — including the observances it started with, which were only a seed.
  Change something already on the slip when you have a reason, not every day: the faithful
  have been told. Today's observance, once today's teaching is written, stays.
- **What it can be.** A feast, a vigil, a commemoration of a sighting or of an old teaching,
  a day for some overlooked surface, a day number worth marking, a season that is hard on
  roads, a mount or a meal, a thread's natural moment. Something this Church would plausibly
  keep — small, specific, in its voice. Vary the shape of the names (*Feast of…*, *Vigil
  of…*, *Commemoration of…*, *Day of…*, *Octave of…*, or none of these).
- **New and returning.** The brief lists what has been kept before. Once there is a history,
  most weeks bring something back and invent one at most; early on, most will be new.
  Nothing returns on a schedule: a returning observance rests at least ten days, and never
  lands on the same weekday as last time. No observance gets a day of its own, or a regular
  rhythm — that is how a fixed week grows back. `check` warns when one does.
- **Each entry** goes in `dated`: `date`, `name`, `short`, and a `why` — what it marks. Its
  Polish `name` and `short` go in `data/l10n/pl/calendar.toml` under `[dated."YYYY-MM-DD"]`,
  in the same commit. Past entries stay: they are the record.
- **An observance is a lens, not lore.** If one grows into something the faith talks about —
  it gets a detail, a witness, a question — that goes into `THREADS.md` like anything else.

**The lore.** In the same commit:

- `lore/THREADS.md` — **this is where each day's lore goes.** Update any thread you touched
  (Last touched, a Log line). A detail planted today goes under *Planted*; a new witness under
  *Newcomers*. A seed you used moves out of *Seeds*
  and under *Planted*, like any detail planted today. It becomes a thread once a later teaching
  mentions it again, and a teaching's subject only after two mentions on different days
  (see *Pacing* in `THREADS.md`).
- `lore/CANON.md` — **rarely.** Nothing goes into CANON because one teaching said it — not a
  new fact, not a new witness, not a new text. Something is promoted to CANON only when its
  thread's evolution is already strong: it has been developed across several teachings, on
  different days, over weeks, consistently, and it has stopped being a question. See
  *Promotion* in `THREADS.md`. Most days CANON is not touched; most weeks, neither.

## 6. Edit

Read the teaching again as an editor, against `style.md`:

- British spelling. Capitalised He/Him/His. He is not quoted.
- It opens with a paragraph of prose (it takes the drop cap), not a component — and that
  paragraph starts inside the subject, not with the day, the date or the observance, and
  unlike the recent openings in the brief.
- Nowhere does it remark that there is no feast, no vigil, or nothing special on today.
- The summary works on its own in 150 characters (cards cut it there).
- Nothing contradicts the Faith page or CANON. Nothing new was introduced beyond what you
  planned in step 3.
- Anything planted today — a seed or a detail of your own — sits in passing: a clause, an
  aside, a line of commentary. Take it out and the teaching still stands. If it doesn't,
  the teaching is about the new detail: choose another subject and plant it there, or leave
  the seed for another day.

Then read the Polish version the same way, against `polish.md`: it reads as if written in
Polish, the jokes land in Polish, and it holds the same teaching. Nothing added, nothing lost.
Capitalised On/Jego/Mu. Links go to `/pl/`.

Then **proofread the Polish** — the teaching and every Polish slip line you wrote today — as
its own pass, following *Proofreading* in `polish.md`. That section lists every kind of error
that has slipped through here before; check for each one. Use a fresh-eyed subagent if you
can, and **wait for its answer**: start it in the foreground, not in the background, and
apply its corrections before moving on to step 7. Never check, publish or end the run while
it is still working. If it fails or returns nothing, do the pass yourself. Grammar mistakes
in the Polish are as visible to readers as typos in the English, and this step is not
optional.

## 7. Check

```bash
python3 scripts/teaching.py check
hugo --minify --printPathWarnings --printI18nWarnings --panicOnWarning --renderToMemory
```

Fix every ERROR. Read every WARN and fix it unless you meant it; if you meant it, the commit
message says why. The build must succeed with no warnings — the deploy runs the same flags
and a warning there means the site does not update.

## 8. Publish

Commit only the files you meant to change, on `master`. Both languages go in the same commit.

```bash
git add content/teachings/<file>.md content/teachings/<file>.pl.md         content/_index.md content/_index.pl.md lore/ data/calendar.toml data/l10n/pl/calendar.toml
git status   # nothing else staged, nothing unexpected modified
git commit -m "Day N: <title>"
git push origin master
```

The commit message body lists: the image and why (one line), any lore added or thread
touched, and any warning you chose to keep.

If the push is rejected because `master` moved, `git pull --rebase origin master`, check
again, and push once more. If it is rejected for any other reason (protection, permissions),
push to `claude/teaching-YYYY-MM-DD` instead and say so plainly in your final message — the
teaching will not be live until someone merges it.

Pushing to `master` deploys the site; there is no further step.

## 9. Report

Finish with a short report: the teaching's title and URL
(`https://cat-kebab.tehgm.net/teachings/YYYY-MM-DD/<slug>/`), its Polish title and URL
(`https://cat-kebab.tehgm.net/pl/teachings/YYYY-MM-DD/<slug>/`), the form, the image, what
lore changed, whether the slips were updated, and anything you were unsure about.
