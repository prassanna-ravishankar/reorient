---
name: explore
description: Search across all connected work sources for information — Slack, Drive, Linear, GitHub, Granola, and session memory.
---

# Explore

Answer the user's question by searching across all available sources. Use as many as needed to give a complete answer.

## Sources (check all that are relevant)

1. **Session memory** — search via `memsearch:memory-recall` for past decisions, context, and discussions
2. **Slack** — `uv run python -c "from reorient.slack import recent_mentions; ..."` or search via `slack-reader` browser agent for richer context
3. **Google Drive** — `uv run python -c "from reorient.drive import recently_viewed, recently_edited; ..."`
4. **Linear** — `uv run python -c "from reorient.linear import my_issues, team_activity; ..."`
5. **GitHub** — `gh search issues`, `gh search prs`, `gh pr view`, etc.
6. **Granola** — query via `query_granola_meetings` MCP tool for meeting context
7. **Watchlist** — read `~/.reorient/watchlist.md` for curated bookmarks relevant to the query

## Guidelines

- Start with the source most likely to have the answer
- Cross-reference between sources when useful (e.g. a Slack thread mentioning a doc → fetch the doc)
- Cite sources in your answer so the user can dig deeper
- Keep the answer concise and direct
