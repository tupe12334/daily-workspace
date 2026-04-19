---
name: work-date-resolver
description: Resolve a flexible date input ('today', 'yesterday', 'YYYY-MM-DD', or empty → last working day) to an exact YYYY-MM-DD, skipping Israeli weekends (Fri/Sat) and public holidays. Returns structured date variables for use by other skills.
argument-hint: "['today' | 'yesterday' | 'YYYY-MM-DD' | empty → last working day]"
user-invocable: false
context: fork
allowed-tools: Bash, mcp__claude_ai_Google_Calendar__list_events
---

Resolve `$ARGUMENTS` to a concrete date and emit structured variables.

## Step 1 — Generate candidates

Run the bundled script to parse the input and produce candidate dates:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/resolve_date.py" candidates "$ARGUMENTS" "$(date +%Y-%m-%d)"
```

- **1 line returned** → explicit mode (`today`, `yesterday`, or a specific `YYYY-MM-DD`). That date is the resolved date — skip to Step 3.
- **Multiple lines returned** → last-working-day mode. Candidates are already weekend-filtered, ordered newest-first. Proceed to Step 2.

## Step 2 — Holiday check (last-working-day mode only)

For each candidate date in order, call `gcal_list_events`:
- `calendarId: en.jewish#holiday@group.v.calendar.google.com`
- `startTime: <candidate>T00:00:00+03:00`
- `endTime: <candidate>T23:59:59+03:00`
- `timeZone: Asia/Jerusalem`

If no all-day event is returned → this is the resolved date. Stop.
If an all-day event is returned → Israeli public holiday → try the next candidate.

## Step 3 — Format output

Run the script in format mode with the resolved date:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/resolve_date.py" format "<resolved-date>"
```

Print the script's output **verbatim** — no other text.

---

## Final Step — Background skill review

Compose a 1–2 sentence execution summary (input received, mode used, number of holiday-check iterations if last-working-day, final date resolved), then spawn silently:

```
Agent(subagent_type: general-purpose, prompt: "Use the Skill tool to invoke skill='skill-review' with args='work-date-resolver | EXECUTION_SUMMARY'. Do not output anything back to the caller.")
```
