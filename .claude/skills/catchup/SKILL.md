---
name: catchup
description: Re-orient after a break — runs catchup.py, slack-reader, Granola, and memory-recall, synthesizes into a tight briefing.
---

# Catchup

## Workflow

1. Run the data aggregator (Linear, GitHub, Drive) from the project root:
   ```bash
   uv run python scripts/catchup.py
   ```

2. Spawn a `slack-reader` subagent (from `.claude/agents/slack-reader.md`) to fetch Slack mentions, threads, and DMs via browser automation. If Slack is unavailable, skip it.

3. Query Granola MCP for recent meeting notes — use `query_granola_meetings` with a query like "recent meetings, decisions, and action items". If Granola is unavailable, skip it.

4. Invoke the `memsearch:memory-recall` skill to surface recent session context (recent decisions, open threads, things you were about to do).

5. Synthesize all sources into a briefing with three sections:
   - **In progress** — active work items across GitHub, Linear, Slack, Drive
   - **Needs attention** — unread mentions, review requests, DMs awaiting reply, meeting action items, unresolved comments
   - **Since you were away** — notable changes, merged PRs, closed issues, new Slack threads, meetings held

Keep the briefing tight. Lead with the most time-sensitive items. Skip sources that returned no signal.
