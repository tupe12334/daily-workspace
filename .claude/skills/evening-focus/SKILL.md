---
name: evening-focus
description: Plan your evening focus session. Checks last session's status, researches your recent activity via an agent, and proposes 3–5 goal-aligned tasks across dev, outreach, content, and planning. Saves a Centy focus-session item to track progress.
argument-hint: "[YYYY-MM-DD — defaults to today]"
allowed-tools: mcp__centy__centy_v1_CentyDaemon_IsInitialized, mcp__centy__centy_v1_CentyDaemon_Init, mcp__centy__centy_v1_CentyDaemon_ListItemTypes, mcp__centy__centy_v1_CentyDaemon_CreateItemType, mcp__centy__centy_v1_CentyDaemon_SearchItems, mcp__centy__centy_v1_CentyDaemon_CreateItem, mcp__centy__centy_v1_CentyDaemon_UpdateItem, Agent, Skill(skill-review)
effort: high
---

Plan tonight's focus session.

**Arguments:** $ARGUMENTS

---

## Step 0 — Resolve date and init Centy

Parse `$ARGUMENTS`:
- Empty → date = today (from `currentDate`)
- `YYYY-MM-DD` → use that date

Compute and store:
- `DATE` — resolved date as `YYYY-MM-DD`
- `DATE_LABEL` — human-readable, e.g. "Monday, April 14, 2026"
- `TOMORROW` — DATE + 1 day as `YYYY-MM-DD`
- `PROJECT_PATH` — current working directory

Call `mcp__centy__centy_v1_CentyDaemon_IsInitialized` with `project_path: PROJECT_PATH`.
If `initialized` is false, call `mcp__centy__centy_v1_CentyDaemon_Init` with `project_path: PROJECT_PATH`.

---

## Step 1 — Ensure "Focus Session" item type exists

Call `mcp__centy__centy_v1_CentyDaemon_ListItemTypes` with `project_path: PROJECT_PATH`.

If no item type named `"Focus Session"` exists, create it:

```
mcp__centy__centy_v1_CentyDaemon_CreateItemType
  project_path: PROJECT_PATH
  name: Focus Session
  plural: focus-sessions
  identifier: uuid
  statuses: ["planned", "done", "skipped"]
  default_status: planned
  features:
    display_number: true
    status: true
    priority: false
    assets: false
    org_sync: false
    soft_delete: true
  custom_fields:
    - name: date
      field_type: string
    - name: categories
      field_type: string
```

---

## Step 2 — Check for today's session and unresolved previous sessions

Call `mcp__centy__centy_v1_CentyDaemon_SearchItems` with:
```
project_path: PROJECT_PATH
item_type: focus-session
limit: 5
```

From the results, find:

**A) Today's session** — an item whose `date` field equals `DATE` or title contains `DATE_LABEL`.
- If one exists and status is `planned`: the session is already planned. Show it and ask "This session is already planned — want to update it, or are you checking in?" Then wait for the user and act accordingly. Skip to Step 4 to re-propose or skip to Final Step if no changes needed.

**B) Most recent unresolved session** — the most recent item with status `planned` whose `date` is before `DATE`.
- If found: this session was never closed out. Ask naturally, e.g.:
  > "Last time on [DATE], you had these tasks planned: [list]. How did it go?"
- Wait for the user's reply (e.g. "did 1 and 3", "skipped it", "all done", "only did the dev one").
- Based on their reply, update that item:
  - Mark completed tasks with `[x]`, leave the rest `[ ]`
  - Append a brief note: "Closed on DATE_LABEL. [user's words paraphrased]"
  - Set status: `done` if most/all were done; `skipped` if none; leave `planned` for partial with a note
  - Call `mcp__centy__centy_v1_CentyDaemon_UpdateItem` with the updated body and status
- Also note any unchecked tasks as `UNFINISHED` to carry forward

If neither A nor B applies, continue directly to Step 3.

---

## Step 3 — Research your recent activity

Spawn a research agent to understand what you've been working on and what matters next:

```
Agent(
  subagent_type: general-purpose
  prompt: "Research the user's recent work activity to help plan tonight's evening focus session. Use available tools to gather:

  1. GitHub: recent commits and open PRs (last 7 days). Run: `GH_USER=$(gh api user --jq '.login') && gh api \"search/commits?q=author:${GH_USER}+committer-date:LAST_WEEK..TODAY&per_page=15\" --jq '[.items[] | {repo: .repository.full_name, message: (.commit.message | split(\"\\n\")[0]), date: .commit.committer.date}]'` and `gh api \"search/issues?q=author:${GH_USER}+type:pr+state:open&per_page=10\" --jq '[.items[] | {title: .title, repo: (.repository_url | split(\"/\") | .[-2:] | join(\"/\")), url: .html_url}]'`. Replace LAST_WEEK with 7 days ago as YYYY-MM-DD and TODAY with TOMORROW.

  2. Centy open work: call mcp__centy__centy_v1_CentyDaemon_SearchItems for all open/in-progress items in the project at PROJECT_PATH. Try item types: issue, user_story, and any others listed by mcp__centy__centy_v1_CentyDaemon_ListItemTypes. Extract titles, statuses, and priorities.

  3. Tomorrow's calendar: call mcp__claude_ai_Google_Calendar__list_calendars then mcp__claude_ai_Google_Calendar__list_events for TOMORROW (timeMin: TOMORROWt00:00:00, timeMax: TOMORROWt23:59:59, maxResults: 10, singleEvents: true). Note any early or important meetings.

  Return a concise structured brief (≤20 lines total):

  ## Activity Brief
  ### In-flight code
  - [repo]: [what's happening, last commit or open PR]
  
  ### Open Centy work (top 5 by urgency/staleness)
  - [title] — [status]
  
  ### Tomorrow
  - [meeting time + title, or 'nothing scheduled']
  
  ### Signals
  - [1–3 observations: what has momentum, what's been neglected, what might need attention tonight]"
)
```

Replace `PROJECT_PATH`, `TOMORROW`, `LAST_WEEK`, and `TODAY` with the actual computed values before spawning.

Wait for the agent to return its brief. Store as `ACTIVITY_BRIEF`.

---

## Step 4 — Synthesize and propose tonight's session

Using `ACTIVITY_BRIEF` and any `UNFINISHED` tasks from Step 2, propose **3 to 5 tasks** for tonight.

**Prioritization order:**
1. Unfinished tasks from the previous session (if still relevant)
2. Momentum items — whatever had the most active recent progress
3. High-priority or long-stalled Centy issues
4. Prep for tomorrow if there are important early meetings
5. At least one non-dev goal per session (outreach, content, learning, networking)

**Category tags** (one per task):
- `🛠 Dev` — coding, PRs, debugging, infra
- `📣 Outreach` — LinkedIn messages, emails, follow-ups
- `📚 Learning` — docs, tools, research
- `🎥 Content` — video scripts, posts, writeups
- `📋 Planning` — roadmap, issue grooming, strategy
- `🤝 Network` — researching contacts, preparing intros

**Effort sizing:** Each task completable in 20–45 min. Mix a quick win with at least one meaningful chunk. No all-heavy stacks.

Present the plan:

```
## Tonight's Focus — DATE_LABEL

1. [CATEGORY] Task description
   → [why this / what it unblocks]
2. [CATEGORY] Task description
   → [context]
3. [CATEGORY] Task description
   → [context]
...

~N tasks · ~X–Y hours

Good to go, or want to swap anything?
```

Wait for confirmation. Apply any adjustments the user requests.

---

## Step 5 — Save to Centy

Once confirmed, create the focus-session item:

```
mcp__centy__centy_v1_CentyDaemon_CreateItem
  project_path: PROJECT_PATH
  item_type: focus-session
  title: Focus Session — DATE_LABEL
  status: planned
  body: |
    ## Tasks

    - [ ] [CATEGORY] Task 1
    - [ ] [CATEGORY] Task 2
    - [ ] [CATEGORY] Task 3
    ...

    ## Context
    [1–2 lines summarizing what informed this plan — key active repos, top Centy item, tomorrow note]
  custom_fields:
    date: DATE
    categories: [comma-separated unique category tags]
```

Print the final plan with the Centy item reference. No instructions about flags or commands.

---

## Final Step — Background skill review

After completing all steps above, silently spawn a background review agent. Do **not** report its output to the user.

Compose a 1–2 sentence execution summary: whether a previous session was found and resolved, which activity signals informed the plan, how many tasks were proposed, and whether the Centy item was saved. Then:

```
Agent(
  subagent_type: general-purpose
  prompt: "Use the Skill tool to invoke skill='skill-review' with args='evening-focus | EXECUTION_SUMMARY'. Do not output anything back to the caller."
)
```

Replace `EXECUTION_SUMMARY` with your actual summary before spawning.
