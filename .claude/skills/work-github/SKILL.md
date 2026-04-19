---
name: work-github
description: Fetch GitHub commits and PRs (authored + reviewed) in the guiddeco org for a given work day. Usable standalone or as a subagent from work-daily.
argument-hint: "['today' | 'yesterday' | 'YYYY-MM-DD' | empty → last working day]"
---

Fetch GitHub activity for: **$ARGUMENTS**

## Step 1 — Resolve date and GitHub user

**Date:** Use the Skill tool to invoke `work-date-resolver` with args `$ARGUMENTS`.
Parse `DATE` from the output.

**GitHub user:** If `GITHUB_USER` is provided in context, use it directly. Otherwise run:
```bash
gh api user --jq '.login'
```
Store as `GITHUB_USER`.

## Step 2 — Fetch data (all 3 in parallel)

**Commits** (guiddeco org only):
```bash
gh api "search/commits?q=author:GITHUB_USER+org:guiddeco+committer-date:DATE..DATE&per_page=30" \
  --jq '[.items[] | {sha: .sha[0:7], repo: .repository.full_name, message: (.commit.message | split("\n")[0]), url: .html_url}]'
```

**Authored PRs** (guiddeco org, updated on DATE):
```bash
gh api "search/issues?q=author:GITHUB_USER+org:guiddeco+type:pr+updated:DATE..DATE&per_page=20&sort=updated" \
  --jq '[.items[] | {number: .number, title: .title, state: .state, repo: (.repository_url | split("/") | .[-2:] | join("/")), url: .html_url}]'
```

**Reviewed PRs** (guiddeco org, updated on DATE):
```bash
gh api "search/issues?q=reviewed-by:GITHUB_USER+org:guiddeco+type:pr+updated:DATE..DATE&per_page=20&sort=updated" \
  --jq '[.items[] | {number: .number, title: .title, state: .state, repo: (.repository_url | split("/") | .[-2:] | join("/")), url: .html_url}]'
```

De-duplicate between authored and reviewed lists by PR number. A PR that appears in both is listed under Authored only.

## Step 3 — Output

Emit **exactly** in this format:

```
GITHUB_RESULT
DATE: <DATE>

COMMITS (N):
- `repo` — message `sha`

AUTHORED_PRS (N):
| # | Title | Repo | State |
|---|-------|------|-------|
| [#N](url) | Title | repo | state |

REVIEWED_PRS (N):
| # | Title | Repo | State |
|---|-------|------|-------|
| [#N](url) | Title | repo | state |
```

If a section is empty, still emit the header and write `(none)` on the next line.
