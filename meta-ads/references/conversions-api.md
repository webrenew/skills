# Meta Pixel and Conversions API

The Pixel sends events from the browser. The Conversions API (CAPI) sends the same events
from the server. Both carry the same `event_name` and `event_id`, so Meta keeps one.

## 1. Tracking context saved with each lead

The server needs to know, for each lead, what the visitor agreed to and which browser sent
it. Collect this in the form and store it with the lead (an extra `tracking` field on the
lead model in `launch-lead-capture`, section 5):

```ts
// lib/tracking-context.ts (browser)
export interface TrackingContext {
  eventId: string           // shared by the Pixel event and the CAPI event
  adConsent: boolean        // from the consent banner, at submit time
  analyticsConsent: boolean
  fbp: string | null        // _fbp cookie
  fbc: string | null        // _fbc cookie, or built from ?fbclid=
  gaClientId: string | null // from the _ga cookie, for GA4 server events
}

function readCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`))
  return match ? decodeURIComponent(match[1]) : null
}

/** Reads the cookies and builds the context. Call it once, on submit. */
export function getTrackingContext(consent: { ads: boolean; analytics: boolean }): TrackingContext {
  const fbclid = new URLSearchParams(window.location.search).get("fbclid")
  const ga = readCookie("_ga")
  return {
    eventId: crypto.randomUUID(),
    adConsent: consent.ads,
    analyticsConsent: consent.analytics,
    fbp: consent.ads ? readCookie("_fbp") : null,
    fbc: consent.ads ? readCookie("_fbc") ?? (fbclid ? `fb.1.${Date.now()}.${fbclid}` : null) : null,
    gaClientId: consent.analytics && ga ? ga.split(".").slice(2).join(".") : null,
  }
}
```

- `fbclid` is on the landing URL, not on the form page if the visitor clicked around. Save
  it in `sessionStorage` on landing (with the UTMs that `launch-lead-capture` keeps) and read
  it from there.
- Validate the context on the server like every other field: strings with a length limit,
  booleans as booleans.

## 2. The Pixel, behind consent

```tsx
// components/meta-pixel.tsx
"use client"

import Script from "next/script"
import { usePathname } from "next/navigation"
import { useEffect, useRef } from "react"

const PIXEL_ID = process.env.NEXT_PUBLIC_META_PIXEL_ID

const PIXEL_BASE = `
!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
document,'script','https://connect.facebook.net/en_US/fbevents.js');
fbq('consent', 'revoke');
fbq('init', '${PIXEL_ID}');
fbq('track', 'PageView');
`

/** Loads the Pixel with consent revoked. The base code counts the first page; the effect counts each route change. */
export function MetaPixel() {
  const pathname = usePathname()
  const isFirstPage = useRef(true)

  useEffect(() => {
    if (isFirstPage.current) {
      isFirstPage.current = false
      return
    }
    window.fbq?.("track", "PageView")
  }, [pathname])

  if (!PIXEL_ID) return null
  return (
    <Script id="meta-pixel" strategy="afterInteractive">
      {PIXEL_BASE}
    </Script>
  )
}
```

- The base code sends the first `PageView`. The effect skips its first run and sends one
  `PageView` for each client-side route change, so each page counts once. (React Strict Mode
  runs effects twice in development only; check counts on a production build.)
- The banner calls `window.fbq?.("consent", "grant")` when the visitor accepts ad cookies,
  next to `applyConsent` from `google-analytics`. Where no consent is needed, the banner
  grants it on load.
- While consent is revoked, the Pixel sends nothing. Check it in the Network tab (step 5).

## 3. One `track` helper for GA4 and Meta

Extend the helper from `google-analytics` (references/implementation.md):

```ts
// lib/analytics.ts (additions)
const META_EVENT: Partial<Record<SiteEvent, string>> = {
  "Lead Submitted": "Lead",
  "Call Clicked": "Contact",
  "Booking Completed": "Schedule",
  "Checkout Started": "InitiateCheckout",
  "Purchase Completed": "Purchase",
}

declare global {
  interface Window {
    fbq?: (...args: unknown[]) => void
  }
}

/** Sends one site event to GA4 and the Pixel. Pass eventId when the server also sends it. */
export function track(name: SiteEvent, params: EventParams = {}, options: { eventId?: string } = {}) {
  if (typeof window === "undefined") return
  window.gtag?.("event", GA4_EVENT[name], params)
  const metaName = META_EVENT[name]
  if (!metaName) return
  window.fbq?.("track", metaName, params, options.eventId ? { eventID: options.eventId } : undefined)
}
```

```ts
// The lead form
const tracking = getTrackingContext(consentChoice)
const result = await submitLead({ ...values, tracking })
if (result.ok) track("Lead Submitted", { value: 150, currency: "USD" }, { eventId: tracking.eventId })
```

## 4. The server event

Send it after the lead is stored, from the lead pipeline (for example a step in
`lead-intake`, `launch-lead-capture`), so a slow Meta API never slows the form.

```ts
// lib/meta-capi.ts (server only)
import { createHash } from "node:crypto"

const GRAPH_VERSION = process.env.META_GRAPH_VERSION // the current Graph API version, e.g. "v24.0"

function sha256(value: string): string {
  return createHash("sha256").update(value).digest("hex")
}

/** Lowercase and trim an email; keep digits only for a phone in E.164 (country code, no +). */
export function normalizeEmail(email: string) {
  return email.trim().toLowerCase()
}
export function normalizePhone(phoneE164: string) {
  return phoneE164.replace(/\D/g, "")
}

interface CapiLead {
  eventName: "Lead" | "Schedule" | "Purchase"
  eventId: string
  eventTime: Date
  sourceUrl: string
  email: string | null
  phoneE164: string | null
  fbp: string | null
  fbc: string | null
  clientIp: string | null
  userAgent: string | null
  value?: number
  currency?: string
}

/** Sends one CAPI event. The caller checks ad consent first and never calls this without it. */
export async function sendCapiEvent(lead: CapiLead) {
  const pixelId = process.env.META_PIXEL_ID
  const token = process.env.META_CAPI_TOKEN // server secret: Events Manager, Settings, Conversions API
  if (!pixelId || !token || !GRAPH_VERSION) return

  const userData = {
    em: lead.email ? [sha256(normalizeEmail(lead.email))] : undefined,
    ph: lead.phoneE164 ? [sha256(normalizePhone(lead.phoneE164))] : undefined,
    fbp: lead.fbp ?? undefined,
    fbc: lead.fbc ?? undefined,
    client_ip_address: lead.clientIp ?? undefined,
    client_user_agent: lead.userAgent ?? undefined,
  }

  const body = {
    data: [
      {
        event_name: lead.eventName,
        event_time: Math.floor(lead.eventTime.getTime() / 1000),
        event_id: lead.eventId,
        action_source: "website",
        event_source_url: lead.sourceUrl,
        user_data: userData,
        custom_data: lead.value ? { value: lead.value, currency: lead.currency ?? "USD" } : undefined,
      },
    ],
    // test_event_code: "TEST12345", // from Events Manager, Test events, while you verify
    access_token: token, // in the body, so the token stays out of URLs and request logs
  }

  const response = await fetch(`https://graph.facebook.com/${GRAPH_VERSION}/${pixelId}/events`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  })
  if (!response.ok) throw new Error(`Meta CAPI returned ${response.status}`)
}
```

```ts
// In the pipeline step, after the lead is stored:
if (!lead.isTest && lead.status !== "spam" && lead.tracking?.adConsent) {
  try {
    await sendCapiEvent({ eventName: "Lead", eventId: lead.tracking.eventId, /* ... */ })
  } catch (error) {
    logger.warn("Meta CAPI event failed", { leadId: lead.id, error }) // never block the lead
  }
}
```

- Keep the token, the IP address and the user agent on the server. Capture IP and user agent
  from the form request when the lead is created.
- Pin `META_GRAPH_VERSION` to a version that is current when you build it, and update it when
  Meta deprecates that version (Meta sends notices in the developer dashboard).
- Test with `test_event_code` and the **Test events** tab, then remove the code.
- Test leads and spam leads never send events.

## 5. Checks in Events Manager

- [ ] Each event shows **Browser** and **Server** as sources, and the deduplication rate is
  high (most server events matched to a browser event).
- [ ] Event match quality for `Lead` is "Good" or better. Low scores usually mean no email or
  phone hash, or no `fbp`/`fbc`.
- [ ] Diagnostics has no open issues (for example, a missing `event_id`, or personal data in
  a URL parameter).
- [ ] With the banner set to **Reject**, no request goes to `facebook.com/tr` from the
  browser and no CAPI event is sent for that lead.
