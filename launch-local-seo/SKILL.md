---
name: launch-local-seo
description: >
  Get a small business found in local search and the Google map pack. Use this skill when a
  site serves customers in a city or service area (trades, clinics, salons, restaurants, law,
  real estate, home services) or when the user mentions local SEO, "near me" searches, ranking
  on Google Maps, Google Business Profile, map pack, more Google reviews, service-area pages, NAP consistency, citations, reviews, or
  LocalBusiness schema.
---

# Local SEO: Get Found by Customers Nearby

**RULE: One business identity, the same everywhere. Name, address, phone, hours and category
must match on the site, the schema, Google Business Profile and every directory.**

Local ranking depends on three things Google names itself: relevance, distance and
prominence. You cannot change distance. This skill makes relevance clear and builds
prominence with reviews and consistent listings.

## 1. Put the identity in one place in code

Create one source of truth and render the footer, contact page and schema from it. Hand-typed
copies drift, and drift costs rankings.

```ts
// lib/business.ts
export const business = {
  name: "Harbor Plumbing",                 // exactly as on the storefront and GBP, no keywords
  type: "Plumber",                         // most specific schema.org LocalBusiness subtype
  phone: "+1-843-555-0142",                // E.164 for schema; format for display separately
  email: "hello@harborplumbing.com",
  address: { street: "12 King St", city: "Charleston", region: "SC", postalCode: "29401", country: "US" },
  geo: { latitude: 32.7765, longitude: -79.9311 },
  hours: [{ days: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], opens: "07:00", closes: "18:00" }],
  areaServed: ["Charleston", "Mount Pleasant", "Summerville"],
  sameAs: ["https://www.facebook.com/harborplumbing", "https://www.yelp.com/biz/harbor-plumbing-charleston"],
  googleReviewUrl: "https://search.google.com/local/writereview?placeid=PLACE_ID",
} as const
```

A service-area business with no storefront hides its street address on Google Business
Profile. Then leave `street` out of the site and schema too, and lean on `areaServed`.

## 2. LocalBusiness structured data

Render JSON-LD once, in the root layout or on the home and contact pages.

```tsx
// components/local-business-jsonld.tsx
import { business } from "@/lib/business"

export function LocalBusinessJsonLd() {
  const data = {
    "@context": "https://schema.org",
    "@type": business.type,
    name: business.name,
    url: "https://harborplumbing.com",
    telephone: business.phone,
    email: business.email,
    address: {
      "@type": "PostalAddress",
      streetAddress: business.address.street,
      addressLocality: business.address.city,
      addressRegion: business.address.region,
      postalCode: business.address.postalCode,
      addressCountry: business.address.country,
    },
    geo: { "@type": "GeoCoordinates", ...business.geo },
    openingHoursSpecification: business.hours.map((h) => ({
      "@type": "OpeningHoursSpecification", dayOfWeek: h.days, opens: h.opens, closes: h.closes,
    })),
    areaServed: business.areaServed.map((name) => ({ "@type": "City", name })),
    sameAs: business.sameAs,
  }
  // Escape "<" so a value can never close the script tag (the Next.js JSON-LD guidance).
  const json = JSON.stringify(data).replace(/</g, "\\u003c")
  return <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: json }} />
}
```

- Do **not** add `Review` or `AggregateRating` markup for reviews the business collects about
  itself. Google does not show stars for self-serving LocalBusiness reviews.
- Validate with the Rich Results Test and the Schema Markup Validator before launch.

## 3. Pages that match how customers search

Customers search "service + place": "water heater repair Charleston".

- **One page per core service.** Each has its own H1, what is included, price guidance
  ("from $X" if the owner allows), photos of real jobs, an FAQ and a call to action.
- **Service-area pages only with local substance.** A page for each town is useful when it
  shows real work there: projects, reviews from that town, local details (permits, water,
  housing stock). Pages that swap only the city name are doorway pages. Google demotes them.
  If the owner cannot supply local substance, list the areas on one "Areas we serve" page.
- **Title pattern:** `{Service} in {City} | {Business name}`. Keep it under about 60 characters.
- **Click-to-call** on every page: `<a href="tel:+18435550142">`. On mobile, a call is often
  the conversion.

## 4. Google Business Profile (the owner does this; you prepare it)

You cannot edit the profile through the site. Prepare the text and a checklist for the owner:

| Field | Guidance |
|---|---|
| Business name | Real-world name only. Keywords in the name break the guidelines and risk suspension. |
| Primary category | The most specific match (for example "Plumber", not "Contractor"). It is the biggest relevance signal. |
| Secondary categories | Only services the business actually provides. |
| Description | Up to 750 characters. Lead with what they do and where. No links, no promotions. |
| Services | One entry per service page, with a short description. |
| Hours | Same as `lib/business.ts`, including holiday hours. |
| Website link | Add UTM tags so visits are measurable: `?utm_source=google&utm_medium=organic&utm_campaign=gbp` |
| Photos | Real work, team, vehicles, storefront. Add new photos monthly. |
| Posts | Offers, recent projects, seasonal tips, about once a week. |

## 5. Reviews: ask every customer, the same way

Reviews drive prominence and they also convert visitors.

- Ask every customer after the job, by email or text, with the direct review link
  (`googleReviewUrl` above; find the Place ID with Google's Place ID Finder).
- **Never gate reviews.** Do not send happy customers to Google and unhappy ones to a private
  form. Google prohibits selective review requests, and consumer-protection rules in several
  countries treat suppressing negative reviews as deceptive.
- **Never offer incentives** for reviews.
- The owner replies to every review, the negative ones within 48 hours, calmly and with a fix.
- Show recent reviews on the site with the reviewer's first name and the date.

The `launch-speed-to-lead` skill sends the review request automatically one day after the
owner marks a job `won`.

## 6. Citations: the same identity on the directories that matter

Make listings match `lib/business.ts` exactly on Apple Business Connect, Bing Places, Yelp,
Facebook, and the top one or two directories for the industry (for example Angi or Houzz for
trades, Healthgrades or Zocdoc for clinics). Fix mismatches before you add new listings. Ten
consistent listings beat fifty inconsistent ones.

## 7. Measure

- GBP Performance: calls, direction requests, website clicks, searches by keyword.
- Analytics: sessions with `utm_campaign=gbp`, and leads and calls from them.
- Search Console: impressions and clicks for "service + city" queries.
- Review count and average rating, each month.

## Output

When you audit a site, report a table: **item | status (pass / fix / owner action) | why it
matters | the fix**. Put owner actions (GBP, directories, review requests) in a separate list,
in plain language, ready to send to the owner.

## Related Launch skills

- `launch-site-checklist`: run it before go-live. It includes the local checks.
- `launch-landing-page`: turns local visitors into calls and leads.
