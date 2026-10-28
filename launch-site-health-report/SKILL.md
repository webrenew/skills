---
name: launch-site-health-report
description: >
  Build a scheduled job that checks a small business website every week and emails the owner
  a short plain-English report: is the site up, does the form still deliver, how fast is it,
  are links broken, when do the certificate and domain expire, and how many leads came in.
  Alerts at once when something breaks. Use this skill for site monitoring, weekly reports,
  uptime checks, form tests, Core Web Vitals tracking, broken-link checks, or "tell me if my
  site breaks". Built with Trigger.dev scheduled tasks. Part of the Webrenew Launch pack.
---

# Site Health Report: Know the Site Works Without Checking It

**RULE: Breakages alert at once. Everything else waits for one short weekly email that the
owner can read in under a minute.**

Most small business sites break quietly: a form stops delivering after a plugin or provider
change, a certificate expires, a page starts to 404. The owner finds out from a customer, or
never. This job finds out first.

## What to check

| Check | How | Alert at once when |
|---|---|---|
| Site is up | `GET` the home page and main landing page | Status is not 200, or the response takes over 10 s |
| Form delivers | Submit a test lead, then confirm it was stored and the alert was sent | The test lead is missing after 5 minutes |
| Certificate | Read the TLS certificate expiry | Under 14 days left |
| Domain | Registrar or RDAP expiry date | Under 30 days left and auto-renew is off |
| Broken links | Fetch every URL in `sitemap.xml` and internal links on key pages | A page in the sitemap returns 4xx or 5xx |
| `noindex` | Check robots meta and `robots.txt` on key pages | A production page says `noindex` |
| Speed | Chrome UX Report (field data) or PageSpeed Insights | LCP, INP or CLS moves from "good" to "poor" |
| Leads | Count leads this week vs last week, by source | (report only) |

## Scheduled task

```ts
// trigger/site-health.ts
import { schedules } from "@trigger.dev/sdk"

import { runChecks } from "@/lib/site-health/checks"
import { sendAlert, sendWeeklyReport } from "@/lib/site-health/report"

export const siteHealthDaily = schedules.task({
  id: "site-health-daily",
  cron: { pattern: "0 7 * * *", timezone: "America/New_York", environments: ["PRODUCTION"] },
  maxDuration: 300,
  run: async () => {
    const results = await runChecks({ quick: true })        // uptime, form, TLS, noindex
    const broken = results.filter((r) => r.status === "fail")
    if (broken.length > 0) await sendAlert(broken)
    return { failed: broken.length }
  },
})

export const siteHealthWeekly = schedules.task({
  id: "site-health-weekly",
  cron: { pattern: "0 8 * * 1", timezone: "America/New_York", environments: ["PRODUCTION"] },
  maxDuration: 900,
  run: async () => {
    const results = await runChecks({ quick: false })       // everything, including links and speed
    await sendWeeklyReport(results)
    return { checks: results.length }
  },
})
```

Use the business's time zone. For tighter uptime checking than daily, use a dedicated uptime
service (Vercel, Better Stack, UptimeRobot, Checkly) and keep this job for the deeper checks.

## Check snippets

**Certificate expiry**

```ts
import tls from "node:tls"

export function certificateDaysLeft(host: string): Promise<number> {
  return new Promise((resolve, reject) => {
    const socket = tls.connect({ host, port: 443, servername: host }, () => {
      const validTo = new Date(socket.getPeerCertificate().valid_to)
      socket.end()
      resolve(Math.floor((validTo.getTime() - Date.now()) / 86_400_000))
    })
    socket.setTimeout(10_000, () => socket.destroy(new Error("TLS timeout")))
    socket.on("error", reject)
  })
}
```

**Field speed data (Chrome UX Report API)**

```ts
export async function fieldVitals(origin: string) {
  const response = await fetch(
    `https://chromeuxreport.googleapis.com/v1/records:queryRecord?key=${process.env.CRUX_API_KEY}`,
    { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ origin, formFactor: "PHONE" }) },
  )
  if (response.status === 404) return null      // not enough traffic for field data
  if (!response.ok) throw new Error(`CrUX ${response.status}`)
  const { record } = await response.json()
  return {
    lcp: record.metrics.largest_contentful_paint?.percentiles.p75,
    inp: record.metrics.interaction_to_next_paint?.percentiles.p75,
    cls: record.metrics.cumulative_layout_shift?.percentiles.p75,
  }
}
```

Small sites often have too little traffic for field data. Fall back to a PageSpeed Insights
lab run (`https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=...&strategy=mobile`)
and say in the report that it is a lab estimate.

**Form test**

- Submit through the real form endpoint with a marker the system recognizes (for example a
  dedicated test email address), so it skips the customer follow-up and owner alert, and
  write the result to the lead store with `isTest: true`.
- Confirm the row exists and the notification job ran. Then delete or hide the test lead.
- Never let test leads reach the owner's CRM totals or the conversion events.

**Broken links:** fetch the sitemap, request each URL with a concurrency limit of about 4
and a timeout, and check only the site's own domain. Report each broken URL with the page
that links to it.

## The weekly email

Write it for the owner, not for a developer. Three numbers first, then only what needs
attention.

```
Subject: Harbor Plumbing site: all good · 14 leads this week (+3)

This week
• 14 leads (last week 11). Top source: Google Business Profile (6).
• Site was up for every check. Form test passed on Monday.
• Phone speed: good (page shows in 1.9 s for most visitors).

Needs attention
• 2 broken links on /services/drains: the "Warranty" link goes to a removed page.
  We will fix it, or reply "ignore".

Coming up
• Domain renews automatically on 3 March 2027.
```

- When nothing needs attention, say so in the subject line. That is the best report.
- No charts the owner must interpret. Every issue says what it means for customers and
  what happens next.
- Send from the agency or system address, with a reply address that a person reads.

## Alerts

- One alert per broken thing per day, not one per check run.
- Say the impact first: "Your contact form has not delivered leads since 06:10."
- Include the next step and who is on it.

## Related Launch skills

- `launch-site-checklist`: the one-time launch check that this job repeats.
- `launch-lead-capture`: the form and the delivery path that the form test exercises.
- `website-speed-optimization`: fixes when the speed check fails.
