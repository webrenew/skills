---
name: content-topic-plan
description: >
  Decide what a small business writes next and build an editorial calendar the owner can
  keep: real customer questions, ranked by the leads they can bring, each tied to a service page
  and to one first-hand asset. Use this skill when the user asks what to blog about, wants
  content ideas, a content plan, an editorial or content calendar, topic clusters, small-business
  keyword research, blog topics, or more traffic from search and AI answers (AI Overviews,
  ChatGPT, Perplexity). Exports the calendar as CSV and ICS.
---

# Topic Plan: Know What to Write Next

**RULE: Every topic is a real question a customer asked, tied to one service page, with one
first-hand asset only this business has. No city-swap pages, no bulk batches.**

Small businesses do not win search with volume. They win with answers to the questions their
own customers ask, written by someone who did the work. Google's spam policies name "scaled
content abuse": many pages made mainly to rank, by people or by AI. A plan of two good posts a
month beats fifty thin ones, and it is a plan the owner can keep.

Load the content kit first (`content-voice-and-proof`). The readers, places and proof bank
decide which topics this business can write well.

## 1. Collect questions from real sources

Collect questions in the customers' own words. Use `references/question-sources.md` for where
to look and how to export each source.

| Source | What it gives |
|---|---|
| Lead forms and emails | The exact words people use before they hire |
| Call notes, the owner's memory | The questions asked on every job |
| Reviews (the business's and competitors') | Worries and outcomes that matter |
| Google Business Profile | Public questions on the profile, and the search terms in Performance |
| People Also Ask, autocomplete | How people phrase the question in search |
| Search Console, Queries report | Questions the site already shows for, with clicks and position |
| Seasons and local events | Freeze warnings, storm season, school start, tax deadlines |

Aim for 30 to 60 raw questions. Merge duplicates that ask the same thing in different words.

## 2. Tag each question by intent

| Intent | The reader wants to | Example | Best format |
|---|---|---|---|
| `learn` | Understand a problem | "Why is my water heater making noise?" | Blog post |
| `do` | Fix it themselves | "How to relight a pilot light" | Blog post with steps and a safety limit |
| `compare` | Choose between options | "Tankless vs tank water heater" | Blog post with an honest comparison |
| `hire` | Pick a business now | "Water heater repair Mount Pleasant" | Service page, not a post |

`hire` questions belong on service pages (see `launch-local-seo`). A post that targets a
`hire` query competes with the business's own service page.

## 3. Map each topic to a service page

Each post supports one service page, its hub. The post links to the hub, and the hub links
back to its best posts (see `content-blog-post`, step 4).

- A topic with no matching service is off-plan unless the owner wants to add the service.
- Group topics by hub. A hub with no posts is a gap. A hub with ten posts and no leads needs
  a better service page, not more posts.

## 4. Check what exists

Before you add a topic, check that no existing post already answers it.

- **Launch sites:** call `list_posts` and read the titles, slugs and categories. Call
  `read_post` when a title is close.
- **Other sites:** read the sitemap or the blog index.
- Same question already answered: mark the topic `refresh` and hand it to `content-refresh`.
  Two posts on one question compete with each other.

## 5. Score and rank

Score each topic from 0 to 3 on each line. Use `references/scoring.md` for the scale.

| Factor | Weight | Asks |
|---|---|---|
| Lead value | x3 | Does this reader hire soon, for a profitable service? |
| Proof on hand | x2 | Is there a real job, photo, number or quote in the proof bank for it? |
| Search demand | x1 | Do people search for it (Search Console, People Also Ask, autocomplete)? |
| Effort | minus x1 | How much owner time does it need (interview, photos, review)? |

**Gate:** a topic with proof 0 is not scheduled. Ask the owner for one first-hand asset (a
photo, a job, a number, a story), or make the answer a short FAQ on the service page.

Every scheduled topic names its **first-hand asset** in the plan: "photos from job #4471",
"Sam's checklist from 18 years of service calls", "2025 job count by month".

## 6. Set a cadence the owner can keep

Ask how many hours a month the owner can give: about 45 to 60 minutes per post or case study,
for the interview, photos and approval, and about 30 minutes per refresh.

| Owner time per month | Cadence |
|---|---|
| 1 hour | 1 post |
| 3 hours | 2 posts + 1 case study (`content-case-study`) |
| 5 to 6 hours | 4 posts + 1 case study + 1 refresh (`content-refresh`) |

Never schedule more than the owner can approve. A post waits for approval; it never goes out
on silence (see `content-publish-check`). Put seasonal topics 4 to 6 weeks before the season.
Spread posts evenly; do not batch a month's posts on one day.

## 7. What not to plan

- **City-swap pages:** the same post for each town with the name changed. These are doorway
  pages. A town gets its own post only with real local substance (a job there, a local fact).
- **Bulk batches:** 20 posts written in one sitting from a keyword list. Each post needs its
  own brief and its own proof.
- **Topics outside the claim limits:** a topic that needs a price, a promise or advice the
  business cannot give.
- **News and trends** with no link to a service.

## Output

```
## Topic plan for <business>, <months>

### Ranked topics
| # | Question (customer words) | Intent | Hub page | First-hand asset | Score | Status |

### Calendar
| Date | Type (post / case study / refresh) | Topic | Asset to collect | Owner task and due date |

### Not planned, and why
[city-swap ideas, topics with no proof, hire topics that belong on service pages]

### Files
content-plan.csv and content-plan.ics (format in references/calendar-export.md)
```

## Related skills

- `content-voice-and-proof`: the readers and proof bank this plan draws on.
- `content-blog-post`: writes each scheduled post from its brief.
- `content-case-study`: the monthly case study in the cadence.
- `content-refresh`: takes topics that an existing post already covers.
- `launch-local-seo`: service pages, the hubs every post links to.
- `seo-technical`: sitemaps and indexing for the new posts.
