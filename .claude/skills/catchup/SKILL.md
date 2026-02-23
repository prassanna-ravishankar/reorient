---
name: catchup
description: Re-orient after a break — aggregates live work context from all sources and session memory into a concise briefing.
---

# Catchup

## Workflow

1. Run the data aggregator (Linear, GitHub, Drive) from the project root:
   ```bash
   uv run python scripts/catchup.py
   ```

2. Get recent Slack activity (mentions, threads, DMs). If unavailable, skip.

3. Query Granola MCP for recent meeting notes, decisions, and action items. If unavailable, skip.

4. Search session memory for recent context (decisions, open threads, things flagged for follow-up).

5. Synthesize all sources into a briefing with three sections:
   - **In progress** — active work items across all sources
   - **Needs attention** — unread mentions, review requests, DMs awaiting reply, meeting action items
   - **Since you were away** — notable changes, merged PRs, closed issues, new threads, meetings held

Keep the briefing tight. Lead with the most time-sensitive items. Skip sources that returned no signal.
