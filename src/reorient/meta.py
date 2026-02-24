"""
Cross-source aggregation. Outputs markdown Claude can reason over directly.
"""

from datetime import datetime, timezone

from reorient import drive, github, linear, slack


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def catchup() -> str:
    sections = [f"# Catchup — {_now()}\n"]

    # Linear
    sections.append("## Linear\n")
    wip = linear.in_progress()
    if wip:
        sections.append("### In Progress")
        for i in wip:
            sections.append(f"- [{i['identifier']}] {i['title']} — {i['url']}")
    active = linear.my_issues(states=["triage", "unstarted"])
    if active:
        sections.append("\n### Up Next (unstarted/triage)")
        for i in active:
            proj = i.get("project") or {}
            sections.append(f"- [{i['identifier']}] {i['title']}" + (f" ({proj['name']})" if proj else ""))

    # GitHub
    sections.append("\n## GitHub\n")
    prs = github.my_open_prs()
    if prs:
        sections.append("### My Open PRs")
        for pr in prs:
            draft = " [DRAFT]" if pr.get("isDraft") else ""
            repo = pr["repository"]["name"]
            sections.append(f"- #{pr['number']} {pr['title']}{draft} — {repo} — {pr['url']}")
    reviews = github.review_requests()
    if reviews:
        sections.append("\n### Needs My Review")
        for pr in reviews:
            repo = pr["repository"]["name"]
            sections.append(f"- #{pr['number']} {pr['title']} — {repo} — {pr['url']}")

    # Slack
    try:
        mentions = slack.recent_mentions(10)
        dms = slack.unread_dms(5)
        if mentions or dms:
            sections.append("\n## Slack\n")
            if mentions:
                sections.append("### Recent Mentions")
                for m in mentions:
                    sections.append(f"- [{m['channel']}] {m['sender']}: {m['text'][:120]}")
            if dms:
                sections.append("\n### Unread DMs")
                for d in dms:
                    sections.append(f"- {d['from']} ({d['unread_count']} unread): {d['latest_text'][:120]}")
    except Exception:
        pass  # slack unavailable, skip

    # Drive
    sections.append("\n## Google Drive\n")
    viewed = drive.recently_viewed(10)
    if viewed:
        sections.append("### Recently Viewed")
        for f in viewed:
            ts = (f.get("viewedByMeTime") or "")[:10]
            sections.append(f"- {f['name']} ({ts}) — {f.get('webViewLink','')}")
    edited = drive.recently_edited(10)
    if edited:
        sections.append("\n### Recently Edited by Me")
        for f in edited:
            ts = (f.get("modifiedByMeTime") or "")[:10]
            sections.append(f"- {f['name']} ({ts}) — {f.get('webViewLink','')}")

    return "\n".join(sections)


def standup() -> str:
    sections = [f"# Standup — {_now()}\n"]

    sections.append("## Shipped / Completed\n")
    merged = github.recently_merged(5)
    for pr in merged:
        repo = pr["repository"]["name"]
        ts = (pr.get("closedAt") or "")[:10]
        sections.append(f"- PR #{pr['number']} {pr['title']} ({repo}) — {ts}")
    done = linear.recently_completed(5)
    for i in done:
        ts = (i.get("updatedAt") or "")[:10]
        sections.append(f"- [{i['identifier']}] {i['title']} — {ts}")

    sections.append("\n## In Progress\n")
    for i in linear.in_progress():
        sections.append(f"- [{i['identifier']}] {i['title']} — {i['url']}")

    sections.append("\n## Needs Attention\n")
    for pr in github.review_requests(5):
        repo = pr["repository"]["name"]
        sections.append(f"- Review requested: #{pr['number']} {pr['title']} ({repo})")

    return "\n".join(sections)


def team_pulse() -> str:
    sections = [f"# Team Pulse — {_now()}\n"]
    activity = linear.team_activity(20)
    if activity:
        for i in activity:
            assignee = (i.get("assignee") or {}).get("name", "unassigned")
            state = i["state"]["type"]
            sections.append(f"- [{i['identifier']}] [{state}] {i['title']} → {assignee}")
    return "\n".join(sections)
