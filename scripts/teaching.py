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
# The customary week and dated observances. Custom, not law — the writer keeps it.
CALENDAR_TOML = ROOT / "data" / "calendar.toml"

DAY_ABBR = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Signs & Wonders is rewritten once a week, on this weekday.
SIGNS_WEEKDAY = 0  # Monday

# An image used within this many days should be passed over unless nothing
# else fits. Not an error: the writer may overrule it, and should say why.
IMAGE_COOLDOWN_DAYS = 10

# The skill asks for a lesser observance roughly once a week or two. After this
# many days without one kept or announced, the brief says one may be due.
LESSER_DUE_DAYS = 10

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


def observances_on(d: dt.date, cal: dict) -> list[str]:
    """What data/calendar.toml holds for a day: dated observances first, then
    the customary one. Empty means an ordinary day."""
    out = []
    for e in cal.get("dated", []):
        if as_date(e.get("date")) == d:
            out.append(f"{e.get('name', '?')} (dated{': ' + e['why'] if e.get('why') else ''})")
    for e in cal.get("weekly", []):
        if e.get("day") == DAY_ABBR[d.weekday()]:
            out.append(f"{e.get('name', '?')} (custom)")
    return out


def customary_names(cal: dict) -> set[str]:
    """Names and short names of the customary week and of ordinary time,
    casefolded. A feast that is none of these is a lesser observance."""
    entries = cal.get("weekly", []) + [cal.get("ordinary", {})]
    return {str(e[k]).casefold() for e in entries for k in ("name", "short") if e.get(k)}


def slip_announcements(panel: dict) -> dict[dt.date, str]:
    """What the homepage calendar slip announces, by date. Its leads are
    weekday abbreviations, counted forward from the day it was last written."""
    upd = as_date(panel.get("updated"))
    out: dict[dt.date, str] = {}
    if not upd:
        return out
    for line in panel.get("lines", []):
        lead = line.get("lead")
        if lead in DAY_ABBR:
            offset = (DAY_ABBR.index(lead) - upd.weekday()) % 7
            out[upd + dt.timedelta(days=offset)] = str(line.get("text", ""))
    return out


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
    ordinary = cal.get("ordinary", {}).get("name", "Ordinary Kebab Time")
    obs = observances_on(today, cal)
    print(f"- Observance in the calendar: {'; '.join(obs) if obs else ordinary}")
    print(f"- Front matter date: {today.isoformat()}T00:00:00Z")
    print("- The page header already prints the weekday, the date, the day number and the feast.")
    print("  The teaching does not repeat them.")
    if todays:
        print(f"- ALREADY WRITTEN: {', '.join(t.path.name for t in todays)} — do not write another.")
    else:
        print("- Today's teaching: not yet written.")
    print()

    print("## The week ahead (for the Calendar of Feasts)")
    print("From data/calendar.toml, and what the homepage slip has already announced.")
    slip = next((p for p in load_panels() if p.get("id") == "calendar"), {})
    announced = slip_announcements(slip)
    for i in range(7):
        d = today + dt.timedelta(days=i)
        obs = observances_on(d, cal)
        line = "; ".join(obs) if obs else ordinary
        if d in announced:
            line += f"  — on the slip: {announced[d]!r}"
        mark = ""
        if i == 0:
            mark = " ← today" if obs else " ← today (nothing on: leave it off the slip, and set no line bold)"
        print(f"- {DAY_ABBR[d.weekday()]} {d.isoformat()}: {line}{mark}")
    later = sorted((as_date(e.get("date")), e.get("name", "?")) for e in cal.get("dated", [])
                   if as_date(e.get("date")) and as_date(e.get("date")) >= today + dt.timedelta(days=7))
    if later:
        print("Further ahead: " + "; ".join(f"{d} {n}" for d, n in later))

    # Lesser observances: a past teaching's `feast` off the customary week, or
    # one already announced — on the slip, or dated in data/calendar.toml.
    customary = customary_names(cal)
    kept = [t for t in past if t.fm.get("feast") and str(t.fm["feast"]).casefold() not in customary]
    ahead = {d: text for d, text in announced.items() if d >= today and text.casefold() not in customary}
    for e in cal.get("dated", []):
        d = as_date(e.get("date"))
        if d and d >= today:
            ahead.setdefault(d, e.get("name", "?"))
    if kept:
        since = (today - kept[0].date).days
        print(f"Last lesser observance kept: {kept[0].fm['feast']}, {kept[0].date} ({days(since)} ago)")
    elif past:
        since = (today - past[-1].date).days
        print(f"Last lesser observance kept: none since the record began ({days(since)} ago)")
    else:
        since = 0
    if ahead:
        d = min(ahead)
        print(f"Next lesser observance announced: {ahead[d]}, {d}")
    elif since >= LESSER_DUE_DAYS:
        print("  → one may be due (roughly one a week or two; see *The calendar* in the skill)")
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
    for e in cal.get("weekly", []):
        if e.get("day") not in DAY_ABBR:
            r.error(f"data/calendar.toml: weekly {e.get('name')!r} has day {e.get('day')!r}; "
                    f"use one of {', '.join(DAY_ABBR)}")
        for key in ("name", "short", "when"):
            if not e.get(key):
                r.error(f"data/calendar.toml: weekly {e.get('name')!r} is missing `{key}`")
    for e in cal.get("dated", []):
        if not isinstance(e.get("date"), dt.date):
            r.error(f"data/calendar.toml: dated {e.get('name')!r} needs date = YYYY-MM-DD (unquoted)")
        if not e.get("name"):
            r.error("data/calendar.toml: a dated observance has no `name`")
    if not cal.get("ordinary", {}).get("name"):
        r.error("data/calendar.toml: [ordinary] needs a `name`")


def check_translations(r: Report):
    """A translation is of something: its English original must exist, or it
    would be a page in one language with nothing behind it in the other."""
    for p in sorted(TEACHINGS.glob("*.md")):
        m = TRANSLATION_RE.match(p.name)
        if m and not (TEACHINGS / f"{m.group(1)}.md").exists():
            r.error(f"{p.name}: a translation with no English original ({m.group(1)}.md)")


def cmd_check(today: dt.date, everything: bool) -> int:
    r = Report()
    check_calendar_data(r)
    check_translations(r)
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
        return r.done()

    todays = [t for t in teachings if t.date == today]
    if not todays:
        r.error(f"no teaching dated {today}")
    for t in todays:
        check_structure(t, r, known_shortcodes, image_files)
        check_testimony_numbers(t, r, numbers)

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

    check_panels(today, r)
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
    if not 2 <= len(lines) <= 4:
        r.error(f"calendar: {len(lines)} lines; keep two to four")
    # A day with nothing on is left off the slip. Today is on it when
    # data/calendar.toml has something for today, or when the writer has
    # announced a lesser observance for it; otherwise the slip opens with the
    # next observance and sets nothing bold.
    calendar = load_calendar()
    ordinary = {str(v).casefold() for k, v in calendar.get("ordinary", {}).items() if k in ("name", "short")}
    week = {DAY_ABBR[(today + dt.timedelta(days=i)).weekday()]: i for i in range(7)}
    order = []
    for line in lines:
        lead = line.get("lead", "")
        if lead not in week:
            r.error(f"calendar: lead {lead!r} is not a day abbreviation ({', '.join(DAY_ABBR)})")
        else:
            order.append(week[lead])
        if str(line.get("text", "")).casefold() in ordinary:
            r.error(f"calendar: {lead} reads {line.get('text')!r}; a day with nothing on is left off")
    opens_today = bool(order) and order[0] == 0
    if observances_on(today, calendar) and not opens_today:
        r.error(f"calendar: must open with today ({DAY_ABBR[today.weekday()]}), which has an observance")
    elif not opens_today and any(line.get("strong") for line in lines):
        r.error("calendar: today has nothing on, so no line is set bold")
    if order != sorted(order) or len(set(order)) != len(order):
        r.error("calendar: days must run forward from today, each once")


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
