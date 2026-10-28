---
name: launch-lead-capture
description: >
  Build or fix the forms on a small business site so more visitors become leads and no lead
  is ever lost. Use this skill for contact forms, quote requests, estimate forms, "call me
  back" forms, newsletter sign-ups and any lead form, and when the user mentions form
  conversion, form spam, leads not arriving, form notifications, honeypot, CAPTCHA, or
  marketing consent. Covers fields, copy, validation, spam protection, storage-first delivery,
  consent and conversion tracking.
---

# Lead Capture: More Leads, and None Lost

**RULE: Store the lead first, then notify. A form that only sends an email loses the lead
when the email fails, and nobody finds out.**

Two jobs: get the visitor to submit, and make sure the business receives every submission.
Most sites fail the second job silently.

## 1. Ask only for what the first reply needs

Every extra field costs submissions. For a first contact you need:

| Field | Why |
|---|---|
| Name | To greet them. One field, not first and last. |
| Email **or** phone | To reply. Let them choose. Require one, not both. |
| What they need | One free-text field, or one select plus an optional note. |

Ask budget, address and timeline on the call or in the follow-up, not on the form. Add a
field only when the reply is impossible without it (for example a postcode for a business
that serves a fixed area).

## 2. Copy and layout

- **Heading states the outcome:** "Get a free quote in 1 business day", not "Contact us".
- **The button says what they get:** "Get my quote", not "Submit".
- **Put copy above the button**, never beside it. Stack the reassurance first ("No spam. We
  reply within 1 business hour."), then the button.
- Offer a phone link next to the form for people who prefer to call: `<a href="tel:...">`.
- **Success state** replaces the form and says what happens next, who replies and when, and
  gives the phone number for urgent jobs.

## 3. Fields that work on phones

```tsx
<label htmlFor="name">Name</label>
<input id="name" name="name" autoComplete="name" required />

<label htmlFor="email">Email</label>
<input id="email" name="email" type="email" autoComplete="email" inputMode="email" />

<label htmlFor="phone">Phone</label>
<input id="phone" name="phone" type="tel" autoComplete="tel" inputMode="tel" />
```

- A visible label above each field. Placeholders are not labels.
- `autoComplete` values let the phone fill the form in one tap.
- Tap targets at least 44 px high. Font size at least 16 px, so iOS does not zoom in.
- Validate on blur and on submit, not on every keystroke. Put the error under the field, in
  words that say how to fix it.

## 4. Spam protection without friction

Use cheap invisible checks first. Add a CAPTCHA only if spam still gets through.

1. **Honeypot:** a field hidden from people (off-screen, `tabIndex={-1}`,
   `autoComplete="off"`, `aria-hidden`). Bots fill it.
2. **Time trap:** render the start time in a hidden field. Submissions faster than about 3
   seconds are suspect. Autofill can make a real person that fast, so this is a signal, not
   proof.
3. **Server-side validation** of every field with a schema. Never trust the browser.
4. **Rate limit** by IP (for example 5 submissions per 10 minutes).
5. Only then, **Cloudflare Turnstile** or a similar low-friction challenge.

A trapped submission gets the normal success state, so bots learn nothing. If its fields
are valid, it is **stored with status `spam`**, not dropped, so the owner can rescue a real
lead that tripped a trap. A trapped submission that also fails validation has nothing usable
to store and is discarded.

## 5. The lead model (shared by the whole Launch pack)

Every Launch skill reads and writes the same lead record. Create it once, in the project's
database, with these fields and statuses. Other skills refer to them by these names.

```ts
// lib/leads.ts
export const LEAD_STATUSES = ["new", "contacted", "booked", "cancelled", "won", "lost", "spam"] as const
export type LeadStatus = (typeof LEAD_STATUSES)[number]

export interface Lead {
  id: string                    // UUID
  createdAt: Date
  name: string
  email: string | null
  phone: string | null
  need: string
  town: string | null
  status: LeadStatus            // change it only through setStatus (rules below)
  spamReason: string | null     // "honeypot" | "too-fast" | "owner" when status is "spam"
  isTest: boolean               // health-check leads: never counted, followed up or re-alerted
  marketingConsent: boolean
  consentAt: Date | null
  utm: Record<string, string>
  ownerAlertClaimedAt: Date | null  // set just before the owner alert is sent
  ownerAlertedAt: Date | null       // set after the owner alert (plain or triage card) is sent
  ownerReAlertedAt: Date | null     // set after the one 30-minute reminder
  repliedAt: Date | null        // set when the lead replies by email or text
  unsubscribedAt: Date | null
  unsubscribeToken: string      // random, unguessable
  sentSteps: string[]           // customer messages already sent, e.g. ["confirmation", "check-in"]
  bookingUid: string | null     // the current booking, from launch-booking-payments
}
```

### Status rules

A status moves only along these arrows. `setStatus(id, to, { from })` is a conditional
update (`... where status = any(from)`), so a late event can never undo a later state. For
example, a reply that arrives after the job is `won` does not change anything.

| To | Allowed from | Set by |
|---|---|---|
| `new` | (created) | the form |
| `contacted` | `new` | the owner ("I talked to them", or approving a reply), an inbound reply |
| `booked` | `new`, `contacted`, `cancelled` | the booking webhook |
| `cancelled` | `booked`, and only when the event's booking id equals `bookingUid` | the booking webhook |
| `won`, `lost` | any status except `spam` | the owner. `won` starts the review request. |
| `spam` | any status | the bot traps or the owner. Kept in a spam list, never deleted. |

Customer follow-ups run only while the status is `new`. Agents never change a status.

### Helpers

The helpers that other skills call, and what each must do:

| Helper | Does |
|---|---|
| `getLead(id)` | Returns the `Lead`, or `null`. |
| `createLead(input, { isTest, spamReason })` | Stores the lead (status `spam` when `spamReason` is set) and returns the id. |
| `setStatus(id, to, { from })` | Conditional status change per the rules above. Returns whether it changed. |
| `claimOwnerAlert(id)` | Atomically sets `ownerAlertClaimedAt` where it is null, or older than 15 minutes with no `ownerAlertedAt`. Returns whether this caller won the claim. |
| `releaseOwnerAlert(id)`, `markOwnerAlerted(id)` | Clear the claim after a failed send; set `ownerAlertedAt` after a successful one. |
| `listUnalertedLeads({ olderThanMinutes, newerThanHours })` | Non-spam leads with no `ownerAlertedAt`, in that age window. |
| `listLeadsToReAlert()` | `status = new`, not `isTest`, `ownerAlertedAt` over 30 minutes ago, `ownerReAlertedAt` null. |
| `recordStepSent(id, step)` | Adds `step` to `sentSteps` (atomic append, no duplicates). |
| `markLeadBooked`, `markBookingRescheduled`, `markBookingCancelled` | See `launch-booking-payments`. |
| `nextBusinessMorning(from, businessDays)` | The next opening time after `businessDays` working days, in the business's time zone. |

## 6. Store first, then run one pipeline

```ts
// app/contact/actions.ts
"use server"

import { z } from "zod"

import { createLead, leadInputSchema } from "@/lib/leads"
import { startLeadIntake } from "@/lib/lead-intake"

function botReason(input: unknown): string | null {
  const fields = (input ?? {}) as { website?: unknown; startedAt?: unknown }
  if (typeof fields.website === "string" && fields.website !== "") return "honeypot"
  const startedAt = Number(fields.startedAt)
  if (startedAt > 0 && Date.now() - startedAt < 3000) return "too-fast"
  return null
}

export async function submitLead(input: unknown) {
  const parsed = leadInputSchema.safeParse(input)
  const spamReason = botReason(input)

  // A trapped submission looks like success to the sender, but it is still stored, as spam,
  // so a fast autofill by a real person is never lost.
  if (!parsed.success) {
    return spamReason ? { ok: true as const } : { ok: false as const, errors: z.flattenError(parsed.error).fieldErrors }
  }

  const id = await createLead(parsed.data, { isTest: false, spamReason })
  if (!spamReason) await startLeadIntake(id)
  return { ok: true as const }
}
```

```ts
// lib/leads.ts (input schema)
export const leadInputSchema = z.object({
  name: z.string().trim().min(1).max(100),
  email: z.email().optional().or(z.literal("")),
  phone: z.string().trim().max(30).optional(),
  need: z.string().trim().min(1).max(2000),
  town: z.string().trim().max(100).optional(),
  marketingConsent: z.boolean(),
  utm: z.record(z.string(), z.string().max(200)).optional(),
}).refine((lead) => lead.email || lead.phone, { message: "Add an email or a phone number." })
```

### One orchestrator, one owner of each message

`lead-intake` is the only task the form starts. Each message has exactly one sender:

| Message | Sent by | Skill |
|---|---|---|
| Owner alert | `sendOwnerAlert`, called by `lead-intake`: the triage card if triage is on and succeeds, otherwise the plain alert | this skill, `launch-lead-triage-agent` |
| Owner reminder after 30 minutes (once, real leads still `new`) | `lead-intake-sweeper` | this skill |
| Customer confirmation ("we got your request") | `lead-follow-up`, step `confirmation` | `launch-speed-to-lead` |
| Personal first reply (answers their question) | the owner, after approving the triage draft | `launch-lead-triage-agent` |
| Follow-ups and review request | `lead-follow-up`, `review-request` | `launch-speed-to-lead` |

```ts
// lib/lead-intake.ts
import { idempotencyKeys, tasks } from "@trigger.dev/sdk"

import type { leadIntake } from "@/trigger/lead-intake"

export async function startLeadIntake(leadId: string) {
  try {
    await tasks.trigger<typeof leadIntake>("lead-intake", { leadId }, {
      idempotencyKey: await idempotencyKeys.create(`lead-intake:${leadId}`, { scope: "global" }),
    })
  } catch (error) {
    // The lead is stored. The sweeper below alerts the owner if this start failed.
    console.error("lead-intake start failed", leadId, error)
  }
}
```

```ts
// lib/owner-alerts.ts
import { claimOwnerAlert, markOwnerAlerted, releaseOwnerAlert, type Lead } from "@/lib/leads"
import type { PreparedTriage } from "@/lib/lead-triage-run"

/**
 * The only function that alerts the owner about a new lead. Claim first, so a retry or the
 * sweeper cannot send a second alert on SMS or Slack, which have no idempotency keys.
 */
export async function sendOwnerAlert(lead: Lead, triage: PreparedTriage | null) {
  if (!(await claimOwnerAlert(lead.id))) return "already"
  try {
    await deliverOwnerAlert(lead, triage)   // triage card if present, else the plain alert;
                                            // test leads go to the test inbox
  } catch (error) {
    await releaseOwnerAlert(lead.id)         // let the retry send it
    throw error
  }
  await markOwnerAlerted(lead.id)
  return "sent"
}
```

```ts
// trigger/lead-intake.ts
import { idempotencyKeys, schedules, schemaTask } from "@trigger.dev/sdk"
import { z } from "zod"

import { getLead, listLeadsToReAlert, listUnalertedLeads } from "@/lib/leads"
import { alertAgency, sendOwnerAlert, sendOwnerReminder } from "@/lib/owner-alerts"
import { leadFollowUp } from "./lead-follow-up"              // launch-speed-to-lead
// launch-lead-triage-agent. Without that skill, delete this import and the triage block.
import { prepareTriage, type PreparedTriage } from "@/lib/lead-triage-run"

const TRIAGE_ENABLED = process.env.LEAD_TRIAGE_ENABLED === "true"

export const leadIntake = schemaTask({
  id: "lead-intake",
  schema: z.object({ leadId: z.string() }),
  retry: { maxAttempts: 6, minTimeoutInMs: 10_000, maxTimeoutInMs: 300_000, factor: 2 },
  run: async ({ leadId }) => {
    const lead = await getLead(leadId)
    if (!lead || lead.status === "spam") return { skipped: true }

    // Customer messages: one sequence per lead, ever (global key, 30-day TTL).
    if (!lead.isTest && lead.email) {
      await leadFollowUp.trigger({ leadId }, {
        idempotencyKey: await idempotencyKeys.create(`lead-follow-up:${leadId}`, { scope: "global" }),
      })
    }

    if (lead.ownerAlertedAt) return { alerted: "already" }

    // Triage only prepares the card. A triage failure means a plain alert, never two alerts.
    let triage: PreparedTriage | null = null
    if (TRIAGE_ENABLED && !lead.isTest) {
      try {
        triage = await prepareTriage(lead)
      } catch (error) {
        console.error("triage failed, sending plain alert", leadId, error)
      }
    }
    return { alerted: await sendOwnerAlert(lead, triage) }
  },
})

/**
 * Safety net, every 10 minutes:
 * - restart intake for a lead whose alert never went out (up to 24 hours old);
 * - report leads older than that to the agency once, instead of retrying forever;
 * - send the one 30-minute reminder for real leads still waiting.
 */
export const leadIntakeSweeper = schedules.task({
  id: "lead-intake-sweeper",
  cron: "*/10 * * * *",
  run: async () => {
    const stuck = await listUnalertedLeads({ olderThanMinutes: 5, newerThanHours: 24 })
    for (const lead of stuck) {
      await leadIntake.trigger({ leadId: lead.id }, {
        idempotencyKey: await idempotencyKeys.create(`lead-intake:${lead.id}`, { scope: "global" }),
      })
    }
    await alertAgency(await listUnalertedLeads({ olderThanMinutes: 24 * 60, newerThanHours: 25 }))

    const waiting = await listLeadsToReAlert()
    for (const lead of waiting) await sendOwnerReminder(lead)   // sets ownerReAlertedAt; business hours only
    return { restarted: stuck.length, reminded: waiting.length }
  },
})
```

Every sender checks its marker before sending (`ownerAlertClaimedAt` and `ownerAlertedAt`
for the owner, `sentSteps` for the customer) and sets it after a successful send, so a
retried run never sends twice. Provider idempotency keys
(Resend keeps them for 24 hours) are a second layer, not the only one.

Adapt the storage to the project (Supabase, Postgres, a CRM API), but keep the order:
**validate, store, then start the pipeline.**

### A test entry point for the health check

The form is a Server Action, which has no stable URL. Give the weekly check its own door
that runs the same pipeline:

```ts
// app/api/leads/test/route.ts
import { timingSafeEqual } from "node:crypto"

import { createLead } from "@/lib/leads"
import { startLeadIntake } from "@/lib/lead-intake"

function authorized(header: string | null) {
  const secret = process.env.LEAD_TEST_SECRET
  if (!secret || !header) return false
  const a = Buffer.from(header)
  const b = Buffer.from(secret)
  return a.length === b.length && timingSafeEqual(a, b)
}

export async function POST(request: Request) {
  if (!authorized(request.headers.get("x-lead-test-secret"))) return new Response("forbidden", { status: 403 })
  const id = await createLead(
    { name: "Health check", email: process.env.LEAD_TEST_INBOX ?? "", need: "Automated form test", marketingConsent: false },
    { isTest: true, spamReason: null },
  )
  await startLeadIntake(id)
  return Response.json({ id })
}
```

`isTest` leads alert the test inbox instead of the owner, skip customer follow-ups and the
reminder, and are left out of every count and conversion report.

## 7. Consent

- Answering the enquiry needs no extra consent. Marketing does.
- Use a separate marketing checkbox, **unchecked by default**, with plain words: "Send me
  occasional offers. You can unsubscribe at any time."
- Store the choice and the time with the lead. Never send marketing to a lead without it.

## 8. Track the conversion only after success

Fire the analytics event when the server confirms the lead was stored, not on the button
click. Keep UTM parameters and the landing page with the lead, so the owner sees which
channel sends customers.

```ts
const result = await submitLead(values)
if (result.ok) track("Lead Submitted", { form: "quote" })
```

## 9. Test

- Submit a real lead through the form on production at launch and after every change to it.
- Check that the owner alert and the customer confirmation both arrive, and that the lead
  is in the database with its UTM data.
- `launch-site-health-report` can repeat this test each week.

## Audit output

For an existing form, report: **fields to remove**, **copy changes** (heading, button, success
state), **delivery risk** (notify-only, no retries, no alert on failure), **spam controls**,
**consent**, and **tracking**, each with the exact change.

## Related Launch skills

- `launch-speed-to-lead`: reply to the lead within minutes and follow up.
- `launch-lead-triage-agent`: let an agent sort leads and draft replies for approval.
- `launch-site-health-report`: calls the test entry point each week.
