---
name: content-case-study
description: >
  Turn a finished job into a case study that wins the next one: pick a won job with photos, get
  written consent, interview the customer in five questions, and write problem, what we found,
  what we did, the result in numbers and the customer's own words, within the FTC rules on
  testimonials and reviews. Use this skill when the user asks for a case study, a project post,
  a job story, a before-and-after, a testimonial, a success story, a portfolio entry, "post
  about this job", or "show off this project".
---

# Case Study: Finished Jobs Become Proof That Wins the Next One

**RULE: Only real jobs, real numbers and the customer's own words, with written consent. Never
a made-up, merged or AI-written testimonial, and never an edit that changes what the customer
meant.**

A case study is the strongest proof a small business can publish: a neighbour with the same
problem, what the business did, and what changed. It also feeds the proof bank, so every later
post can point to it.

## 1. Pick the job

A good case study job:

- Is done and won (status `won` in `launch-lead-capture`), and the customer was happy.
- Matches a core service and a question in the topic plan (`content-topic-plan`).
- Has photos: before, during and after, taken by the business.
- Has a result someone can measure: time, money, a number, a problem that stopped.
- Is typical. A one-off miracle sets a promise the business cannot keep.

Ask the owner for one job a month. The review request after a won job (`launch-speed-to-lead`)
is a good moment to ask for the case study too.

## 2. Get written consent first

No draft goes to anyone before consent is in writing. Use
`references/consent-template.md`.

- Consent says exactly what the business will use: name or initials, neighbourhood, photos
  of the home, quotes, and where (website, social media, email, print).
- The customer can review the final text before it goes live, and can withdraw consent later.
  Withdrawal means the business removes it from the site and stops new use.
- Record the consent in the proof bank: `consent: written YYYY-MM-DD`, and keep the signed
  copy.
- **Clinics and health businesses:** a patient story, photo or quote needs a HIPAA-compliant
  marketing authorization, not only a consent form. Use the practice's own authorization form.
- **Children:** a parent's written consent for any child's name, face or story.
- Never offer payment, a discount or a gift for a positive story. If the customer got any
  discount or connection (a family member, a staff member, a free service), the case study
  says so.

## 3. Interview the customer (five questions)

Ask by phone or email. Use `references/customer-interview.md` for the questions and how to
take notes. Record the answers word for word. With permission, record the call.

The customer's words go into the post as they said them. Light trims for length use "...",
and never change the meaning or make it stronger.

## 4. Structure

| Section | What it holds |
|---|---|
| Title | The outcome and the place: "A 1998 water heater replaced in one visit in Mount Pleasant" |
| Summary | 2 to 3 sentences: who, the problem, the result with a number |
| The problem | What the customer saw, in their words; why it mattered to them |
| What we found | The cause, with a "before" photo; what a reader in the same spot needs to know |
| What we did | The work, in steps; choices made and why; time on site |
| The result | Numbers: time, cost range if the owner allows, what stopped or changed; an "after" photo |
| In their words | The customer's quote, word for word, with first name or initials and neighbourhood, as consent allows |
| What this means for you | When the reader's problem is the same, and when it is not |
| Action | One call to action, copy above the button, linked to the service page |

Length: 400 to 900 words. Photos carry much of it.

## 5. Privacy

- **Neighbourhood or town only.** Never a street address, house number, or a photo that shows
  one (street signs, house numbers, mailboxes, licence plates).
- Strip GPS location data from every photo file.
- No faces, family photos, documents or screens in the background without consent.
- Business customers: the company name only with their approval, and nothing under an NDA.

## 6. The rules on testimonials

The FTC's rule on consumer reviews and testimonials (16 CFR Part 465, in force since October
2024) and its Endorsement Guides apply to case studies.

- **No fake testimonials.** No quote from a person who does not exist or did not have the
  experience. No AI-written testimonial, and no quote "improved" by an AI.
- **No merged customers.** One case study is one real job.
- **No edits that change the meaning.** No out-of-context quotes.
- **Disclose connections.** Staff, family, a free or discounted job, a gift: say so, next to
  the quote.
- **Typical results.** If the result is not typical, say what is typical.
- **No review schema.** Do not add `Review` or `AggregateRating` markup for the business's own
  case studies or testimonials. Use `BlogPosting` or `Article` (see `content-blog-post`).

Run `content-publish-check` on the draft. The consent is a check item, and a case study with
no written consent is NOT READY.

## 7. Save it, then reuse it

- Save the case study like a post (`content-blog-post`, step 7), in a "Projects" or "Case
  studies" category.
- Add proof bank entries: the job, the photos, the quote, each with the consent date.
- Link to it from the hub service page, near the call to action.
- Hand it to `content-repurpose`: a before-and-after carousel and a Google Business Profile
  update are the natural first posts, if consent covers social use.

## Output

```
## Job and consent
[job id, service, neighbourhood, date, consent date and scope, what still needs consent]

## Case study
[the complete text, top to bottom, ready to publish]

## Photos
| File | Shows | Alt text | Consent covers |

## Proof bank entries
[new entries in the kit format]

## Notes
[claims to confirm with the owner, anything the customer must review before publish]
```

## Related skills

- `content-voice-and-proof`: the proof bank this skill adds to.
- `content-publish-check`: the claim, consent and approval check before publish.
- `content-blog-post`: how to save and package the case study.
- `content-repurpose`: before-and-after posts for social channels.
- `launch-speed-to-lead`: the review request after a won job, a good time to ask.
- `launch-local-seo`: review rules (never gate, never pay) that apply here too.
