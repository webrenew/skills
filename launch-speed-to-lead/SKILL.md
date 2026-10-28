---
name: launch-speed-to-lead
description: >
  Reply to every new lead within minutes and follow up automatically until the lead books,
  replies or opts out. Use this skill when the user mentions lead follow-up, speed to lead,
  auto-reply, instant response, missed leads, nurture sequence, drip emails after an enquiry,
  owner alerts for new leads, or review requests after a job. Built for Next.js with Resend
  and Trigger.dev, and the ideas apply to any stack. Part of the Webrenew Launch pack.
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
| +1 business day, if no reply or booking | Lead | Short check-in that answers the most common question for their request | Restart the conversation |
| +3 business days | Lead | Proof: a relevant project, review or before-and-after | Build trust |
| +7 business days | Lead | "Close the loop": should we keep your request open? | A clear yes or no |
| After a completed job | Customer | Thank-you and review request (`launch-local-seo` has the link) | Reviews |

Keep each message short, plain and from a person ("Sam at Harbor Plumbing"), with a reply
address that a person reads. Write in the business's voice. Never pretend a message is
hand-typed if it is not.

## Stop conditions

Check all of these before **every** send, not only at the start:

- The lead replied (by email, text, or a status the owner set).
- The lead booked (see `launch-booking-payments`, which marks the lead `booked`).
- The lead unsubscribed or asked to stop.
- The owner marked the lead won, lost or spam.
- The send would land outside business hours for a follow-up (instant replies are fine at
  any hour; follow-ups wait for the morning in the business's time zone).

## Implementation (Trigger.dev + Resend)

One durable task per lead. It waits between steps and re-reads the lead before each send.

```ts
// trigger/lead-follow-up.ts
import { schemaTask, wait } from "@trigger.dev/sdk"
import { Resend } from "resend"
import { z } from "zod"

import { getLead, nextBusinessMorning } from "@/lib/leads"
import { confirmationEmail, checkInEmail, proofEmail, closeLoopEmail } from "@/emails/lead-sequence"

const resend = new Resend(process.env.RESEND_API_KEY)
const FROM = "Sam at Harbor Plumbing <sam@harborplumbing.com>"

const STEPS = [
  { key: "check-in", afterBusinessDays: 1, email: checkInEmail },
  { key: "proof", afterBusinessDays: 3, email: proofEmail },
  { key: "close-loop", afterBusinessDays: 7, email: closeLoopEmail },
] as const

async function shouldStop(leadId: string) {
  const lead = await getLead(leadId)
  return !lead || lead.status !== "new" || lead.repliedAt !== null || lead.unsubscribedAt !== null
}

export const leadFollowUp = schemaTask({
  id: "lead-follow-up",
  schema: z.object({ leadId: z.string() }),
  run: async ({ leadId }) => {
    const lead = await getLead(leadId)
    if (!lead?.email) return { sent: 0 }

    await resend.emails.send(
      { from: FROM, to: lead.email, subject: "We got your request", react: confirmationEmail(lead) },
      { idempotencyKey: `${leadId}:confirmation` },
    )

    let sent = 1
    for (const step of STEPS) {
      await wait.until({ date: nextBusinessMorning(lead.createdAt, step.afterBusinessDays) })
      if (await shouldStop(leadId)) break
      await resend.emails.send(
        {
          from: FROM, to: lead.email, subject: step.email.subject(lead), react: step.email.body(lead),
          headers: { "List-Unsubscribe": `<https://harborplumbing.com/unsubscribe?lead=${lead.unsubscribeToken}>` },
        },
        { idempotencyKey: `${leadId}:${step.key}` },
      )
      sent++
    }
    return { sent }
  },
})
```

Start it from the lead notification task (see `launch-lead-capture`) with
`idempotencyKey: leadId`, so one lead never gets two sequences. Waits in Trigger.dev do not
use compute while they sleep, so a seven-day sequence costs the same as an instant one.

### Detect replies

- Use a reply-to address on a domain with inbound email (Resend inbound, or the owner's
  mailbox with a forwarding rule to a webhook). On an inbound message from the lead's address,
  set `repliedAt`.
- Give the owner one button in the alert email or dashboard: "I talked to them". It sets the
  lead status, which stops the sequence.

## Owner alert

The owner alert matters as much as the customer email. Make it actionable from a phone:

```
New lead: Dana Ruiz, water heater leaking (Mount Pleasant)
Call: tel:+18435550199   Email: mailto:dana@example.com
Came from: Google Business Profile, page /water-heater-repair
Mark as handled: https://.../leads/123/handled
```

Send it by the channel the owner reads fastest: SMS or Slack for most trades, email for
offices. Alert again (or alert a second person) if a lead is still `new` after 30 minutes in
business hours.

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
- Send from the business's own domain with SPF, DKIM and DMARC set, or the emails land in spam.
- Never add a lead to a newsletter without the marketing consent from the form.

## Measure

- Median time to first reply (target: under 5 minutes for the automatic reply, under 1
  hour in business hours for a human call).
- Share of leads that reply or book, by step. Remove steps that never get a response.
- Unsubscribe and spam-complaint rates. A complaint rate above about 0.3% hurts delivery for
  every email the business sends.

## Related Launch skills

- `launch-lead-capture`: stores the lead and starts this sequence.
- `launch-lead-triage-agent`: drafts a personal first reply for the owner to approve.
- `launch-agent-guardrails`: rules for any message an agent writes.
