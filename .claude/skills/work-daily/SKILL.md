---
name: work-daily
description: Generate a personal daily work summary. Aggregates calendar meetings, GitHub commits and PRs, Jira tickets, Slack highlights, and key emails into one structured digest for any given day.
argument-hint: "[date — 'today', 'yesterday', or 'YYYY-MM-DD'; defaults to today]"
---

Generate your personal daily work summary for: **$ARGUMENTS**

## Step 1 — Resolve date and identity (in parallel)

Spawn both agents simultaneously in a single message:

```
Agent({ description: "Resolve date",     prompt: "Use the Skill tool to invoke skill='work-date-resolver' with args='$ARGUMENTS'. Return the complete output verbatim." })
Agent({ description: "Resolve identity", prompt: "Use the Skill tool to invoke skill='work-identity'. Return the complete output verbatim." })
```

Parse from date output: `DATE`, `DATE_LABEL`.
Parse from identity output: `GITHUB_USER`, `SLACK_USER_ID`, `CALENDAR_ID`, `TIMEZONE`.

## Step 2 — Fetch all data sources in parallel

Send all 5 agents in a **single message** so they run concurrently. Embed the resolved identity values directly in each prompt so sub-skills skip their own resolution:

```
Agent({ description: "Calendar", prompt: "Use the Skill tool to invoke skill='work-calendar' with args='DATE'. CALENDAR_ID=<CALENDAR_ID>, TIMEZONE=<TIMEZONE> — use these directly, skip self-resolution. Return the complete output verbatim." })
Agent({ description: "GitHub",   prompt: "Use the Skill tool to invoke skill='work-github'   with args='DATE'. GITHUB_USER=<GITHUB_USER> — use this directly, skip self-resolution. Return the complete output verbatim." })
Agent({ description: "Jira",     prompt: "Use the Skill tool to invoke skill='work-jira'     with args='DATE'. Return the complete output verbatim." })
Agent({ description: "Slack",    prompt: "Use the Skill tool to invoke skill='work-slack'    with args='DATE'. SLACK_USER_ID=<SLACK_USER_ID> — use this directly, skip self-resolution. Return the complete output verbatim." })
Agent({ description: "Gmail",    prompt: "Use the Skill tool to invoke skill='work-gmail'    with args='DATE'. Return the complete output verbatim." })
```

Replace `<CALENDAR_ID>`, `<TIMEZONE>`, `<GITHUB_USER>`, `<SLACK_USER_ID>` with the actual resolved values before spawning.

If any agent fails or returns empty, skip that section silently.

## Step 3 — Synthesize and render

Parse each provider's structured block (`CALENDAR_RESULT`, `GITHUB_RESULT`, `JIRA_RESULT`, `SLACK_RESULT`, `GMAIL_RESULT`) and compose the final digest. Omit any section with no data.

**Formatting rules:**
- Sort meetings by start time
- Times in HH:MM 24h (TIMEZONE)
- Separate Authored / Reviewed PR sub-tables; omit sub-table if empty
- Skip Slack bot noise and single-emoji threads
- Skip email newsletters and auto-notifications

```
# Daily Summary — DATE_LABEL

## Meetings (N)
| Time | Event | Duration |
|------|-------|----------|
| HH:MM | Title | Xm |
> (Key note for events with a description)

## Code Shipped
### Commits (N)
- `repo` — message `sha`

### Pull Requests (N)
**Authored:**
| # | Title | Repo | State |
|---|-------|------|-------|
| [#N](url) | Title | repo | open/merged/closed |
**Reviewed:**
| # | Title | Repo | State |
|---|-------|------|-------|
| [#N](url) | Title | repo | open/merged/closed |

## Jira Tickets (N)
| Key | Summary | Status |
|-----|---------|--------|
| [GD-XXXX](url) | Summary | Status |

## Slack Highlights
- **#channel** — thread summary

## Key Emails
- **→** Subject → Recipient — key ask
- **←** Subject ← Sender — action required

## Day at a Glance
**N** meetings · **N** commits · **N** PRs · **N** Jira tickets · **N** Slack threads · **N** emails
```

## Final Step — Background skill review

Compose a 1–2 sentence execution summary (sources with results, failures, total counts), then spawn silently:
```
Agent(subagent_type: general-purpose, prompt: "Use the Skill tool to invoke skill='skill-review' with args='work-daily | EXECUTION_SUMMARY'. Do not output anything back to the caller.")
```
