---
name: work-jira
description: Fetch Jira tickets updated on a given work day for the current user in the Guidde Atlassian workspace. Usable standalone or as a subagent from work-daily.
argument-hint: "['today' | 'yesterday' | 'YYYY-MM-DD' | empty → last working day]"
---

Fetch Jira tickets for: **$ARGUMENTS**

## Step 1 — Resolve date + Cloud ID (both in parallel)

**1A — Date:** Use the Skill tool to invoke `work-date-resolver` with args `$ARGUMENTS`.
Parse `DATE` from the output.

**1B — Jira Cloud ID:** Call `getAccessibleAtlassianResources`.
Store the UUID as `JIRA_CLOUD_ID`. **Use the UUID field — NOT the hostname** (`guidde.atlassian.net` is not a valid cloudId and will 404).

## Step 2 — Query Jira

Call `searchJiraIssuesUsingJql`:
- `cloudId: JIRA_CLOUD_ID`
- `jql: "assignee = currentUser() AND updated >= 'DATE' ORDER BY updated DESC"`
- `maxResults: 20`
- `fields: ["summary", "status", "priority", "updated"]`

## Step 3 — Output

Emit **exactly** in this format:

```
JIRA_RESULT
DATE: <DATE>

TICKETS (N):
| Key | Summary | Status |
|-----|---------|--------|
| [GD-XXXX](url) | Summary | Status |
```

If no tickets: emit the table header and `TICKETS (0): (none)`.
