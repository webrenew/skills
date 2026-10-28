---
name: content-blog-post
description: >
  Write one blog post for a small business that answers one customer question better than anyone
  nearby: a brief first, an answer-first structure that search engines and AI answers can quote,
  real proof from the business's own jobs, internal links to the service page, real photos,
  metadata and BlogPosting schema, ready to save with Launch's write_post or as Markdown. Use
  this skill when the user asks to write a blog post, an article, a how-to, a guide, an FAQ
  answer, a "repair or replace" or "cost of" post, SEO content, or content for AI Overviews,
  and when they want a post drafted from a topic in the content plan.
---

# Blog Post: Answer One Question Better Than Anyone Nearby

**RULE: One post, one question, one reader, and something only this business knows. If a
competitor could publish the post with only the name changed, do not write it.**

A good small-business post answers the question in the first lines, shows the reader that
this business has done the work, and gives one clear next step. It is as long as the answer
needs and no longer.

## 0. Load the kit

Load the content kit from `content-voice-and-proof`: voice, readers, places, proof bank, claim
limits, authors. Load identity and services from `lib/business.ts` and
`lib/business-profile.ts` (or the business profile on a Launch site).

No kit yet: ask the owner five questions and continue. Mark the post "kit missing" in the
notes, and suggest `content-voice-and-proof` next.

1. Who asks this question, and what is going on for them?
2. What is your short answer, the one you give on the phone?
3. Tell me about a real job where this came up. Do you have photos?
4. What may we say about price and timing?
5. Who signs the post?

## 1. Brief first

Write the brief and stop for the owner's check before a long draft. A wrong brief wastes
the whole draft.

| Brief field | Example |
|---|---|
| Question, in the customer's words | "Water heater leaking from the bottom: can it be fixed?" |
| Reader and situation | Homeowner, tank 10+ years old, water on the garage floor this morning |
| Intent | `compare` (repair or replace) |
| The answer, in 2 sentences | "A leak from the tank itself means the tank has failed and must be replaced. A leak from a valve or fitting above it is often a cheap repair." |
| First-hand proof | Job #4471, Mount Pleasant, 6 photos; Sam's rule of thumb from 18 years of calls |
| Service page to link | `/services/water-heaters` |
| The one action | Book a service call |
| Claim limits | Repairs "from $149" only; no same-day promise |
| Target query + 2 to 3 related | "water heater leaking from bottom"; "repair or replace water heater", "water heater pressure relief valve leaking" |

**Stop rule:** no first-hand proof, no post. Ask the owner for a job, a photo, a number or a
story. If none exists, write the answer as an FAQ entry on the service page instead.

## 2. Structure

| Part | Rule |
|---|---|
| H1 | The question, or the outcome the reader wants, in their words |
| SEO title | 60 characters or fewer; the target query near the start. A Launch post has one `title` field for the H1 and the page title: write one title that does both jobs. |
| First 40 to 60 words | Answer the question directly, in full sentences, with no lead-in. This passage is what AI answers and featured snippets quote. |
| H2s | The reader's next questions, in order. Each section opens with a one-sentence answer, then the detail. |
| Experience | What the business saw on real jobs, in the text, with a real photo: "On a call in Mount Pleasant last month, the leak came from..." |
| Steps | Numbered, one action per step, for anything the reader does |
| Price | Only ranges or "from" prices in the claim limits; say what changes the price. No price guide: say what the quote depends on. |
| When to call a pro | An honest line: what the reader can check safely, and where to stop |
| Local detail | Only true local facts from the kit (housing age, water, weather, permits). Never a town name dropped in for search. |
| Close | A 2-line summary, then one call to action. The copy sits above the button, never beside it. |
| Length | What the answer needs: usually 700 to 1,500 words. Cut any section that does not answer a reader question. |

Use `references/post-template.md` for a full outline with an example.

## 3. Voice

- Write in the owner's voice from the kit, on top of plain English (`asd-ste100-writing`).
  Run its checker in `descriptive` mode on the draft.
- Remove every AI tell in `references/ai-tells.md` and every `neverSay` phrase.
- Short paragraphs: 1 to 3 sentences. One idea per sentence.
- "You" for the reader, "we" or "I" for the business, as the owner talks.
- Facts with numbers, not adjectives: "most repairs take one visit", not "fast service".

## 4. Links

- **One required link** to the hub service page, in the body, where the reader is ready for
  it. Not only in the footer.
- **One to three links** to related posts, where they answer the next question.
- **Descriptive anchors:** "water heater repair prices", never "click here" or "read more".
- **Links back:** add a link to the new post from one or two older pages (the hub page and the
  closest post). List these edits in the output; they need approval too.
- **Outbound links** only to primary sources: the manufacturer's manual, the code or the
  regulator, the original study. Never to a competitor or a content farm.

## 5. Images

- Real job photos first, from the proof bank, with consent where a customer's home or face
  shows.
- Never stock photos or AI images shown as the business's work. A diagram is fine when it is
  labelled as a diagram.
- Alt text says what the photo shows and why it matters: "Rusted base of a 1998 water
  heater tank, the cause of the leak". No "image of", no keyword lists, under 125 characters.
- Cover image 1200 x 630 pixels for link previews, under 300 KB, WebP or JPEG.
- Strip GPS location from photo files before upload. No house numbers, licence plates or
  faces without consent.

## 6. Package

| Field | Rule |
|---|---|
| Slug | Lowercase, hyphens, 3 to 6 words, no dates or stop words: `water-heater-leaking-from-bottom` |
| SEO title | 60 characters or fewer |
| Meta description | 140 to 155 characters; the answer plus a reason to click |
| Category | The hub service name |
| Published / updated dates | `YYYY-MM-DD`; both the same on a new post |
| Author | A real person from the kit's `authors` |
| Schema | `BlogPosting` JSON-LD with the real author, dates and cover image |

- FAQ markup only for questions and answers that are visible on the page, word for word.
  Google shows FAQ rich results for very few sites now; add it only if it is true to the page.
- Never `Review` or `AggregateRating` markup for the business's own reviews. Google does not
  show stars for self-serving reviews, and fake or selected markup breaks its policies.

Use `references/post-package.md` for the JSON-LD, the `write_post` call and the Markdown
frontmatter.

## 7. Write to the site

Never publish without the owner's approval. Run `content-publish-check` on the final draft;
it ends in an approval card.

- **Launch sites:** after approval, save the post with `write_post`. Text blocks take HTML with
  `p`, `h2` to `h4`, `ul`, `ol`, `li`, `a`, `strong`, `em`, `br` and `blockquote`. There are
  no tables: write a comparison as a list. Image blocks take 1 to 6 columns; video blocks take
  YouTube or Vimeo ids. Call `list_posts` first so the slug is new. An overwrite is kept in
  `post_history`, and `restore_post` undoes it.
- **Other sites:** a Markdown file with frontmatter, in the folder the site's blog reads.

## Output

```
## Brief
[the table from step 1]

## Post
[the complete post, top to bottom, ready to paste: never a fragment]

## Metadata
| Field | Value |
[slug, SEO title (with character count), meta description (with count), category, dates,
author, cover image]

## Images
| File | Source (proof bank id) | Alt text | Consent |

## Links
[the hub link, related posts, and the 1 to 2 older pages to edit, with the anchor text]

## Notes
[claims to verify, proof to request from the owner, any rule broken on purpose and why]
```

## Related skills

- `content-voice-and-proof`: the kit this post is written from.
- `content-topic-plan`: where the question and its first-hand asset come from.
- `content-publish-check`: the claim and quality check, and the owner approval card.
- `content-repurpose`: turns the published post into channel posts.
- `asd-ste100-writing`: plain-English rules and the copy checker.
- `seo-technical`: metadata, structured data and the sitemap on the site.
- `launch-local-seo`: the service pages each post links to.
- `launch-landing-page`: the call to action rules (copy above the button).
