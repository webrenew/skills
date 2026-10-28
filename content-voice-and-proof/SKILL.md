---
name: content-voice-and-proof
description: >
  Build a small business's content kit so every post sounds like the owner and proves what it
  says with real work: the owner's voice, the readers, services, places served, a proof bank of
  real jobs, numbers, photos and approved quotes, claim limits and a real byline. Use this skill
  before the first blog post, when the user asks to set up brand voice, tone of voice, an author
  bio, E-E-A-T, "write like us", "make it sound like me", or a content kit, and whenever
  content sounds generic, bland or "like AI". The other content-* skills load this kit first.
---

# Voice and Proof: Content That Sounds Like the Owner and Proves It

**RULE: Write only what this business can show. Every post rests on the owner's own words and
on real work from the proof bank; anything a competitor could publish with only the name
changed does not go out.**

Readers and search engines both look for the same thing: signs that a real person with real
experience wrote the page. Google's quality guidelines call it E-E-A-T (experience, expertise,
authoritativeness, trust). A small business has more of this than any large site, but only if
someone writes it down. This skill writes it down once, in one place, so every post can use it.

## What the kit holds

| Part | What it is | Where it comes from |
|---|---|---|
| Identity | Name, phone, hours, service area | `lib/business.ts` (`launch-local-seo`). Never copied into the kit. |
| Services and prices | Each service, its price guide, phrases to never say | `lib/business-profile.ts` (`launch-lead-triage-agent`). Never copied into the kit. |
| Voice | How the owner sounds: words to use, words to avoid, sentence habits | The owner's own emails and review replies |
| Readers | Two or three kinds of customer, their situation, their worry, their words | Reviews, lead forms, calls |
| Places | Towns and neighborhoods served, with true local detail | The owner, the job history |
| Proof bank | Real jobs, numbers, photos and approved quotes, each with source, date and consent | Job records, photos, reviews |
| Claim limits | What the business may say about prices, licenses, guarantees, timing | The owner, license records, the written guarantee |
| Authors | Real names, roles, credentials, a short bio and a photo | The owner and staff |

**One store, not two.** The site, the schema, the lead triage agent and every post read the
business's facts from the same files. The kit adds only what content needs. When a fact
changes (a new phone number, a new price guide), change it in `lib/business.ts` or
`lib/business-profile.ts`, and bump the profile version. Never fix it in a post.

## 1. Interview the owner (12 questions or fewer)

Ask in one message, or on a 20-minute call. Use `references/owner-interview.md`. The answers
fill the voice, readers, places, claim limits and authors. Do not ask what the site, the
business profile or the reviews already answer.

If the owner has no time, ask the five questions marked **core** and fill the rest later.
Never fill a gap with a guess. Leave the field empty and put the question on the owner
to-do list. A post that needs an empty field (a license number, the guarantee, a bio) cannot
pass `content-publish-check` until the owner fills it.

## 2. Take the voice from the owner's own writing

Ask for 5 to 10 things the owner wrote to customers: emails, quotes, replies to reviews, text
messages, social posts. Owner-written text beats any description of a voice.

From the samples, write down:

- **Words we use:** the owner's own terms for the work ("service call", not "appointment";
  "crawl space", not "sub-floor area"). Keep the trade terms customers also use.
- **Words we avoid in content:** words the owner dislikes in posts. Keep them in the kit's
  `voice.wordsWeAvoid`. Posts also drop the AI tells listed in the `content-blog-post`
  skill; that list stays there.
- **Phrases never to say anywhere:** a claim or phrase that no lead reply and no post may use
  ("lifetime guarantee", "cheapest in town") goes in `neverSay` in `lib/business-profile.ts`.
  The triage agent matches `neverSay` as a substring of every reply draft, so add only
  multi-word phrases there, never single common words.
- **Sentence habits:** short or long, "we" or "I", how they greet and sign off, how much humor.
- **Three sample sentences** in the voice, taken word for word from the samples.

Write the voice in plain terms. "Friendly, direct, explains the why, never talks down, signs as
Sam" is useful. "Authentic and approachable" is not.

## 3. Take the customers' words from reviews and leads

Read the last 30 to 50 reviews, lead form messages and call notes. Write down:

- The exact phrases customers use for their problem ("water coming through the ceiling",
  "AC blowing warm air"). Posts use these words in titles and first lines.
- The questions they ask before they hire, and the worries behind them (price, mess, trust,
  timing).
- The outcomes they praise ("cleaned up after", "explained everything").

Strip names and contact details. Keep the wording.

## 4. Build the proof bank

Each entry is one fact a post can show. Use the format in `references/content-kit.md`.

| Field | Rule |
|---|---|
| `type` | `job`, `number`, `photo`, `quote`, `credential` or `award` |
| `summary` | One sentence, what happened or what is true |
| `place` | Town or neighborhood only. Never a street address. |
| `date` | When the job was done or the fact was true |
| `source` | Where it can be checked: job record, invoice, review link, license lookup, photo file |
| `consent` | `not-needed` (the business's own fact), `written YYYY-MM-DD`, or `pending`. Customer quotes, names, faces and homes need written consent. |
| `useUntil` | When to check it again: prices and counts go stale |

Start with 10 entries. Good first entries: three recent jobs with photos, the license and
insurance numbers, years in business, jobs done last year (from the records, not memory),
two or three approved review quotes, the written guarantee. `content-case-study` adds more
entries each time a job is finished.

Rules:
- A number goes in only with a source. "Over 2,000 jobs" needs the job records; a round
  guess is a claim the business cannot defend.
- A quote goes in word for word, with the reviewer's consent if it names them or appears
  outside the review site.
- Photos are real and the business took them, or has the right to use them. Never stock
  photos or AI images shown as the business's work.

## 5. Write the claim limits

Claim limits stop a post from promising what the business does not offer. Fill each line or
mark it "do not mention".

- **Prices:** only the price guides in `businessProfile.services`, as ranges or "from" prices,
  or "do not publish prices".
- **Timing:** what the business can promise ("most repairs in one visit") and what it cannot
  ("same-day").
- **Licenses and insurance:** name, number, issuer, and the public lookup link.
- **Guarantee:** the exact written wording. Posts quote it word for word or link to it.
- **Comparisons:** never name or run down a competitor.
- **Regulated topics:** health, legal, money and safety claims follow `content-publish-check`.

## 6. Name a real author

Every post carries a real person's name, not "Admin" or the business name.

- Name, role, years in the trade, and credentials that a reader can check.
- A 40 to 60 word bio in the owner's voice, and a real photo.
- An author page on the site that lists the bio and the author's posts. `BlogPosting` schema
  points to it (see `content-blog-post`).
- When an agent drafts and the owner edits and approves, the owner is the author. The
  approval log (see `content-publish-check`) records who approved each version.

## 7. Store the kit

- **Code sites:** `lib/content-kit.ts`, which imports identity and services from the existing
  files and adds only the content parts. See `references/content-kit.md` for the shape.
- **Sites without a code store** (a Launch site, another CMS): keep `content-kit.md` with the
  site files, in the same sections. Point to the business profile for identity and prices;
  do not copy them.
- Give the kit a `version`. Bump it on each change, and record the version a post used.
- Photos live in the site's media storage, with the proof bank entry id in the file name.

## Output

```
## Content kit (version N)
[the complete lib/content-kit.ts or content-kit.md, ready to save]

## Owner to-do
[questions still open, consents to collect, photos to send, in plain words for the owner]

## Changes to the business profile
[multi-word phrases added to neverSay, price guides to confirm; bump the profile version]
```

## Related skills

- `content-topic-plan`: picks what to write, using the readers and the proof bank.
- `content-blog-post`: writes each post from this kit.
- `content-publish-check`: checks every claim against the proof bank and the claim limits.
- `content-case-study`: turns finished jobs into new proof bank entries.
- `asd-ste100-writing`: the plain-English rules the voice sits on top of.
- `launch-local-seo`: owns `lib/business.ts`, the one business identity.
- `launch-lead-triage-agent`: owns `lib/business-profile.ts`, the services, prices and
  `neverSay` list that the kit reuses.
