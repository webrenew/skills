# Post Package

Metadata, schema and the two ways to save a post. Fill every value from the brief, the kit and
the business identity. Never invent an author, a date or an image.

## BlogPosting JSON-LD

Render it on the post page, from the post and the kit, not by hand per post. If the blog
template has no JSON-LD yet, add it once to the template.

```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "Water heater leaking from the bottom? What it means",
  "description": "A leak from the tank means replacement; a leak from a valve is often a cheap repair. How to tell which one you have, from a Charleston plumber.",
  "image": ["https://harborplumbing.com/images/blog/water-heater-leak-cover.jpg"],
  "datePublished": "2026-11-04",
  "dateModified": "2026-11-04",
  "author": {
    "@type": "Person",
    "name": "Sam Harbor",
    "jobTitle": "Owner and master plumber",
    "url": "https://harborplumbing.com/about/sam-harbor"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Harbor Plumbing",
    "url": "https://harborplumbing.com",
    "logo": { "@type": "ImageObject", "url": "https://harborplumbing.com/logo.png" }
  },
  "mainEntityOfPage": "https://harborplumbing.com/blog/water-heater-leaking-from-bottom"
}
```

- `headline` matches the H1. On a Launch post the H1 is the post `title`, so `headline`
  equals `title`. `description` matches the meta description.
- `dateModified` changes only when the content changes in a real way (see `content-refresh`).
- In Next.js, escape `<` in the JSON (`.replace(/</g, "\\u003c")`), as `launch-local-seo` does.
- Validate with the Rich Results Test before the first post goes live.

## FAQ markup

Google stopped showing FAQ rich results on 7 May 2026, so `FAQPage` markup gives no display in
Search. What helps is the visible Q&A itself: H2 questions with a one-sentence answer. If a
template already outputs `FAQPage`, it must match the visible questions and answers word for
word. Do not add it to new posts for display.

## Launch: `write_post`

Call `list_posts` first and confirm the slug is new. Call `write_post` only after the owner
approves. A new post needs `title`, `publishedAt` and `updatedAt`.

```json
{
  "post": {
    "slug": "water-heater-leaking-from-bottom",
    "title": "Water heater leaking from the bottom? What it means",
    "description": "A leak from the tank means replacement; a leak from a valve is often a cheap repair. How to tell which one you have, from a Charleston plumber.",
    "cover": "https://harborplumbing.com/images/blog/water-heater-leak-cover.jpg",
    "category": "water-heaters",
    "categoryLabel": "Water heaters",
    "publishedAt": "2026-11-04",
    "updatedAt": "2026-11-04",
    "blocks": [
      {
        "type": "text",
        "html": "<p>A leak from the bottom of the tank itself almost always means the tank has rusted through, and it must be replaced. A leak from a valve, pipe or fitting near the bottom is often a repair that costs much less.</p><p>Last month in Mount Pleasant we found water under a 1998 tank. The drain valve was dry; the rust was at the seam.</p>"
      },
      {
        "type": "images",
        "cols": 1,
        "items": [
          {
            "src": "https://harborplumbing.com/images/jobs/job-2026-09-mtp-water-heater-1.jpg",
            "alt": "Rusted seam at the base of a 1998 water heater tank, the source of the leak",
            "caption": "The tank seam on a Mount Pleasant job, October 2026"
          }
        ]
      },
      {
        "type": "text",
        "html": "<h2>How do I find where the leak starts?</h2><p>Dry the tank and the floor, then watch for 10 minutes.</p><ol><li>Turn off the power, or set the gas valve to pilot.</li><li>Dry the base of the tank and the floor.</li></ol><p>See our <a href=\"/services/water-heaters\">water heater repair prices and service area</a>.</p>"
      }
    ]
  }
}
```

Blocks (the one place this skill defines them):

| Block | Fields |
|---|---|
| `text` | `html` with only `p`, `h2`, `h3`, `h4`, `ul`, `ol`, `li`, `a`, `strong`, `em`, `br`, `blockquote`. No `h1` (the template renders the title), no tables, no inline styles. |
| `images` | `cols` 1 to 6, and `items`: `{ src, alt?, caption?, ratio? }`. Always give `alt`. |
| `video` | `provider` (`youtube` or `vimeo`) and `id` |

- To update a post, send the slug and only the fields that change. Send `blocks` only to
  replace the whole body.
- `post_history` lists the last 10 versions; `restore_post` puts one back.

## Other sites: Markdown

```markdown
---
title: "Water heater leaking from the bottom? What it means"
description: "A leak from the tank means replacement; a leak from a valve is often a cheap repair. How to tell which one you have, from a Charleston plumber."
slug: water-heater-leaking-from-bottom
category: water-heaters
author: sam-harbor
publishedAt: 2026-11-04
updatedAt: 2026-11-04
cover: /images/blog/water-heater-leak-cover.jpg
coverAlt: "Plumber pointing to the rusted base of a water heater tank"
draft: true
---
```

Match the field names the site's blog already reads. Add a separate `seoTitle` only when the
blog template reads one and the H1 is longer than 60 characters. Keep `draft: true` until the
owner approves.
