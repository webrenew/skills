---
name: content-repurpose
description: >
  Turn one published blog post or case study into two to three weeks of channel posts without
  retyping: Google Business Profile updates and offers, Facebook, Instagram, Nextdoor, LinkedIn,
  a short video script, a service-page FAQ entry and an email to opted-in contacts, each in the
  channel's native format, with UTM tags on every link and a posting schedule. Use this skill
  when the user asks to repurpose content, share a post, "post this on social", write Google
  Business Profile posts, social posts from a blog, a newsletter or email from a post, or a
  week of updates from one article.
---

# Repurpose: One Post Becomes a Week of Updates

**RULE: Each channel gets its own native post, written for how people read there, from facts
already approved in the source post. Nothing new is claimed, and every link carries UTM tags.**

The owner has already approved the facts in the post. Repurposing reuses those facts, so a
week of updates costs minutes, not hours. The work is to fit each channel, not to paste the
same paragraph everywhere.

## 1. Start from an approved source

- The source is a published post or case study that passed `content-publish-check`.
- Copy facts, prices, quotes and photos only from the source and the proof bank. A new claim
  in a social post needs the same check as a new claim in a post.
- Pull out the parts that travel: the one-sentence answer, the best photo, one first-hand
  detail, one number, one customer quote (if consent covers social use), the call to action.

## 2. Pick the channels the business uses

Write only for channels the business already posts on and can answer comments on. A channel
with no replies for a week does more harm than no channel.

| Channel | Best for | Format notes |
|---|---|---|
| Google Business Profile | Local searchers about to call | An update or an offer with a photo and a button; no phone number in the text |
| Facebook | Past customers, neighbours | 2 to 4 short lines, a real photo, the link |
| Instagram | Before-and-after, visual work | A photo carousel; the caption carries the answer; links do not click in captions |
| Nextdoor | Homeowners nearby | Post from the business page; helpful first, no hard sell |
| LinkedIn | B2B services, the owner's network | From the owner's profile, a short story with a lesson |
| Short video | Reels, Shorts, TikTok | 30 to 60 seconds, real job footage, captions on |
| Service-page FAQ | Search and AI answers | The question and the 40 to 60 word answer, with a link to the post |
| Email | Opted-in contacts only | One topic, one link, an unsubscribe link and the postal address |

`references/channel-formats.md` has the length limits, image sizes and a worked example for
each channel.

## 3. Write each post natively

- **Lead with the reader's problem or the result,** not "New blog post!".
- **One post, one action.** The link to the post, or the booking or call button.
- **Google Business Profile:** no phone number or email in the text; Google can reject the
  post. Use the Call or Book button. In the profile's Updates area, use Add update for tips and
  project posts and Add offer for a real promotion with dates and terms.
- **Instagram:** put the answer in the caption. The link goes in the bio or a story link
  sticker; say "link in bio" only when it is there.
- **Email:** send only to contacts who opted in to marketing email. Include a one-click
  unsubscribe link and the business's postal address. Follow the email rules in
  `launch-speed-to-lead`; never add a lead to a list without their consent.
- **Customer quotes and photos:** only when the written consent covers social media, not only
  the website.
- **Hashtags:** 0 to 5, specific ("#CharlestonPlumber"), never a block of 30.
- **No engagement bait** ("Comment YES if...") and no fake urgency.

## 4. Tag every link

Every link back to the site carries UTM tags, so the monthly report (`content-refresh`) can
show which channel brings leads. Build them with the Webrenew UTM link builder
(webrenew.com/tools/utm-link-builder) or by hand:

| Channel | `utm_source` | `utm_medium` | `utm_campaign` | `utm_content` |
|---|---|---|---|---|
| Google Business Profile | `google` | `organic` | `gbp` | post slug |
| Facebook | `facebook` | `social` | post slug | `post`, `story` |
| Instagram | `instagram` | `social` | post slug | `bio`, `story` |
| Nextdoor | `nextdoor` | `social` | post slug | `post` |
| LinkedIn | `linkedin` | `social` | post slug | `owner`, `page` |
| Email | `newsletter` | `email` | post slug | `issue-YYYY-MM` |

GBP links follow `launch-local-seo` (`utm_campaign=gbp`), so profile traffic stays in one
campaign; the post slug goes in `utm_content`. Use lowercase and hyphens everywhere.

## 5. Spread it over two to three weeks

One burst on one day reaches fewer people than the same posts spread out. A sample schedule:

| Day | Channel | Angle |
|---|---|---|
| 0 | Service-page FAQ | Add the question and answer, link to the post |
| 0 | Google Business Profile | The answer and the best photo, "Learn more" button |
| 1 | Facebook | The first-hand story, the link |
| 3 | Instagram | Carousel: the problem, the cause, the fix |
| 5 | LinkedIn or Nextdoor | The lesson from the job, or the local tip |
| 8 | Short video | 45 seconds at the job, captions on |
| 10 | Email | Only in the business's regular newsletter, if it has one |
| 14 | Google Business Profile | A second angle: a different photo or the "when to call a pro" tip |

Move the days to fit the owner's own posting rhythm. Keep at least two days between posts on
the same channel.

## 6. Approval

Each channel post gets its own approval card (see `content-publish-check`), because the
owner approves one item per tap. The facts are already approved in the source, so a card
lists a confirmation only for new wording. Send the cards together for the owner to tap
through, or each one a day before its date. A rejected post leaves the schedule; the others
keep their dates. Never post on silence.

## Output

```
## Source
[post title, URL, approved date]

## Posts
### Google Business Profile, day 0
[paste-ready text] · Photo: [file, alt] · Button: [type] · Link: [full URL with UTM]
### Facebook, day 1
...

## Schedule
| Date | Channel | Post | Link (with UTM) | Photo | Status |

## Notes
[consents to confirm for social use, channels skipped and why]
```

## Related skills

- `content-blog-post` and `content-case-study`: the sources this skill repurposes.
- `content-publish-check`: the approval card for each channel post.
- `content-refresh`: reads the UTM data back in the monthly report.
- `launch-local-seo`: Google Business Profile rules and the `gbp` UTM campaign.
- `launch-speed-to-lead`: the email consent and unsubscribe rules.
- `vercel-marketing-analytics`: events that tie a UTM visit to a lead.
