# Content Kit Format

The kit adds only what content needs. Identity comes from `lib/business.ts`
(`launch-local-seo`). Services, price guides, the booking link, tone, written policies and
`neverSay` come from the business profile, `lib/business-profile.ts` (shape below). Never
copy those fields into the kit.

## Code sites: `lib/content-kit.ts`

```ts
// lib/content-kit.ts
import { business } from "@/lib/business"                   // launch-local-seo: the one identity
import { businessProfile } from "@/lib/business-profile"    // services, prices, policies, tone, neverSay (below)

export type ProofType = "job" | "number" | "photo" | "quote" | "credential" | "award"

export interface ProofEntry {
  id: string                      // "job-2026-09-mtp-water-heater"; also in photo file names
  type: ProofType
  summary: string                 // one sentence, true and checkable
  place?: string                  // town or neighborhood, never a street address
  date: string                    // YYYY-MM-DD
  source: string                  // job record, invoice, review URL, license lookup, photo file
  consent: "not-needed" | `written ${string}` | "pending"
  useUntil?: string               // YYYY-MM-DD: check again after this date
  photos?: { file: string; alt: string }[]
}

export const contentKit = {
  version: 1,
  profileVersion: businessProfile.version,   // the profile this kit was checked against
  voice: {
    // The profile's tone (it wins: reply agents read it), plus detail only content needs.
    summary: `${businessProfile.tone} Explains the why. Never talks down.`,
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
    licenses: [] as { name: string; number: string; lookupUrl: string }[],
    // The guarantee wording lives in businessProfile.policies.guarantee, never here.
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
}
```

When the proof bank passes about 50 entries, or the owner wants to add entries from a phone,
move `proof` to a database table with the same fields. Keep the rest of the kit in code.

## Sites without a code store: `content-kit.md`

Same sections, as headings: `Voice`, `Readers`, `Places`, `Claim limits`, `Authors`,
`Proof bank`. Write one line at the top:

> Identity: see the business identity. Services, prices, policies, tone and the booking link:
> see the business profile. Do not copy them here.

Write the proof bank as a table with the same columns as `ProofEntry`.

## The business profile

The business profile is the one store for services, prices, written policies, tone and the
booking link. If the business already keeps them in its own config, point the kit at that
file instead. Otherwise create it once, as `lib/business-profile.ts` in code or
`business-profile.md` beside the kit (same fields):

```ts
// lib/business-profile.ts
export type PolicyKey = "cancellation" | "refund" | "reschedule" | "deposit" | "guarantee"

export const businessProfile = {
  version: 1,   // bump on every change; the kit and each post record the version they used
  services: [
    { key: "water-heater", name: "Water heater repair and replacement", priceGuide: "Repairs from $149; replacement quoted on site" },
    { key: "drain", name: "Drain cleaning", priceGuide: "From $129" },
  ],
  // undefined until the live booking page exists; then paste its URL here (for example
  // "https://cal.com/<business>/visit"). The key stays, so code that reads it still compiles.
  bookingUrl: undefined as string | undefined,
  tone: "Friendly, direct, no jargon. Sign as Sam.",   // the voice in one line; the kit builds on it
  // Written terms, word for word, only for the keys the business has written down: the terms
  // of doing business (cancellation, refund, reschedule, deposit) and the guarantee, the
  // promise about the work. Posts and replies quote a value word for word. Omit an unwritten
  // key; never write a placeholder such as "do not mention".
  policies: {
    cancellation: "Free to cancel up to 24 hours before the visit.",
  } as Partial<Record<PolicyKey, string>>,   // widened, so a missing key reads as undefined
  // Multi-word phrases that no post and no customer reply may contain. Checks match them as
  // substrings, so never add single common words.
  neverSay: ["same-day", "lifetime guarantee", "cheapest in town"],
} as const
```

Identity (name, phone, hours, service area) stays in `lib/business.ts`. Never keep a second
copy of the profile in the kit. If an older kit still has `claimLimits.guarantee`, move the
wording, word for word, into `businessProfile.policies.guarantee` and delete the field. Any
agent that drafts replies to customers later reads the same file (see
`launch-agent-guardrails`, section 2).

## Proof bank examples

| id | type | summary | place | date | source | consent | useUntil |
|---|---|---|---|---|---|---|---|
| job-2026-09-mtp-water-heater | job | Replaced a leaking 1998 40-gallon tank with a 50-gallon unit in one visit | Mount Pleasant | 2026-09-14 | Job #4471, 6 photos | written 2026-09-15 | |
| num-2025-jobs | number | 1,212 service calls in 2025 | | 2025-12-31 | Job system export, Jan 2026 | not-needed | 2026-12-31 |
| quote-dana-r | quote | "They showed me the old part and explained why it failed." | Summerville | 2026-08-02 | Google review link | written 2026-08-05 | |
| cred-master-plumber | credential | SC Master Plumber license | | 2026-01-01 | State license lookup link | not-needed | 2026-12-31 |

Photos live in the site's media storage, named with the entry `id`
(`job-2026-09-mtp-water-heater-1.jpg`). In the Markdown table, add a `photos` column with each
file name and its alt text, or leave it empty when the entry has none. `useUntil` is optional. Leave it empty for facts that do not go stale (a finished job, a
quote); set it for prices, counts and licenses, which need a check on that date.
