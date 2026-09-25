#!/usr/bin/env bash
# Installs Hugo in Claude Code cloud sessions, so the daily routine can build
# the site before it publishes. Run by the SessionStart hook in
# .claude/settings.json; does nothing on your own machine.
#
# Hugo comes from PyPI rather than GitHub releases: the cloud session's GitHub
# proxy only reaches repositories attached to the session, so a release
# download from gohugoio/hugo is refused. The `hugo` package on PyPI is the
# same extended binary, and PyPI is on the default network allowlist.
#
# Keep HUGO_VERSION in step with .github/workflows/deploy.yml.
set -euo pipefail

[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0

HUGO_VERSION=0.152.2

if command -v hugo >/dev/null 2>&1 && hugo version | grep -q "v${HUGO_VERSION}"; then
  exit 0
fi

if command -v uv >/dev/null 2>&1; then
  uv tool install --force "hugo==${HUGO_VERSION}" >&2
  bin="$(uv tool dir --bin)"
else
  python3 -m pip install --user --break-system-packages "hugo==${HUGO_VERSION}" >&2
  bin="$HOME/.local/bin"
fi

# Put it on PATH for the rest of the session.
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export PATH=\"${bin}:\$PATH\"" >> "$CLAUDE_ENV_FILE"
fi

"${bin}/hugo" version >&2
