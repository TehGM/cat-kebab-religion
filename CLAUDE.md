# Cat Kebab Religion

A Hugo site of daily "teachings" about a cat who rides a kebab through space. The README
covers structure, front matter, components, images and the build; read it before changing
templates or content.

## Writing the daily teaching

Use the `daily-teaching` skill (`.claude/skills/daily-teaching/`). It is what the scheduled
routine runs, and it is the procedure for writing one by hand too. The lore it keeps to is in
`lore/` — `CANON.md` for what is settled (changed rarely), `THREADS.md` for what is open and
where each day's additions go. The Faith page (`content/faith/_index.md`) is standing doctrine
and outranks both; don't edit it as part of a daily teaching. Its list of observances comes
from `data/calendar.toml`, which the daily writer does keep.

`scripts/teaching.py` does the bookkeeping: `context` prints the brief for a day, `check`
validates that day's teaching and the homepage slips, `check --all` is what CI runs.

## Build

```bash
hugo --minify --printPathWarnings --printI18nWarnings --panicOnWarning
```

CI (`.github/workflows/deploy.yml`) runs the same flags; any warning fails the deploy and the
live site stays as it was. In cloud sessions Hugo is installed by the SessionStart hook
(`scripts/install-hugo.sh`).
