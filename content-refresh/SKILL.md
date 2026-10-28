---
name: content-refresh
description: >
  Find which of a small business's blog posts bring leads and calls, and fix the ones that slip:
  an inventory from the post list, Search Console, leads by landing page and a spot check of AI
  answers; a keep, refresh, merge or remove decision for each post; safe updates that keep URLs;
  and a one-minute monthly report for the owner that leads with leads and calls. Use this skill
  for a content audit, "is the blog working?", a traffic drop, outdated or old posts, content
  pruning, merging duplicate posts, a monthly content report, or blog performance.
---

# Content Refresh: Know Which Posts Bring Leads, and Fix the Ones That Slip

**RULE: Judge each post by the leads and calls it brings, then by search. Keep every URL that
earns links or visits. Change the updated date only when the content changed in a real way.**

Most small-business blogs have a few posts that bring almost all the leads, and many that
bring none. A monthly check keeps the good posts current and stops weak posts from competing
with them. It takes less time than a new post and often earns more.

## 1. Build the inventory

One row per post. Use the last 3 months, and the same 3 months a year ago for seasonal
businesses.

| Column | Source |
|---|---|
| Slug, title, category, published, updated | Launch: `list_posts`. Other sites: the sitemap or the CMS export. |
| Hub service page | The post's main service link (`content-blog-post`, step 4) |
| Leads | Leads whose `utm` data points to the post (`utm_campaign` or `utm_content` equal to the slug; `launch-lead-capture`), plus `Lead Submitted` events on the post's path (`vercel-marketing-analytics`) |
| Calls | `Call Clicked` events on the post (`launch-landing-page`, `vercel-marketing-analytics`) |
| Clicks, impressions, average position | Search Console, Pages report, filtered to the post URL |
| Top 3 queries | Search Console, Queries for that page |
| Change vs last period | Clicks and leads, up or down |
| AI answer citation | From step 2 |
| Facts that may be stale | Prices, years, counts, product models, rules in the post |

Use `references/inventory-template.md` for the sheet and the Search Console steps.

## 2. Spot-check AI answers

Pick about 10 key customer questions from the topic plan (`content-topic-plan`). Ask each in
Google (AI Overview or AI Mode), ChatGPT and Perplexity, from the business's area if possible.
Note:

- Is the business's post cited or linked? Which sources are?
- Does the answer contradict the post? Then either the post is wrong (fix it) or the answer
  is (make the post's answer block clearer, with the source).
- What do the cited pages have that the post does not: a clear answer in the first lines, a
  number, a table, a date, a named expert?

This is a spot check, not a ranking report. Answers change by person, place and day.

## 3. Decide: keep, refresh, merge or remove

| Decision | When | What to do |
|---|---|---|
| **Keep** | Brings leads or calls, facts are current | Nothing. Check again next quarter. |
| **Refresh** | Brings visits or leads, but clicks fell, position slipped, facts are stale or the answer is weak | Update facts, answer block, proof, links; step 4 |
| **Merge** | Two or more posts answer the same question and split the visits | Move the best parts into the stronger URL; 308 redirect the others to it |
| **Remove** | No leads, no visits, no links for 12 months, and no future value; or wrong and not worth fixing | Redirect (308) to the closest post or the hub page. A 410 only when nothing relates, and only with a middleware or host rule that serves it |

- A post with leads or calls is never removed. It can be merged only when it is the
  surviving URL, or when the 308 redirect sends its traffic to a post that answers the same
  question at least as well.
- A post with good links from other sites keeps its URL or gets a 308 redirect.
- When in doubt between refresh and remove, refresh once and check again in 3 months.

## 4. Refresh safely

- **Keep the URL.** Never change the slug of a post that has visits or links. If a slug must
  change, add a 308 redirect from the old URL the same day.
- **Fix the facts first:** prices from the claim limits, years, counts from the proof bank,
  product models, rules and codes.
- **Answer first:** rewrite the first 40 to 60 words to answer the question in full.
- **Add proof:** a newer job, photo or number from the proof bank.
- **Match the queries:** if Search Console shows the post appears for a question it does not
  answer, add an H2 for it, or plan a separate post if it is a different question.
- **Links:** add links to newer related posts, and from newer posts back to this one.
- **Updated date:** change `updatedAt` (and `dateModified` in the schema) only when the content
  changed in a real way: new facts, a new section, a corrected answer. Never for a typo, and
  never to look fresh. Google tells site owners not to change dates without real changes.
- **Check again:** run `content-publish-check` on the refreshed post. It needs owner approval,
  like a new post.

## 5. Merge and redirect

1. Pick the stronger URL: more leads first, then more links, then more clicks.
2. Move unique sections, proof and photos into it. Do not paste whole posts. Run
   `content-publish-check` on the merged text and get the owner's approval card for the
   merge and each removal before any write, redirect or delete.
3. Add a 308 permanent redirect from each old URL to the stronger one (Next.js `redirects()`
   with `permanent: true`, or the host's redirect settings).
4. Update internal links to point straight to the stronger URL.
5. Remove the old URLs from the sitemap.

On Launch sites, save the merged post with `write_post`, add the 308 redirect, and only then
`delete_post` the old one, so the old URL never returns a 404. Both keep the old version, so
`restore_post` can undo the overwrite or the delete (the tool contract is in the
`content-blog-post` skill's `references/post-package.md`).

## 6. The monthly owner report

One minute to read. Leads and calls first, because that is what the owner pays for. Use
`references/monthly-report.md`.

```
Blog report: October 2026, Harbor Plumbing

Leads and calls from the blog: 9 leads, 14 calls (September: 6 and 11)
Best post: "Water heater leaking from the bottom?": 5 leads, 8 calls

Fixed this month:
• Refreshed "Tankless vs tank": new 2026 prices, a job from Summerville
• Merged two drain posts into one; the old address now forwards

Needs you (5 minutes):
• Approve the refreshed "Tankless vs tank" post (link)
• Send photos from the Summerville drain job for next month's case study

Next month: 2 new posts, 1 case study, 1 refresh
```

- Numbers with the previous month next to them. No charts in the email.
- At most three owner tasks, each with the time it takes.
- No jargon: "visits from Google", not "organic sessions"; "shows up in Google", not
  "impressions".

`launch-site-health-report` sends the weekly site email. This report can go in the first
weekly email of the month, or on its own.

## Output

```
## Inventory
| Post | Hub | Leads | Calls | Clicks (change) | Position | Top query | AI cited | Decision |

## Decisions
[each refresh, merge and remove, with the reason and the redirect map]

## Refreshed posts
[the complete refreshed text for each, after content-publish-check]

## Redirects
| From | To | Type (308, or 410 with its middleware or host rule) |

## Owner report
[the monthly report, ready to send]
```

## Related skills

- `content-publish-check`: runs again on every refreshed post.
- `content-topic-plan`: new topics from the gaps this audit finds, and the AI spot-check list.
- `content-blog-post`: structure and package rules for the refreshed post.
- `content-voice-and-proof`: current prices, numbers and new proof.
- `launch-site-health-report`: the weekly email this report can join.
- `vercel-marketing-analytics`: the lead and call events by page.
- `seo-technical`: redirects, canonical URLs and the sitemap.
