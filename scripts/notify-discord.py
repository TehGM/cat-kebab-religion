#!/usr/bin/env python3
"""Announces new teachings on Discord, once they are live.

Run by the deploy workflow after the Pages deploy has succeeded:

    python3 scripts/notify-discord.py <before-sha> <after-sha>
    python3 scripts/notify-discord.py <before-sha> <after-sha> --dry-run

Every teaching *added* between the two commits is announced, each language to
its own webhook, as an embed in that language:

    YYYY-MM-DD-slug.md     →  DISCORD_WEBHOOK_EN
    YYYY-MM-DD-slug.pl.md  →  DISCORD_WEBHOOK_PL

Either webhook may be unset, and that language is simply skipped. Edits to an
existing teaching, the slips, the lore and the scheduled rebuilds announce
nothing, because they add no teaching. A Polish version pushed later than its
English one is announced when it lands. Drafts and teachings dated in the
future are skipped: they are not live.

--dry-run prints the payloads instead of posting them.

Announcing is a courtesy, never a gate. Whatever goes wrong — a deleted
webhook, Discord down, a teaching it cannot read, git itself — is reported as
a warning (a GitHub annotation when run in Actions) and the script still exits
0, so the site and the workflow are never failed by it.

Standard library only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from teaching import FILENAME_RE, HUGO_TOML, ROOT, as_date, day_no, read_front_matter  # noqa: E402

LANGS = {
    "en": {"webhook": "DISCORD_WEBHOOK_EN", "path": "", "day": "Day {n}"},
    "pl": {"webhook": "DISCORD_WEBHOOK_PL", "path": "pl/", "day": "Dzień {n}"},
}
COLOUR = 0xA8873C  # --gold, assets/css/main.css
USER_AGENT = "cat-kebab-religion-notifier (https://cat-kebab.tehgm.net, 1.0)"


def warn(message: str) -> None:
    """A warning that shows on the workflow run's summary in Actions, and as
    plain output anywhere else."""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::warning title=Discord announcement::{message}")
    else:
        print(f"WARN  {message}")


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def added_teachings(before: str, after: str) -> list[Path]:
    # A new branch, or a force-push that dropped `before`, leaves nothing to
    # diff against; fall back to the commit before `after`.
    if not before.strip("0") or git("cat-file", "-e", f"{before}^{{commit}}").returncode != 0:
        before = f"{after}~1"
    out = git("diff", "--name-only", "--diff-filter=A", before, after, "--", "content/teachings/")
    if out.returncode != 0:
        raise RuntimeError(f"git diff failed: {out.stderr.strip()}")
    return [ROOT / line for line in sorted(out.stdout.splitlines()) if line.strip()]


def language_of(path: Path) -> str | None:
    """"en" for YYYY-MM-DD-slug.md, "pl" for YYYY-MM-DD-slug.pl.md, else None."""
    name = path.name
    if name.endswith(".pl.md"):
        return "pl" if FILENAME_RE.match(name[: -len(".pl.md")] + ".md") else None
    return "en" if FILENAME_RE.match(name) else None


def embed_for(path: Path, lang: str, site: dict) -> dict | None:
    fm, _ = read_front_matter(path)
    date = as_date(fm.get("date"))
    today = dt.datetime.now(dt.timezone.utc).date()
    if fm.get("draft") or not date or date > today:
        return None

    base = site["baseURL"].rstrip("/") + "/"
    home = base + LANGS[lang]["path"]
    url = f"{home}teachings/{date.isoformat()}/{fm['slug']}/"
    params = site.get("languages", {}).get(lang, {}).get("params", {})

    footer = LANGS[lang]["day"].format(n=day_no(date))
    if fm.get("feast"):
        footer += f" · {fm['feast']}"
    description = str(fm.get("summary", ""))
    if fm.get("standfirst"):
        description = f"*{fm['standfirst']}*\n\n{description}"

    embed = {
        "title": str(fm.get("title", ""))[:256],
        "url": url,
        "description": description[:4096],
        "color": COLOUR,
        "author": {"name": params.get("church", site.get("title", "")), "url": home},
        "footer": {"text": footer},
        "timestamp": f"{date.isoformat()}T00:00:00Z",
    }
    if fm.get("image"):
        embed["image"] = {"url": f"{base}img/cat/{Path(fm['image']).name}"}
    return embed


def post(webhook: str, payload: dict) -> None:
    req = urllib.request.Request(
        webhook,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        resp.read()


def announce(args: argparse.Namespace) -> None:
    site = tomllib.loads(HUGO_TOML.read_text(encoding="utf-8"))
    for path in added_teachings(args.before, args.after):
        lang = language_of(path)
        if not lang or not path.exists():
            continue
        try:
            embed = embed_for(path, lang, site)
        except Exception as e:  # a teaching that won't parse is still not our failure
            warn(f"{path.name}: could not read it ({e}); not announced")
            continue
        if not embed:
            print(f"{path.name}: not live (draft or future-dated); not announced")
            continue
        payload = {"embeds": [embed], "allowed_mentions": {"parse": []}}
        if args.dry_run:
            print(f"--- {path.name} → {LANGS[lang]['webhook']}")
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            continue
        webhook = os.environ.get(LANGS[lang]["webhook"], "").strip()
        if not webhook:
            print(f"{path.name}: {LANGS[lang]['webhook']} is not set; not announced")
            continue
        try:
            post(webhook, payload)
            print(f"{path.name}: announced")
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            hint = " — the webhook may have been deleted" if e.code in (401, 404) else ""
            warn(f"{path.name}: Discord answered {e.code}{hint}: {detail}")
        except Exception as e:  # timeouts, DNS, TLS, a malformed URL in the secret
            warn(f"{path.name}: could not post to Discord: {e}")


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except AttributeError:
            pass

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    try:
        announce(args)
    except Exception as e:
        warn(f"announcing stopped early: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
