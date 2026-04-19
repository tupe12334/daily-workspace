---
name: work-identity
description: Resolve the authenticated user's identity for all work integrations. Reads from info.md when available, resolves remaining fields dynamically. Returns a structured IDENTITY_RESULT block. Usable standalone or called in parallel from work-daily.
allowed-tools: mcp__claude_ai_Atlassian__atlassianUserInfo, mcp__claude_ai_Google_Calendar__list_calendars, mcp__claude_ai_Slack__slack_search_users
---

Resolve the authenticated user's identity across all work integrations.

## Step 1 — Read info.md

Read `info.md` from the current working directory. If the file exists, parse its YAML frontmatter and map fields:

## Step 2 — Resolve remaining fields (in parallel)

Run only the calls needed for still-unresolved fields. All can run simultaneously:

**USER_NAME** — always resolve (not in info.md):

```bash
gh api user --jq '.name'
```

Also use this call to resolve `GITHUB_USER` if unresolved: `gh api user --jq '{login: .login, name: .name}'`.

**If SLACK_USER_ID is unresolved:**
Call `slack_search_users` with `query: USER_EMAIL`.
Find the entry whose email matches. If no match, retry with `query: USER_NAME`.
Store the matching member `id` as `SLACK_USER_ID`.

**TIMEZONE** — always resolve (not in info.md):
Call `list_calendars`. Find the entry with `primary: true`.
Store its `timeZone` as `TIMEZONE`.
If `CALENDAR_ID` is also unresolved, store its `id` as `CALENDAR_ID`.

**JIRA_ACCOUNT_ID** — always resolve (not in info.md):
Call `atlassianUserInfo`. Store the `accountId` field as `JIRA_ACCOUNT_ID`.

## Step 3 — Output

Emit **exactly** in this format:

```
IDENTITY_RESULT

GITHUB_USER: <login>
GITHUB_ORG: <organization>
USER_EMAIL: <email>
USER_NAME: <full name>
SLACK_USER_ID: <member id>
CALENDAR_ID: <primary calendar id>
TIMEZONE: <Area/City>
JIRA_ACCOUNT_ID: <accountId>
```

Emit `<unresolved>` for any field that could not be determined.
