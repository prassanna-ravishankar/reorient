---
name: standup
description: Generate standup — runs standup.py and memory-recall, outputs yesterday/today/blockers.
---

# Standup

## Workflow

1. Run the standup aggregator from the project root:
   ```bash
   uv run python scripts/standup.py
   ```

2. Invoke the `memsearch:memory-recall` skill to retrieve recent session context (yesterday's decisions, completed tasks, open threads).

3. Produce a short standup in three bullets:
   - **Yesterday** — what was completed or meaningfully progressed (PRs merged, issues closed, decisions made)
   - **Today** — what's actively in flight or next up (open PRs, in-progress Linear issues, pending reviews)
   - **Blockers** — anything waiting on someone else, stuck, or needs a decision

Write in first person, past/present tense. Keep each bullet to 1-3 items. Omit sections with nothing relevant.
