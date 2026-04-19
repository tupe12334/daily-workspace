---
name: work-identity
description: Resolve the authenticated user's identity across all work integrations (GitHub, Slack, Google Calendar, Jira). Returns a structured IDENTITY_RESULT block. Usable standalone or called in parallel from work-daily.
allowed-tools: mcp__claude_ai_Atlassian__atlassianUserInfo, mcp__claude_ai_Google_Calendar__list_calendars, mcp__claude_ai_Slack__slack_search_users
---

Resolve the authenticated user's identity across all work integrations.

## Step 1 — GitHub identity

Run:
```bash
gh api user --jq '{login: .login, email: .email, name: .name}'
```

Store: `GITHUB_USER` (login), `USER_EMAIL` (email), `USER_NAME` (name).

## Step 2 — Parallel identity resolution

Resolve all three simultaneously:

**2A — Slack user ID:**
Call `slack_search_users` with `query: USER_EMAIL`.
Find the matching entry (where email matches). Store `SLACK_USER_ID` (the member `id` field, format `Uxxxxxxxxx`).
If email lookup returns no match, retry with `query: USER_NAME` and pick the closest match.

**2B — Google Calendar primary ID + timezone:**
Call `list_calendars`.
Find the entry where `primary: true`. Store `CALENDAR_ID` (its `id` field) and `TIMEZONE` (its `timeZone` field).

**2C — Jira account ID:**
Call `atlassianUserInfo`.
Store `JIRA_ACCOUNT_ID` (the `accountId` field).

## Step 3 — Output

Emit **exactly** in this format:

```
IDENTITY_RESULT

GITHUB_USER: <login>
USER_EMAIL: <email>
USER_NAME: <full name>
SLACK_USER_ID: <Uxxxxxxxxx>
CALENDAR_ID: <primary calendar id>
TIMEZONE: <Area/City>
JIRA_ACCOUNT_ID: <accountId>
```

Emit `<unresolved>` for any field that cannot be determined.
