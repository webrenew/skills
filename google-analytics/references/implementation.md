# GA4 implementation

Code for the install paths in `SKILL.md`, step 2. Use one path per site.

## Next.js (App Router)

### 1. Consent default, before any Google tag

The default must run before the Google tag sends its first hit. In the root layout, a
`beforeInteractive` script runs before the page hydrates and before `afterInteractive`
scripts such as `GoogleAnalytics`.

```tsx
// app/layout.tsx
import Script from "next/script"
import { GoogleAnalytics } from "@next/third-parties/google"

const GA_ID = process.env.NEXT_PUBLIC_GA_ID // "G-XXXXXXX", public by design

// Denied until the banner says otherwise. Narrow it with `region` if the owner chooses to
// ask only some regions, for example region: ["AT", "BE", ..., "GB", "CH"].
const CONSENT_DEFAULT = `
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag("consent", "default", {
  ad_storage: "denied",
  ad_user_data: "denied",
  ad_personalization: "denied",
  analytics_storage: "denied",
  wait_for_update: 500
});
gtag("set", "ads_data_redaction", true);
`

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <Script id="consent-default" strategy="beforeInteractive">
          {CONSENT_DEFAULT}
        </Script>
      </head>
      <body>{children}</body>
      {GA_ID ? <GoogleAnalytics gaId={GA_ID} /> : null}
    </html>
  )
}
```

- `wait_for_update` gives the banner 500 ms to send a stored choice before the first hit.
- **Basic consent mode:** do not render `GoogleAnalytics` until the banner reports consent.
  Keep the choice in state from the banner's callback, then render the component.
- Skip the component in preview deployments if the preview has its own traffic, so tests do
  not count as customers: set `NEXT_PUBLIC_GA_ID` only for production.

### 2. Connect the banner

Most banner providers send `gtag("consent", "update", ...)` themselves when their Google
consent mode option is on. For a custom banner:

```ts
// lib/consent.ts
type Choice = { analytics: boolean; ads: boolean }

/** Sends the visitor's banner choice to Google tags. Call it on load (stored choice) and on change. */
export function applyConsent(choice: Choice) {
  if (typeof window === "undefined" || typeof window.gtag !== "function") return
  const ads = choice.ads ? "granted" : "denied"
  window.gtag("consent", "update", {
    analytics_storage: choice.analytics ? "granted" : "denied",
    ad_storage: ads,
    ad_user_data: ads,
    ad_personalization: ads,
  })
}
```

### 3. One helper for every conversion

The Launch skills call `track("Lead Submitted", ...)`. Keep that call site and map the name to
GA4 in one place. `meta-ads` adds its Pixel call to the same helper.

```ts
// lib/analytics.ts
export type SiteEvent =
  | "Lead Submitted"
  | "Call Clicked"
  | "Booking Started"
  | "Booking Completed"
  | "Checkout Started"
  | "Purchase Completed"

const GA4_EVENT: Record<SiteEvent, string> = {
  "Lead Submitted": "generate_lead",
  "Call Clicked": "call_click",
  "Booking Started": "booking_start",
  "Booking Completed": "book_appointment",
  "Checkout Started": "begin_checkout",
  "Purchase Completed": "purchase",
}

/** Values only: ids, labels, money. Never a name, email, phone or free text. */
export type EventParams = Record<string, string | number>

declare global {
  interface Window {
    gtag?: (...args: unknown[]) => void
  }
}

/** Sends one site event to GA4. Call it after the server confirms success, never on click intent. */
export function track(name: SiteEvent, params: EventParams = {}) {
  if (typeof window === "undefined" || typeof window.gtag !== "function") return
  window.gtag("event", GA4_EVENT[name], params)
}
```

- `@next/third-parties` also exports `sendGAEvent("event", name, params)`. Either works; one
  helper keeps the names in one table.
- The `gtag` stub from the consent script queues events until the tag loads, so an early
  `track` call is not lost.

### 4. Fire each event once

```tsx
// Lead form: the success branch, not the button onClick.
const result = await submitLead(values)
if (result.ok) track("Lead Submitted", { form: "quote", service: values.service, value: 150, currency: "USD" })

// Call link: a tap is the event.
<a href="tel:+18435550100" onClick={() => track("Call Clicked", { location: "header" })}>
  (843) 555-0100
</a>
```

Common causes of double counts:

| Cause | Fix |
|---|---|
| GA4 in GTM and in the code | Keep one |
| Manual `page_view` on route change plus enhanced measurement | Remove the manual call |
| Event in a `useEffect` on the thank-you page | Fire from the submit handler. If the page must fire it, key it on the lead id in `sessionStorage` |
| Enhanced measurement form interactions on | Turn it off (`SKILL.md`, step 1) |
| React Strict Mode runs effects twice in development | Only in development. Test counts on a production build |

### 5. Enhanced conversions for Google Ads

Send user data only when `ad_user_data` is granted, right before the conversion. The Google
tag normalizes and hashes the values before it sends them.

```ts
// After a successful lead, with ads consent granted:
window.gtag?.("set", "user_data", { email: lead.email, phone_number: lead.phoneE164 })
window.gtag?.("event", "conversion", { send_to: "AW-XXXXXXX/LABEL" }) // only if the Google Ads tag is the conversion source
```

If GA4 is the conversion source in Google Ads (imported key events), turn on enhanced
conversions in Google Ads and follow its "Google tag" setup; do not add `user_data` to GA4
events as parameters.

## Other sites (framework-agnostic)

Paste in `<head>`, in this order, on every page:

```html
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag("consent", "default", {
    ad_storage: "denied", ad_user_data: "denied",
    ad_personalization: "denied", analytics_storage: "denied",
    wait_for_update: 500
  });
</script>
<!-- The consent banner's own script, if it must load before tags -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXX"></script>
<script>
  gtag("js", new Date());
  gtag("config", "G-XXXXXXX");
</script>
```

- WordPress: use one plugin (Site Kit, or the consent plugin's Google integration), not a
  plugin and a theme snippet.
- Shopify: use the Google & YouTube app. It sends `purchase` with the order id.
- Webflow, Squarespace, Wix: use the built-in GA4 field and add only the event calls.
- Event calls are the same as above: `gtag("event", "generate_lead", { form: "quote" })`,
  after the form's success state, not on submit click.

## Server events with the Measurement Protocol

Use this for results that the browser does not see: a booking webhook, a Stripe webhook, a
lead marked "won" in the CRM.

1. Keep the GA4 `client_id` with the lead. It is the part of the `_ga` cookie after
   `GA1.1.`. Read it in the browser and post it with the form.
2. Keep the visitor's consent with the lead. Send nothing when `analytics_storage` was denied.
3. Create an API secret in the data stream (Measurement Protocol API secrets). It is a server
   secret: keep it in an environment variable, never in client code.

```ts
// lib/ga4-server.ts
const GA4_ENDPOINT = "https://www.google-analytics.com/mp/collect"

/** Sends one server-side GA4 event for a visitor who granted analytics consent. */
export async function sendServerEvent(input: {
  clientId: string
  name: string
  params: Record<string, string | number>
}) {
  const measurementId = process.env.NEXT_PUBLIC_GA_ID
  const apiSecret = process.env.GA4_API_SECRET
  if (!measurementId || !apiSecret) return

  const url = `${GA4_ENDPOINT}?measurement_id=${measurementId}&api_secret=${apiSecret}`
  const response = await fetch(url, {
    method: "POST",
    body: JSON.stringify({ client_id: input.clientId, events: [{ name: input.name, params: input.params }] }),
  })
  if (!response.ok) throw new Error(`GA4 Measurement Protocol returned ${response.status}`)
}
```

- The collect endpoint accepts almost anything. Test with
  `https://www.google-analytics.com/debug/mp/collect` first; it returns validation messages.
- Send each result from one place only: the browser or the server, not both.
