# The one-minute weekly report

Five lines the owner can read on a phone. Every number has a comparison. Every week ends
with one action.

## Template

```
Week of <Monday date>: <leads> leads (<+/- vs last week>), <calls> calls, <bookings> bookings, <sales> in sales.
Best channel: <channel>, <leads> leads at <cost per lead> each.
Weakest: <channel>, <leads> leads at <cost per lead> each.
Top page for leads: <path> (<leads> leads).
One thing to do: <one action, with who does it>.
```

Rules:

- **Leads, bookings and sales come from the lead store** (`launch-lead-capture`), without
  test and spam leads. GA4 undercounts visitors who decline consent or block scripts, so the
  owner's totals never come from GA4.
- **Channel mix comes from the lead's stored UTMs and `gclid`**, with GA4 as the trend check.
  If the two disagree by more than about 20%, check the tag before you report.
- **Cost per lead** = ad spend for the week from Google Ads or Meta, divided by the leads from
  that channel in the lead store. Not the platform's own conversion count: platforms count
  their own clicks generously.
- **Calls:** `call_click` events in GA4 are taps, not answered calls. Say "call taps" unless a
  call tracking number gives real calls.
- One action only, the one that makes the most money or saves the most: answer waiting leads,
  pause a channel that has cost more than a job's profit with no lead, fix a broken form.
- When nothing changed, say so in one line. That is a good report.

## GA4 Data API query

For a scheduled job (for example in `launch-site-health-report`), give a Google Cloud service
account **Viewer** access on the GA4 property, enable the Google Analytics Data API, and run
one report:

```ts
// lib/ga4-weekly.ts
import { BetaAnalyticsDataClient } from "@google-analytics/data"

const client = new BetaAnalyticsDataClient() // credentials from the environment, server only

/** Key events by default channel group for the last 7 full days. */
export async function weeklyChannelReport(propertyId: string) {
  const [report] = await client.runReport({
    property: `properties/${propertyId}`,
    dateRanges: [
      { startDate: "7daysAgo", endDate: "yesterday", name: "this_week" },
      { startDate: "14daysAgo", endDate: "8daysAgo", name: "last_week" },
    ],
    dimensions: [{ name: "sessionDefaultChannelGroup" }, { name: "eventName" }],
    metrics: [{ name: "eventCount" }],
    dimensionFilter: {
      filter: {
        fieldName: "eventName",
        inListFilter: { values: ["generate_lead", "call_click", "book_appointment", "purchase"] },
      },
    },
  })
  return report.rows ?? []
}
```

- Wrap the call in try/catch in the job. A failed GA4 query must not stop the rest of the
  weekly email; say "analytics unavailable this week" instead.
- The Data API has daily quotas per property. One weekly report uses a tiny part of them.

## In the GA4 interface

For an owner who wants to look:

- **Reports, Acquisition, Traffic acquisition:** sessions and key events by channel.
- **Reports, Engagement, Pages and screens**, filtered to `generate_lead`: pages that
  produce leads.
- **Advertising, Attribution:** paths before a key event. Useful only with steady volume.
- Save one Exploration named "Weekly leads by channel" and share its link with the owner.
