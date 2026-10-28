---
name: launch-lead-capture
description: >
  Build or fix the forms on a small business site so more visitors become leads and no lead
  is ever lost. Use this skill for contact forms, quote requests, estimate forms, "call me
  back" forms, newsletter sign-ups and any lead form, and when the user mentions form
  conversion, form spam, leads not arriving, form notifications, honeypot, CAPTCHA, or
  marketing consent. Covers fields, copy, validation, spam protection, storage-first delivery,
  consent and conversion tracking. Part of the Webrenew Launch pack.
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
   `autoComplete="off"`, `aria-hidden`). Bots fill it. Reject any submission where it has a
   value.
2. **Time trap:** render the start time in a hidden field. Reject submissions faster than
   about 3 seconds.
3. **Server-side validation** of every field with a schema. Never trust the browser.
4. **Rate limit** by IP (for example 5 submissions per 10 minutes).
5. Only then, **Cloudflare Turnstile** or a similar low-friction challenge.

For a rejected bot, return the normal success state. Do not tell bots what they did wrong.

## 5. Store first, then notify in the background

```ts
// app/contact/actions.ts
"use server"

import { tasks } from "@trigger.dev/sdk"
import { z } from "zod"

import { db } from "@/lib/db"
import type { leadNotification } from "@/trigger/lead-notification"

const leadSchema = z.object({
  name: z.string().trim().min(1).max(100),
  email: z.email().optional().or(z.literal("")),
  phone: z.string().trim().max(30).optional(),
  need: z.string().trim().min(1).max(2000),
  marketingConsent: z.boolean(),
  website: z.string().max(0),            // honeypot: must stay empty
  startedAt: z.coerce.number(),          // time trap
  utm: z.record(z.string(), z.string().max(200)).optional(),
}).refine((lead) => lead.email || lead.phone, { message: "Add an email or a phone number." })

export async function submitLead(input: unknown) {
  const parsed = leadSchema.safeParse(input)
  if (!parsed.success) return { ok: false as const, errors: z.flattenError(parsed.error).fieldErrors }

  const lead = parsed.data
  const isBot = lead.website !== "" || Date.now() - lead.startedAt < 3000
  if (isBot) return { ok: true as const }           // look normal to bots

  const { id } = await db.leads.insert({
    name: lead.name, email: lead.email || null, phone: lead.phone || null, need: lead.need,
    marketingConsent: lead.marketingConsent, consentAt: lead.marketingConsent ? new Date() : null,
    utm: lead.utm ?? {}, status: "new",
  })

  // The lead is safe in the database. Delivery can retry without losing it.
  await tasks.trigger<typeof leadNotification>("lead-notification", { leadId: id }, { idempotencyKey: id })
  return { ok: true as const }
}
```

```ts
// trigger/lead-notification.ts
import { schemaTask } from "@trigger.dev/sdk"
import { z } from "zod"

export const leadNotification = schemaTask({
  id: "lead-notification",
  schema: z.object({ leadId: z.string() }),
  retry: { maxAttempts: 6, minTimeoutInMs: 10_000, maxTimeoutInMs: 300_000, factor: 2 },
  run: async ({ leadId }) => {
    // Load the lead, alert the owner (email, SMS or Slack), send the customer's confirmation.
    // Pass `leadId` + channel as the provider's idempotency key so a retry never sends twice.
  },
})
```

Adapt the database call to the project (Supabase, Postgres, a CRM API). Keep the order:
**validate, store, then queue delivery.** If the project has no database, send the lead to a
CRM or a sheet with retries, and alert the owner when delivery fails after the last retry.

## 6. Consent

- Answering the enquiry needs no extra consent. Marketing does.
- Use a separate marketing checkbox, **unchecked by default**, with plain words: "Send me
  occasional offers. You can unsubscribe at any time."
- Store the choice and the time with the lead. Never send marketing to a lead without it.

## 7. Track the conversion only after success

Fire the analytics event when the server confirms the lead was stored, not on the button
click. Keep UTM parameters and the landing page with the lead, so the owner sees which
channel sends customers.

```ts
const result = await submitLead(values)
if (result.ok) track("lead_submitted", { form: "quote" })
```

## 8. Test

- Submit a real test lead on production at launch and after every change to the form.
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
