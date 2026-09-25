# Cat Kebab Religion

A Hugo site of daily "teachings" about a cat who rides a kebab through space. The README
covers structure, front matter, components, images and the build; read it before changing
templates or content.

## Writing the daily teaching

Use the `daily-teaching` skill (`.claude/skills/daily-teaching/`). It is what the scheduled
routine runs, and it is the procedure for writing one by hand too. Every teaching is
published in English and Polish: the English first, then a Polish retelling beside it
(`*.pl.md`), per `polish.md` in the skill; the homepage slips have a Polish twin in
`content/_index.pl.md`. See "Localization" in the README. The lore it keeps to is in
`lore/` — `CANON.md` for what is settled (changed rarely), `THREADS.md` for what is open and
where each day's additions go. The Faith page (`content/faith/_index.md`) is standing doctrine
and outranks both; don't edit it (or its Polish version, `_index.pl.md`) as part of a daily
teaching. Observances live in `data/calendar.toml`, which the daily writer keeps: there
is no fixed week, and every feast is its own invention.

`scripts/teaching.py` does the bookkeeping: `context` prints the brief for a day, `check`
validates that day's teaching and the homepage slips, `check --all` is what CI runs.

## Build

```bash
hugo --minify --printPathWarnings --printI18nWarnings --panicOnWarning
```

CI (`.github/workflows/deploy.yml`) runs the same flags; any warning fails the deploy and the
live site stays as it was. In cloud sessions Hugo is installed by the SessionStart hook
(`scripts/install-hugo.sh`).
