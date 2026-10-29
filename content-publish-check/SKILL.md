---
name: content-publish-check
description: >
  Check a small business's blog post, case study, page or social post before it goes live, so
  nothing is published that the owner cannot stand behind: a claim ledger with a source for every
  number, price, time, guarantee, credential and outside fact; extra care for health, legal,
  money and safety topics; plain-English and voice edits; search and AI-answer checks; link,
  image and consent rights; and an owner approval card. Use this skill when the user asks to
  review, proofread, fact-check, edit or approve content, asks "is this ready to publish?",
  "check this post", "can we say this?", or before any write_post or publish step.
---

# Publish Check: Nothing Goes Live That the Owner Cannot Stand Behind

**RULE: Every number, price, time, guarantee, credential and outside fact has a source. No
source: cut it, soften it to what is true, or ask the owner. Never invent a stronger claim.**

One wrong price, one made-up statistic or one customer photo used without consent costs the
business more than a year of posts earns. This check finds those before a reader does, fixes
what it can, and gives the owner a short card to approve.

Load the content kit (`content-voice-and-proof`) and the business profile first. The proof
bank, the claim limits and the profile's prices and `policies` are the sources this check
trusts.

## 1. Build the claim ledger

Read the draft line by line. Put every checkable claim in the ledger.

| # | Claim (as written) | Type | Source | Status |
|---|---|---|---|---|
| 1 | "Repairs from $149" | price | `priceGuide` of the `water-heater` entry in `businessProfile.services` | verified |
| 2 | "Most tanks last 8 to 12 years" | outside fact | Manufacturer guide, link and year | verified |
| 3 | "We are the most trusted plumber in Charleston" | superlative | none | cut |
| 4 | "Done in one visit" | timing | Claim limits: "most repairs in one visit" | soften to "most repairs" |
| 5 | "Licensed and insured" | credential | Proof bank `cred-master-plumber` | verified |

**Types:** price, timing, guarantee, policy, credential, number (about the business), outside
fact, quote, comparison, superlative, health, legal, money, safety.

**Status:** `verified` (a source in the kit or a primary source), `owner` (only the owner can
confirm; goes on the approval card), `soften` (rewrite to what the source supports), `cut`.

Rules:
- **No "studies show", "experts say", "research proves".** Name the source or cut it.
- **Statistics** need a primary source (the study, the agency, the manufacturer) and its
  year. A blog that quotes a blog is not a source.
- **Superlatives** (best, most trusted, number one, cheapest, fastest) are cut, unless an
  independent, dated source proves them ("Best of Charleston 2026, Charleston City Paper").
- **Guarantees and policies** (cancellation, refund, reschedule, deposit) are quoted word for
  word from the profile's `policies`, or linked. No written value: `owner`, or cut.
- **Customer quotes** are word for word, with written consent in the proof bank. No edit that
  changes the meaning. Trim only with "...", and never so it says more than the customer did.
- **Prices and timing** come only from the claim limits.
- **Numbers about the business** ("1,200 jobs last year") come only from the proof bank.

## 2. High-risk topics: health, legal, money, safety

These topics can hurt a reader who follows bad advice. Google's quality guidelines call them
"your money or your life" topics and hold them to a higher standard. Use
`references/high-risk-topics.md` for the rules by industry.

- A qualified person reviews the post: a licensed professional in the field. Name them on the
  post ("Reviewed by Dr. Ana Ruiz, DDS").
- Cite the authority (the regulator, the code, the official guidance), with a link.
- Include an honest "when to call a licensed pro" section.
- No DIY steps for work that is dangerous or needs a permit (gas lines, venting, panel
  internals, structural work, roofing at height). Explain the risk and stop. Owner-level
  shutoffs that the manufacturer describes are fine: an appliance's own gas control to
  "pilot", a breaker, the main water valve.
- Follow the industry's advertising rules (dental and medical boards, the state bar for
  attorneys, financial regulators).
- No client or patient details without written authorization. A clinic needs HIPAA-compliant
  authorization before any patient story, photo or testimonial appears.

## 3. Edit passes, in this order

One pass per concern. A pass that tries to fix everything fixes nothing.

1. **Answer:** the first 40 to 60 words answer the question in full. Each H2 opens with its
   answer.
2. **Cut:** remove sections, sentences and words that add no fact, step or reason. Most drafts
   lose 15 to 25 percent here.
3. **Proof:** at least one first-hand detail from the proof bank in the first 200 words. Each
   general claim has a real example nearby.
4. **Plain English:** run the `asd-ste100-writing` checker by section (`procedural` for
   steps, `descriptive` for explanations, `marketing` for the call to action) and fix what it
   flags. Never change customer quotes, the kit's sample sentences or the byline, and keep the
   owner's "we" and "I"; list these as accepted deviations in the output. Remove the AI
   tells in the `content-blog-post` skill's `references/ai-tells.md`: stock phrases, the
   rule of three everywhere, empty openers, stacked hedges.
5. **Voice:** read it as the owner. Replace any sentence the owner would not say to a customer.
   No `neverSay` phrases and no words from the kit's `wordsWeAvoid`.
6. **Action:** one call to action, with copy above the button, that matches the post's intent.

## 4. Search and AI-answer checks

These checks apply to posts, case studies and pages. A channel post (social, Google Business
Profile, email) skips this table. Check it instead against its channel's limits (the
`content-repurpose` skill's `references/channel-formats.md`) and its link and UTM tags. All
other sections still apply to it: 1 (claim ledger), 2 (high-risk topics), 3 (every edit pass,
including plain English and AI tells), 5 (links and media rights) and 6 (approval).

| Check | Pass when |
|---|---|
| SEO title | 60 characters or fewer, target query near the start |
| Meta description | 140 to 155 characters, states the answer |
| H1 | Exactly one, and it matches the question |
| Answer-first block | The first 40 to 60 words answer the question with no lead-in |
| Slug | Lowercase, hyphens, short, no date, new (not already used) |
| Internal links | One link to the hub service page in the body; 1 to 3 related posts; descriptive anchors |
| Alt text | Every image; says what it shows; under 125 characters |
| Schema | Valid `BlogPosting` with a real author and dates; any `FAQPage` markup matches visible Q&A word for word; no self-serving review markup |
| Duplicate | No existing post answers the same question (`list_posts` or the sitemap) |
| Thin or city-swap | Not a copy of another post with the town or service name changed |
| Indexable | No `noindex`; canonical points to itself; in the sitemap after publish |

Mark each `pass` or `fix`, with the fix.

## 5. Links and media rights

- Every link returns 200 (no redirects to a home page, no 404s).
- Every image is the business's own, or licensed for this use. Record the source.
- A photo that shows a customer, their home, their car or their child needs written consent
  in the proof bank. No house numbers, street signs, license plates or faces without it.
  Strip GPS location data from photo files.
- Paid links, affiliate links and partner links use `rel="sponsored"`. A post about a
  supplier who gave a discount says so.

## 6. Owner approval

The owner approves the exact version that goes live. Use the card in
`references/approval-card.md`: the title, the link to the draft, the claims only the owner can
confirm, and one-tap Approve, Edit and Reject.

- **Never publish on silence.** No answer means no publish. Remind once after two business
  days, then wait.
- Log each decision: approver, time, version (a hash of the text or the draft id) and the
  claims they confirmed. This follows the draft, approve, send rule in
  `launch-agent-guardrails`.
- An edit after approval needs a new approval, unless it fixes only spelling.

## Output

```
## Verdict: READY | READY AFTER OWNER CONFIRMS | NOT READY
[one line: why]

## Claim ledger
| # | Claim | Type | Source | Status |

## Checks
| Check | Pass / fix | Fix |

## Corrected text
[the complete corrected post, top to bottom, ready to publish: never a diff or a fragment]

## Owner approval card
[the card from references/approval-card.md, filled in]
```

- **READY:** every claim is verified; every check passes. The card asks only for approval.
- **READY AFTER OWNER CONFIRMS:** the only open items are `owner` claims on the card.
- **NOT READY:** any high-risk topic without a qualified reviewer, any missing consent, any
  claim with no source that the post cannot work without, or a duplicate post.

## Related skills

- `content-voice-and-proof`: the proof bank and claim limits this check trusts.
- `content-blog-post`: the draft this check reviews, and the AI-tells list.
- `content-case-study`: consent and testimonial rules for customer stories.
- `content-refresh`: runs this check again on every refreshed post.
- `asd-ste100-writing`: the plain-English checker in pass 4.
- `launch-agent-guardrails`: the approval and logging rules this check follows.
- `seo-technical`: indexing, canonical and schema detail.
