# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

`reorient` eliminates "weekend amnesia" by surfacing context from Linear, GitHub, Google Drive, and Slack so you can re-orient quickly after any break.

## Daily Use

Run these skills from this directory:

```
/catchup    re-orient after a break — live data + session memory
/standup    generate standup — shipped, in progress, blockers
```

Scripts can also be run directly:
```bash
uv run python scripts/catchup.py
uv run python scripts/standup.py
```

Session memory is handled automatically by the memsearch plugin — no manual action needed. Past catchup sessions are searchable via `memsearch:memory-recall`.

## Auth State

| Source | Status | Notes |
|--------|--------|-------|
| Google Drive | done | token at `~/.reorient/google_token.json` |
| Linear | done | `LINEAR_API_KEY` in `.env` |
| GitHub | done | via `gh` CLI auth |
| Slack | done | via browser automation; profile at `~/.reorient/browser-profile` |

---

## Implementation Reference

For adding connectors or extending functionality.

### Architecture

```
Data Sources (Linear · GitHub · Drive · Slack)
        ↓
src/reorient/
  drive.py · linear.py · github.py  ← per-source Python clients
  meta.py  ← aggregation, outputs markdown
        ↓
.claude/agents/slack-reader.md  ← browser-based Slack reader (subagent)
        ↓
scripts/catchup.py · standup.py  ← thin CLI wrappers
        ↓
.claude/skills/catchup · standup  ← skills call scripts + slack-reader + memory-recall
```

### Slack via Browser Automation

Slack uses `agent-browser` with a saved browser profile instead of the Slack API (workspace app approval was slow). The `slack-reader` subagent:
1. Opens Slack headless with the profile at `~/.reorient/browser-profile`
2. Navigates Activity → Mentions, Activity → Thread replies, DMs
3. Extracts text via `data-qa="virtual-list-item"` DOM selector
4. Returns a plain text summary

To re-login if the session expires:
```bash
agent-browser --profile ~/.reorient/browser-profile open "$SLACK_WORKSPACE_URL" --headed
```

### Adding a New Connector

1. Add `src/reorient/<source>.py` — client functions returning `list[dict]`
2. Add auth token to `.env` and document in Auth State table above
3. Call it from `meta.py` in the relevant section (`catchup()`, `standup()`, etc.)
4. No script or skill changes needed unless the source warrants its own skill

### Conventions

- Source modules return plain dicts — `meta.py` owns formatting
- Scripts print markdown to stdout — Claude reasons over it directly
- Secrets via `.env` only (gitignored); load with `python-dotenv`
- Run `uv run ty check src/` before committing

### Development Commands

```bash
uv run python scripts/catchup.py   # test catchup output
uv add <package>                    # add dependency
uv run ty check src/               # type check
```
