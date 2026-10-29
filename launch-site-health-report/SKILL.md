---
name: launch-site-health-report
description: >
  Build scheduled jobs that check a small business website every morning and alert when
  something breaks, plus a short plain-English weekly email for the owner: is the site up,
  does the form still deliver, how fast is it, are links broken, when do the certificate and
  domain expire, and how many leads came in. Use this skill for site monitoring, weekly reports,
  uptime checks, form tests, Core Web Vitals tracking, broken-link checks, or "tell me if my
  site breaks". Built with Trigger.dev scheduled tasks.
---

# Site Health Report: Know the Site Works Without Checking It

**RULE: A breakage alerts the same morning the daily check finds it. Everything else waits
for one short weekly email that the owner can read in under a minute.**

Most small business sites break quietly: a form stops delivering after a plugin or provider
change, a certificate expires, a page starts to 404. The owner finds out from a customer, or
never. This job finds out first.

## What to check

| Check | How | Alert at once when |
|---|---|---|
| Site is up | `GET` the home page and main landing page | Status is not 200, or the response takes over 10 s |
| Form delivers | Call the test entry point, then confirm the lead was stored and `ownerAlertedAt` is set | Not stored, or no alert after 5 minutes. A 503 from the test route (`LEAD_TEST_SECRET` or `LEAD_TEST_INBOX` unset), a 401 or 403 (the job's secret does not match the site's), or a site that is not `business.url`, is a configuration error: alert the agency, and do not tell the owner the form is broken. |
| Certificate | Read the TLS certificate and its expiry | Not valid for the hostname, or under 14 days left |
| Domain | Expiry date from RDAP (auto-renew status is only in the registrar's account) | Under 30 days left |
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

interface CertificateCheck {
  daysLeft: number | null    // null when the server sent no certificate
  valid: boolean             // false for expired, self-signed or wrong-hostname certificates
  problem: string | null     // e.g. "CERT_HAS_EXPIRED", "ERR_TLS_CERT_ALTNAME_INVALID"
}

export function checkCertificate(host: string): Promise<CertificateCheck> {
  return new Promise((resolve, reject) => {
    // rejectUnauthorized: false so a bad certificate is reported, not thrown. We only read
    // the certificate; no data is sent over this socket.
    const socket = tls.connect({ host, port: 443, servername: host, rejectUnauthorized: false }, () => {
      const validTo = socket.getPeerCertificate().valid_to as string | undefined   // {} when there is none
      const expiresAt = validTo ? new Date(validTo).getTime() : Number.NaN
      const daysLeft = Number.isNaN(expiresAt) ? null : Math.floor((expiresAt - Date.now()) / 86_400_000)
      // Decide "no certificate" first: without one, `authorized` is false as well.
      const problem =
        daysLeft === null ? "NO_CERTIFICATE" : socket.authorized ? null : String(socket.authorizationError ?? "UNTRUSTED")
      socket.end()
      resolve({ daysLeft, valid: problem === null, problem })
    })
    socket.setTimeout(10_000, () => socket.destroy(new Error("TLS timeout")))
    socket.on("error", reject)
  })
}
```

**Field speed data (Chrome UX Report API)**

```ts
interface CruxMetric {
  percentiles: { p75: number | string }
}

/** CrUX sends p75 values as strings (CLS) or numbers, and leaves a metric out when data is thin. */
function p75(metric: CruxMetric | undefined): number | undefined {
  if (!metric) return undefined
  const value = Number(metric.percentiles.p75)
  return Number.isFinite(value) ? value : undefined
}

export async function fieldVitals(origin: string) {
  const response = await fetch(
    `https://chromeuxreport.googleapis.com/v1/records:queryRecord?key=${process.env.CRUX_API_KEY}`,
    { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ origin, formFactor: "PHONE" }) },
  )
  if (response.status === 404) return null      // not enough traffic for field data
  if (!response.ok) throw new Error(`CrUX ${response.status}`)
  const { record } = (await response.json()) as { record: { metrics: Record<string, CruxMetric | undefined> } }
  return {
    lcp: p75(record.metrics.largest_contentful_paint),   // milliseconds
    inp: p75(record.metrics.interaction_to_next_paint),  // milliseconds
    cls: p75(record.metrics.cumulative_layout_shift),    // unitless
  }
}
```

Small sites often have too little traffic for field data. Fall back to a PageSpeed Insights
lab run (`https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=...&strategy=mobile&key=...`;
an API key avoids the shared quota) and say in the report that it is a lab estimate.

**Form test**

The form is a Server Action with no stable URL, and a scripted submit would trip its bot
traps. Use the test entry point from `launch-lead-capture` (`POST /api/leads/test` with the
`x-lead-test-secret` header). It runs the real pipeline with `isTest: true`: the lead is
stored, the alert goes to the test inbox, and no customer follow-up starts.

```ts
// lib/site-health/form-test.ts (runs inside the scheduled task)
import { wait } from "@trigger.dev/sdk"

import { business } from "@/lib/business"                 // launch-local-seo
import { getLead } from "@/lib/leads"

export type FormTestResult = "delivered" | "not-delivered" | "not-configured"

export async function formDelivers(site: string): Promise<FormTestResult> {
  // The secret goes only to the business's own site. A wrong site setting is a configuration
  // error, never a reason to post the secret elsewhere.
  if (new URL(site).origin !== new URL(business.url).origin) return "not-configured"
  const response = await fetch(`${site}/api/leads/test`, {
    method: "POST",
    headers: { "x-lead-test-secret": process.env.LEAD_TEST_SECRET ?? "" },
  })
  // The test route is not set up (503), or this job's LEAD_TEST_SECRET does not match the
  // site's (401/403, for example after a rotation). Report that to the agency, not as a broken form.
  if ([401, 403, 503].includes(response.status)) return "not-configured"
  if (!response.ok) return "not-delivered"
  const { id } = (await response.json()) as { id: string }
  await wait.for({ minutes: 5 })                        // Trigger.dev: no compute while waiting
  const lead = await getLead(id)
  return lead?.ownerAlertedAt ? "delivered" : "not-delivered"
}
```

Test leads stay out of every count, report and conversion event. Delete them after 30 days.

**Broken links:** fetch the sitemap, request each URL with a concurrency limit of about 4
and a timeout, and check only the site's own domain. Report each broken URL with the page
that links to it.

## The weekly email

Write it for the owner, not for a developer. Three numbers first, then only what needs
attention.

```
Subject: Harbor Plumbing site: 2 broken links · 14 leads this week (+3)

This week
• 14 leads (last week 11). Top source: Google Business Profile (6).
• Site was up for every check. Form test passed on Monday.
• Phone speed: good (page shows in 1.9 s for most visitors).

Needs attention
• 2 broken links on /services/drains: the "Warranty" link goes to a removed page.
  We will fix it, or reply "ignore".

Coming up
• Domain expires on 3 March 2027. Check that auto-renew is on at the registrar.
```

- The subject names the most important item that needs attention. When nothing needs
  attention, say so: `Harbor Plumbing site: all good · 14 leads this week (+3)`. That is the
  best report.
- No charts the owner must interpret. Every issue says what it means for customers and
  what happens next.
- Send from the agency or system address, with a reply address that a person reads.

## Alerts

- One alert per broken thing per day, not one per check run.
- Say the impact first: "Your contact form has not delivered leads since 06:10."
- Include the next step and who is on it.

## Related skills

- `launch-site-checklist`: the one-time launch check that this job repeats.
- `launch-lead-capture`: the form and the delivery path that the form test exercises.
- `website-speed-optimization`: fixes when the speed check fails.
