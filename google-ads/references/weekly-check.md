# Google Ads weekly check

About 15 minutes. Compare the last 7 days with the 7 days before, and the last 30 days with
the 30 before.

## 1. Spend

- [ ] Spend is within the owner's approved monthly budget, pro rata.
- [ ] No day spent above 150% of the expected day without a reason.
- [ ] Billing is active; no failed payment.

## 2. Results (from the lead store, not only Google Ads)

- [ ] Paid leads, calls and bookings this week, with the `gclid` or `google` source.
- [ ] Cost per lead = spend / paid leads. Compare with the owner's target (job profit x close
  rate is the most a lead can cost).
- [ ] Lead quality: how many were real customers, spam, wrong service or out of area. Ask the
  owner, or read the lead statuses.
- [ ] Google Ads conversions and lead store counts are within about 20% of each other. A
  bigger gap means a tracking problem: check `google-analytics`, step 8.

## 3. Search terms

- [ ] Read every search term with spend. Draft negatives (`references/negative-keywords.md`).
- [ ] Note new themes that converted and draft keywords for them.

## 4. Ads, assets and policy

- [ ] No disapproved or limited ads, assets or keywords. Read the policy reason.
- [ ] Ad strength and asset performance: replace headlines rated "Low" after 4+ weeks.
- [ ] Call asset schedule still matches the hours someone answers.

## 5. Settings drift

- [ ] Search Partners and Display still off.
- [ ] Location option still "presence".
- [ ] Auto-applied recommendations still off.
- [ ] One primary conversion source for each result.

## 6. Recommendations tab

Read it; do not apply it. Draft a change request only for a recommendation that fits the
plan (for example a sitelink suggestion), never for "raise your budget" alone.

## Report to the owner

```
Google Ads, week of <date>
Spent $<x> of $<budget> planned. <n> leads at $<cpl> each (last week <n> at $<cpl>).
Good: <the theme or ad that brought most leads>.
Waste stopped: <n> negatives added for <themes>.
For your approval:
1. <change> - why: <reason> - cost: <$ or none> - expected: <effect>
```

Each change request waits for the owner's yes before anyone applies it.
