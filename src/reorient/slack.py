"""
Slack client via Slack SDK.

Auth: set SLACK_USER_TOKEN in .env (xoxp- user token).
"""

import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()


def _client() -> WebClient:
    token = os.getenv("SLACK_USER_TOKEN")
    if not token:
        raise EnvironmentError("SLACK_USER_TOKEN not set in .env")
    return WebClient(token=token)


def _my_user_id() -> str:
    resp = _client().auth_test()
    return resp["user_id"]


def recent_mentions(limit: int = 15) -> list[dict]:
    """Messages that mention me, last 7 days."""
    try:
        resp = _client().search_messages(
            query="to:me",
            sort="timestamp",
            sort_dir="desc",
            count=limit,
        )
        return [
            {
                "channel": m.get("channel", {}).get("name", ""),
                "sender": m.get("username", "") or m.get("user", ""),
                "text": m.get("text", "")[:300],
                "ts": m.get("ts", ""),
                "permalink": m.get("permalink", ""),
            }
            for m in resp.get("messages", {}).get("matches", [])
        ]
    except SlackApiError:
        return []


def unread_dms(limit: int = 10) -> list[dict]:
    """DMs with unread messages."""
    client = _client()
    try:
        convos = client.conversations_list(types="im", limit=50)
    except SlackApiError:
        return []

    unread = []
    for ch in convos.get("channels", []):
        if not ch.get("is_im"):
            continue
        unread_count = ch.get("unread_count_display", 0)
        if unread_count == 0:
            continue
        # get latest message
        try:
            hist = client.conversations_history(channel=ch["id"], limit=1)
            msgs = hist.get("messages", [])
            latest = msgs[0] if msgs else {}
            # resolve user name
            user_info = client.users_info(user=ch["user"])
            name = user_info.get("user", {}).get("real_name", ch["user"])
            unread.append({
                "from": name,
                "unread_count": unread_count,
                "latest_text": latest.get("text", "")[:300],
                "channel_id": ch["id"],
            })
        except SlackApiError:
            continue
        if len(unread) >= limit:
            break
    return unread


def recent_threads(limit: int = 10) -> list[dict]:
    """Threads I've participated in with recent replies."""
    client = _client()
    since = datetime.now(timezone.utc) - timedelta(days=7)
    try:
        resp = client.search_messages(
            query="from:me has:thread",
            sort="timestamp",
            sort_dir="desc",
            count=limit,
        )
        threads = []
        for m in resp.get("messages", {}).get("matches", []):
            threads.append({
                "channel": m.get("channel", {}).get("name", ""),
                "text": m.get("text", "")[:300],
                "ts": m.get("ts", ""),
                "permalink": m.get("permalink", ""),
            })
        return threads
    except SlackApiError:
        return []
