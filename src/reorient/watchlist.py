"""
Watchlist — curated links at ~/.reorient/watchlist.md.
Parses URLs, enriches via the appropriate API, and reports changes.
"""

import json
import re
import subprocess
from pathlib import Path

from reorient import drive

_WATCHLIST_PATH = Path.home() / ".reorient" / "watchlist.md"

_DRIVE_RE = re.compile(r"https://docs\.google\.com/\S+|https://drive\.google\.com/\S+")
_GH_PR_RE = re.compile(r"https://github\.com/[\w-]+/[\w.-]+/pull/\d+")
_LINEAR_RE = re.compile(r"https://linear\.app/[\w-]+/issue/([\w-]+)")


def _parse_watchlist() -> dict[str, list[str]]:
    """Extract URLs from watchlist, grouped by type."""
    if not _WATCHLIST_PATH.exists():
        return {}
    text = _WATCHLIST_PATH.read_text()
    return {
        "drive": _DRIVE_RE.findall(text),
        "github_prs": _GH_PR_RE.findall(text),
        "linear": _LINEAR_RE.findall(text),
    }


def _enrich_github_pr(url: str) -> dict | None:
    """Get PR status via gh CLI."""
    try:
        result = subprocess.run(
            ["gh", "pr", "view", url, "--json", "number,title,state,updatedAt,url"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            return None
        return json.loads(result.stdout)
    except Exception:
        return None


def check() -> dict[str, list[dict]]:
    """Check all watchlist items for current status. Returns enriched data by type."""
    urls = _parse_watchlist()
    results: dict[str, list[dict]] = {"drive": [], "github_prs": [], "linear": []}

    if urls.get("drive"):
        results["drive"] = drive.enrich_urls(urls["drive"])

    for pr_url in urls.get("github_prs", []):
        enriched = _enrich_github_pr(pr_url)
        if enriched:
            results["github_prs"].append(enriched)

    # Linear issues returned as identifiers — caller can query via linear module
    results["linear"] = [{"identifier": lid} for lid in urls.get("linear", [])]

    return results
