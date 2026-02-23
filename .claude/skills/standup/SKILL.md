---
name: standup
description: Generate standup — runs standup.py, slack-reader agent, and memory-recall, outputs yesterday/today/blockers.
---

# Standup

## Workflow

1. Run the standup aggregator from the project root:
   ```bash
   uv run python scripts/standup.py
   ```

2. Spawn a `slack-reader` subagent (from `.claude/agents/slack-reader.md`) to fetch recent Slack activity. If Slack is unavailable, skip it.

3. Invoke the `memsearch:memory-recall` skill to retrieve recent session context (yesterday's decisions, completed tasks, open threads).

4. Produce a short standup in three bullets:
   - **Yesterday** — what was completed or meaningfully progressed (PRs merged, issues closed, decisions made, Slack threads resolved)
   - **Today** — what's actively in flight or next up (open PRs, in-progress Linear issues, pending reviews, open Slack threads)
   - **Blockers** — anything waiting on someone else, stuck, or needs a decision

Write in first person, past/present tense. Keep each bullet to 1-3 items. Omit sections with nothing relevant.
