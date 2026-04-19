---
name: work-github
description: Fetch GitHub commits and PRs (authored + reviewed) for a given work day. Usable standalone or as a subagent from work-daily.
argument-hint: "['today' | 'yesterday' | 'YYYY-MM-DD' | empty → last working day]"
---

Fetch GitHub activity for: **$ARGUMENTS**

## Step 1 — Resolve date, user, and org

**Date:** Use the Skill tool to invoke `work-date-resolver` with args `$ARGUMENTS`.
Parse `DATE` from the output.

**GitHub user:** If `GITHUB_USER` is provided in context, use it directly. Otherwise run:
```bash
gh api user --jq '.login'
```
Store as `GITHUB_USER`.

**GitHub org:** If `GITHUB_ORG` is provided in context, use it directly. Otherwise read `info.md` from the current working directory and parse `github_organization`. Store as `GITHUB_ORG`.

## Step 2 — Fetch data (all 3 in parallel)

**Commits:**
```bash
gh api "search/commits?q=author:GITHUB_USER+org:GITHUB_ORG+committer-date:DATE..DATE&per_page=30" \
  --jq '[.items[] | {sha: .sha[0:7], repo: .repository.full_name, message: (.commit.message | split("\n")[0]), url: .html_url}]'
```

**Authored PRs:**
```bash
gh api "search/issues?q=author:GITHUB_USER+org:GITHUB_ORG+type:pr+updated:DATE..DATE&per_page=20&sort=updated" \
  --jq '[.items[] | {number: .number, title: .title, state: .state, repo: (.repository_url | split("/") | .[-2:] | join("/")), url: .html_url}]'
```

**Reviewed PRs:**
```bash
gh api "search/issues?q=reviewed-by:GITHUB_USER+org:GITHUB_ORG+type:pr+updated:DATE..DATE&per_page=20&sort=updated" \
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
