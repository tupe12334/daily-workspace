---
name: work-gmail
description: Fetch key Gmail emails (sent and received important) for a given work day. Usable standalone or as a subagent from work-daily.
argument-hint: "['today' | 'yesterday' | 'YYYY-MM-DD' | empty → last working day]"
---

Fetch Gmail activity for: **$ARGUMENTS**

## Step 1 — Resolve date

Use the Skill tool to invoke `work-date-resolver` with args `$ARGUMENTS`.
Parse `DATE`, `GMAIL_DATE`, `GMAIL_NEXT_DATE` from the output.
(GMAIL_DATE and GMAIL_NEXT_DATE are in `YYYY/MM/DD` format, required by Gmail's search API.)

## Step 2 — Search (both in parallel)

Use `search_threads` (not `search_messages`):

**Sent emails:**
- `query: "from:me after:GMAIL_DATE before:GMAIL_NEXT_DATE"`

**Received important:**
- `query: "to:me is:important after:GMAIL_DATE before:GMAIL_NEXT_DATE"`

For received: read 3–5 threads (using `get_thread`) to extract subject and key point.

**Skip:**
- Newsletters, marketing emails, automated notifications, calendar invites, CI/CD alerts
- Emails with no actionable content

## Step 3 — Output

Emit **exactly** in this format:

```
GMAIL_RESULT
DATE: <DATE>

SENT (N):
- **→** Subject → Recipient — key ask or decision

RECEIVED_IMPORTANT (N):
- **←** Subject ← Sender — action required or key takeaway
```

If a section is empty: `(none)` on the next line.
