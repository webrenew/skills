---
name: google-analytics
description: >
  Set up, fix or audit Google Analytics 4 (GA4) for a small business website so the owner can
  see which channels and ads bring leads, calls, bookings and sales. Use this skill for a new
  GA4 property or data stream, the Google tag or gtag.js, @next/third-parties, consent mode v2
  and the cookie banner, key events and conversions, UTM links, linking Google Ads or Search
  Console, enhanced conversions, DebugView or Tag Assistant, and when the user says "set up
  Google Analytics", "GA4 is not tracking", "conversions are doubled", "which ads bring
  leads", "track form submissions" or "weekly analytics report".
---

# Google Analytics: Count the Leads, Not Only the Visits

**RULE: Each key event fires once, only after the server confirms success, only with the
visitor's consent, and never with personal data in it.**

A small business does not need 40 reports. It needs one answer each week: how many leads,
calls, bookings and sales came in, and from which channel. Everything in this skill serves
that answer and the ad platforms that learn from it (`google-ads`, `meta-ads`).

## 1. Own the property

- The **owner's** Google account owns the GA4 account and property. The agency gets
  Administrator or Editor access on the property. Never build the property in an agency
  account: the owner loses the history when the agency leaves.
- One property per business, one **Web** data stream per site. Copy the Measurement ID
  (`G-XXXXXXX`); it is public and goes in the page.
- Admin settings to change on day one:

| Setting | Value | Why |
|---|---|---|
| Data retention (Data collection and modification) | 14 months | The default of 2 months removes year-over-year comparisons in Explorations |
| Reporting time zone and currency | The business's own | Days and values match the owner's books |
| Internal traffic rule, then the filter set to **Active** | Office and agency IP addresses | Staff visits do not count as customers |
| Unwanted referrals (data stream, Configure tag settings) | Payment and booking domains, for example `checkout.stripe.com` | A return from checkout stays in the original session and channel |
| Enhanced measurement: **Form interactions** | Off | It fires on every submit, also failed ones. The site sends `generate_lead` after success instead |
| Enhanced measurement: page changes based on browser history events | On | Single-page apps (Next.js) get one page view per route change without extra code |
| Data redaction (data stream) | Email on, plus query parameters such as `email`, `phone`, `name` | A safety net if a form ever puts personal data in a URL |

## 2. Install the tag once

Use exactly one install path. Two paths (for example the Next.js component plus a Google Tag
Manager container that also has GA4) send every page view twice.

- **Next.js:** `@next/third-parties` `GoogleAnalytics` in the root layout, or `gtag.js` with
  `next/script`. Do not send `page_view` manually on route change: enhanced measurement
  already does it.
- **Other sites (WordPress, Webflow, static HTML, Shopify):** the Google tag snippet in
  `<head>`, or the platform's own GA4 field. Not both.

Code for both paths, the consent default and the event helper is in
[references/implementation.md](references/implementation.md).

## 3. Consent mode v2: respect the banner

Consent mode tells Google tags what the visitor agreed to. It has four signals:
`analytics_storage`, `ad_storage`, `ad_user_data` and `ad_personalization`.

1. Find the site's consent banner (Cookiebot, CookieYes, OneTrust, Termly, or a custom one).
   The banner is the only source of the visitor's choice. This skill does not decide what the
   law needs; the owner and the banner provider do.
2. Set the **default** state before the Google tag loads: `denied` for all four where the
   banner asks for consent (EEA, UK, Switzerland, and any region the owner chooses). Use the
   `region` parameter if the default differs by region.
3. When the visitor chooses, the banner calls `gtag("consent", "update", ...)` with the
   choice. Many banner providers do this for you when their Google consent mode setting is
   on. Check it in Tag Assistant (step 8), not in their documentation.
4. Pick **basic** mode (no Google tag loads until the visitor accepts) or **advanced** mode
   (the tag loads with `denied` and sends cookieless pings that Google uses for modeling).
   Write the choice down. Google Ads features for EEA and UK visitors need consent mode.
5. The same choice gates everything else: the Meta Pixel (`meta-ads`), enhanced
   conversions, and any server-side event sent for the visitor later.

## 4. Key events: one name for each business result

GA4 calls a conversion a **key event**. The `launch-*` skills use one event name for each result
on the site. Map each to a GA4 name, and mark only the results as key events:

| Site event (`launch-*` skills) | GA4 event | Key event | Fire when |
|---|---|---|---|
| `Lead Submitted` | `generate_lead` | Yes | The server confirms that it stored the lead (`launch-lead-capture`, section 8) |
| `Call Clicked` | `call_click` | Yes | A visitor taps a `tel:` link |
| `Booking Started` | `booking_start` | No | The booking widget opens |
| `Booking Completed` | `book_appointment` | Yes | The booking is confirmed (`launch-booking-payments`) |
| `Checkout Started` | `begin_checkout` | No | The checkout opens |
| `Purchase Completed` | `purchase` | Yes | Payment succeeded, with `transaction_id`, `value` and `currency` |

- Send parameters that help the owner decide: `form` (`quote`, `contact`), `service`,
  `value` and `currency`. An estimated lead value (for example the average job value times
  the close rate) lets the ad platforms bid for better leads.
- Mark key events in Admin, Events (or Key events, New key event). New custom events show
  there after they first fire.
- `purchase` must carry a unique `transaction_id`, so a refreshed thank-you page does not
  count twice.
- A booking or payment that completes on another domain (a hosted Cal.com page, Stripe
  Checkout) cannot fire in the browser on your site. Fire it when the visitor returns to your
  confirmation page, once per booking or session id, or from the server with the Measurement
  Protocol. The server path is in [references/implementation.md](references/implementation.md).

## 5. UTM discipline

Google Ads auto-tagging (`gclid`) labels Google Ads traffic without UTMs. Every other link
that you control gets UTMs, so GA4 puts it in the right channel.

| Link | `utm_source` | `utm_medium` | `utm_campaign` |
|---|---|---|---|
| Google Business Profile website link | `google` | `organic` | `gbp` (`launch-local-seo`) |
| Meta ads | `facebook` or `instagram` | `paid-social` | The campaign name |
| Organic social posts | `facebook`, `instagram`, `linkedin` | `social` | The post or topic |
| Email | `newsletter` or the tool name | `email` | The email name |
| QR code on a truck, flyer or invoice | `truck`, `flyer`, `invoice` | `offline` | The print run |

- Lowercase only, words joined with `-`. `Facebook` and `facebook` are two sources in GA4.
- Keep a shared sheet of the links you made. Never put UTMs on internal links: they start a
  new session and erase the real source.
- Store the UTMs and `gclid` with each lead (`launch-lead-capture`), so a lead in the
  database shows its channel even if analytics was blocked.
- In Google Ads, add a final URL suffix such as
  `utm_source=google&utm_medium=cpc&utm_campaign={campaignid}` only if the lead store needs
  UTMs. GA4 still uses `gclid` for Google Ads traffic.

## 6. Link Google Ads and Search Console

- **Google Ads:** Admin, Product links, Google Ads links. Turn on auto-tagging in Google Ads.
  Then import the GA4 key events into Google Ads, or use the Google Ads tag for conversions.
  Pick one source as **primary** for each result; the other is secondary. Two primary
  sources double the conversions and the bids (`google-ads`, step 6).
- **Search Console:** Admin, Product links, Search Console links. The owner then sees search
  queries and landing pages next to leads.
- **Enhanced conversions** (Google Ads): the Google tag sends a hashed email or phone with a
  conversion, which recovers conversions that cookies miss. Turn it on in Google Ads, Goals,
  Settings, and accept the customer data terms. Send the user data only when `ad_user_data`
  is granted, only to Google Ads, and never as a GA4 event parameter. Code is in
  [references/implementation.md](references/implementation.md).

## 7. Privacy: no personal data in GA4

Google's terms forbid personal data in GA4, and a leak is hard to delete.

- No names, emails, phone numbers, street addresses or free-text form answers in event
  parameters, user properties, page titles or URLs.
- Forms submit with `POST`. A `GET` form puts the answers in the URL, and GA4 collects them.
- Use a lead id from your database when you need to join GA4 to a lead, never the email.
- The privacy policy names Google Analytics and, if used, Google Ads and Meta
  (`launch-site-checklist`, section 8).

## 8. Verify before you trust a number

Checklist: [references/verify-checklist.md](references/verify-checklist.md). In short:

1. **Tag Assistant** (tagassistant.google.com): connect to the live site. Confirm one Google
   tag, consent defaults before the first hit, and the update after you click the banner.
2. **DebugView** (Admin, DebugView): with Tag Assistant connected, submit a real test lead.
   `generate_lead` appears **once**, with the right parameters and no personal data.
3. **Realtime** report: the page views and the test events show within a minute.
4. Delete the manual test lead from the lead store, or send it through the health check's
   test entry point (`launch-site-health-report`), so it stays out of the owner's counts.

## 9. The one-minute weekly report

The owner reads five lines, not a dashboard. Add them to the weekly email from
`launch-site-health-report`, or send them alone. Template and the GA4 Data API query are in
[references/weekly-report.md](references/weekly-report.md).

```
Week of 20 Oct: 31 leads (+6 vs last week), 12 calls, 9 bookings, $4,180 in sales.
Best channel: Google Ads, 14 leads at $38 each.
Weakest: Facebook ads, 3 leads at $95 each.
Top page for leads: /water-heater-repair (11 leads).
One thing to do: answer the 4 leads still waiting since Friday.
```

Leads and sales come from the lead store, not GA4: GA4 misses visitors who decline consent or
block scripts. GA4 supplies the channel mix and the trends. Costs come from Google Ads and
Meta.

## Output

**For a new setup:** the admin settings table filled in, the install code for the site's
framework, the consent default and its banner connection, the event map with the code that
fires each key event, the UTM sheet, the product links made, and the verification results
with screenshots or DebugView notes.

**For an audit:** one row per check, **pass / fail / missing**, with the fix:

| Check | Status | Fix |
|---|---|---|
| One Google tag on each page | fail | Remove the hard-coded gtag in `app/layout.tsx`; GTM already loads GA4 |
| `generate_lead` fires once, after success | fail | Move it from the button `onClick` to the success branch of the submit handler |
| Consent default before the tag | missing | Add the consent default script (references/implementation.md) |
| Data retention | fail | Change 2 months to 14 months |

## Related skills

- `google-ads`: imports these key events and bids on them.
- `meta-ads`: maps the same results to Pixel and Conversions API events.
- `launch-lead-capture`: fires `Lead Submitted` after the server stores the lead, and keeps
  UTMs with it.
- `launch-booking-payments`: the booking and purchase events.
- `launch-landing-page`: the pages that the key events measure.
- `launch-site-checklist`: the go-live check for analytics and consent.
- `launch-site-health-report`: sends the weekly report.
- `seo-technical`: Search Console and crawl health.
- `content-refresh`: reads leads and calls by blog post from these events.
