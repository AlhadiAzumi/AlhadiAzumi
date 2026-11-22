#!/usr/bin/env python3
"""Render small theme-aware README workbench SVGs.

Manual focus: data/workbench.json
Automatic data: latest pushed public, non-profile repository from GitHub REST.
No external fonts, JS, assets, or dependency packages needed.
"""
import datetime as dt
import html
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OWNER = "HsHs-dev"
OUT = ROOT / "assets"
STATE = ROOT / "data" / "last_public_push.json"
TODAY = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")


def fit(value, length=37):
    value = str(value).replace("\n", " ").strip()
    return value if len(value) <= length else value[:length - 1].rstrip() + "…"


def xml(value):
    return html.escape(str(value), quote=True)


def latest_public_repo():
    """Fetch a real update when possible; otherwise reuse last verified metadata."""
    req = urllib.request.Request(
        f"https://api.github.com/users/{OWNER}/repos?per_page=100&sort=pushed&type=owner",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "HsHs-dev-profile-workbench",
            **({"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"} if os.getenv("GITHUB_TOKEN") else {}),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            repos = json.load(response)
        if not isinstance(repos, list):
            raise ValueError("Unexpected GitHub REST response")
        candidates = [r for r in repos if r.get("name", "").lower() != OWNER.lower() and not r.get("fork")]
        if candidates:
            repo = max(candidates, key=lambda r: r.get("pushed_at") or "")
            result = {"name": repo["name"], "pushed_at": (repo.get("pushed_at") or "")[:10]}
            STATE.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            return result
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as err:
        print(f"GitHub fetch unavailable ({type(err).__name__}); using cached metadata if possible")
    if STATE.is_file():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            pass
    return {"name": "Awaiting first public sync", "pushed_at": ""}


def render(mode, focus, recent):
    is_dark = mode == "dark"
    bg = "#151C29" if is_dark else "#F6F9FE"
    line = "#3B4E66" if is_dark else "#D4DFED"
    ink = "#E6EDF7" if is_dark else "#253346"
    muted = "#9AABC0" if is_dark else "#5D7188"
    chip = "#233247" if is_dark else "#E6EFF8"
    teal = "#79DDEB" if is_dark else "#087F91"
    blue = "#79B8FF" if is_dark else "#235AA7"
    green = "#9BDD98" if is_dark else "#27754C"
    violet = "#C4B5FD" if is_dark else "#7252BB"
    amber = "#F2BB71" if is_dark else "#A65B0E"
    building, learning, exploring = [xml(fit(focus[key], 35)) for key in ("building", "learning", "exploring")]
    repo = xml(fit(recent.get("name", "Awaiting sync"), 27))
    pushed = xml(recent.get("pushed_at", "") or "pending first sync")
    info = f"Building {building}; learning {learning}; exploring {exploring}; latest public push {repo}, {pushed}."
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="660" height="174" viewBox="0 0 660 174" role="img" aria-labelledby="title desc">
<title id="title">Workbench status</title><desc id="desc">{info}</desc>
<style>
.cursor {{ animation:blink 1.4s steps(2,end) infinite; }}
.dot {{ animation:breathe 3s ease-in-out infinite; }}
@keyframes blink {{ 0%,49% {{opacity:1}} 50%,100% {{opacity:0}} }}
@keyframes breathe {{0%,100% {{opacity:.35}} 50% {{opacity:1}} }}
@media(prefers-reduced-motion:reduce) {{.cursor,.dot {{animation:none!important;opacity:1}} }}
</style>
<rect x="1" y="1" width="658" height="172" rx="14" fill="{bg}" stroke="{line}" stroke-width="1.5" />
<path d="M1 37H659" stroke="{line}" stroke-width="1.2"/>
<circle cx="19" cy="19" r="4" fill="#F19B99"/><circle cx="34" cy="19" r="4" fill="#F2BB71"/><circle cx="49" cy="19" r="4" fill="#9BDD98"/>
<text x="72" y="23" font-family="ui-monospace,Consolas,monospace" font-size="13" fill="{muted}">~/workbench</text>
<circle class="dot" cx="527" cy="19" r="4" fill="{green}"/>
<text x="539" y="23" font-family="ui-monospace,Consolas,monospace" font-size="11" fill="{muted}">in progress</text>
<text x="22" y="64" font-family="ui-monospace,Consolas,monospace" font-size="12" fill="{blue}">$</text>
<text x="40" y="64" font-family="ui-monospace,Consolas,monospace" font-size="12" fill="{ink}">status --now</text>
<rect class="cursor" x="141" y="53" width="7" height="13" rx="1" fill="{teal}"/>
<text x="22" y="94" font-family="ui-monospace,Consolas,monospace" font-size="11" fill="{muted}">building</text>
<text x="103" y="94" font-family="ui-monospace,Consolas,monospace" font-size="12" fill="{green}">{building}</text>
<text x="22" y="119" font-family="ui-monospace,Consolas,monospace" font-size="11" fill="{muted}">learning</text>
<text x="103" y="119" font-family="ui-monospace,Consolas,monospace" font-size="12" fill="{teal}">{learning}</text>
<text x="22" y="144" font-family="ui-monospace,Consolas,monospace" font-size="11" fill="{muted}">exploring</text>
<text x="103" y="144" font-family="ui-monospace,Consolas,monospace" font-size="12" fill="{violet}">{exploring}</text>
<path d="M396 50V155" stroke="{line}" stroke-dasharray="3 5"/>
<rect x="413" y="57" width="219" height="91" rx="9" fill="{chip}" />
<text x="429" y="78" font-family="ui-monospace,Consolas,monospace" font-size="10" letter-spacing="1" fill="{muted}">LAST PUBLIC REPO PUSH</text>
<text x="429" y="102" font-family="ui-monospace,Consolas,monospace" font-size="14" font-weight="bold" fill="{amber}">{repo}</text>
<text x="429" y="123" font-family="ui-monospace,Consolas,monospace" font-size="11" fill="{muted}">{pushed}</text>
<text x="505" y="161" font-family="ui-monospace,Consolas,monospace" font-size="9" fill="{muted}">sync {TODAY} UTC</text>
</svg>'''
    return svg


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    focus = json.loads((ROOT / "data" / "workbench.json").read_text(encoding="utf-8"))
    for key in ("building", "learning", "exploring"):
        if not isinstance(focus.get(key), str) or not focus[key].strip():
            raise ValueError(f"workbench.json needs a nonempty string for {key}")
    recent = latest_public_repo()
    for mode in ("dark", "light"):
        path = OUT / f"workbench.{mode}.svg"
        path.write_text(render(mode, focus, recent) + "\n", encoding="utf-8")
        print("Wrote", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
