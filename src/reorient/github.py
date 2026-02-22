"""
GitHub client via gh CLI.
No token setup needed - uses existing `gh auth` session.
"""

import json
import os
import subprocess

from dotenv import load_dotenv

load_dotenv()

_org = os.getenv("GITHUB_ORG")
if not _org:
    raise EnvironmentError("GITHUB_ORG not set in .env")
ORG: str = _org

PR_FIELDS = "number,title,url,state,isDraft,createdAt,updatedAt,repository,author,labels"
MERGED_FIELDS = "number,title,url,closedAt,repository,author"


def _gh(*args: str) -> list[dict]:
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh error: {result.stderr.strip()}")
    return json.loads(result.stdout)


def my_open_prs(limit: int = 20) -> list[dict]:
    """Open PRs I authored in the configured org."""
    return _gh(
        "search", "prs",
        "--author", "@me",
        "--state", "open",
        "--owner", ORG,
        "--limit", str(limit),
        "--json", PR_FIELDS,
    )


def review_requests(limit: int = 20) -> list[dict]:
    """Open PRs waiting for my review."""
    return _gh(
        "search", "prs",
        "--review-requested", "@me",
        "--state", "open",
        "--owner", ORG,
        "--limit", str(limit),
        "--json", PR_FIELDS,
    )


def recently_merged(limit: int = 10) -> list[dict]:
    """PRs I merged recently - useful for standup."""
    return _gh(
        "search", "prs",
        "--author", "@me",
        "--merged",
        "--owner", ORG,
        "--limit", str(limit),
        "--json", MERGED_FIELDS,
    )


def pr_checks(repo: str, pr_number: int) -> list[dict]:
    """
    CI check status for a specific PR.
    repo should be in 'owner/name' format, e.g. 'myorg/myrepo'.
    """
    return _gh(
        "pr", "checks", str(pr_number),
        "--repo", repo,
        "--json", "name,status,conclusion,startedAt,completedAt",
    )
