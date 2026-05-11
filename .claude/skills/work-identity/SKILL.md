---
name: work-identity
description: Resolve the authenticated user's identity for all work integrations. Reads from info.md when available, resolves remaining fields dynamically, caches results back to info.md. Returns a structured IDENTITY_RESULT block. Usable standalone or called in parallel from work-daily.
user-invocable: false
allowed-tools: Bash, Read, Write, Edit, mcp__claude_ai_Atlassian__atlassianUserInfo, mcp__claude_ai_Google_Calendar__list_calendars, mcp__claude_ai_Slack__slack_search_users
---

Resolve the authenticated user's identity across all work integrations.

## Args

- ``(empty) — default. Use cached values from`info.md` when present.
- `refresh` — ignore `info.md` cache; re-resolve every field, then overwrite `info.md`.

## Step 1 — Read info.md

Read `info.md` from the current working directory. If it does not exist, treat all fields as unresolved and proceed.

If it exists, parse YAML frontmatter and map fields:

| info.md key           | Output field      |
| --------------------- | ----------------- |
| `work_email`          | `USER_EMAIL`      |
| `user_name`           | `USER_NAME`       |
| `github_username`     | `GITHUB_USER`     |
| `github_organization` | `GITHUB_ORG`      |
| `slack_user_id`       | `SLACK_USER_ID`   |
| `calendar_id`         | `CALENDAR_ID`     |
| `timezone`            | `TIMEZONE`        |
| `jira_account_id`     | `JIRA_ACCOUNT_ID` |

Treat empty string `""` and missing keys as unresolved.

If args contain `refresh`, ignore parsed values and mark all fields unresolved.

## Step 2 — Resolve remaining fields (parallel)

Emit **all** tool calls for unresolved fields in a **single assistant message** so they execute concurrently. Do not chain sequentially.

Resolvers:

**`GITHUB_USER` / `USER_NAME` / `USER_EMAIL`** — single `gh` call covers all three:

```bash
gh api user --jq '{login: .login, name: .name, email: .email}'
```

Map: `login → GITHUB_USER`, `name → USER_NAME`, `email → USER_EMAIL`.
If `gh` exits non-zero (auth missing), STOP and emit:

```
ERROR: gh CLI not authenticated. Run `gh auth login`.
```

**`GITHUB_ORG`** — only if unresolved AND user wants a single primary org. Multi-org users should leave empty in `info.md`. Resolver:

```bash
gh api user/orgs --jq '.[0].login // empty'
```

If empty, leave `<unresolved>` (callers like work-github must tolerate this).

**`SLACK_USER_ID`** — requires `USER_EMAIL` resolved first (sequential dependency; run after Step 2's `gh` call returns):

- Call `slack_search_users` with `query: <USER_EMAIL>`.
- Filter results: `deleted == false`, exact email match.
- If 0 matches, retry with `query: <USER_NAME>`, same filter.
- Store member `id`. If still 0, leave `<unresolved>`.

**`CALENDAR_ID` and/or `TIMEZONE`** — call `list_calendars` if **either** is unresolved:

- Find entry with `primary: true`.
- If `CALENDAR_ID` unresolved: store `id`.
- If `TIMEZONE` unresolved: store `timeZone`.

**`JIRA_ACCOUNT_ID`** — call `atlassianUserInfo`. Store `accountId`.
(This call also returns email/name; use as backup for `USER_EMAIL`/`USER_NAME` if `gh` returned null.)

## Step 3 — Cache write-back

If any field was newly resolved in Step 2 (and args did not contain a `no-cache` directive — currently always cache), write `info.md`:

- If `info.md` exists: use Edit to update only the changed keys, preserving other frontmatter and comments.
- If `info.md` does not exist: use Write to create it from the schema in `info.example.md`, with resolved values filled in.

Never overwrite a non-empty `info.md` value with `<unresolved>`.

## Step 4 — Output

Emit **exactly** this fenced block:

```
IDENTITY_RESULT

GITHUB_USER: <login>
GITHUB_ORG: <organization-or-unresolved>
USER_EMAIL: <email>
USER_NAME: <full name>
SLACK_USER_ID: <member id>
CALENDAR_ID: <primary calendar id>
TIMEZONE: <Area/City>
JIRA_ACCOUNT_ID: <accountId>
```

Use `<unresolved>` for any field that could not be determined.
