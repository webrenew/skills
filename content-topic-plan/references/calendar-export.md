# Calendar Export

Give the owner two files: a CSV for a spreadsheet and an ICS file for their calendar. Both
come from the same calendar table.

## CSV: `content-plan.csv`

One row per item. Quote every field, and double any `"` inside a field (`""`), as RFC 4180
asks; a field with a line break needs the same quotes. Dates are `YYYY-MM-DD`.

```csv
"uid","sequence","date","type","topic","intent","hub_page","first_hand_asset","owner_task","owner_due","status","score"
"content-post-water-heater-leaking-from-bottom","0","2026-11-04","post","Water heater leaking from the bottom: repair or replace?","compare","/services/water-heaters","Photos and notes from job #4471","Send 3 photos and approve the draft","2026-11-02","planned","18"
"content-case-study-mount-pleasant-tank","0","2026-11-18","case-study","A 1998 tank replaced in one visit in Mount Pleasant","learn","/services/water-heaters","Job #4471 with written consent","Ask the customer the 5 questions","2026-11-11","planned","15"
```

`type` is one of `post`, `case-study` and `refresh`. A question that an existing post already
answers becomes a `refresh` row with that post's slug, handed to `content-refresh`. `status`
is one of `planned`, `brief`, `draft`, `waiting-for-owner`, `approved`, `published`,
`skipped`. The `uid` is `content-<type>-<slug>`.

## ICS: `content-plan.ics`

One all-day event per owner task, on the owner's due date, so the calendar shows what the
owner must do, not only what goes live. Use CRLF line endings (RFC 5545). `DTEND` is the day
after `DTSTART` for an all-day event. Build each `UID` from the item type and slug only, never
a date, plus `@` and the site's domain (the CSV `uid` + `@harborplumbing.com`), so it stays
the same when the plan moves and a re-import updates the event instead of adding a copy. The
CSV's `uid` and `sequence` columns store both values: add 1 to `sequence` when a row's date or
task changes, and write it as `SEQUENCE`. Set `DTSTAMP` to the time of each export, in UTC.
Calendar apps then accept the update.

```ics
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Webrenew//content-topic-plan//EN
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:content-post-water-heater-leaking-from-bottom@harborplumbing.com
DTSTAMP:20261028T120000Z
SEQUENCE:0
DTSTART;VALUE=DATE:20261102
DTEND;VALUE=DATE:20261103
SUMMARY:Blog: send photos and approve the water heater post
DESCRIPTION:Goes live 2026-11-04. Photos from job #4471. About 30 minutes.
END:VEVENT
END:VCALENDAR
```

Escape commas, semicolons and backslashes in text fields with a backslash, and fold lines
longer than 75 octets.
