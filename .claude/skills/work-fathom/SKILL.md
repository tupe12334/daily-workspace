---
name: work-fathom
description: Fetch Fathom meeting recordings with AI summaries and action items for a given work day. Usable standalone or as a subagent from work-daily.
argument-hint: "['today' | 'yesterday' | 'YYYY-MM-DD' | empty → last working day]"
---

Fetch Fathom recordings for: **$ARGUMENTS**

## Step 1 — Resolve date

Use the Skill tool to invoke `work-date-resolver` with args `$ARGUMENTS`.
Parse `DATE` from the output (YYYY-MM-DD).

## Step 2 — Resolve identity and fetch meetings via MCP

Call `mcp__fathom__get_identity` to get the authenticated user's email. Then call `mcp__fathom__list_meetings` filtered to that user's own recordings only.

Pass: `created_after: DATE T00:00:00Z`, `created_before: DATE T23:59:59Z`, `recorded_by: [user_email]`, `include_summary: true`, `include_action_items: true`.

If the MCP call fails or requires re-authentication, emit:
```
FATHOM_RESULT
DATE: <DATE>
ERROR: Fathom MCP unavailable — re-run to trigger OAuth if this is first use
```
And stop.

## Step 3 — Enrich with summaries and action items (if not included)

If the meeting list tool does not return summaries/action items inline, call the per-recording summary and action items tools for each meeting (e.g. `get_recording_summary`, `get_recording_action_items`) in parallel.

## Step 4 — Output

Emit **exactly** in this format:

```
FATHOM_RESULT
DATE: <DATE>

MEETINGS (N):
| Time  | Title | Duration | Attendees |
|-------|-------|----------|-----------|
| HH:MM | Title | Xm       | name1, name2 |

[For each meeting with a summary or action items:]
---
MEETING: <Title>
URL: <recording_url>
SUMMARY:
  <summary content, max 600 chars>
ACTION ITEMS:
- <item> [(<assignee>)]
```

If no meetings found:
```
FATHOM_RESULT
DATE: <DATE>

MEETINGS (0):
(none)
```

Times in HH:MM 24h format. Duration rounded to nearest minute.
