---
name: launch-speed-to-lead
description: >
  Reply to every new lead within minutes and follow up automatically until the lead books,
  replies or opts out. Use this skill when the user mentions lead follow-up, speed to lead,
  auto-reply, instant response, missed leads, nurture sequence, drip emails after an enquiry,
  owner alerts for new leads, or review requests after a job. Built for Next.js with Resend
  and Trigger.dev, and the ideas apply to any stack.
---

# Speed to Lead: Reply in Minutes, Follow Up Without Thinking About It

**RULE: The first reply goes out within 5 minutes, any hour. Every later message checks
first whether the lead has replied, booked or opted out, and stops if so.**

A lead who has to wait calls the next business on the list. Research on web leads (Harvard
Business Review, "The Short Life of Online Sales Leads", 2011) found that firms that replied
within an hour were about 7 times as likely to qualify the lead as firms that replied an
hour later. Most small businesses reply the next day, or never. Automation closes that gap.

## The sequence

| When | To | Message | Goal |
|---|---|---|---|
| Instant | Owner | New lead alert with name, need, and one-tap call and email links | The owner can call while the lead is still on the site |
| Instant | Lead | Personal confirmation: what happens next, when, who; booking link; phone number | The lead stops shopping around |
| +1 business day, if no reply or booking (and consent where needed, see "Email rules") | Lead | Short check-in "in case you have more questions", with the answer to the most common one for their request. It reads right whether or not the owner has replied in person. | Restart the conversation |
| +3 business days | Lead | Proof: a relevant project, review or before-and-after | Build trust |
| +7 business days | Lead | "Close the loop": should we keep your request open? | A clear yes or no |
| 1 day after the owner marks the job `won` | Customer | Thank-you and review request (see "Review request after a won job") | Reviews |

Keep each message short, plain and from a person ("Sam at Harbor Plumbing"), with a reply
address that a person reads. Write in the business's voice. Never pretend a message is
hand-typed if it is not.

## Stop conditions

Check all of these before **every** follow-up, not only at the start. The confirmation ("we
got your request") answers the customer's own request, so it needs no marketing consent and
goes out even after a reply. It still stops for spam, an unsubscribe, a test lead and a lead
marked `possibleSpam`.

- The lead replied (`repliedAt` is set).
- The status is not `new` or `contacted`: they booked (see `launch-booking-payments`), their
  booking was cancelled, or the owner marked the lead won, lost or spam. The owner's own
  reply (status `contacted`) does not stop the sequence; the customer's answer does.
- The lead unsubscribed (`unsubscribedAt` is set).
- The lead is marked `possibleSpam` and the owner has not tapped "Not spam" yet.
- The lead is marked `isTest` (for example a launch test entry, marked after it was sent).
- A follow-up needs marketing consent here and `marketingConsent` is false (see "Email rules").
- The send would land outside business hours for a follow-up (instant replies are fine at
  any hour; follow-ups wait for the morning in the business's time zone).

## Implementation (Trigger.dev + Resend)

This uses the shared lead model and the `lead-intake` orchestrator from
`launch-lead-capture`. `lead-intake` starts this task once per lead with a global
idempotency key. Do not start it from anywhere else.

```ts
// lib/send-email.ts
import { Resend } from "resend"

import { business } from "@/lib/business"

const resend = new Resend(process.env.RESEND_API_KEY)
const SITE = business.url                              // launch-local-seo

/** The footer link and the List-Unsubscribe header use this one URL. Tokens can hold + / =. */
export function unsubscribeUrl(token: string) {
  return `${SITE}/unsubscribe?token=${encodeURIComponent(token)}`
}

/** Resend returns `{ data, error }` and does not throw. Throw, so the task retries. */
export async function sendEmail(payload: Parameters<typeof resend.emails.send>[0], idempotencyKey: string) {
  const { data, error } = await resend.emails.send(payload, { idempotencyKey })
  if (error) throw new Error(`Resend: ${error.name}: ${error.message}`)
  return data
}
```

```ts
// trigger/lead-follow-up.ts
import { schemaTask, wait } from "@trigger.dev/sdk"
import { z } from "zod"

import { getLead, nextBusinessMorning, recordStepSent, type Lead } from "@/lib/leads"
import { sendEmail, unsubscribeUrl } from "@/lib/send-email"
import { checkInEmail, closeLoopEmail, confirmationEmail, proofEmail } from "@/emails/lead-sequence"

const FROM = "Sam at Harbor Plumbing <sam@harborplumbing.com>"
// UK and EU: true (follow-ups only with marketing consent). A US business that relies on
// CAN-SPAM can set FOLLOW_UPS_NEED_CONSENT=false. See "Email rules".
const FOLLOW_UPS_NEED_CONSENT = process.env.FOLLOW_UPS_NEED_CONSENT !== "false"

const FOLLOW_UPS = [
  { key: "check-in", afterBusinessDays: 1, email: checkInEmail },
  { key: "proof", afterBusinessDays: 3, email: proofEmail },
  { key: "close-loop", afterBusinessDays: 7, email: closeLoopEmail },
] as const

// The owner's reply moves a lead to "contacted" and keeps the sequence going. The customer's
// reply (repliedAt), a booking, an opt-out and the final statuses stop it.
const FOLLOW_UP_STATUSES = new Set<Lead["status"]>(["new", "contacted"])

function stillWaiting(lead: Lead | null): lead is Lead & { email: string } {
  if (!lead?.email || !FOLLOW_UP_STATUSES.has(lead.status)) return false
  if (lead.isTest || lead.repliedAt || lead.unsubscribedAt || lead.possibleSpam) return false
  return !FOLLOW_UPS_NEED_CONSENT || lead.marketingConsent
}

export const leadFollowUp = schemaTask({
  id: "lead-follow-up",
  schema: z.object({ leadId: z.string() }),
  retry: { maxAttempts: 5, minTimeoutInMs: 30_000, maxTimeoutInMs: 600_000, factor: 2 },
  run: async ({ leadId }) => {
    const first = await getLead(leadId)
    if (!first?.email || first.isTest || first.possibleSpam) return { sent: [] }

    // A retry starts run() again from the top. `sentSteps` makes every step run once.
    // `first` is read fresh on every attempt, so a retry sees a lead marked spam since.
    if (first.status === "spam" || first.unsubscribedAt) return { sent: [] }
    if (!first.sentSteps.includes("confirmation")) {
      await sendEmail({ from: FROM, to: first.email, subject: "We got your request", react: confirmationEmail(first) }, `${leadId}:confirmation`)
      await recordStepSent(leadId, "confirmation")
    }

    // Steps are planned from the lead's arrival. When the sequence starts late (the owner
    // clears a possible-spam lead days later, or a run succeeds after an outage), past steps
    // must not fire back to back: each waits for the next business morning after the one before.
    let earliest = new Date()
    for (const step of FOLLOW_UPS) {
      if (first.sentSteps.includes(step.key)) continue   // sent before a retry
      const planned = nextBusinessMorning(first.createdAt, step.afterBusinessDays)
      const due = planned > earliest ? planned : nextBusinessMorning(earliest, 1)
      earliest = due
      await wait.until({ date: due })
      const lead = await getLead(leadId)               // re-read: they may have replied or booked
      if (!stillWaiting(lead)) break
      if (lead.sentSteps.includes(step.key)) continue
      await sendEmail({
        from: FROM, to: lead.email, subject: step.email.subject(lead), react: step.email.body(lead),
        headers: {
          "List-Unsubscribe": `<${unsubscribeUrl(lead.unsubscribeToken)}>`,
          "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
        },
      }, `${leadId}:${step.key}`)
      await recordStepSent(leadId, step.key)
    }
    const final = await getLead(leadId)
    return { sent: final?.sentSteps ?? [] }
  },
})
```

Waits in Trigger.dev do not use compute while they sleep, so a seven-day sequence costs the
same as an instant one. `wait.until` with a past date returns at once. That is why every step
checks `sentSteps` before it sends, and why a late start moves each due step to the next
business morning after the step before it instead of sending them all at once.

### The unsubscribe route

`List-Unsubscribe-Post` tells mailbox providers that the URL accepts a one-click `POST`
(RFC 8058) and answers 200 with no redirect. Build that route. Its `GET` asks first, so a link
scanner that opens the footer link does not unsubscribe anyone.

```ts
// app/unsubscribe/route.ts
import { unsubscribeByToken } from "@/lib/leads"

function page(body: string) {
  return new Response(
    `<!doctype html><meta name="viewport" content="width=device-width"><title>Unsubscribe</title>` +
      `<main style="font:16px system-ui;max-width:32rem;margin:4rem auto;padding:0 1rem">${body}</main>`,
    { headers: { "content-type": "text/html; charset=utf-8" } },
  )
}

const INCOMPLETE = "<p>This link is incomplete. Reply to this email and we will remove you.</p>"

// The footer link: confirm with one button.
export function GET(request: Request) {
  const token = new URL(request.url).searchParams.get("token") ?? ""
  if (!token) return page(INCOMPLETE)
  return page(
    `<p>Stop follow-up emails from Harbor Plumbing?</p>` +
      `<form method="post" action="/unsubscribe?token=${encodeURIComponent(token)}"><button>Unsubscribe</button></form>`,
  )
}

// The button above, and the mailbox's one-click unsubscribe. Always 200, never a redirect.
export async function POST(request: Request) {
  const token = new URL(request.url).searchParams.get("token") ?? ""
  if (!token) return page(INCOMPLETE)                  // writes nothing
  await unsubscribeByToken(token)
  return page("<p>You are unsubscribed. We will not email you again about this request.</p>")
}
```

The answer is the same for an unknown token, so the route tells nobody which tokens exist.
A link with no token (cut off by a mail client) gets a page that asks the person to reply
instead.
The footer link in every follow-up uses `unsubscribeUrl(lead.unsubscribeToken)` too.

### Review request after a won job

When the owner marks a lead `won`, start one more task. It is separate from the follow-up
sequence, which has stopped by then.

```ts
// trigger/review-request.ts
import { schemaTask, wait } from "@trigger.dev/sdk"
import { z } from "zod"

import { business } from "@/lib/business"                 // launch-local-seo
import { getLead, recordStepSent } from "@/lib/leads"
import { sendEmail } from "@/lib/send-email"
import { reviewRequestEmail } from "@/emails/lead-sequence"

export const reviewRequest = schemaTask({
  id: "review-request",
  schema: z.object({ leadId: z.string() }),
  run: async ({ leadId }) => {
    await wait.for({ days: 1 })                       // after the job, not during it
    const lead = await getLead(leadId)
    if (!lead?.email || lead.status !== "won" || lead.unsubscribedAt || lead.sentSteps.includes("review-request")) return
    await sendEmail({
      from: "Sam at Harbor Plumbing <sam@harborplumbing.com>", to: lead.email,
      subject: "How did we do?", react: reviewRequestEmail(lead, business.googleReviewUrl),
    }, `${leadId}:review-request`)
    await recordStepSent(leadId, "review-request")
  },
})
```

Ask every won customer the same way. Never filter by how happy they seem (see
`launch-local-seo`, section 5).

### Phone-only leads

The form allows a phone number without an email. Those leads get no emails, so the owner
alert must say **"Call: no email given"** at the top, and the 30-minute reminder (see "Owner alert") matters
most for them. Send texts only with explicit text consent (see "Text messages").

### Detect replies

- Use a reply-to address on a domain with inbound email (Resend inbound, or the owner's
  mailbox with a forwarding rule to a webhook). On an inbound message from the lead's address,
  set `repliedAt` and call `setStatus(id, "contacted", { from: ["new"] })`.
- Give the owner one button in the alert email or dashboard: "I talked to them". A
  conversation counts as their reply: it sets `repliedAt` and makes the same status change,
  which stops the sequence. A lead that is already `booked` or `won`
  keeps that status (see the status rules in `launch-lead-capture`).

## Owner alert

The owner alert matters as much as the customer email. Make it actionable from a phone:

```
New lead: Dana Ruiz, water heater leaking (Mount Pleasant)
Call: tel:+18435550199   Email: mailto:dana@example.com
Came from: Google Business Profile, page /water-heater-repair
I talked to them: https://.../leads/123/contacted
```

Send it by the channel the owner reads fastest: SMS or Slack for most trades, email for
offices. The owner alert itself, and one reminder (or an alert to a second person) when a
real lead is still `new` after 30 minutes in business hours, come from `lead-intake` and its
sweeper in `launch-lead-capture`. Test leads never get the reminder.

## Text messages

Text gets the fastest replies, and it has the strictest rules:

- Send texts only to people who gave clear consent to receive them, on the form, in words.
- In the US, business texting needs A2P 10DLC registration through the SMS provider, and
  TCPA rules apply. Other countries have their own rules. Confirm the rules for the owner's
  country before you turn on texts.
- Every text sequence honors STOP.

## Email rules

- Follow-up and marketing emails include an unsubscribe link and the business's postal
  address (CAN-SPAM in the US; similar rules elsewhere). The direct reply to their enquiry is
  transactional.
- **Legal basis.** The confirmation answers the customer's own request, so it needs no
  marketing consent. The check-in, proof and close-the-loop emails go beyond that reply. In
  the US, CAN-SPAM allows them with an unsubscribe link and the postal address. In the UK and
  EU, send them only to leads with `marketingConsent`, unless the business's adviser confirms
  that the soft opt-in covers them. `FOLLOW_UPS_NEED_CONSENT` (on by default) enforces this.
- Send from the business's own domain with SPF, DKIM and DMARC set, or the emails land in spam.
- Never add a lead to a newsletter without the marketing consent from the form.

## Measure

- Median time to first reply (target: under 5 minutes for the automatic reply, under 1
  hour in business hours for a human call).
- Share of leads that reply or book, by step. Remove steps that never get a response.
- Unsubscribe and spam-complaint rates. Google's sender rules ask senders to stay under 0.1%
  and never reach 0.3%. Above that, delivery suffers for every email the business sends.

## Related Launch skills

- `launch-lead-capture`: the lead model, and the `lead-intake` task that starts this sequence.
- `launch-lead-triage-agent`: drafts a personal first reply for the owner to approve.
- `launch-agent-guardrails`: rules for any message an agent writes.
