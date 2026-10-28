# Content Kit Format

The kit adds only what content needs. Identity comes from `lib/business.ts`
(`launch-local-seo`). Services, price guides, tone and `neverSay` come from
`lib/business-profile.ts` (`launch-lead-triage-agent`). Never copy those fields into the kit.

## Code sites: `lib/content-kit.ts`

```ts
// lib/content-kit.ts
import { business } from "@/lib/business"                   // launch-local-seo: the one identity
import { businessProfile } from "@/lib/business-profile"    // launch-lead-triage-agent: services, prices, neverSay

export type ProofType = "job" | "number" | "photo" | "quote" | "credential" | "award"

export interface ProofEntry {
  id: string                      // "job-2026-09-mtp-water-heater"; also in photo file names
  type: ProofType
  summary: string                 // one sentence, true and checkable
  place?: string                  // town or neighbourhood, never a street address
  date: string                    // YYYY-MM-DD
  source: string                  // job record, invoice, review URL, licence lookup, photo file
  consent: "not-needed" | `written ${string}` | "pending"
  useUntil?: string               // YYYY-MM-DD: check again after this date
  photos?: { file: string; alt: string }[]
}

export const contentKit = {
  version: 1,
  profileVersion: businessProfile.version,   // the profile this kit was checked against
  voice: {
    summary: "Friendly and direct. Explains the why. Never talks down. Signs as Sam.",
    wordsWeUse: ["service call", "water heater", "crawl space", "flat-rate price"],
    // Words we never use live in businessProfile.neverSay, shared with lead replies.
    habits: ["Short sentences", "'We' for the team, 'I' when Sam tells a story", "One dry joke at most"],
    samples: [
      "We'll give you the price before we pick up a wrench.",
      "Most of the time it's the anode rod, and that's a cheap fix.",
    ],
  },
  readers: [
    {
      who: "Homeowner with an older house",
      situation: "Water heater is 10+ years old and starts to leak or run cold",
      worry: "Surprise cost, and someone pushing a full replacement",
      theirWords: ["water heater leaking from the bottom", "no hot water", "repair or replace"],
    },
  ],
  places: [
    // Must also be in business.areaServed. Only details the owner confirms.
    { name: "Mount Pleasant", localFacts: ["Many 1990s homes with original 40-gallon tanks"] },
  ],
  claimLimits: {
    prices: "Use only businessProfile.services[].priceGuide, as written.",
    timing: { may: ["Most repairs are done in one visit"], mayNot: ["same-day", "within the hour"] },
    licences: [{ name: "SC Master Plumber", number: "TODO: ask owner", lookupUrl: "TODO" }],
    guarantee: "TODO: ask owner for the written wording",
    regulated: [],                // e.g. "gas lines: permit required, no DIY steps"
  },
  authors: [
    {
      slug: "sam-harbor",
      name: "Sam Harbor",
      role: "Owner and master plumber",
      yearsInTrade: 18,
      bio: "TODO: 40 to 60 words in Sam's voice",
      photo: "/images/team/sam.jpg",
      url: `${business.url}/about/sam-harbor`,
    },
  ],
  proof: [] as ProofEntry[],
} as const
```

When the proof bank passes about 50 entries, or the owner wants to add entries from a phone,
move `proof` to a database table with the same fields. Keep the rest of the kit in code.

## Sites without a code store: `content-kit.md`

Same sections, as headings: `Voice`, `Readers`, `Places`, `Claim limits`, `Authors`,
`Proof bank`. Write one line at the top:

> Identity, services and prices: see the business profile. Do not copy them here.

Write the proof bank as a table with the same columns as `ProofEntry`.

## Proof bank examples

| id | type | summary | place | date | source | consent |
|---|---|---|---|---|---|---|
| job-2026-09-mtp-water-heater | job | Replaced a leaking 1998 40-gallon tank with a 50-gallon unit in one visit | Mount Pleasant | 2026-09-14 | Job #4471, 6 photos | written 2026-09-15 |
| num-2025-jobs | number | 1,212 service calls in 2025 | | 2025-12-31 | Job system export, Jan 2026 | not-needed |
| quote-dana-r | quote | "They showed me the old part and explained why it failed." | Summerville | 2026-08-02 | Google review link | written 2026-08-05 |
| cred-master-plumber | credential | SC Master Plumber licence | | 2026-01-01 | State licence lookup link | not-needed |
