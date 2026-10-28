# Calendar Export

Give the owner two files: a CSV for a spreadsheet and an ICS file for their calendar. Both
come from the same calendar table.

## CSV: `content-plan.csv`

One row per item. Quote every field. Dates are `YYYY-MM-DD`.

```csv
"date","type","topic","intent","hub_page","first_hand_asset","owner_task","owner_due","status","score"
"2026-11-04","post","Water heater leaking from the bottom: repair or replace?","compare","/services/water-heaters","Photos and notes from job #4471","Send 3 photos and approve the draft","2026-11-02","planned","18"
"2026-11-18","case-study","A 1998 tank replaced in one visit in Mount Pleasant","learn","/services/water-heaters","Job #4471 with written consent","Ask the customer the 5 questions","2026-11-11","planned","15"
```

`status` is one of `planned`, `brief`, `draft`, `waiting-for-owner`, `approved`, `published`,
`skipped`.

## ICS: `content-plan.ics`

One all-day event per owner task, on the owner's due date, so the calendar shows what the
owner must do, not only what goes live. Use CRLF line endings (RFC 5545). `DTEND` is the day
after `DTSTART` for an all-day event. Each `UID` stays the same when the plan changes, so a
re-import updates events instead of adding copies.

```ics
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Webrenew//content-topic-plan//EN
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:content-2026-11-04-water-heater-leaking@harborplumbing.com
DTSTAMP:20261028T120000Z
DTSTART;VALUE=DATE:20261102
DTEND;VALUE=DATE:20261103
SUMMARY:Blog: send 3 photos and approve "Water heater leaking from the bottom"
DESCRIPTION:Goes live 2026-11-04. Photos from job #4471. About 30 minutes.
END:VEVENT
END:VCALENDAR
```

Escape commas, semicolons and backslashes in text fields with a backslash, and fold lines
longer than 75 octets.
