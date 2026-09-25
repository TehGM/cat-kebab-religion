#!/usr/bin/env python3
"""The daily teaching's clerk.

Everything a writer needs to know that can be *derived* rather than
remembered: what day it is in the Eternal Orbit, which feast falls on it, what
the last fortnight looked like, which images were used recently, and whether
today's teaching and the homepage slips are in order.

    python3 scripts/teaching.py context            # brief for today's writer
    python3 scripts/teaching.py context --date 2026-10-02
    python3 scripts/teaching.py check              # today's teaching + slips
    python3 scripts/teaching.py check --all        # every teaching, structure only (CI)

Every teaching has a Polish version beside it (YYYY-MM-DD-slug.pl.md), and the
homepage slips and the calendar have Polish counterparts. `check` holds them to
the English: same slug, date and image, slips rewritten on the same days, a
Polish name for every observance. `check --all` only warns about a missing
translation, so a forgotten one never holds back the English site.

"Today" is the current UTC date unless --date says otherwise. Exit status is 1
when `check` finds an error; warnings are printed and do not fail.

Standard library only (Python 3.11+, for tomllib).
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEACHINGS = ROOT / "content" / "teachings"
HOME = ROOT / "content" / "_index.md"
IMAGES_TOML = ROOT / "data" / "images.toml"
IMAGES_DIR = ROOT / "assets" / "img" / "cat"
SHORTCODES_DIR = ROOT / "layouts" / "shortcodes"
HUGO_TOML = ROOT / "hugo.toml"
# Every observance, past and announced. There is no fixed week; the writer keeps it.
CALENDAR_TOML = ROOT / "data" / "calendar.toml"
# The Polish side. Teachings sit beside the English as *.pl.md.
HOME_PL = ROOT / "content" / "_index.pl.md"
CALENDAR_PL = ROOT / "data" / "l10n" / "pl" / "calendar.toml"
IMAGES_PL = ROOT / "data" / "l10n" / "pl" / "images.toml"

DAY_ABBR = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
# The Polish calendar slip's leads, in the same order.
DAY_ABBR_PL = ["Pn", "Wt", "Śr", "Cz", "Pt", "Sb", "Nd"]

# Signs & Wonders is rewritten once a week, on this weekday.
SIGNS_WEEKDAY = 0  # Monday

# An image used within this many days should be passed over unless nothing
# else fits. Not an error: the writer may overrule it, and should say why.
IMAGE_COOLDOWN_DAYS = 10

# The coming week — today and the next six days — holds this many observances,
# so the homepage slip has two to four lines.
WEEK_MIN, WEEK_MAX = 2, 4

# An observance that returns should not come back sooner than this, and should
# not keep landing on the same weekday: that is how a fixed week forms again.
RETURN_GAP_DAYS = 10

# Shortcodes built for the Faith page. A teaching has no business using them.
FAITH_ONLY = {"articles", "cols", "col", "feasts", "plainly"}

REQUIRED = ["title", "slug", "date", "summary", "form", "seal"]

FILENAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
# A translation sits beside its original with the language before the
# extension — 2026-09-25-slug.pl.md, _index.pl.md. This script checks the
# English only; translations are someone else's to keep. See the README.
TRANSLATION_RE = re.compile(r"^(.+)\.([a-z]{2}(?:-[a-z]+)?)\.md$")
SHORTCODE_RE = re.compile(r"\{\{[<%]\s*(?!/)([a-zA-Z0-9_-]+)")
IMAGE_ATTR_RE = re.compile(r"""\bimage\s*=\s*["']([^"']+)["']""")
ARTICLES = {"the", "a", "an"}


# --------------------------------------------------------------------------
# Reading the site

def read_front_matter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^\+\+\+\s*\n(.*?)\n\+\+\+\s*\n?(.*)$", text, re.S)
    if not m:
        raise ValueError(f"{path.name}: no TOML front matter (+++)")
    return tomllib.loads(m.group(1)), m.group(2)


def as_date(value) -> dt.date | None:
    if isinstance(value, dt.datetime):
        if value.tzinfo is not None:
            value = value.astimezone(dt.timezone.utc)
        return value.date()
    if isinstance(value, dt.date):
        return value
    return None


def epoch() -> dt.date:
    cfg = tomllib.loads(HUGO_TOML.read_text(encoding="utf-8"))
    return dt.date.fromisoformat(str(cfg.get("params", {}).get("epoch", "2024-04-28")))


def day_no(d: dt.date) -> int:
    """Mirrors layouts/partials/day-no.html."""
    return (d - epoch()).days + 1


def load_calendar() -> dict:
    return tomllib.loads(CALENDAR_TOML.read_text(encoding="utf-8"))


def dated(cal: dict) -> list[dict]:
    """Every observance with a usable date, oldest first."""
    out = [e for e in cal.get("dated", []) if as_date(e.get("date"))]
    return sorted(out, key=lambda e: as_date(e["date"]))


def observances_on(d: dt.date, cal: dict) -> list[dict]:
    """The observances data/calendar.toml holds for a day. Empty means an
    ordinary day. There should never be more than one."""
    return [e for e in dated(cal) if as_date(e["date"]) == d]


def coming_week(today: dt.date, cal: dict) -> list[dict]:
    """Observances from today through the next six days, in order."""
    end = today + dt.timedelta(days=7)
    return [e for e in dated(cal) if today <= as_date(e["date"]) < end]


def ordinary_names(cal: dict) -> set[str]:
    o = cal.get("ordinary", {})
    return {str(o[k]).casefold() for k in ("name", "short") if o.get(k)}


def previous_keeping(e: dict, cal: dict) -> dt.date | None:
    """When an observance of the same name was last kept before this one."""
    d = as_date(e["date"])
    name = str(e.get("name", "")).casefold()
    before = [as_date(x["date"]) for x in dated(cal)
              if str(x.get("name", "")).casefold() == name and as_date(x["date"]) < d]
    return max(before) if before else None


class Teaching:
    def __init__(self, path: Path):
        self.path = path
        self.fm, self.body = read_front_matter(path)
        self.date = as_date(self.fm.get("date"))
        self.shortcodes = SHORTCODE_RE.findall(self.body)
        body_images = IMAGE_ATTR_RE.findall(self.body)
        lead = self.fm.get("image") or ""
        self.images = [Path(i).name for i in ([lead] if lead else []) + body_images]
        prose = re.sub(r"\{\{[<%].*?[%>]\}\}", " ", self.body, flags=re.S)
        self.words = len(re.findall(r"[A-Za-z']+", prose))
        paragraphs = [p.strip() for p in prose.split("\n\n") if p.strip()]
        self.opening_line = paragraphs[0] if paragraphs else ""

    @property
    def title(self) -> str:
        return str(self.fm.get("title", ""))

    def opening(self) -> str:
        words = [w for w in re.findall(r"[A-Za-z']+", self.title)]
        while words and words[0].lower() in ARTICLES:
            words = words[1:]
        return words[0].lower() if words else ""


def load_teachings() -> list[Teaching]:
    out = []
    for p in sorted(TEACHINGS.glob("*.md")):
        if p.name == "_index.md" or TRANSLATION_RE.match(p.name):
            continue
        out.append(Teaching(p))
    out.sort(key=lambda t: (t.date or dt.date.min, t.path.name), reverse=True)
    return out


def load_images() -> list[dict]:
    """The catalogued images. Only these can be chosen: a file with no entry has
    no `depicts` to choose it by, and cataloguing is done by hand."""
    data = tomllib.loads(IMAGES_TOML.read_text(encoding="utf-8"))
    return data.get("image", [])


def load_calendar_pl() -> dict:
    if not CALENDAR_PL.exists():
        return {}
    return tomllib.loads(CALENDAR_PL.read_text(encoding="utf-8"))


def polish_name(entry: dict, cal_pl: dict, kind: str) -> dict:
    """The Polish words for one calendar entry: kind is "dated" or "ordinary".
    Empty when it has none."""
    if kind == "dated":
        d = as_date(entry.get("date"))
        return cal_pl.get("dated", {}).get(d.isoformat() if d else "", {})
    return cal_pl.get("ordinary", {})


def polish_path(t: "Teaching") -> Path:
    return t.path.with_name(t.path.stem + ".pl.md")


def load_panels_pl() -> list[dict]:
    if not HOME_PL.exists():
        return []
    fm, _ = read_front_matter(HOME_PL)
    return fm.get("panels", [])


def load_panels() -> list[dict]:
    fm, _ = read_front_matter(HOME)
    return fm.get("panels", [])


def last_used(teachings: list[Teaching], before: dt.date) -> dict[str, dt.date]:
    """Most recent date each image was used by a teaching dated before `before`."""
    seen: dict[str, dt.date] = {}
    for t in teachings:
        if not t.date or t.date >= before:
            continue
        for img in t.images:
            if img not in seen or t.date > seen[img]:
                seen[img] = t.date
    return seen


def days(n: int) -> str:
    return f"{n} day" if n == 1 else f"{n} days"


def shorten(s: str, n: int) -> str:
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "…"


# --------------------------------------------------------------------------
# context

def cmd_context(today: dt.date, show_images: bool) -> int:
    teachings = load_teachings()
    todays = [t for t in teachings if t.date == today]
    past = [t for t in teachings if t.date and t.date < today]

    print(f"# Brief for {today.isoformat()}")
    print()
    print(f"- Weekday: {today.strftime('%A')}")
    print(f"- Day of the Eternal Orbit: {day_no(today)}")
    cal = load_calendar()
    cal_pl = load_calendar_pl()
    ordinary = cal.get("ordinary", {}).get("name", "Ordinary Kebab Time")
    obs = observances_on(today, cal)
    if obs:
        e = obs[0]
        print(f"- Observance today: {e.get('name')} — set `feast` to this")
        print(f"  In Polish: {polish_name(e, cal_pl, 'dated').get('name', '?')}"
              " — the Polish version's `feast` uses this name")
    else:
        print(f"- Observance today: none announced ({ordinary}) — leave `feast` out")
    print(f"- Front matter date: {today.isoformat()}T00:00:00Z")
    print("- The page header already prints the weekday, the date, the day number and the feast.")
    print("  The teaching does not repeat them.")
    if todays:
        print(f"- ALREADY WRITTEN: {', '.join(t.path.name for t in todays)} — do not write another.")
        for t in todays:
            pl = polish_path(t)
            print(f"  Polish version: {pl.name} — {'written' if pl.exists() else 'NOT YET WRITTEN'}")
    else:
        print("- Today's teaching: not yet written, in either language.")
    print()

    print("## The calendar (data/calendar.toml)")
    print("There is no fixed week: every observance is announced here by the writer, a few days")
    print("ahead. The homepage slip is written from this. See *The calendar* in the skill.")
    week = coming_week(today, cal)
    by_day = {as_date(e["date"]): e for e in week}
    for i in range(7):
        d = today + dt.timedelta(days=i)
        mark = " ← today" if i == 0 else ""
        e = by_day.get(d)
        if e:
            pl = polish_name(e, cal_pl, "dated").get("name", "NO POLISH NAME")
            why = f" — {e['why']}" if e.get("why") else ""
            print(f"- {DAY_ABBR[d.weekday()]}/{DAY_ABBR_PL[d.weekday()]} {d.isoformat()}: "
                  f"{e.get('name')} [pl: {pl}]{why}{mark}")
        else:
            print(f"- {DAY_ABBR[d.weekday()]}/{DAY_ABBR_PL[d.weekday()]} {d.isoformat()}: —{mark}")
    n = len(week)
    if n < WEEK_MIN:
        print(f"  → {n} in the coming week; announce {WEEK_MIN - n} more, so it holds "
              f"{WEEK_MIN}–{WEEK_MAX}. Prefer the far end of the week, so each is announced ahead.")
    elif n > WEEK_MAX:
        print(f"  → {n} in the coming week; {WEEK_MIN}–{WEEK_MAX} is the measure")
    else:
        print(f"  ({n} in the coming week; {WEEK_MIN}–{WEEK_MAX} is the measure — add one only if "
              "the week wants it)")
    later = [e for e in dated(cal) if as_date(e["date"]) >= today + dt.timedelta(days=7)]
    if later:
        print("Further ahead: " + "; ".join(f"{e['date']} {e.get('name', '?')}" for e in later))

    kept: dict[str, list[dt.date]] = {}
    for e in dated(cal):
        if as_date(e["date"]) < today:
            kept.setdefault(str(e.get("name", "?")), []).append(as_date(e["date"]))
    if kept:
        print("Kept before (most recent first) — what could return:")
        for name, dates in sorted(kept.items(), key=lambda kv: max(kv[1]), reverse=True)[:20]:
            last = max(dates)
            print(f"- {name} — {len(dates)}× · last {last} ({last.strftime('%a')}, "
                  f"{days((today - last).days)} ago)")
    else:
        print("Kept before: nothing yet.")
    print()

    print("## Homepage slips")
    for p in load_panels():
        pid = p.get("id", "?")
        upd = as_date(p.get("updated"))
        if upd is None:
            age = "never"
        else:
            n = (today - upd).days
            age = "today" if n == 0 else f"{days(n)} ago"
        due = ""
        if pid == "litany":
            due = "  → rewrite today" if upd != today else "  (done today)"
        elif pid == "signs":
            owed = today.weekday() == SIGNS_WEEKDAY and upd != today
            stale = upd is None or (today - upd).days >= 7
            due = "  → rewrite today" if (owed or stale) else f"  (next on {DAY_ABBR[SIGNS_WEEKDAY]})"
        elif pid == "calendar":
            due = "  → roll forward today" if upd != today else "  (done today)"
        print(f"- {pid}: updated {age}{due}")
        for line in p.get("lines", []):
            lead = f"{line['lead']} — " if line.get("lead") else ""
            print(f"    {lead}{line.get('text', '')}")
        if p.get("note"):
            print(f"    note: {p['note']}")
    print()

    print("## Homepage slips, in Polish (content/_index.pl.md)")
    print("Rewritten on the same days as the English; the Polish words are their own.")
    for p in load_panels_pl():
        print(f"- {p.get('id', '?')}: updated {as_date(p.get('updated'))}")
        for line in p.get("lines", []):
            lead = f"{line['lead']} — " if line.get("lead") else ""
            print(f"    {lead}{line.get('text', '')}")
        if p.get("note"):
            print(f"    note: {p['note']}")
    print()

    recent = past[:14]
    print(f"## The last {len(recent)} teachings (newest first)")
    if not recent:
        print("- None. The record begins here.")
    for t in recent:
        fm = t.fm
        comps = ", ".join(dict.fromkeys(t.shortcodes)) or "none"
        print(f"- {t.date} (day {day_no(t.date)}) — {t.title}")
        print(f"    form: {fm.get('form', '?')} · seal: {fm.get('seal', '')} · feast: {fm.get('feast', '')}")
        print(f"    tags: {', '.join(fm.get('tags', []))} · words: {t.words} · components: {comps}")
        print(f"    images: {', '.join(t.images) or 'none'}")
        print(f"    summary: {shorten(fm.get('summary', ''), 200)}")
        print(f"    opens: {shorten(t.opening_line, 160)}")
    print()

    week = past[:7]
    if week:
        print("## Avoid repeating (last 7)")
        print(f"- Forms: {', '.join(str(t.fm.get('form', '?')) for t in week)}")
        print(f"- Title openings: {', '.join(t.opening() for t in week)}")
        print(f"- Seals: {', '.join(str(t.fm.get('seal', '')) for t in week)}")
        print()

    entries = load_images()
    used = last_used(teachings, today)
    nos = [e["no"] for e in entries if isinstance(e.get("no"), int)]
    if nos:
        print(f"Highest sighting number in use: {max(nos)}")
        print()

    if show_images:
        print(f"## Images (cooldown {IMAGE_COOLDOWN_DAYS} days)")
        for e in entries:
            if e.get("hidden"):
                continue
            f = e["file"]
            when = used.get(f)
            if when:
                ago = (today - when).days
                status = f"used {when} ({ago}d ago)" + (" — COOLING DOWN" if ago < IMAGE_COOLDOWN_DAYS else "")
            else:
                status = "never used in a teaching"
            print(f"- {f} · № {e.get('no', '?')} · {e.get('title', '')} · {status}")
            print(f"    keywords: {', '.join(e.get('keywords', []))}")
            print(f"    depicts: {' '.join(str(e.get('depicts', '')).split())}")
    return 0


# --------------------------------------------------------------------------
# check

class Report:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str):
        self.errors.append(msg)

    def warn(self, msg: str):
        self.warnings.append(msg)

    def done(self) -> int:
        for w in self.warnings:
            print(f"WARN  {w}")
        for e in self.errors:
            print(f"ERROR {e}")
        if not self.errors:
            print(f"OK ({len(self.warnings)} warning{'s' if len(self.warnings) != 1 else ''})")
        return 1 if self.errors else 0


def check_structure(t: Teaching, r: Report, known_shortcodes: set[str], image_files: set[str]):
    name = t.path.name
    fm = t.fm
    for key in REQUIRED:
        if not fm.get(key):
            r.error(f"{name}: missing `{key}`")
    if fm.get("draft", False):
        r.error(f"{name}: draft = true — it would never be published")

    m = FILENAME_RE.match(name)
    if not m:
        r.error(f"{name}: filename must be YYYY-MM-DD-slug.md, lowercase, hyphenated")
    else:
        if fm.get("slug") and fm["slug"] != m.group(2):
            r.error(f"{name}: slug {fm['slug']!r} does not match the filename's {m.group(2)!r}")
        if t.date and t.date.isoformat() != m.group(1):
            r.error(f"{name}: date {t.date} does not match the filename's {m.group(1)}")

    raw = fm.get("date")
    if isinstance(raw, dt.datetime):
        if raw.tzinfo is None or raw.utcoffset() != dt.timedelta(0) or raw.time() != dt.time(0, 0):
            r.error(f"{name}: date must be midnight UTC, e.g. {t.date}T00:00:00Z — a later hour "
                    "can be in the future at build time, and Hugo does not publish the future")
    elif raw is not None:
        r.error(f"{name}: date must be a TOML datetime, e.g. 2026-10-02T00:00:00Z")

    for sc in t.shortcodes:
        if sc not in known_shortcodes:
            r.error(f"{name}: unknown shortcode `{sc}`")
        elif sc in FAITH_ONLY:
            r.warn(f"{name}: `{sc}` is a Faith-page component, not meant for teachings")

    for img in t.images:
        if img not in image_files:
            r.error(f"{name}: image {img!r} is not in assets/img/cat/")

    if fm.get("caption") and not fm.get("image"):
        r.warn(f"{name}: caption without an image is never shown")

    summary = str(fm.get("summary", ""))
    if len(summary) > 240:
        r.warn(f"{name}: summary is {len(summary)} characters; keep it to one or two sentences")
    seal = str(fm.get("seal", ""))
    if len(seal) > 24:
        r.warn(f"{name}: seal is {len(seal)} characters; the stamp wants 24 or fewer")



def check_testimony_numbers(t: Teaching, r: Report, numbers: dict[str, int]):
    for m in re.finditer(r"\{\{%\s*testimony\b([^%]*)%\}\}", t.body):
        attrs = m.group(1)
        img = IMAGE_ATTR_RE.search(attrs)
        no = re.search(r"""\bno\s*=\s*["']([^"']+)["']""", attrs)
        if img and no:
            f = Path(img.group(1)).name
            given = int(re.sub(r"\D", "", no.group(1)) or 0)
            if f in numbers and numbers[f] != given:
                r.warn(f"{t.path.name}: testimony shows {f} as № {no.group(1)}, "
                       f"but data/images.toml records it as № {numbers[f]:,}")


def check_calendar_data(r: Report):
    try:
        cal = load_calendar()
    except (OSError, tomllib.TOMLDecodeError) as e:
        r.error(f"data/calendar.toml: {e}")
        return
    if "weekly" in cal:
        r.error("data/calendar.toml: there is no fixed week — every observance is a `dated` entry")
    seen: dict[dt.date, str] = {}
    for e in cal.get("dated", []):
        d = e.get("date")
        if not isinstance(d, dt.date) or isinstance(d, dt.datetime):
            r.error(f"data/calendar.toml: dated {e.get('name')!r} needs date = YYYY-MM-DD (unquoted)")
            continue
        for key in ("name", "short"):
            if not e.get(key):
                r.error(f"data/calendar.toml: dated {e.get('name')!r} ({d}) is missing `{key}`")
        if d in seen:
            r.error(f"data/calendar.toml: two observances on {d} ({seen[d]!r}, {e.get('name')!r}); "
                    "one a day at most")
        seen[d] = str(e.get("name"))
        if str(e.get("name", "")).casefold() in ordinary_names(cal):
            r.error(f"data/calendar.toml: {d} is called {e.get('name')!r} — a day with nothing on "
                    "has no entry")
    if not cal.get("ordinary", {}).get("name"):
        r.error("data/calendar.toml: [ordinary] needs a `name`")


def check_calendar_week(today: dt.date, r: Report):
    """The coming week holds two to four observances, and none of them is
    turning into a fixed day or a fixed rhythm."""
    cal = load_calendar()
    week = coming_week(today, cal)
    if len(week) < WEEK_MIN:
        r.error(f"calendar: {len(week)} observance(s) from {today} to "
                f"{today + dt.timedelta(days=6)}; announce {WEEK_MIN}–{WEEK_MAX} in "
                "data/calendar.toml")
    elif len(week) > WEEK_MAX:
        r.warn(f"calendar: {len(week)} observances in the coming week; {WEEK_MIN}–{WEEK_MAX} is the measure")
    for e in week:
        d = as_date(e["date"])
        prev = previous_keeping(e, cal)
        if not prev:
            continue
        if (d - prev).days < RETURN_GAP_DAYS:
            r.warn(f"calendar: {e.get('name')!r} on {d} returns {days((d - prev).days)} after "
                   f"{prev}; let it rest at least {RETURN_GAP_DAYS} days")
        if d.weekday() == prev.weekday():
            r.warn(f"calendar: {e.get('name')!r} falls on a {d.strftime('%A')} again, as on "
                   f"{prev} — a returning feast on the same weekday is how a fixed week forms")


def check_translations(r: Report):
    """A translation is of something: its English original must exist, or it
    would be a page in one language with nothing behind it in the other."""
    for p in sorted(TEACHINGS.glob("*.md")):
        m = TRANSLATION_RE.match(p.name)
        if m and not (TEACHINGS / f"{m.group(1)}.md").exists():
            r.error(f"{p.name}: a translation with no English original ({m.group(1)}.md)")


POLISH_REQUIRED = ["title", "slug", "date", "summary", "seal"]
# A Markdown link from the root that is not under /pl/ leads out of Polish.
ROOT_LINK_RE = re.compile(r"\]\((/(?!pl/)[^)]*)\)")


def check_polish(t: Teaching, r: Report, strict: bool, known_shortcodes: set[str],
                 image_files: set[str], cal: dict, cal_pl: dict):
    """The Polish version of one teaching. A retelling, not a translation — so
    only what must match is held to the English: the slug (URLs mirror the
    English), the date, the picture. Missing it is an error on the day and a
    warning in CI."""
    path = polish_path(t)
    if not path.exists():
        (r.error if strict else r.warn)(f"{t.path.name}: no Polish version ({path.name})")
        return
    name = path.name
    try:
        pl = Teaching(path)
    except (ValueError, tomllib.TOMLDecodeError) as e:
        r.error(f"{name}: {e}")
        return
    fm = pl.fm
    for key in POLISH_REQUIRED:
        if not fm.get(key):
            r.error(f"{name}: missing `{key}`")
    if fm.get("draft", False):
        r.error(f"{name}: draft = true — it would never be published")
    if fm.get("slug") != t.fm.get("slug"):
        r.error(f"{name}: slug {fm.get('slug')!r} must be the English one, {t.fm.get('slug')!r} — "
                "Polish URLs mirror the English")
    if fm.get("date") != t.fm.get("date"):
        r.error(f"{name}: date must be the English one, {t.fm.get('date')}")
    if (fm.get("image") or "") != (t.fm.get("image") or ""):
        r.error(f"{name}: image {fm.get('image')!r} differs from the English {t.fm.get('image')!r}")
    for sc in pl.shortcodes:
        if sc not in known_shortcodes:
            r.error(f"{name}: unknown shortcode `{sc}`")
        elif sc in FAITH_ONLY:
            r.warn(f"{name}: `{sc}` is a Faith-page component, not meant for teachings")
    for img in pl.images:
        if img not in image_files:
            r.error(f"{name}: image {img!r} is not in assets/img/cat/")
    for m in ROOT_LINK_RE.finditer(pl.body):
        r.error(f"{name}: link to {m.group(1)!r} leads to the English site; use /pl{m.group(1)}")
    seal = str(fm.get("seal", ""))
    if len(seal) > 24:
        r.warn(f"{name}: seal is {len(seal)} characters; the stamp wants 24 or fewer")

    # The day's observance goes by the Polish calendar's name for it.
    obs = observances_on(t.date, cal) if t.date else []
    if obs:
        want = polish_name(obs[0], cal_pl, "dated").get("name")
        if want and str(fm.get("feast", "")).casefold() != want.casefold():
            r.warn(f"{name}: feast {fm.get('feast')!r}; the Polish calendar calls "
                   f"{obs[0].get('name')!r} {want!r}")
    elif fm.get("feast") and not t.fm.get("feast"):
        r.warn(f"{name}: has a feast, {fm.get('feast')!r}, and the English has none")


def check_polish_calendar(r: Report, strict: bool):
    """Every observance in data/calendar.toml has Polish words, or the Polish
    slip and teaching have nothing to call it."""
    where = CALENDAR_PL.relative_to(ROOT).as_posix()
    say = r.error if strict else r.warn
    try:
        cal, cal_pl = load_calendar(), load_calendar_pl()
    except (OSError, tomllib.TOMLDecodeError) as e:
        r.error(f"{where}: {e}")
        return
    if "weekly" in cal_pl:
        r.error(f"{where}: there is no fixed week — remove [weekly.*]")
    for kind, entries in (("dated", dated(cal)), ("ordinary", [cal.get("ordinary", {})])):
        for e in entries:
            pl = polish_name(e, cal_pl, kind)
            label = f'[dated."{as_date(e.get("date"))}"]' if kind == "dated" else "[ordinary]"
            for key in ("name", "short"):
                if not pl.get(key):
                    say(f"{where}: {label} ({e.get('name')!r}) has no Polish `{key}`")


def check_polish_images(r: Report):
    """Catalogued images with no Polish title show their English one on the
    Polish wall. Cataloguing is done by hand, so this only warns."""
    if not IMAGES_PL.exists():
        return
    pl = tomllib.loads(IMAGES_PL.read_text(encoding="utf-8"))
    missing = [e["file"] for e in load_images() if e.get("title") and not pl.get(e["file"], {}).get("title")]
    if missing:
        r.warn(f"{IMAGES_PL.relative_to(ROOT).as_posix()}: no Polish title for {', '.join(missing)}")


def check_polish_panels(r: Report):
    """The Polish slips are rewritten on the same days as the English ones, and
    the Polish calendar slip names the same days, bold where the English is."""
    en = {p.get("id"): p for p in load_panels()}
    pl = {p.get("id"): p for p in load_panels_pl()}
    for pid, panel in en.items():
        if pid not in pl:
            r.error(f"content/_index.pl.md: no panel with id = {pid!r}")
            continue
        if as_date(pl[pid].get("updated")) != as_date(panel.get("updated")):
            r.error(f"{pid} (Polish): updated {as_date(pl[pid].get('updated'))}, but the English "
                    f"was updated {as_date(panel.get('updated'))} — rewrite both on the same day")
    if "calendar" in en and "calendar" in pl:
        want = [DAY_ABBR_PL[DAY_ABBR.index(l.get("lead"))] if l.get("lead") in DAY_ABBR else "?"
                for l in en["calendar"].get("lines", [])]
        got = [l.get("lead") for l in pl["calendar"].get("lines", [])]
        if got != want:
            r.error(f"calendar (Polish): leads {got}, but the English slip names {want}")
        elif [bool(l.get("strong")) for l in en["calendar"].get("lines", [])] != \
                [bool(l.get("strong")) for l in pl["calendar"].get("lines", [])]:
            r.error("calendar (Polish): bold lines differ from the English slip")
        cal, cal_pl = load_calendar(), load_calendar_pl()
        upd = as_date(pl["calendar"].get("updated"))
        for line in pl["calendar"].get("lines", []) if upd else []:
            lead = line.get("lead")
            if lead not in DAY_ABBR_PL:
                continue
            d = upd + dt.timedelta(days=(DAY_ABBR_PL.index(lead) - upd.weekday()) % 7)
            for e in observances_on(d, cal):
                words = polish_name(e, cal_pl, "dated")
                ok = {str(words.get(k, "")).casefold() for k in ("name", "short")}
                if str(line.get("text", "")).casefold() not in ok:
                    r.warn(f"calendar (Polish): {lead} reads {line.get('text')!r}; "
                           f"{CALENDAR_PL.relative_to(ROOT).as_posix()} calls it {words.get('short')!r}")


def cmd_check(today: dt.date, everything: bool) -> int:
    r = Report()
    check_calendar_data(r)
    check_translations(r)
    check_polish_calendar(r, strict=not everything)
    cal, cal_pl = load_calendar(), load_calendar_pl()
    teachings = load_teachings()
    known_shortcodes = {p.stem for p in SHORTCODES_DIR.glob("*.html")}
    image_files = {p.name for p in IMAGES_DIR.iterdir()}
    entries = load_images()
    numbers = {e["file"]: e["no"] for e in entries if isinstance(e.get("no"), int)}

    by_date: dict[dt.date, list[str]] = {}
    for t in teachings:
        if t.date:
            by_date.setdefault(t.date, []).append(t.path.name)
    for d, names in by_date.items():
        if len(names) > 1:
            r.error(f"two teachings on {d}: {', '.join(names)} — there is one teaching per day")

    if everything:
        for t in teachings:
            check_structure(t, r, known_shortcodes, image_files)
            check_testimony_numbers(t, r, numbers)
            check_polish(t, r, False, known_shortcodes, image_files, cal, cal_pl)
        return r.done()

    todays = [t for t in teachings if t.date == today]
    if not todays:
        r.error(f"no teaching dated {today}")
    for t in todays:
        check_structure(t, r, known_shortcodes, image_files)
        check_testimony_numbers(t, r, numbers)
        check_polish(t, r, True, known_shortcodes, image_files, cal, cal_pl)

        used = last_used(teachings, today)
        for img in t.images:
            when = used.get(img)
            if when and (today - when).days < IMAGE_COOLDOWN_DAYS:
                r.warn(f"{t.path.name}: {img} was used {days((today - when).days)} ago ({when}); "
                       "fine only if nothing else fitted — say so in the commit message")

        week = [p for p in teachings if p.date and p.date < today][:7]
        form = t.fm.get("form")
        if form and form in [p.fm.get("form") for p in week[:3]]:
            r.warn(f"{t.path.name}: form {form!r} was used in the last three teachings")
        opening = t.opening()
        if opening and opening in [p.opening() for p in week[:5]]:
            r.warn(f"{t.path.name}: title opens with {opening!r}, like one of the last five")
        seal = t.fm.get("seal")
        if seal and seal in [p.fm.get("seal") for p in week]:
            r.warn(f"{t.path.name}: seal {seal!r} was used in the last seven")

        obs = observances_on(today, cal)
        feast = t.fm.get("feast")
        if obs and str(feast or "").casefold() != str(obs[0].get("name", "")).casefold():
            r.error(f"{t.path.name}: feast is {feast!r}; data/calendar.toml has "
                    f"{obs[0].get('name')!r} today")
        elif not obs and feast:
            r.error(f"{t.path.name}: feast is {feast!r}, but data/calendar.toml has nothing on "
                    f"{today} — announce it there, or leave `feast` out")

    check_calendar_week(today, r)

    check_panels(today, r)
    check_polish_panels(r)
    check_polish_images(r)
    return r.done()


def check_panels(today: dt.date, r: Report):
    panels = {p.get("id"): p for p in load_panels()}
    missing = [pid for pid in ("litany", "signs", "calendar") if pid not in panels]
    for pid in missing:
        r.error(f"content/_index.md: no panel with id = {pid!r}")
    if missing:
        return

    litany = panels["litany"]
    if as_date(litany.get("updated")) != today:
        r.error("litany: not rewritten today (set `updated` when you rewrite it)")
    n = len(litany.get("lines", []))
    if not 3 <= n <= 4:
        r.warn(f"litany: {n} lines; three or four is the form")

    signs = panels["signs"]
    upd = as_date(signs.get("updated"))
    if today.weekday() == SIGNS_WEEKDAY and upd != today:
        r.error(f"signs: it is {DAY_ABBR[SIGNS_WEEKDAY]}, and Signs & Wonders is rewritten today")
    elif upd is None or (today - upd).days >= 7:
        r.error("signs: more than a week old; rewrite it")

    cal = panels["calendar"]
    if as_date(cal.get("updated")) != today:
        r.error("calendar: not rolled forward today (set `updated` when you do)")
    lines = cal.get("lines", [])
    # The slip is written from data/calendar.toml: the coming week's
    # observances, in order, up to four. When today has nothing on it opens
    # with the next one and sets nothing bold.
    calendar = load_calendar()
    want = coming_week(today, calendar)[:WEEK_MAX]
    want_leads = [DAY_ABBR[as_date(e["date"]).weekday()] for e in want]
    got_leads = [line.get("lead") for line in lines]
    if got_leads != want_leads:
        r.error(f"calendar: slip names {got_leads}, but data/calendar.toml has {want_leads} "
                "for the coming week — write the slip from the calendar")
    else:
        for line, e in zip(lines, want):
            ok = {str(e.get(k, "")).casefold() for k in ("name", "short")}
            if str(line.get("text", "")).casefold() not in ok:
                r.error(f"calendar: {line.get('lead')} reads {line.get('text')!r}; "
                        f"data/calendar.toml calls it {e.get('short')!r}")
    if not observances_on(today, calendar) and any(line.get("strong") for line in lines):
        r.error("calendar: today has nothing on, so no line is set bold")


# --------------------------------------------------------------------------

def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except AttributeError:
            pass

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("context", help="print the brief for a day's writer")
    c.add_argument("--date", help="YYYY-MM-DD; defaults to today, UTC")
    c.add_argument("--no-images", action="store_true", help="omit the image catalogue")
    k = sub.add_parser("check", help="validate a day's teaching and the homepage slips")
    k.add_argument("--date", help="YYYY-MM-DD; defaults to today, UTC")
    k.add_argument("--all", action="store_true", help="structure of every teaching only (for CI)")
    args = ap.parse_args()

    today = dt.date.fromisoformat(args.date) if args.date else dt.datetime.now(dt.timezone.utc).date()
    if args.cmd == "context":
        return cmd_context(today, not args.no_images)
    return cmd_check(today, args.all)


if __name__ == "__main__":
    sys.exit(main())
