---
name: launch-booking-payments
description: >
  Let a small business's customers book a time and pay online without a phone call, and keep
  every booking and payment in sync with the lead. Use this skill for appointment booking,
  scheduling embeds, Cal.com, deposits, Stripe Checkout, Payment Links, no-show protection,
  booking and payment webhooks, and when the user mentions "let customers book online",
  "take a deposit", "sell a package", or booking conversion. Part of the Webrenew Launch pack.
---

# Booking and Payments: Book and Pay Without a Phone Call

**RULE: The server decides what a customer pays, and a verified webhook decides that they
paid or booked. Never trust a price, amount or "success" that comes from the browser.**

## 1. Pick the right action for the business

| Business | Main action | Tool |
|---|---|---|
| Fixed-length appointments (salon, clinic, consultant, lessons) | Book a time | Cal.com (embed or link) |
| Appointments with no-show risk | Book a time + deposit | Cal.com with Stripe payment, or Stripe Checkout then booking |
| Jobs that need a look first (trades, renovations) | Request a quote | Form (`launch-lead-capture`), then book a visit |
| Fixed-price products or packages | Pay now | Stripe Checkout or Payment Links |
| Recurring service (cleaning, lawn care, memberships) | Subscribe | Stripe Checkout in `subscription` mode |

Do not force booking on a business that must quote first. A calendar that offers slots the
owner cannot keep creates angry customers.

## 2. Booking with Cal.com

- **Embed inline on the page** for the highest completion; a pop-up is fine on a busy page.
  A plain link to the Cal.com page works when an embed is not possible.
- **Prefill** name and email when the visitor came from a lead form, so they do not type twice.
- **Pass attribution** in metadata (UTM source and campaign, the lead id) so the booking
  links back to the lead and the channel.
- Ask only the questions the appointment needs. Add buffer times and a minimum notice period
  so the owner is not surprised by a booking in 20 minutes.
- Send reminders 24 hours and 2 hours before. Reminders cut no-shows more than anything else.

### Verify the webhook, then update the lead

Cal.com signs the raw body with the webhook secret (HMAC SHA-256, hex) in the
`x-cal-signature-256` header.

```ts
// app/api/webhooks/cal/route.ts
import { createHmac, timingSafeEqual } from "node:crypto"

import { markLeadBooked } from "@/lib/leads"

function verify(rawBody: string, signature: string | null, secret: string | undefined) {
  if (!secret || !signature) return false
  const expected = createHmac("sha256", secret).update(rawBody).digest("hex")
  if (expected.length !== signature.length) return false
  return timingSafeEqual(Buffer.from(expected), Buffer.from(signature))
}

export async function POST(request: Request) {
  const rawBody = await request.text()           // verify the exact bytes Cal signed
  if (!verify(rawBody, request.headers.get("x-cal-signature-256"), process.env.CAL_WEBHOOK_SECRET)) {
    return new Response("invalid signature", { status: 401 })
  }

  const event = JSON.parse(rawBody)
  if (event.triggerEvent === "BOOKING_CREATED") {
    // `uid` is stable across Cal's retries: use it as the idempotency key.
    await markLeadBooked({
      bookingUid: event.payload.uid,
      email: event.payload.attendees?.[0]?.email,
      startTime: event.payload.startTime,
      leadId: event.payload.metadata?.leadId,
    })
  }
  return new Response("ok")
}
```

`markLeadBooked` sets the lead's status to `booked`, which stops the follow-up sequence in
`launch-speed-to-lead`. Handle `BOOKING_CANCELLED` and `BOOKING_RESCHEDULED` the same way.

## 3. Payments with Stripe

- **Payment Links** need no code: good for a few fixed products or a deposit link in an email.
- **Checkout Sessions** from the server when the price depends on the order, or when the
  payment must link to a lead or booking.

```ts
// app/checkout/actions.ts
"use server"

import { redirect } from "next/navigation"
import Stripe from "stripe"

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!)

// The browser sends only a product key; the server owns the price.
const PRICES = { deposit: "price_123", "deep-clean": "price_456" } as const

export async function startCheckout(product: keyof typeof PRICES, leadId: string) {
  const session = await stripe.checkout.sessions.create({
    mode: "payment",
    line_items: [{ price: PRICES[product], quantity: 1 }],
    client_reference_id: leadId,
    metadata: { leadId, product },
    success_url: "https://example.com/thanks?session_id={CHECKOUT_SESSION_ID}",
    cancel_url: "https://example.com/pricing",
  })
  if (!session.url) throw new Error("Stripe returned no checkout URL")
  redirect(session.url)
}
```

### Fulfil from the webhook, once

```ts
// app/api/webhooks/stripe/route.ts
import Stripe from "stripe"

import { fulfilOrder } from "@/lib/orders"

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!)

export async function POST(request: Request) {
  const rawBody = await request.text()
  let event: Stripe.Event
  try {
    event = stripe.webhooks.constructEvent(rawBody, request.headers.get("stripe-signature") ?? "", process.env.STRIPE_WEBHOOK_SECRET!)
  } catch {
    return new Response("invalid signature", { status: 400 })
  }

  if (event.type === "checkout.session.completed" && event.data.object.payment_status === "paid") {
    await fulfilOrder(event.data.object.id)   // unique on session id: a retried event does nothing twice
  }
  return new Response("ok")
}
```

- The thank-you page shows "Payment received" only after it confirms the session server-side.
  It never fulfils anything.
- Store the Checkout Session id with a unique constraint so Stripe's retries are harmless.
- Bank debits and some local methods confirm later: `checkout.session.completed` arrives with
  `payment_status: "unpaid"`, then `checkout.session.async_payment_succeeded` (or `_failed`).
  Fulfil on the success event too if those methods are on.
- Use test mode and test keys until launch. Switch keys and the webhook endpoint together.

## 4. Deposits and no-shows

- A deposit of a small fixed amount, credited against the final bill, cuts no-shows without
  scaring customers away. State the cancellation window next to the button, in plain words.
- Refunds and cancellations follow a written policy linked from the booking page.

## 5. Measure each step

Track `booking_started`, `booking_completed`, `checkout_started` and `purchase`, with the UTM
data from the lead. A big drop between started and completed points at the step to fix:
too many questions, no slots soon enough, or surprise costs at checkout.

## Related Launch skills

- `launch-lead-capture`: when the business must quote before it books.
- `launch-speed-to-lead`: stops follow-ups when a booking arrives.
- `launch-site-checklist`: confirms live keys and live calendars at launch.
