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
    // Content only. Phrases that lead replies must avoid too go in businessProfile.neverSay.
    wordsWeAvoid: ["state-of-the-art", "hassle-free", "your comfort is our priority"],
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
    // Empty until the owner confirms: never a placeholder a post could quote.
    licences: [] as { name: string; number: string; lookupUrl: string }[],
    guarantee: null as string | null,   // the exact written wording
    regulated: [] as string[],    // e.g. "gas lines: permit required, no DIY steps"
  },
  authors: [
    {
      slug: "sam-harbor",
      name: "Sam Harbor",
      role: "Owner and master plumber",
      yearsInTrade: 18,
      bio: "",                              // 40 to 60 words in Sam's voice; empty until approved
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

## No business profile yet

`lib/business-profile.ts` comes from `launch-lead-triage-agent`. A site without it (no triage
agent, or no code store) still keeps one store for services and prices: create it once with
the same fields (`version`, `services` with `key`, `name` and `priceGuide`, `tone`,
`neverSay`), as `lib/business-profile.ts` in code or `business-profile.md` beside the kit. If
the business already keeps services and prices in its own config, point the kit at that file
instead. Never keep a second copy in the kit. When the triage agent comes later, it reads the
same file.

## Proof bank examples

| id | type | summary | place | date | source | consent | useUntil |
|---|---|---|---|---|---|---|---|
| job-2026-09-mtp-water-heater | job | Replaced a leaking 1998 40-gallon tank with a 50-gallon unit in one visit | Mount Pleasant | 2026-09-14 | Job #4471, 6 photos | written 2026-09-15 | |
| num-2025-jobs | number | 1,212 service calls in 2025 | | 2025-12-31 | Job system export, Jan 2026 | not-needed | 2026-12-31 |
| quote-dana-r | quote | "They showed me the old part and explained why it failed." | Summerville | 2026-08-02 | Google review link | written 2026-08-05 | |
| cred-master-plumber | credential | SC Master Plumber licence | | 2026-01-01 | State licence lookup link | not-needed | 2026-12-31 |

Photos live in the site's media storage, named with the entry `id`
(`job-2026-09-mtp-water-heater-1.jpg`). In the Markdown table, add a `photos` column with each
file name and its alt text, or leave it empty when the entry has none. `useUntil` is optional. Leave it empty for facts that do not go stale (a finished job, a
quote); set it for prices, counts and licences, which need a check on that date.
