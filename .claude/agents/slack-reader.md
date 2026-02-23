# Slack Reader

Read Slack via browser automation. Returns a plain text summary of mentions, threads, and DMs.

## Setup

- Browser profile: `~/.reorient/browser-profile` (must be logged in to Slack already)
- Workspace URL: read from `SLACK_WORKSPACE_URL` in `.env`

## Instructions

1. Load the workspace URL from `.env`:
   ```bash
   SLACK_URL=$(grep SLACK_WORKSPACE_URL .env | cut -d= -f2)
   ```

2. Open Slack with the saved profile:
   ```bash
   agent-browser --profile ~/.reorient/browser-profile open "$SLACK_URL"
   agent-browser wait 3000
   ```

3. Navigate to **Activity → Mentions** tab and extract items:
   ```bash
   agent-browser snapshot -i
   # Find and click the "Activity" tab, then the "Mentions" subtab
   agent-browser eval --stdin <<'EVALEOF'
   JSON.stringify(
     Array.from(document.querySelectorAll('[data-qa="virtual-list-item"]'))
       .slice(0, 15)
       .map(el => el.textContent.trim().substring(0, 300))
       .filter(t => t.length > 0)
   )
   EVALEOF
   ```

4. Navigate to **Activity → Thread replies** tab and extract items using the same eval pattern.

5. Navigate to **DMs** tab and extract items using the same eval pattern.

6. Close the browser:
   ```bash
   agent-browser close
   ```

7. Return the combined output as plain text with three sections:
   - **Mentions** — @Prass and @channel mentions with channel, sender, preview, time
   - **Active Threads** — threads with new replies
   - **Recent DMs** — latest DMs with sender and preview

## Important

- Do NOT include any workspace IDs, internal URLs, or sensitive content in error messages.
- If the browser fails to open or Slack doesn't load, return "Slack data unavailable" rather than exposing error details.
- The `data-qa="virtual-list-item"` selector is stable across Slack updates.
- The eval output is double-JSON-encoded — parse with `json.loads(json.loads(raw))`.
