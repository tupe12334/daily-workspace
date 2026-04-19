#!/usr/bin/env python3
"""
work-date-resolver helper script.

Commands:
  candidates <input> <today-YYYY-MM-DD>
      Parse the date input and emit an ordered list of non-weekend candidate
      dates to check for holidays (newest first).

      Explicit inputs ('today', 'yesterday', 'YYYY-MM-DD') emit exactly one
      date — no holiday check needed for these.

      Empty / unrecognised input (last-working-day mode) emits up to 30
      non-weekend candidates starting from today-1.

  format <YYYY-MM-DD>
      Given the final resolved date, print all formatted output variables.
"""
import sys
from datetime import date, timedelta

_WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
_MONTHS   = ["January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"]
_TZ = "+03:00"


def _parse(s: str) -> date:
    y, m, d = s.split("-")
    return date(int(y), int(m), int(d))


def _is_weekend(d: date) -> bool:
    return d.weekday() in (4, 5)  # Friday=4, Saturday=5


def _label(d: date) -> str:
    return f"{_WEEKDAYS[d.weekday()]}, {_MONTHS[d.month - 1]} {d.day}, {d.year}"


def cmd_candidates(inp: str, today_str: str) -> None:
    today = _parse(today_str)
    s = inp.strip().lower()

    if s == "today":
        print(today.isoformat())
        return

    if s == "yesterday":
        print((today - timedelta(days=1)).isoformat())
        return

    if len(s) == 10 and s[4] == "-" and s[7] == "-":
        try:
            _parse(s)          # validate it's a real date
            print(s)
            return
        except ValueError:
            pass

    # last-working-day mode: emit up to 30 non-weekend candidates, newest first
    candidate = today - timedelta(days=1)
    emitted = 0
    while emitted < 30:
        if not _is_weekend(candidate):
            print(candidate.isoformat())
            emitted += 1
        candidate -= timedelta(days=1)


def cmd_format(date_str: str) -> None:
    d = _parse(date_str)
    nd = d + timedelta(days=1)
    print(f"DATE: {d.isoformat()}")
    print(f"DATE_LABEL: {_label(d)}")
    print(f"WEEKDAY: {_WEEKDAYS[d.weekday()]}")
    print(f"DATE_START: {d.isoformat()}T00:00:00{_TZ}")
    print(f"DATE_END: {d.isoformat()}T23:59:59{_TZ}")
    print(f"NEXT_DATE: {nd.isoformat()}")
    print(f"GMAIL_DATE: {d.strftime('%Y/%m/%d')}")
    print(f"GMAIL_NEXT_DATE: {nd.strftime('%Y/%m/%d')}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "candidates":
        cmd_candidates(sys.argv[2] if len(sys.argv) > 2 else "", sys.argv[3])
    elif cmd == "format":
        cmd_format(sys.argv[2])
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)
