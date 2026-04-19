---
name: work-calendar
description: Fetch Google Calendar events for a given work day. Usable standalone or as a subagent from work-daily.
argument-hint: "['today' | 'yesterday' | 'YYYY-MM-DD' | empty → last working day]"
---

Fetch calendar events for: **$ARGUMENTS**

## Step 1 — Resolve date and calendar identity

**Date:** Use the Skill tool to invoke `work-date-resolver` with args `$ARGUMENTS`.
Parse `DATE`, `DATE_LABEL`, `DATE_START`, `DATE_END` from the output.

**Calendar identity:** If `CALENDAR_ID` and `TIMEZONE` are provided in context, use them directly. Otherwise call `list_calendars` and find the entry with `primary: true`. Store its `id` as `CALENDAR_ID` and its `timeZone` as `TIMEZONE`.

## Step 2 — Fetch events

Call `list_events` (Google Calendar MCP):
- `calendarId: CALENDAR_ID`
- `startTime: DATE_START`
- `endTime: DATE_END`
- `timeZone: TIMEZONE`
- `pageSize: 20`
- `orderBy: startTime`

**Keep only work-relevant events.** Exclude:
- `eventType: outOfOffice` or `eventType: workingLocation`
- Personal events with no work context
- Company-wide ceremonies: all-hands, team happy hours, holidays, birthday events
- Auto-generated events (invites with no attendee action needed)

Keep: 1:1s, focused work sessions, external meetings, standups, and any meeting the authenticated user organises or is a named subject of.

## Step 3 — Output

Emit **exactly** in this format (preserve the section headers so the caller can parse them):

```
CALENDAR_RESULT
DATE: <DATE>
DATE_LABEL: <DATE_LABEL>

| Time  | Event | Duration |
|-------|-------|----------|
| HH:MM | Title | Xm       |
> Key note (only for events with a meaningful description — omit line if none)

COUNT: N
```

If no events after filtering: emit the table header + `COUNT: 0`.
Times in HH:MM 24-hour format (TIMEZONE). Duration rounded to nearest 5 minutes.
