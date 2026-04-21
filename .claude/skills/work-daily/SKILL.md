---
name: work-daily
description: Generate a personal daily work summary. Aggregates calendar meetings, Fathom recordings, GitHub commits and PRs, Jira tickets, Slack highlights, and key emails into one structured digest for any given day.
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
Parse from identity output: `GITHUB_USER`, `GITHUB_ORG`, `SLACK_USER_ID`, `CALENDAR_ID`, `TIMEZONE`.

## Step 2 — Fetch all data sources in parallel

Send all 6 agents in a **single message** so they run concurrently. Embed the resolved identity values directly in each prompt so sub-skills skip their own resolution:

```
Agent({ description: "Calendar", prompt: "Use the Skill tool to invoke skill='work-calendar' with args='DATE'. CALENDAR_ID=<CALENDAR_ID>, TIMEZONE=<TIMEZONE> — use these directly, skip self-resolution. Return the complete output verbatim." })
Agent({ description: "Fathom",   prompt: "Use the Skill tool to invoke skill='work-fathom'   with args='DATE'. Return the complete output verbatim." })
Agent({ description: "GitHub",   prompt: "Use the Skill tool to invoke skill='work-github'   with args='DATE'. GITHUB_USER=<GITHUB_USER>, GITHUB_ORG=<GITHUB_ORG> — use these directly, skip self-resolution. Return the complete output verbatim." })
Agent({ description: "Jira",     prompt: "Use the Skill tool to invoke skill='work-jira'     with args='DATE'. Return the complete output verbatim." })
Agent({ description: "Slack",    prompt: "Use the Skill tool to invoke skill='work-slack'    with args='DATE'. SLACK_USER_ID=<SLACK_USER_ID> — use this directly, skip self-resolution. Return the complete output verbatim." })
Agent({ description: "Gmail",    prompt: "Use the Skill tool to invoke skill='work-gmail'    with args='DATE'. Return the complete output verbatim." })
```

Replace `<CALENDAR_ID>`, `<TIMEZONE>`, `<GITHUB_USER>`, `<GITHUB_ORG>`, `<SLACK_USER_ID>` with the actual resolved values before spawning.

If any agent fails or returns empty, skip that section silently.

## Step 3 — Synthesize and render

Parse each provider's structured block (`CALENDAR_RESULT`, `FATHOM_RESULT`, `GITHUB_RESULT`, `JIRA_RESULT`, `SLACK_RESULT`, `GMAIL_RESULT`) and compose the final digest. Omit any section with no data. If `FATHOM_RESULT` contains `ERROR:`, skip the Fathom section silently.

**Formatting rules:**
- Sort meetings by start time
- Times in HH:MM 24h (TIMEZONE)
- Separate Authored / Reviewed PR sub-tables; omit sub-table if empty
- Skip Slack bot noise and single-emoji threads
- Skip email newsletters and auto-notifications
- For Fathom: show summaries as blockquotes; group action items under each meeting title; omit meeting if summary and action items are both empty

```
# Daily Summary — DATE_LABEL

## Meetings (N)
| Time | Event | Duration |
|------|-------|----------|
| HH:MM | Title | Xm |
> (Key note for events with a description)

## Meeting Recordings (N)  ← from Fathom; omit section if 0 recordings
**[Meeting Title](recording_url)** — Xm
> Summary key points (condensed to 2–3 sentences)
- [ ] Action item 1 (assignee)
- [ ] Action item 2

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
**N** meetings · **N** recordings · **N** commits · **N** PRs · **N** Jira tickets · **N** Slack threads · **N** emails

---

## Standup Summary
Two sentences, written to be spoken aloud in a daily standup meeting. Sentence 1: what you accomplished (key code shipped, decisions made, or meetings that moved things forward). Sentence 2: what you're focused on next or any blockers, drawn from open Jira tickets, open PRs, or pending action items. Concise, first-person, no jargon, natural spoken English.
```

## Step 4 — Save to file

After rendering the digest to the user, write it to a dated markdown file:

- Path: `daily/<DATE>.md` (relative to the working directory, e.g. `daily/2026-04-20.md`)
- Content: the full rendered digest (everything from `# Daily Summary —` through the end)
- Create the `daily/` directory if it does not exist (use `mkdir -p daily`)
- Overwrite if the file already exists (re-running the same date refreshes it)

Use the Write tool directly — do not spawn an agent for this step.

## Final Step — Background skill review

Compose a 1–2 sentence execution summary (sources with results, failures, total counts), then spawn silently:
```
Agent(subagent_type: general-purpose, prompt: "Use the Skill tool to invoke skill='skill-review' with args='work-daily | EXECUTION_SUMMARY'. Do not output anything back to the caller.")
```
