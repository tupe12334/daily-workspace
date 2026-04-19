---
name: work-slack
description: Fetch Slack highlights (messages sent and mentions received) for a given work day. Usable standalone or as a subagent from work-daily.
argument-hint: "['today' | 'yesterday' | 'YYYY-MM-DD' | empty → last working day]"
---

Fetch Slack activity for: **$ARGUMENTS**

## Step 1 — Resolve date and Slack user ID

**Date:** Use the Skill tool to invoke `work-date-resolver` with args `$ARGUMENTS`.
Parse `DATE` from the output.

**Slack user ID:** If `SLACK_USER_ID` is provided in context, use it directly. Otherwise:
1. Run `gh api user --jq '{email: .email, name: .name}'` to get the GitHub user's email and name.
2. Call `slack_search_users` with `query: <email>`. Find the matching entry and store its `id` as `SLACK_USER_ID`.
3. If email lookup returns no match, retry with `query: <name>`.

## Step 2 — Search Slack (both in parallel)

Use `slack_search_public_and_private`:

**Sent messages:**
- `query: "from:<@SLACK_USER_ID> on:DATE"`

**Mentions:**
- `query: "<@SLACK_USER_ID> on:DATE"`

**Filter out:**
- Bot messages and automated notifications
- Single-emoji reactions and reaction-only threads
- Off-topic / non-work channels (e.g. `#random`, `#general-social`)

## Step 3 — Output

Emit **exactly** in this format:

```
SLACK_RESULT
DATE: <DATE>

HIGHLIGHTS (N):
- **#channel** — thread summary (one line per distinct thread/topic)
```

Combine sent and mentions into a single de-duplicated list, grouped loosely by thread.
If nothing substantive: emit `HIGHLIGHTS (0): (none)`.
