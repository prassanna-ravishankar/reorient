---
name: catchup
description: Re-orient after a break — runs catchup.py and memory-recall, synthesizes into a tight briefing.
---

# Catchup

## Workflow

1. Run the data aggregator from the project root:
   ```bash
   uv run python scripts/catchup.py
   ```

2. Invoke the `memsearch:memory-recall` skill to surface recent session context (recent decisions, open threads, things you were about to do).

3. Synthesize both into a briefing with three sections:
   - **In progress** — active work items across GitHub, Linear, Slack, Drive
   - **Needs attention** — unread mentions, review requests, unresolved comments, stalled PRs
   - **Since you were away** — notable changes, merged PRs, closed issues, new assignments

Keep the briefing tight. Lead with the most time-sensitive items. Skip sources that returned no signal.
