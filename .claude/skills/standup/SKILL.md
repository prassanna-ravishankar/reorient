---
name: standup
description: Generate a daily standup summary from live work data and session memory — yesterday/today/blockers.
---

# Standup

## Workflow

1. Run the standup aggregator (Linear, GitHub, Slack) from the project root:
   ```bash
   uv run python scripts/standup.py
   ```
   This includes Slack data via the SDK. If Slack data is missing from the output, fall back to the `slack-reader` browser agent.

2. Query Granola MCP for yesterday's meeting notes and decisions. If unavailable, skip.

3. Search session memory for recent context (completed tasks, open threads, decisions made).

4. Produce a short standup in three bullets:
   - **Yesterday** — what was completed or meaningfully progressed
   - **Today** — what's actively in flight or next up
   - **Blockers** — anything waiting on someone else, stuck, or needs a decision

Write in first person, past/present tense. Keep each bullet to 1-3 items. Omit sections with nothing relevant.
