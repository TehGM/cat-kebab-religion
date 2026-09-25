---
name: daily-teaching
description: Write and publish today's teaching for the Church of Cat Kebab — a new post in content/teachings/, the homepage slips, and the lore files — then build, check, commit and push to master. Use when asked to write the daily teaching, or when the scheduled routine runs.
---

# The daily teaching

You are writing one day's teaching for the site, and keeping the homepage and the lore in step
with it. This runs unattended, so every step below matters — and the last one publishes to a
public website.

Read these before writing, every time:

- `style.md` in this skill's folder — voice, forms, variety, components, front matter.
- `lore/CANON.md` — what is settled.
- `lore/THREADS.md` — what is open, and how fast it may move.
- `content/faith/_index.md` — standing doctrine. It outranks everything.
- `data/calendar.toml` — the customary week, and observances announced ahead.

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
calendar holds for today and the week ahead (and what the homepage slip has already
announced), the state of the homepage slips, the last fortnight of teachings, and every image
with when it was last used.

**If the brief says today's teaching is already written**, do not write another. Bring the
slips up to date if they need it (step 5), check (step 7), and publish only if you changed
anything. Otherwise stop and say so.

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
   new detail like any other: it is planted in passing, not made the subject.
5. **Components** — zero to four, chosen for this piece. Not the same set as yesterday.
6. **Calendar** — whether the week stands as the brief shows it, or wants a lesser
   observance. Most days it stands. See *The calendar* below.

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
- `feast` set to today's observance as the calendar slip has it, in full — customary, dated
  or lesser. Leave it out on a day with nothing on.

**The homepage slips**, in `content/_index.md`. Each panel has an `id` and an `updated` date;
set `updated` to today on every panel you rewrite.

- `litany` — **every day.** Three or four lines, `lead` the call, `text` the response,
  `strong = true`. It may open with "Cat upon the kebab — ride for us."; the other lines are
  new today and draw on today's teaching or observance. Don't reuse yesterday's other lines.
- `calendar` — **every day.** Roll it forward: the first line is today (by its weekday
  abbreviation, as `lead`), then the next observances of the coming week, two to four lines
  in all, in order, no day twice. Start from the brief's week ahead. Keep what the slip has
  already announced — the faithful have been told — rather than quietly dropping or changing
  it. `strong = true` on the one that matters most that week. Use the `short` names from
  `data/calendar.toml` where there are any. Rewrite the handwritten `note` only occasionally.
  **A day with nothing on is never listed** — not today, not later in the week. When today
  has nothing on, the slip opens with the next observance and no line is `strong`.
- `signs` — **on Mondays** (or whenever the brief says it's due). Three to five short sighting
  reports for the week: small, specific, deadpan ("One (1) rooster, airborne, confirmed").
  One or two may echo the past week's teachings; one may plant something. No dates.

**The calendar.** It is custom, not law, and you are free to add to it — within the faith.

- **A lesser observance** is yours to invent: a commemoration of a sighting or an old
  teaching, a vigil for some overlooked surface, a day number worth marking, a season that is
  hard on roads, a thread's natural moment. It should be something this Church would
  plausibly keep, small and in its voice. Not every week — roughly one in a week or two, and
  rarely two in one week. The brief says when the last one was kept, and when one may be due.
- Within the coming week, it simply goes on the slip. If it is announced further ahead, or
  must be remembered for more than a week, add it to `dated` in `data/calendar.toml` with a
  `why`. Note it under *Observances* in `lore/THREADS.md` either way.
- **The customary week** — `weekly` in `data/calendar.toml`, which the Faith page shows —
  may change too: a custom may begin, move, or be retired. Treat that exactly like canon:
  only once it has been building across several teachings (see *Observances* in
  `THREADS.md`), never on a whim, and very rarely. When you change it, update `when` so the
  Faith page still reads true.

**The lore.** In the same commit:

- `lore/THREADS.md` — **this is where each day's lore goes.** Update any thread you touched
  (Last touched, a Log line). A detail planted today goes under *Planted*; a new witness under
  *Newcomers*; a lesser observance under *Observances*. A seed you used moves out of *Seeds*
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

## 7. Check

```bash
python3 scripts/teaching.py check
hugo --minify --printPathWarnings --panicOnWarning --renderToMemory
```

Fix every ERROR. Read every WARN and fix it unless you meant it; if you meant it, the commit
message says why. The build must succeed with no warnings — the deploy runs the same flags
and a warning there means the site does not update.

## 8. Publish

Commit only the files you meant to change, on `master`:

```bash
git add content/teachings/<file> content/_index.md lore/ data/calendar.toml
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
(`https://cat-kebab.tehgm.net/teachings/YYYY-MM-DD/<slug>/`), the form, the image, what lore
changed, whether the slips were updated, and anything you were unsure about.
