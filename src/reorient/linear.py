"""
Linear client (GraphQL API).

Auth: set LINEAR_API_KEY in .env
Get your key at: linear.app → Settings → API → Personal API keys
"""

import os
from dotenv import load_dotenv
import httpx

load_dotenv()

_API_URL = "https://api.linear.app/graphql"


def _headers() -> dict:
    key = os.getenv("LINEAR_API_KEY")
    if not key:
        raise EnvironmentError("LINEAR_API_KEY not set in .env")
    return {"Authorization": key, "Content-Type": "application/json"}


def _query(q: str, variables: dict | None = None) -> dict:
    resp = httpx.post(
        _API_URL,
        json={"query": q, "variables": variables or {}},
        headers=_headers(),
    )
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(f"Linear API error: {data['errors']}")
    return data["data"]


def viewer() -> dict:
    """Current authenticated user."""
    data = _query("{ viewer { id name email } }")
    return data["viewer"]


def my_issues(states: list[str] | None = None) -> list[dict]:
    """
    Issues assigned to me, optionally filtered by state type.
    State types: 'triage', 'backlog', 'unstarted', 'started', 'completed', 'cancelled'
    Defaults to active states only (triage, unstarted, started).
    """
    if states is None:
        states = ["triage", "unstarted", "started"]

    state_filter = ", ".join(f'"{s}"' for s in states)

    q = f"""
    {{
      issues(
        filter: {{
          assignee: {{ isMe: {{ eq: true }} }}
          state: {{ type: {{ in: [{state_filter}] }} }}
        }}
        orderBy: updatedAt
      ) {{
        nodes {{
          id identifier title priority
          state {{ name type }}
          project {{ name }}
          team {{ name }}
          updatedAt
          url
        }}
      }}
    }}
    """
    return _query(q)["issues"]["nodes"]


def in_progress() -> list[dict]:
    """Issues I'm currently working on (state type = started)."""
    return my_issues(states=["started"])


def recently_completed(limit: int = 10) -> list[dict]:
    """Issues I completed recently - useful for standup."""
    q = f"""
    {{
      issues(
        first: {limit}
        filter: {{
          assignee: {{ isMe: {{ eq: true }} }}
          state: {{ type: {{ eq: "completed" }} }}
        }}
        orderBy: updatedAt
      ) {{
        nodes {{
          id identifier title
          state {{ name }}
          project {{ name }}
          team {{ name }}
          updatedAt
          url
        }}
      }}
    }}
    """
    return _query(q)["issues"]["nodes"]


def my_team_ids() -> list[str]:
    """IDs of all teams I'm a member of."""
    q = """
    {
      viewer {
        teamMemberships {
          nodes { team { id name } }
        }
      }
    }
    """
    memberships = _query(q)["viewer"]["teamMemberships"]["nodes"]
    return [m["team"]["id"] for m in memberships]


def team_activity(limit: int = 20) -> list[dict]:
    """Recently updated issues across my teams (not just assigned to me)."""
    team_ids = my_team_ids()
    if not team_ids:
        return []

    ids_value = "[" + ", ".join(f'"{tid}"' for tid in team_ids) + "]"
    q = f"""
    {{
      issues(
        first: {limit}
        filter: {{
          team: {{ id: {{ in: {ids_value} }} }}
        }}
        orderBy: updatedAt
      ) {{
        nodes {{
          id identifier title
          state {{ name type }}
          assignee {{ name }}
          project {{ name }}
          team {{ name }}
          updatedAt
          url
        }}
      }}
    }}
    """
    return _query(q)["issues"]["nodes"]
